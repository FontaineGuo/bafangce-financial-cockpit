# 数据获取模块
import akshare as ak
import sys
import os
import datetime

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import normalize_number, is_trading_day

def get_stock_update_action(stock_code):
    """
    根据当前时间和数据状态决定股票数据的更新动作
    
    Args:
        stock_code (str): 股票代码
    
    Returns:
        str: 更新动作，可能的值为：
            - "use_cache": 使用缓存
            - "fetch_once": 获取一次
            - "fetch_realtime": 获取实时数据
    """
    today = datetime.date.today()
    current_time = datetime.datetime.now().time()
    
    # 1. 检查交易日状态
    if not is_trading_day(today):
        if has_stock_data(stock_code):
            return "use_cache"  # 使用缓存
        else:
            return "fetch_once"  # 获取一次
    
    # 2. 检查交易时间段
    trading_start = datetime.time(9, 30)
    trading_end = datetime.time(15, 0)
    
    if trading_start <= current_time <= trading_end:
        # 交易时间：检查最后更新时间
        last_update = get_stock_last_update_time(stock_code)
        if last_update and (datetime.datetime.now() - last_update).total_seconds() < 300:  # 5分钟
            return "use_cache"  # 使用缓存
        else:
            return "fetch_realtime"  # 获取实时
    
    else:
        # 非交易时间
        if has_stock_data(stock_code):
            return "use_cache"  # 使用缓存
        else:
            return "fetch_once"  # 获取一次

def has_stock_data(stock_code):
    """
    检查数据库中是否已有该股票的数据
    
    Args:
        stock_code (str): 股票代码
    
    Returns:
        bool: True表示有数据，False表示没有数据
    """
    from core.database import get_stock_by_code
    try:
        result = get_stock_by_code(stock_code)
        return result is not None
    except Exception:
        # 如果表不存在或其他错误，返回False
        return False

def get_stock_last_update_time(stock_code):
    """
    获取指定股票数据的最后更新时间
    
    Args:
        stock_code (str): 股票代码
    
    Returns:
        datetime.datetime or None: 最后更新时间，如果没有数据则返回None
    """
    from core.database import get_stock_last_update_time as db_get_last_update
    try:
        return db_get_last_update(stock_code)
    except Exception:
        # 如果表不存在或其他错误，返回None
        return None

