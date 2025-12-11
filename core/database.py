# 数据库操作模块
import sqlite3
from config.constants import DB_PATH

def connect_db():
    """连接数据库"""
    return sqlite3.connect(DB_PATH)

def create_tables():
    """
    创建数据库表
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    # 创建基金数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_data (
            fund_code TEXT PRIMARY KEY,
            fund_name TEXT NOT NULL,
            net_value FLOAT,
            total_net_value FLOAT,
            prev_net_value FLOAT,
            prev_total_net_value FLOAT,
            daily_growth_value FLOAT,
            daily_growth_rate FLOAT,
            purchase_status TEXT,
            redemption_status TEXT,
            fee_rate TEXT,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建股票数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_data (
            stock_code TEXT PRIMARY KEY,
            stock_name TEXT NOT NULL,
            current_price FLOAT,
            total_shares FLOAT,
            circulating_shares FLOAT,
            total_market_value FLOAT,
            circulating_market_value FLOAT,
            industry TEXT,
            listing_date TEXT,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建持仓数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_type TEXT NOT NULL,
            quantity FLOAT NOT NULL,
            purchase_price FLOAT NOT NULL,
            current_price FLOAT,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def execute_query(query, params=None):
    """执行查询"""
    conn = connect_db()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    result = cursor.fetchall()
    conn.close()
    return result

def execute_transaction(queries):
    """执行事务"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        for query, params in queries:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"事务执行失败: {e}")
        return False
    finally:
        conn.close()

def insert_fund_data(fund_data, conn=None):
    """插入或更新基金数据"""
    query = '''
        INSERT OR REPLACE INTO fund_data (
            fund_code, fund_name, net_value, total_net_value, 
            prev_net_value, prev_total_net_value, daily_growth_value, 
            daily_growth_rate, purchase_status, redemption_status, fee_rate, update_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    '''
    
    params = (
        fund_data['fund_code'],
        fund_data['fund_name'],
        fund_data.get('net_value'),
        fund_data.get('total_net_value'),
        fund_data.get('prev_net_value'),
        fund_data.get('prev_total_net_value'),
        fund_data.get('daily_growth_value'),
        fund_data.get('daily_growth_rate'),
        fund_data.get('purchase_status'),
        fund_data.get('redemption_status'),
        fund_data.get('fee_rate')
    )
    
    # 如果提供了连接，则使用该连接，否则创建新连接
    if conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
    else:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

def batch_insert_fund_data(fund_data_list, conn=None):
    """批量插入或更新基金数据"""
    query = '''
        INSERT OR REPLACE INTO fund_data (
            fund_code, fund_name, net_value, total_net_value, 
            prev_net_value, prev_total_net_value, daily_growth_value, 
            daily_growth_rate, purchase_status, redemption_status, fee_rate, update_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    '''
    
    # 准备参数列表
    params_list = []
    for fund_data in fund_data_list:
        params = (
            fund_data['fund_code'],
            fund_data['fund_name'],
            fund_data.get('net_value'),
            fund_data.get('total_net_value'),
            fund_data.get('prev_net_value'),
            fund_data.get('prev_total_net_value'),
            fund_data.get('daily_growth_value'),
            fund_data.get('daily_growth_rate'),
            fund_data.get('purchase_status'),
            fund_data.get('redemption_status'),
            fund_data.get('fee_rate')
        )
        params_list.append(params)
    
    # 如果提供了连接，则使用该连接，否则创建新连接
    if conn:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
    else:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()

def get_fund_by_code(fund_code):
    """
    根据基金代码获取基金数据
    
    Args:
        fund_code (str): 基金代码
    
    Returns:
        dict: 基金数据字典，如果不存在则返回None
    """
    
    query = '''
        SELECT * FROM fund_data 
        WHERE fund_code = ?
    '''
    
    result = execute_query(query, (fund_code,))
    if result:
        # 将查询结果转换为字典
        columns = ['fund_code', 'fund_name', 'net_value', 'total_net_value', 
                  'prev_net_value', 'prev_total_net_value', 'daily_growth_value', 
                  'daily_growth_rate', 'purchase_status', 'redemption_status', 'fee_rate', 'update_time']
        return dict(zip(columns, result[0]))
    return None

