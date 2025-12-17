# AKSHARE客户端模块 - 封装AKSHARE的调用和缓存机制
import sys
import os
import time
import json
import akshare as ak
import datetime

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 缓存目录配置
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache', 'akshare')

# 确保缓存目录存在
os.makedirs(CACHE_DIR, exist_ok=True)

# 缓存有效期（秒）
CACHE_EXPIRE = {
    'stock_quote': 60,  # 股票行情缓存1分钟
    'etf_quote': 60,    # ETF行情缓存1分钟
    'fund_quote': 180,  # 基金行情缓存3分钟
    'basic_info': 3600  # 基本信息缓存1小时
}

def _get_cache_filepath(category, code):
    """
    获取缓存文件路径
    
    Args:
        category (str): 缓存类别
        code (str): 产品代码
        
    Returns:
        str: 缓存文件路径
    """
    return os.path.join(CACHE_DIR, f'{category}_{code}.json')

def _read_cache(category, code):
    """
    读取缓存
    
    Args:
        category (str): 缓存类别
        code (str): 产品代码
        
    Returns:
        dict or None: 缓存数据
    """
    try:
        cache_file = _get_cache_filepath(category, code)
        
        # 检查缓存文件是否存在
        if not os.path.exists(cache_file):
            return None
        
        # 读取缓存文件
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # 检查缓存是否过期
        current_time = time.time()
        if cache_data.get('timestamp', 0) + CACHE_EXPIRE.get(category, 60) < current_time:
            return None
        
        return cache_data.get('data')
    except Exception as e:
        print(f"读取缓存失败: {e}")
        return None

def _write_cache(category, code, data):
    """
    写入缓存
    
    Args:
        category (str): 缓存类别
        code (str): 产品代码
        data (dict): 要缓存的数据
    """
    try:
        cache_file = _get_cache_filepath(category, code)
        cache_data = {
            'timestamp': time.time(),
            'data': data
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"写入缓存失败: {e}")

def is_trading_time():
    """
    判断是否为交易时间
    
    Returns:
        bool: 是否为交易时间
    """
    try:
        now = datetime.datetime.now()
        today = now.strftime('%Y-%m-%d')
        weekday = now.weekday()
        
        # 周一到周五
        if weekday >= 5:
            return False
        
        # 上午交易时间 9:30-11:30
        morning_start = datetime.datetime.strptime(f'{today} 09:30:00', '%Y-%m-%d %H:%M:%S')
        morning_end = datetime.datetime.strptime(f'{today} 11:30:00', '%Y-%m-%d %H:%M:%S')
        
        # 下午交易时间 13:00-15:00
        afternoon_start = datetime.datetime.strptime(f'{today} 13:00:00', '%Y-%m-%d %H:%M:%S')
        afternoon_end = datetime.datetime.strptime(f'{today} 15:00:00', '%Y-%m-%d %H:%M:%S')
        
        return (morning_start <= now <= morning_end) or (afternoon_start <= now <= afternoon_end)
    except Exception as e:
        print(f"判断交易时间失败: {e}")
        return True

def get_stock_quote(code, force_update=False):
    """
    获取股票实时行情
    
    Args:
        code (str): 股票代码
        force_update (bool): 是否强制更新缓存
        
    Returns:
        dict: 股票行情数据
    """
    try:
        # 先尝试读取缓存
        if not force_update:
            cached_data = _read_cache('stock_quote', code)
            if cached_data:
                return cached_data
        
        # 构建完整代码
        if not code.startswith('sh') and not code.startswith('sz'):
            # 尝试判断股票市场
            if code.startswith('6'):
                full_code = f'sh{code}'
            else:
                full_code = f'sz{code}'
        else:
            full_code = code
        
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        
        # 查找对应股票
        stock_data = df[df['代码'] == full_code]
        
        if stock_data.empty:
            return None
        
        # 转换为字典格式
        data = {
            'code': full_code,
            'name': stock_data.iloc[0]['名称'],
            'current_price': float(stock_data.iloc[0]['最新价']),
            'open_price': float(stock_data.iloc[0]['今开']),
            'prev_close': float(stock_data.iloc[0]['昨收']),
            'high_price': float(stock_data.iloc[0]['最高']),
            'low_price': float(stock_data.iloc[0]['最低']),
            'volume': int(stock_data.iloc[0]['成交量']),
            'turnover': float(stock_data.iloc[0]['成交额']),
            'change': float(stock_data.iloc[0]['涨跌额']),
            'change_rate': float(stock_data.iloc[0]['涨跌幅'].rstrip('%'))
        }
        
        # 写入缓存
        _write_cache('stock_quote', code, data)
        
        return data
    except Exception as e:
        print(f"获取股票行情失败: {e}")
        return None