def get_stock_data(stock_code, force_update=False):
    """
    使用AKSHARE库获取A股股票实时数据，并支持缓存策略
    
    Args:
        stock_code (str): A股股票代码，例如 "000001"
        force_update (bool): 是否强制更新数据
    
    Returns:
        dict: 股票实时数据，以key-value pair形式返回
    """
    try:
        # 先导入数据库模块
        from core.database import create_tables, get_stock_by_code, insert_or_update_stock_data
        
        # 创建数据库表（如果不存在）
        create_tables()
        
        # 如果强制更新，则直接获取新数据
        if force_update:
            print(f"强制更新股票 {stock_code} 数据")
            return fetch_and_store_stock_data(stock_code)
            
        # 决定更新动作
        action = get_stock_update_action(stock_code)
        print(f"股票 {stock_code} 更新动作: {action}")
        
        if action == "use_cache":
            # 使用缓存数据
            result = get_stock_by_code(stock_code)
            if result:
                print(f"使用股票 {stock_code} 的缓存数据")
                return result
            else:
                # 如果缓存中没有数据，获取一次
                print(f"股票 {stock_code} 缓存中没有数据，获取一次")
                return fetch_and_store_stock_data(stock_code)
        elif action in ["fetch_once", "fetch_realtime"]:
            # 获取新数据
            print(f"获取股票 {stock_code} 新数据: {action}")
            return fetch_and_store_stock_data(stock_code)
        else:
            # 默认使用缓存
            result = get_stock_by_code(stock_code)
            if result:
                print(f"使用股票 {stock_code} 默认缓存数据")
                return result
            else:
                print(f"默认获取股票 {stock_code} 数据")
                return fetch_and_store_stock_data(stock_code)
        
    except Exception as e:
        print(f"获取股票数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def fetch_and_store_stock_data(stock_code):
    """
    获取并存储指定股票的数据
    
    Args:
        stock_code (str): 股票代码
    
    Returns:
        dict: 存储的股票数据，如果获取失败则返回None
    """
    print(f"开始获取股票 {stock_code} 的数据...")
    try:
        # 使用AKSHARE获取股票数据
        print(f"使用AKSHARE获取股票 {stock_code} 数据...")
        stock_data = ak.stock_individual_info_em(symbol=stock_code)
        
        # 如果是DataFrame类型，转换为字典
        if hasattr(stock_data, 'to_dict'):
            # 将DataFrame转换为以'item'为键，'value'为值的字典
            stock_data = dict(zip(stock_data['item'], stock_data['value']))
        
        # 转换数据格式以适应数据库存储
        db_stock_data = {
            'stock_code': stock_code,
            'stock_name': stock_data.get('股票简称', ''),
            'current_price': stock_data.get('最新'),
            'total_shares': stock_data.get('总股本'),
            'circulating_shares': stock_data.get('流通股'),
            'total_market_value': stock_data.get('总市值'),
            'circulating_market_value': stock_data.get('流通市值'),
            'industry': stock_data.get('行业'),
            'listing_date': stock_data.get('上市时间')
        }
        
        # 存储到数据库
        from core.database import insert_or_update_stock_data
        insert_or_update_stock_data(db_stock_data)
        print(f"股票 {stock_code} 数据已存储到数据库")
        
        # 返回数据库中的数据
        from core.database import get_stock_by_code
        return get_stock_by_code(stock_code)
        
    except Exception as e:
        print(f"获取股票 {stock_code} 数据时出错: {e}")
        import traceback
        traceback.print_exc()
        # 如果获取失败，尝试返回数据库中已有的数据
        from core.database import get_stock_by_code
        return get_stock_by_code(stock_code)



def get_fund_last_update_time(fund_code):
    """
    获取指定基金数据的最后更新时间
    
    Args:
        fund_code (str): 基金代码
    
    Returns:
        datetime.datetime or None: 最后更新时间，如果没有数据则返回None
    """
    from core.database import execute_query
    query = '''
        SELECT update_time FROM fund_data 
        WHERE fund_code = ? 
        ORDER BY update_time DESC 
        LIMIT 1
    '''
    result = execute_query(query, (fund_code,))
    if result:
        # SQLite的TIMESTAMP类型返回的是字符串，需要转换为datetime
        return datetime.datetime.strptime(result[0][0], '%Y-%m-%d %H:%M:%S')
    return None

def has_fund_data(fund_code):
    """
    检查数据库中是否已有该基金的数据
    
    Args:
        fund_code (str): 基金代码
    
    Returns:
        bool: True表示有数据，False表示没有数据
    """
    from core.database import execute_query
    today = datetime.date.today().strftime('%Y-%m-%d')
    query = '''
        SELECT COUNT(*) FROM fund_data 
        WHERE fund_code = ? AND DATE(update_time) = ?
    '''
    result = execute_query(query, (fund_code, today))
    return result[0][0] > 0

# ETF相关辅助函数
def get_etf_last_update_time(etf_code):
    """
    获取指定ETF数据的最后更新时间
    
    Args:
        etf_code (str): ETF代码
    
    Returns:
        datetime.datetime or None: 最后更新时间，如果没有数据则返回None
    """
    from core.database import execute_query
    query = '''
        SELECT update_time FROM etf_data 
        WHERE etf_code = ? 
        ORDER BY update_time DESC 
        LIMIT 1
    '''
    result = execute_query(query, (etf_code,))
    if result:
        # SQLite的TIMESTAMP类型返回的是字符串，需要转换为datetime
        return datetime.datetime.strptime(result[0][0], '%Y-%m-%d %H:%M:%S')
    return None

def has_etf_data(etf_code):
    """
    检查数据库中是否已有该ETF的数据
    
    Args:
        etf_code (str): ETF代码
    
    Returns:
        bool: True表示有数据，False表示没有数据
    """
    from core.database import execute_query
    today = datetime.date.today().strftime('%Y-%m-%d')
    query = '''
        SELECT COUNT(*) FROM etf_data 
        WHERE etf_code = ? AND DATE(update_time) = ?
    '''
    result = execute_query(query, (etf_code, today))
    return result[0][0] > 0

def get_etf_update_action(etf_code):
    """
    根据当前时间和数据状态决定ETF数据的更新动作
    
    Args:
        etf_code (str): ETF代码
    
    Returns:
        str: 更新动作，可能的值为：
            - "use_cache": 使用缓存
            - "fetch_once": 获取一次
            - "fetch_realtime": 获取实时数据
    """
    today = datetime.date.today()
    current_time = datetime.datetime.now().time()
    last_update = get_etf_last_update_time(etf_code)
    
    # 1. 检查交易日状态
    if not is_trading_day(today):
        if has_etf_data(etf_code):
            return "use_cache"  # 使用缓存
        else:
            return "fetch_once"  # 获取一次
    
    # 2. 检查交易时间段
    trading_start = datetime.time(9, 30)
    trading_end = datetime.time(15, 0)
    
    if trading_start <= current_time <= trading_end:
        # 交易时间：检查最后更新时间
        if last_update and (datetime.datetime.now() - last_update).total_seconds() < 300:  # 5分钟
            return "use_cache"  # 使用缓存
        else:
            return "fetch_realtime"  # 获取实时
    
    else:
        # 非交易时间
        if has_etf_data(etf_code):
            return "use_cache"  # 使用缓存
        else:
            return "fetch_once"  # 获取一次

def get_fund_update_action(fund_code):
    """
    根据当前时间和数据状态决定基金数据的更新动作
    
    Args:
        fund_code (str): 基金代码
    
    Returns:
        str: 更新动作，可能的值为：
            - "use_cache": 使用缓存
            - "fetch_once": 获取一次
            - "fetch_realtime": 获取实时数据
            - "fetch_nav": 获取净值数据
    """
    today = datetime.date.today()
    current_time = datetime.datetime.now().time()
    last_update = get_fund_last_update_time(fund_code)
    
    # 1. 检查交易日状态
    if not is_trading_day(today):
        if has_fund_data(fund_code):
            return "use_cache"  # 使用缓存
        else:
            return "fetch_once"  # 获取一次
    
    # 2. 检查交易时间段
    trading_start = datetime.time(9, 30)
    trading_end = datetime.time(15, 0)
    nav_end = datetime.time(20, 0)
    
    if trading_start <= current_time <= trading_end:
        # 交易时间：检查最后更新时间
        if last_update and (datetime.datetime.now() - last_update).total_seconds() < 300:  # 5分钟
            return "use_cache"  # 使用缓存
        else:
            return "fetch_realtime"  # 获取实时
    
    elif trading_end < current_time <= nav_end:
        # 净值公布时间：频繁检查
        if last_update and (datetime.datetime.now() - last_update).total_seconds() < 1800:  # 30分钟
            return "use_cache"  # 使用缓存
        else:
            return "fetch_nav"  # 获取净值
    
    else:
        # 非交易时间
        return "use_cache"

# 顶级函数：解析日期字符串
def get_date_from_key(key):
    """从字段名中提取日期"""
    # 提取日期部分，格式为YYYY-MM-DD
    try:
        date_str = key.split('-')[0:3]  # 获取前三个部分：年、月、日
        date_str = '-'.join(date_str)
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, IndexError):
        # 如果无法解析日期，返回一个很早的日期
        return datetime.date(1900, 1, 1)

