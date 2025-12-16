# akshare客户端模块 - 隔离外部依赖调用
import akshare as ak
import sys
import os
import datetime

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import normalize_number

# 数据缓存字典 - 简单的内存缓存
_data_cache = {
    'stock': {},
    'etf': {},
    'fund': {}
}

# 缓存过期时间设置（秒）
CACHE_EXPIRY = {
    'stock': 300,  # 5分钟
    'etf': 3600,   # 1小时
    'fund': 3600   # 1小时
}

def _get_cached_data(data_type, code):
    """
    从缓存中获取数据
    
    Args:
        data_type (str): 数据类型 ('stock', 'etf', 'fund')
        code (str): 产品代码
    
    Returns:
        tuple: (数据, 是否有效)
    """
    if data_type in _data_cache and code in _data_cache[data_type]:
        cached_entry = _data_cache[data_type][code]
        data, timestamp = cached_entry
        if datetime.datetime.now().timestamp() - timestamp < CACHE_EXPIRY[data_type]:
            return data, True
    return None, False

def _set_cached_data(data_type, code, data):
    """
    将数据存入缓存
    
    Args:
        data_type (str): 数据类型 ('stock', 'etf', 'fund')
        code (str): 产品代码
        data: 要缓存的数据
    """
    if data_type not in _data_cache:
        _data_cache[data_type] = {}
    _data_cache[data_type][code] = (data, datetime.datetime.now().timestamp())

def fetch_stock_data(stock_code):
    """
    使用AKSHARE获取股票数据
    
    Args:
        stock_code (str): 股票代码
    
    Returns:
        dict: 股票数据，如果获取失败则返回None
    """
    # 先尝试从缓存获取
    cached_data, is_valid = _get_cached_data('stock', stock_code)
    if is_valid:
        print(f"[缓存命中] 股票 {stock_code}")
        return cached_data
    
    try:
        print(f"[AKSHARE调用] 获取股票 {stock_code} 数据...")
        stock_data = ak.stock_individual_info_em(symbol=stock_code)
        
        # 如果是DataFrame类型，转换为字典
        if hasattr(stock_data, 'to_dict'):
            # 将DataFrame转换为以'item'为键，'value'为值的字典
            stock_data = dict(zip(stock_data['item'], stock_data['value']))
        
        # 缓存数据
        _set_cached_data('stock', stock_code, stock_data)
        return stock_data
    except Exception as e:
        print(f"获取股票 {stock_code} 数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def fetch_etf_data():
    """
    使用AKSHARE获取所有ETF数据
    
    Returns:
        DataFrame: ETF数据，如果获取失败则返回None
    """
    # ETF数据使用特殊的缓存键
    cached_data, is_valid = _get_cached_data('etf', 'all')
    if is_valid:
        print(f"[缓存命中] 所有ETF数据")
        return cached_data
    
    try:
        print(f"[AKSHARE调用] 获取所有ETF数据...")
        etf_data = ak.fund_etf_category_sina(symbol="ETF")
        
        # 缓存数据
        _set_cached_data('etf', 'all', etf_data)
        return etf_data
    except Exception as e:
        print(f"获取ETF数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def fetch_fund_data():
    """
    使用AKSHARE获取所有基金数据
    
    Returns:
        DataFrame: 基金数据，如果获取失败则返回None
    """
    # 基金数据使用特殊的缓存键
    cached_data, is_valid = _get_cached_data('fund', 'all')
    if is_valid:
        print(f"[缓存命中] 所有基金数据")
        return cached_data
    
    try:
        print(f"[AKSHARE调用] 获取所有基金数据...")
        fund_data = ak.fund_em_open_fund_name()
        
        # 缓存数据
        _set_cached_data('fund', 'all', fund_data)
        return fund_data
    except Exception as e:
        print(f"获取基金数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def fetch_fund_nav(fund_code):
    """
    使用AKSHARE获取基金净值数据
    
    Args:
        fund_code (str): 基金代码
    
    Returns:
        dict: 基金净值数据，如果获取失败则返回None
    """
    # 先尝试从缓存获取
    cached_data, is_valid = _get_cached_data('fund', fund_code)
    if is_valid:
        print(f"[缓存命中] 基金 {fund_code} 净值")
        return cached_data
    
    try:
        print(f"[AKSHARE调用] 获取基金 {fund_code} 净值数据...")
        fund_data = ak.fund_em_open_fund_info(fund=fund_code, indicator="单位净值走势")
        
        # 转换为字典格式
        if hasattr(fund_data, 'to_dict'):
            # 获取最新的净值数据
            latest_data = fund_data.iloc[-1].to_dict() if not fund_data.empty else {}
            
            # 缓存数据
            _set_cached_data('fund', fund_code, latest_data)
            return latest_data
        return None
    except Exception as e:
        print(f"获取基金 {fund_code} 净值数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def fetch_stock_kline_data(stock_code, period="daily", start_date=None, end_date=None):
    """
    使用AKSHARE获取股票K线数据
    
    Args:
        stock_code (str): 股票代码
        period (str): K线周期，可选值为：'daily', 'weekly', 'monthly'
        start_date (str): 开始日期，格式为 'YYYY-MM-DD'
        end_date (str): 结束日期，格式为 'YYYY-MM-DD'
    
    Returns:
        DataFrame: K线数据，如果获取失败则返回None
    """
    # 构造缓存键
    cache_key = f"{stock_code}_{period}_{start_date}_{end_date}"
    
    # 先尝试从缓存获取
    cached_data, is_valid = _get_cached_data('stock', cache_key)
    if is_valid:
        print(f"[缓存命中] 股票 {stock_code} K线数据")
        return cached_data
    
    try:
        print(f"[AKSHARE调用] 获取股票 {stock_code} K线数据...")
        
        # 设置默认日期
        if not end_date:
            end_date = datetime.datetime.now().strftime("%Y%m%d")
        if not start_date:
            # 默认获取过去365天的数据
            start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y%m%d")
        
        # 转换日期格式为AKSHARE需要的格式
        start_date = start_date.replace("-", "")
        end_date = end_date.replace("-", "")
        
        # 获取K线数据
        stock_kline_data = ak.stock_zh_a_hist(
            symbol=stock_code, 
            period=period, 
            start_date=start_date, 
            end_date=end_date, 
            adjust="qfq"
        )
        
        # 缓存数据
        _set_cached_data('stock', cache_key, stock_kline_data)
        return stock_kline_data
    except Exception as e:
        print(f"获取股票 {stock_code} K线数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def clear_cache(data_type=None, code=None):
    """
    清除缓存数据
    
    Args:
        data_type (str, optional): 数据类型 ('stock', 'etf', 'fund')
        code (str, optional): 产品代码
    """
    if not data_type:
        # 清除所有缓存
        global _data_cache
        _data_cache = {
            'stock': {},
            'etf': {},
            'fund': {}
        }
        print("已清除所有缓存数据")
    elif data_type in _data_cache:
        if not code:
            # 清除指定类型的所有缓存
            _data_cache[data_type] = {}
            print(f"已清除所有{data_type}类型的缓存数据")
        elif code in _data_cache[data_type]:
            # 清除指定类型和代码的缓存
            del _data_cache[data_type][code]
            print(f"已清除{data_type}类型{code}的缓存数据")