def insert_or_update_stock_data(stock_data, conn=None):
    """
    插入或更新股票数据
    
    Args:
        stock_data (dict): 股票数据字典
        conn (sqlite3.Connection, optional): 数据库连接对象
    """
    query = '''
        INSERT OR REPLACE INTO stock_data (
            stock_code, stock_name, current_price, total_shares, 
            circulating_shares, total_market_value, circulating_market_value, 
            industry, listing_date, update_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    '''
    
    params = (
        stock_data['stock_code'],
        stock_data['stock_name'],
        stock_data.get('current_price'),
        stock_data.get('total_shares'),
        stock_data.get('circulating_shares'),
        stock_data.get('total_market_value'),
        stock_data.get('circulating_market_value'),
        stock_data.get('industry'),
        stock_data.get('listing_date')
    )
    
    # 如果提供了连接，则使用该连接，否则创建新连接
    if conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
    else:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

def get_stock_by_code(stock_code):
    """
    根据股票代码获取股票数据
    
    Args:
        stock_code (str): 股票代码
    
    Returns:
        dict: 股票数据字典，如果不存在则返回None
    """
    query = '''
        SELECT * FROM stock_data 
        WHERE stock_code = ?
    '''
    
    result = execute_query(query, (stock_code,))
    if result:
        # 将查询结果转换为字典
        columns = ['stock_code', 'stock_name', 'current_price', 'total_shares', 
                  'circulating_shares', 'total_market_value', 'circulating_market_value', 
                  'industry', 'listing_date', 'update_time']
        return dict(zip(columns, result[0]))
    return None

def get_stock_last_update_time(stock_code):
    """
    获取股票数据的最后更新时间
    
    Args:
        stock_code (str): 股票代码
    
    Returns:
        datetime.datetime or None: 最后更新时间，如果没有数据则返回None
    """
    query = '''
        SELECT update_time FROM stock_data 
        WHERE stock_code = ? 
        ORDER BY update_time DESC 
        LIMIT 1
    '''
    result = execute_query(query, (stock_code,))
    if result:
        # SQLite的TIMESTAMP类型返回的是字符串，需要转换为datetime
        import datetime
        return datetime.datetime.strptime(result[0][0], '%Y-%m-%d %H:%M:%S')
    return None

def add_holding_to_db(holding):
    """
    向数据库添加持仓记录
    
    Args:
        holding (Holding): 持仓对象
    
    Returns:
        int: 插入记录的ID
    """
    query = '''
        INSERT INTO holdings (
            product_code, product_name, product_type, 
            quantity, purchase_price, current_price
        ) VALUES (?, ?, ?, ?, ?, ?)
    '''
    
    params = (
        holding.product_code,
        holding.product_name,
        holding.product_type,
        holding.quantity,
        holding.purchase_price,
        holding.current_price
    )
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    
    # 获取插入记录的ID
    inserted_id = cursor.lastrowid
    conn.close()
    
    return inserted_id

def get_all_holdings_from_db():
    """
    从数据库获取所有持仓记录
    
    Returns:
        list: Holding对象列表
    """
    from models.holding import Holding
    
    query = '''
        SELECT id, product_code, product_name, product_type, 
               quantity, purchase_price, current_price 
        FROM holdings
    '''
    
    result = execute_query(query)
    holdings = []
    
    for row in result:
        holding = Holding(
            id=row[0],
            product_code=row[1],
            product_name=row[2],
            product_type=row[3],
            quantity=row[4],
            purchase_price=row[5],
            current_price=row[6]
        )
        holdings.append(holding)
    
    return holdings

def update_holding_in_db(holding_id, holding):
    """
    更新数据库中的持仓记录
    
    Args:
        holding_id (int): 持仓记录ID
        holding (Holding): 更新后的持仓对象
    
    Returns:
        bool: 更新是否成功
    """
    query = '''
        UPDATE holdings 
        SET product_code = ?, product_name = ?, product_type = ?, 
            quantity = ?, purchase_price = ?, current_price = ?, 
            update_time = CURRENT_TIMESTAMP
        WHERE id = ?
    '''
    
    params = (
        holding.product_code,
        holding.product_name,
        holding.product_type,
        holding.quantity,
        holding.purchase_price,
        holding.current_price,
        holding_id
    )
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    
    # 检查是否有记录被更新
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def delete_holding_from_db(holding_id):
    """
    从数据库删除持仓记录
    
    Args:
        holding_id (int): 持仓记录ID
    
    Returns:
        bool: 删除是否成功
    """
    query = '''
        DELETE FROM holdings WHERE id = ?
    '''
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, (holding_id,))
    conn.commit()
    
    # 检查是否有记录被删除
    success = cursor.rowcount > 0
    conn.close()
    
    return success