# 顶级函数：解析单条基金数据
def parse_fund_row(row):
    """解析单条基金数据"""
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
    
    return {
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

    # 顶级函数：多进程处理函数
def process_row(row):
    try:
        return parse_fund_row(row)
    except Exception as e:
        return None, row.get('基金代码'), e

def fetch_and_store_fund_data(fund_code):
    """
    获取并存储指定基金的数据
    
    Args:
        fund_code (str): 基金代码
    
    Returns:
        dict: 存储的基金数据，如果获取失败则返回None
    """
    print(f"开始获取基金 {fund_code} 的数据...")
    try:
        # 使用AKSHARE获取基金数据
        print("使用AKSHARE获取基金数据...")
        import pandas as pd
        df = ak.fund_open_fund_daily_em()
        print(f"成功获取 {len(df)} 条基金数据")
        print(f"DataFrame列名: {list(df.columns)}")
        
        # 将所有基金数据写入数据库
        print("开始将所有基金数据写入数据库...")
        from core.database import batch_insert_fund_data, connect_db
        import multiprocessing
        
        # 解析所有基金数据
        start_time = datetime.datetime.now()
        fund_data_list = []
        error_count = 0
        
        # 数据解析是CPU密集型任务，可以使用多进程加速
        # 获取CPU核心数
        num_cores = multiprocessing.cpu_count()
        print(f"检测到 {num_cores} 个CPU核心，使用多进程加速数据解析")
        
        # 将数据分成多个批次
        rows = [row for _, row in df.iterrows()]
        
        # 使用多进程池处理
        with multiprocessing.Pool(processes=num_cores) as pool:
            results = pool.map(process_row, rows)
        
        # 收集结果
        for result in results:
            if isinstance(result, tuple):
                # 解析错误
                error_count += 1
                if error_count <= 10:
                    print(f"解析基金 {result[1]} 时出错: {result[2]}")
            elif result is not None:
                # 解析成功
                fund_data_list.append(result)
        
        print(f"数据解析完成，成功解析 {len(fund_data_list)} 条，失败 {error_count} 条")
        
        # 使用批量插入优化存储
        batch_size = 100  # 批量大小
        stored_count = 0
        
        # 创建数据库连接
        conn = connect_db()
        
        # 分批处理
        for i in range(0, len(fund_data_list), batch_size):
            batch = fund_data_list[i:i+batch_size]
            try:
                batch_insert_fund_data(batch, conn)
                stored_count += len(batch)
                # 每存储1000条记录打印一次进度
                if stored_count % 1000 == 0:
                    print(f"已存储 {stored_count} 条基金数据...")
            except Exception as e:
                print(f"批量插入基金数据时出错（批次 {i//batch_size + 1}）: {e}")
        
        # 提交事务并关闭连接
        conn.commit()
        conn.close()
        
        end_time = datetime.datetime.now()
        print(f"数据存储耗时: {end_time - start_time}")
        print(f"基金数据存储完成，成功存储 {stored_count} 条，失败 {error_count} 条")
        
        # 检查是否找到指定基金
        if fund_code not in df['基金代码'].values:
            print(f"未找到基金代码为 {fund_code} 的数据")
            return None
        
        print(f"基金 {fund_code} 数据已存储到数据库")
        
    except Exception as e:
        print(f"获取基金 {fund_code} 数据时出错: {e}")
        return None
    
    # 返回指定基金的数据
    from core.database import get_fund_by_code
    result = get_fund_by_code(fund_code)
    return result

def get_fund_data(fund_code, force_update=False):
    """
    获取指定基金的数据，并根据缓存策略决定是否更新
    
    Args:
        fund_code (str): 基金代码
        force_update (bool): 是否强制更新数据
    
    Returns:
        dict: 基金数据
    """
    # 先导入数据库模块，确保导入正确
    print("开始获取基金数据...")
    try:
        from core.database import create_tables, get_fund_by_code
        print("成功导入数据库模块")
    except Exception as e:
        print(f"导入数据库模块出错: {e}")
        return None
    
    try:
        # 创建数据库表（如果不存在）
        create_tables()
        print("数据库表创建完成")
        
        # 如果强制更新，则直接获取新数据
        if force_update:
            print("强制更新数据")
            return fetch_and_store_fund_data(fund_code)
            
        # 决定更新动作
        action = get_fund_update_action(fund_code)
        print(f"基金 {fund_code} 更新动作: {action}")
        
        if action == "use_cache":
            # 使用缓存数据
            result = get_fund_by_code(fund_code)
            if result:
                print("使用缓存数据")
                return result
            else:
                # 如果缓存中没有数据，获取一次
                print("缓存中没有数据，获取一次")
                return fetch_and_store_fund_data(fund_code)
        elif action in ["fetch_once", "fetch_realtime", "fetch_nav"]:
            # 获取新数据
            print(f"获取新数据: {action}")
            return fetch_and_store_fund_data(fund_code)
        else:
            # 默认使用缓存
            result = get_fund_by_code(fund_code)
            if result:
                print("使用默认缓存数据")
                return result
            else:
                print("默认获取数据")
                return fetch_and_store_fund_data(fund_code)
        
    except Exception as e:
        print(f"获取基金数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def fetch_and_store_etf_data(etf_code):
    """
    获取并存储指定ETF的数据
    
    Args:
        etf_code (str): ETF代码
    
    Returns:
        dict: 存储的ETF数据，如果获取失败则返回None
    """
    print(f"开始获取ETF {etf_code} 的数据...")
    try:
        # 使用AKSHARE获取ETF数据
        print("使用AKSHARE获取ETF数据...")
        df = ak.fund_etf_fund_daily_em()
        print(f"成功获取 {len(df)} 条ETF数据")
        print(f"DataFrame列名: {list(df.columns)}")
        
        # 查找指定ETF代码
        etf_df = df[df['基金代码'] == etf_code]
        if etf_df.empty:
            print(f"未找到ETF代码为 {etf_code} 的数据")
            return None
        
        # 转换为字典
        etf_data = etf_df.iloc[0].to_dict()
        
        # 动态识别列名
        net_value_col = None
        total_net_value_col = None
        prev_net_value_col = None
        prev_total_net_value_col = None
        
        for key in etf_data.keys():
            if '-单位净值' in key and not net_value_col:
                net_value_col = key
            elif '-累计净值' in key and not total_net_value_col:
                total_net_value_col = key
            elif '-前单位净值' in key or ('-单位净值' in key and net_value_col):
                prev_net_value_col = key
            elif '-前累计净值' in key or ('-累计净值' in key and total_net_value_col):
                prev_total_net_value_col = key
        
        # 存储到数据库
        from core.database import insert_or_update_etf_data
        db_etf_data = {
            'etf_code': etf_data['基金代码'],
            'etf_name': etf_data['基金简称'],
            'type': etf_data['类型'],
            'net_value': normalize_number(etf_data.get(net_value_col)),
            'total_net_value': normalize_number(etf_data.get(total_net_value_col)),
            'prev_net_value': normalize_number(etf_data.get(prev_net_value_col)),
            'prev_total_net_value': normalize_number(etf_data.get(prev_total_net_value_col)),
            'growth_value': normalize_number(etf_data.get('增长值')),
            'growth_rate': normalize_number(etf_data.get('增长率')),
            'market_price': normalize_number(etf_data.get('市价')),
            'discount_rate': normalize_number(etf_data.get('折价率'))
        }
        
        insert_or_update_etf_data(db_etf_data)
        print(f"ETF {etf_code} 数据已存储到数据库")
        
        # 返回数据库中的数据
        from core.database import get_etf_by_code
        return get_etf_by_code(etf_code)
        
    except Exception as e:
        print(f"获取ETF {etf_code} 数据时出错: {e}")
        import traceback
        traceback.print_exc()
        # 如果获取失败，尝试返回数据库中已有的数据
        from core.database import get_etf_by_code
        return get_etf_by_code(etf_code)

def get_etf_data(etf_code, force_update=False):
    """
    获取指定ETF的数据，并根据缓存策略决定是否更新
    
    Args:
        etf_code (str): ETF代码
        force_update (bool): 是否强制更新数据
    
    Returns:
        dict: ETF数据
    """
    # 先导入数据库模块
    try:
        from core.database import create_tables, get_etf_by_code
    except Exception as e:
        print(f"导入数据库模块出错: {e}")
        return None
    
    try:
        # 创建数据库表（如果不存在）
        create_tables()
        
        # 如果强制更新，则直接获取新数据
        if force_update:
            print("强制更新数据")
            return fetch_and_store_etf_data(etf_code)
            
        # 决定更新动作
        action = get_etf_update_action(etf_code)
        print(f"ETF {etf_code} 更新动作: {action}")
        
        if action == "use_cache":
            # 使用缓存数据
            result = get_etf_by_code(etf_code)
            if result:
                print("使用缓存数据")
                return result
            else:
                # 如果缓存中没有数据，获取一次
                print("缓存中没有数据，获取一次")
                return fetch_and_store_etf_data(etf_code)
        elif action in ["fetch_once", "fetch_realtime"]:
            # 获取新数据
            print(f"获取新数据: {action}")
            return fetch_and_store_etf_data(etf_code)
        else:
            # 默认使用缓存
            result = get_etf_by_code(etf_code)
            if result:
                print("使用默认缓存数据")
                return result
            else:
                print("默认获取数据")
                return fetch_and_store_etf_data(etf_code)
        
    except Exception as e:
        print(f"获取ETF数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_realtime_data(product_code, use_cache=True):
    """
    统一获取实时数据接口，自动判断产品类型（股票 > ETF > 基金）
    
    Args:
        product_code (str): 产品代码
        use_cache (bool): 是否使用缓存
    
    Returns:
        tuple: (产品类型, 产品数据)
    """
    print(f"开始获取产品 {product_code} 的实时数据")
    
    # 1. 先尝试获取股票数据
    print("1. 尝试获取股票数据")
    stock_data = get_stock_data(product_code, force_update=not use_cache)
    if stock_data:
        print(f"成功获取股票 {product_code} 的数据")
        return ('stock', stock_data)
    
    # 2. 再尝试获取ETF数据
    print("2. 尝试获取ETF数据")
    etf_data = get_etf_data(product_code, force_update=not use_cache)
    if etf_data:
        print(f"成功获取ETF {product_code} 的数据")
        return ('etf', etf_data)
    
    # 3. 最后尝试获取基金数据
    print("3. 尝试获取基金数据")
    fund_data = get_fund_data(product_code, force_update=not use_cache)
    if fund_data:
        print(f"成功获取基金 {product_code} 的数据")
        return ('fund', fund_data)
    
    print(f"无法获取产品 {product_code} 的数据")
    return (None, None)