def get_etf_quote(code, force_update=False):
    """
    获取ETF实时行情
    
    Args:
        code (str): ETF代码
        force_update (bool): 是否强制更新缓存
        
    Returns:
        dict: ETF行情数据
    """
    try:
        # 先尝试读取缓存
        if not force_update:
            cached_data = _read_cache('etf_quote', code)
            if cached_data:
                return cached_data
        
        # 构建完整代码
        if not code.startswith('sh') and not code.startswith('sz'):
            # ETF通常在上海和深圳交易所，先尝试上海
            full_code = f'sh{code}'
        else:
            full_code = code
        
        # 获取ETF实时行情
        df = ak.fund_etf_spot_em()
        
        # 查找对应ETF
        etf_data = df[df['代码'] == full_code]
        
        if etf_data.empty:
            # 如果上海交易所没有找到，尝试深圳交易所
            if code.startswith('sh'):
                full_code = f'sz{code[2:]}'
                etf_data = df[df['代码'] == full_code]
            
            if etf_data.empty:
                return None
        
        # 转换为字典格式
        data = {
            'code': full_code,
            'name': etf_data.iloc[0]['名称'],
            'net_value': float(etf_data.iloc[0]['最新价']),
            'prev_close': float(etf_data.iloc[0]['昨收']),
            'change': float(etf_data.iloc[0]['涨跌额']),
            'change_rate': float(etf_data.iloc[0]['涨跌幅'].rstrip('%'))
        }
        
        # 写入缓存
        _write_cache('etf_quote', code, data)
        
        return data
    except Exception as e:
        print(f"获取ETF行情失败: {e}")
        return None

def get_fund_quote(code, force_update=False):
    """
    获取基金实时行情
    
    Args:
        code (str): 基金代码
        force_update (bool): 是否强制更新缓存
        
    Returns:
        dict: 基金行情数据
    """
    try:
        # 先尝试读取缓存
        if not force_update:
            cached_data = _read_cache('fund_quote', code)
            if cached_data:
                return cached_data
        
        # 获取基金实时行情
        df = ak.fund_em_open_fund_daily(code)
        
        if df.empty:
            return None
        
        # 转换为字典格式
        data = {
            'code': code,
            'net_value': float(df.iloc[0]['单位净值']),
            'prev_net_value': float(df.iloc[0]['累计净值']),
            'date': df.iloc[0]['净值日期']
        }
        
        # 写入缓存
        _write_cache('fund_quote', code, data)
        
        return data
    except Exception as e:
        print(f"获取基金行情失败: {e}")
        return None

def get_stock_basic_info(code, force_update=False):
    """
    获取股票基本信息
    
    Args:
        code (str): 股票代码
        force_update (bool): 是否强制更新缓存
        
    Returns:
        dict: 股票基本信息
    """
    try:
        # 先尝试读取缓存
        if not force_update:
            cached_data = _read_cache('basic_info', code)
            if cached_data:
                return cached_data
        
        # 构建完整代码
        if not code.startswith('sh') and not code.startswith('sz'):
            if code.startswith('6'):
                full_code = f'sh{code}'
            else:
                full_code = f'sz{code}'
        else:
            full_code = code
        
        # 获取股票基本信息
        df = ak.stock_zh_a_basic_info_em()
        
        # 查找对应股票
        stock_data = df[df['代码'] == full_code]
        
        if stock_data.empty:
            return None
        
        # 转换为字典格式
        data = {
            'code': full_code,
            'name': stock_data.iloc[0]['股票简称'],
            'industry': stock_data.iloc[0]['行业'],
            'region': stock_data.iloc[0]['地区'],
            'listing_date': stock_data.iloc[0]['上市日期']
        }
        
        # 写入缓存
        _write_cache('basic_info', code, data)
        
        return data
    except Exception as e:
        print(f"获取股票基本信息失败: {e}")
        return None

def get_etf_basic_info(code, force_update=False):
    """
    获取ETF基本信息
    
    Args:
        code (str): ETF代码
        force_update (bool): 是否强制更新缓存
        
    Returns:
        dict: ETF基本信息
    """
    try:
        # 先尝试读取缓存
        if not force_update:
            cached_data = _read_cache('basic_info', code)
            if cached_data:
                return cached_data
        
        # ETF基本信息获取相对复杂，这里简化处理
        # 先获取行情数据
        etf_data = get_etf_quote(code, force_update=force_update)
        
        if not etf_data:
            return None
        
        # 构建基本信息
        data = {
            'code': etf_data['code'],
            'name': etf_data['name'],
            'type': 'etf'
        }
        
        # 写入缓存
        _write_cache('basic_info', code, data)
        
        return data
    except Exception as e:
        print(f"获取ETF基本信息失败: {e}")
        return None

def get_fund_basic_info(code, force_update=False):
    """
    获取基金基本信息
    
    Args:
        code (str): 基金代码
        force_update (bool): 是否强制更新缓存
        
    Returns:
        dict: 基金基本信息
    """
    try:
        # 先尝试读取缓存
        if not force_update:
            cached_data = _read_cache('basic_info', code)
            if cached_data:
                return cached_data
        
        # 获取基金基本信息
        df = ak.fund_em_info(code)
        
        if df.empty:
            return None
        
        # 转换为字典格式
        data = {
            'code': code,
            'name': df.iloc[0]['基金名称'],
            'type': df.iloc[0]['基金类型'],
            'manager': df.iloc[0]['基金经理'],
            'fund_company': df.iloc[0]['基金公司'],
            'establish_date': df.iloc[0]['成立日期']
        }
        
        # 写入缓存
        _write_cache('basic_info', code, data)
        
        return data
    except Exception as e:
        print(f"获取基金基本信息失败: {e}")
        return None
