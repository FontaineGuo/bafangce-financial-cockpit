# 数据库操作模块
import sqlite3
from config.constants import DB_PATH

def connect_db():
    """连接数据库"""
    return sqlite3.connect(DB_PATH)

def create_tables():
    """创建数据库表"""
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
    """根据基金代码获取基金数据"""
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
