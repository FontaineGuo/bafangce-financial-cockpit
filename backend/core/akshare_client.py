# AKSHARE客户端模块 - 封装AKSHARE的调用和缓存机制
import sys
import os
import time
import json
import akshare as ak
import datetime
import sqlite3

# 导入辅助函数
from backend.utils.helpers import normalize_number, is_trading_day

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 缓存目录配置
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache', 'akshare')

# 确保缓存目录存在
os.makedirs(CACHE_DIR, exist_ok=True)

# 缓存数据库路径
CACHE_DB_PATH = os.path.join(CACHE_DIR, 'akshare_cache.db')

# 初始化数据库
conn = sqlite3.connect(CACHE_DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# 创建缓存表
cursor.execute('''
CREATE TABLE IF NOT EXISTS cache (
    category TEXT NOT NULL,
    code TEXT,
    data TEXT NOT NULL,
    timestamp REAL NOT NULL,
    PRIMARY KEY (category, code)
)''')
conn.commit()

def _check_update_needed(category, code=None):
    """
    检查是否需要更新缓存
    
    Args:
        category (str): 缓存类别
        code (str, optional): 产品代码
        
    Returns:
        bool: True表示需要更新缓存，False表示不需要
    """
    current_time = time.time()
    current_dt = datetime.datetime.fromtimestamp(current_time)
    current_date = current_dt.date()
    current_hour = current_dt.hour
    current_minute = current_dt.minute
    
    # 获取当前缓存记录
    try:
        cursor.execute('''
        SELECT timestamp FROM cache WHERE category = ? AND code = ?
        ''', (category, code))
        result = cursor.fetchone()
    except Exception as e:
        print(f"查询缓存时间戳失败: {e}")
        return True
    
    # 如果没有缓存记录，需要更新
    if not result:
        return True
    
    cache_timestamp = result[0]
    cache_dt = datetime.datetime.fromtimestamp(cache_timestamp)
    cache_date = cache_dt.date()
    
    # 判断当前是否是交易日
    is_current_trading_day = is_trading_day(current_date)
    
    # 判断当前时间是否在交易时间内（9:30-15:00）
    is_trading_hours = (current_hour > 9 or (current_hour == 9 and current_minute >= 30)) and current_hour < 15
    
    # 情况1：今天是交易日，且在交易时间内，需要更新缓存
    if is_current_trading_day and is_trading_hours:
        return True
    
    # 情况2：今天不是交易日，但上一次缓存时间是在交易日内，需要更新一次
    if not is_current_trading_day:
        is_cache_trading_day = is_trading_day(cache_date)
        if is_cache_trading_day:
            return True
    
    # 其他情况不需要更新
    return False

def _read_cache(category, code=None):
    """
    读取缓存
    
    Args:
        category (str): 缓存类别
        code (str, optional): 产品代码
        
    Returns:
        dict or None: 缓存数据
    """
    try:
        # 检查是否需要更新缓存
        if _check_update_needed(category, code):
            return None
        
        # 读取缓存数据
        cursor.execute('''
        SELECT data FROM cache WHERE category = ? AND code = ?
        ''', (category, code))
        result = cursor.fetchone()
        
        if result:
            return json.loads(result[0])
        else:
            return None
    except Exception as e:
        print(f"读取缓存失败: {e}")
        return None

def _write_cache(category, data, code=None):
    """
    写入缓存
    
    Args:
        category (str): 缓存类别
        data (dict): 要缓存的数据
        code (str, optional): 产品代码
    """
    try:
        current_time = time.time()
        data_json = json.dumps(data, ensure_ascii=False, indent=2)
        
        # 使用REPLACE语句实现新缓存覆盖旧缓存
        cursor.execute('''
        REPLACE INTO cache (category, code, data, timestamp) 
        VALUES (?, ?, ?, ?)
        ''', (category, code, data_json, current_time))
        conn.commit()
    except Exception as e:
        print(f"写入缓存失败: {e}")
        conn.rollback()

# 以下是sample.py中使用的函数

def get_stock_individual_info(code, force_update=False):
    """
    获取股票个股信息
    
    Args:
        code (str): 股票代码
        force_update (bool): 是否强制更新缓存
        
    Returns:
        dict: 股票个股信息
    """
    try:
        # 先尝试读取缓存
        if not force_update:
            cached_data = _read_cache('stock_info', code)
            if cached_data:
                return cached_data
        
        # 获取股票个股信息
        stock_data = ak.stock_individual_info_em(symbol=code)
        
        # 如果是DataFrame类型，转换为字典
        if hasattr(stock_data, 'to_dict'):
            # 将DataFrame转换为以'item'为键，'value'为值的字典
            stock_data = dict(zip(stock_data['item'], stock_data['value']))
        
        # 写入缓存
        _write_cache('stock_info', stock_data, code)
        
        return stock_data
    except Exception as e:
        print(f"获取股票个股信息失败: {e}")
        return None

def get_fund_open_fund_daily(force_update=False):
    """
    获取开放式基金每日数据
    
    Args:
        force_update (bool): 是否强制更新缓存
        
    Returns:
        pandas.DataFrame: 开放式基金每日数据
    """
    try:
        # 先尝试读取缓存
        if not force_update:
            cached_data = _read_cache('fund_daily')
            if cached_data:
                import pandas as pd
                return pd.DataFrame(cached_data)
        
        # 获取开放式基金每日数据
        df = ak.fund_open_fund_daily_em()
        
        # 写入缓存
        _write_cache('fund_daily', df.to_dict('records'))
        
        return df
    except Exception as e:
        print(f"获取开放式基金每日数据失败: {e}")
        return None

def get_fund_etf_fund_daily(force_update=False):
    """
    获取ETF基金每日数据
    
    Args:
        force_update (bool): 是否强制更新缓存
        
    Returns:
        pandas.DataFrame: ETF基金每日数据
    """
    try:
        # 先尝试读取缓存
        if not force_update:
            cached_data = _read_cache('etf_daily')
            if cached_data:
                import pandas as pd
                return pd.DataFrame(cached_data)
        
        # 获取ETF基金每日数据
        df = ak.fund_etf_fund_daily_em()
        
        # 写入缓存
        _write_cache('etf_daily', df.to_dict('records'))
        
        return df
    except Exception as e:
        print(f"获取ETF基金每日数据失败: {e}")
        return None

# 以下是为了保持与data_fetcher.py兼容而保留的函数

def get_stock_quote(code, force_update=False):
    """
    获取股票实时行情（兼容旧版本）
    
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
        
        # 使用新的API获取股票信息
        stock_data = get_stock_individual_info(code, force_update=force_update)
        
        if not stock_data:
            return None
        
        
        data = {
            'stock_code': code,
            'stock_name': stock_data.get('股票简称', ''),
            'current_price': stock_data.get('最新'),
            'total_shares': stock_data.get('总股本'),
            'circulating_shares': stock_data.get('流通股'),
            'total_market_value': stock_data.get('总市值'),
            'circulating_market_value': stock_data.get('流通市值'),
            'industry': stock_data.get('行业'),
            'listing_date': stock_data.get('上市时间'),
            # 添加与其他产品类型一致的字段，确保get_product_info_by_code方法正常工作
            'code': code,
            'name': stock_data.get('股票简称', '')
        }
        
        # 写入缓存
        _write_cache('stock_quote', data, code)
        
        return data
    except Exception as e:
        print(f"获取股票行情失败: {e}")
        return None

def get_stock_basic_info(code, force_update=False):
    """
    获取股票基本信息（兼容旧版本）
    
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
        
        # 使用新的API获取股票信息
        stock_data = get_stock_individual_info(code, force_update=force_update)
        
        if not stock_data:
            return None
        
        # 转换为旧版本的数据格式
        data = {
            'code': code,
            'name': stock_data.get('股票简称')
        }
        
        # 写入缓存
        _write_cache('basic_info', data, code)
        
        return data
    except Exception as e:
        print(f"获取股票基本信息失败: {e}")
        return None

def get_etf_quote(code, force_update=False):
    """
    获取ETF实时行情（兼容旧版本）
    
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
        
        # 获取ETF每日数据
        etf_data = get_fund_etf_fund_daily(force_update=force_update)
        
        if etf_data is None or etf_data.empty:
            return None
        
        # 查找对应ETF
        etf_info = etf_data[etf_data['基金代码'] == code]
        if etf_info.empty:
            # 尝试带前缀的代码格式
            etf_info = etf_data[(etf_data['基金代码'] == f'sh{code}') | (etf_data['基金代码'] == f'sz{code}')]
            if etf_info.empty:
                return None
        
        # 转换为字典
        etf_data_dict = etf_info.iloc[0].to_dict()
        
        # 动态识别净值相关列名
        net_value_col = None
        total_net_value_col = None
        prev_net_value_col = None
        prev_total_net_value_col = None
        
        for key in etf_data_dict.keys():
            if '-单位净值' in key and not net_value_col:
                net_value_col = key
            elif '-累计净值' in key and not total_net_value_col:
                total_net_value_col = key
            elif '-前单位净值' in key or ('-单位净值' in key and net_value_col):
                prev_net_value_col = key
            elif '-前累计净值' in key or ('-累计净值' in key and total_net_value_col):
                prev_total_net_value_col = key
        
        # 转换为字典格式
        data = {
            'etf_code': etf_data_dict['基金代码'],
            'etf_name': etf_data_dict['基金简称'],
            'type': etf_data_dict.get('类型'),
            'net_value': normalize_number(etf_data_dict.get(net_value_col)),
            'total_net_value': normalize_number(etf_data_dict.get(total_net_value_col)),
            'prev_net_value': normalize_number(etf_data_dict.get(prev_net_value_col)),
            'prev_total_net_value': normalize_number(etf_data_dict.get(prev_total_net_value_col)),
            'growth_value': normalize_number(etf_data_dict.get('增长值')),
            'growth_rate': normalize_number(etf_data_dict.get('增长率')),
            'market_price': normalize_number(etf_data_dict.get('市价')),
            'discount_rate': normalize_number(etf_data_dict.get('折价率')),
            # 保留与其他产品类型一致的字段，确保兼容性
            'code': etf_data_dict['基金代码'],
            'name': etf_data_dict['基金简称']
        }
        
        # 写入缓存
        _write_cache('etf_quote', data, code)
        
        return data
    except Exception as e:
        print(f"获取ETF行情失败: {e}")
        return None

def get_etf_basic_info(code, force_update=False):
    """
    获取ETF基本信息（兼容旧版本）
    
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
        
        # 获取ETF行情数据
        etf_data = get_etf_quote(code, force_update=force_update)
        
        if not etf_data:
            return None
        
        # 构建基本信息
        data = {
            'code': etf_data['etf_code'],
            'name': etf_data['etf_name']
        }
        
        # 写入缓存
        _write_cache('basic_info', data, code)
        
        return data
    except Exception as e:
        print(f"获取ETF基本信息失败: {e}")
        return None

def get_fund_quote(code, force_update=False):
    """
    获取基金实时行情（兼容旧版本）
    
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
        
        # 获取基金每日数据
        fund_data = get_fund_open_fund_daily(force_update=force_update)
        
        if fund_data is None or fund_data.empty:
            return None
        
        def get_date_from_key(key):
            """从键名中提取日期信息"""
            import re
            match = re.search(r'(\d{4}-\d{2}-\d{2})', key)
            if match:
                return match.group(1)
            return ''
        
        # 查找对应基金代码
        fund_info = fund_data[fund_data['基金代码'] == code]
        
        if fund_info.empty:
            return None
        
        # 转换为字典
        row = fund_info.iloc[0].to_dict()
        
        # 解析单条基金数据
        net_value = None
        total_net_value = None
        prev_net_value = None
        prev_total_net_value = None
        
        # 收集所有单位净值和累计净值字段
        net_value_fields = []
        total_net_value_fields = []
        
        for key in row.keys():
            if '-单位净值' in key:
                net_value_fields.append(key)
            elif '-累计净值' in key:
                total_net_value_fields.append(key)
        
        # 处理单位净值字段
        if net_value_fields:
            # 按日期排序，最新的日期在前面
            net_value_fields.sort(key=get_date_from_key, reverse=True)
            
            # 尝试获取最新的有效单位净值
            for i, field in enumerate(net_value_fields):
                temp_value = normalize_number(row[field])
                if temp_value is not None:
                    net_value = row[field]
                    # 如果不是第一个字段（最新的），则前一个字段就是上一交易日净值
                    if i > 0:
                        prev_net_value = row[net_value_fields[i-1]]
                    # 如果是第一个字段，且有多个字段，则第二个字段是上一交易日净值
                    elif len(net_value_fields) > 1:
                        prev_net_value = row[net_value_fields[1]]
                    break
        
        # 处理累计净值字段
        if total_net_value_fields:
            # 按日期排序，最新的日期在前面
            total_net_value_fields.sort(key=get_date_from_key, reverse=True)
            
            # 尝试获取最新的有效累计净值
            for i, field in enumerate(total_net_value_fields):
                temp_value = normalize_number(row[field])
                if temp_value is not None:
                    total_net_value = row[field]
                    # 如果不是第一个字段（最新的），则前一个字段就是上一交易日累计净值
                    if i > 0:
                        prev_total_net_value = row[total_net_value_fields[i-1]]
                    # 如果是第一个字段，且有多个字段，则第二个字段是上一交易日累计净值
                    elif len(total_net_value_fields) > 1:
                        prev_total_net_value = row[total_net_value_fields[1]]
                    break
        
        # 转换为字典格式
        data = {
            'fund_code': row['基金代码'],
            'fund_name': row['基金简称'],
            'net_value': normalize_number(net_value),
            'total_net_value': normalize_number(total_net_value),
            'prev_net_value': normalize_number(prev_net_value),
            'prev_total_net_value': normalize_number(prev_total_net_value),
            'daily_growth_value': normalize_number(row.get('日增长值')),
            'daily_growth_rate': normalize_number(row.get('日增长率')),
            'purchase_status': row.get('申购状态'),
            'redemption_status': row.get('赎回状态'),
            'fee_rate': row.get('手续费')
        }
        
        # 写入缓存
        _write_cache('fund_quote', data, code)
        
        return data
    except Exception as e:
        print(f"获取基金行情失败: {e}")
        return None

def get_fund_basic_info(code, force_update=False):
    """
    获取基金基本信息（兼容旧版本）
    
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
        
        # 获取基金每日数据
        fund_data = get_fund_open_fund_daily(force_update=force_update)
        
        if fund_data is None or fund_data.empty:
            return None
        
        # 查找对应基金
        fund_info = fund_data[fund_data['基金代码'] == code]
        
        if fund_info.empty:
            return None
        
        # 转换为字典格式
        data = {
            'code': code,
            'name': fund_info.iloc[0]['基金简称']
        }
        
        # 写入缓存
        _write_cache('basic_info', data, code)
        
        return data
    except Exception as e:
        print(f"获取基金基本信息失败: {e}")
        return None