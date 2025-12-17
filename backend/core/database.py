# 数据库操作模块
import sqlite3
import os
import json
import datetime
from backend.config.constants import DB_PATH

# 确保数据库目录存在
db_dir = os.path.dirname(DB_PATH)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

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
    
    # 创建ETF数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS etf_data (
            etf_code TEXT PRIMARY KEY,
            etf_name TEXT NOT NULL,
            type TEXT,
            net_value FLOAT,
            total_net_value FLOAT,
            prev_net_value FLOAT,
            prev_total_net_value FLOAT,
            growth_value FLOAT,
            growth_rate FLOAT,
            market_price FLOAT,
            discount_rate FLOAT,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建持仓数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY,
            product_code TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_type TEXT NOT NULL,
            category TEXT DEFAULT '',
            quantity FLOAT NOT NULL,
            purchase_price FLOAT NOT NULL,
            current_price FLOAT,
            purchase_date TEXT,
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
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"执行事务失败: {e}")
        return False

def insert(table, data):
    """插入数据"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 构建插入语句
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor.execute(query, tuple(data.values()))
        
        # 获取插入的ID
        inserted_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return inserted_id
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"插入数据失败: {e}")
        return None

def update(table, condition, data):
    """更新数据"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 构建更新语句
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        condition_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition_clause}"
        
        params = list(data.values()) + list(condition.values())
        cursor.execute(query, params)
        
        # 获取受影响的行数
        affected_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected_rows > 0
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"更新数据失败: {e}")
        return False

def delete(table, condition):
    """删除数据"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 构建删除语句
        condition_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
        query = f"DELETE FROM {table} WHERE {condition_clause}"
        
        params = list(condition.values())
        cursor.execute(query, params)
        
        # 获取受影响的行数
        affected_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected_rows > 0
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"删除数据失败: {e}")
        return False

def find(table, condition={}, sort_by=None, limit=None):
    """查询数据"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 构建查询语句
        query = f"SELECT * FROM {table}"
        
        params = []
        
        if condition:
            condition_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
            query += f" WHERE {condition_clause}"
            params = list(condition.values())
        
        if sort_by:
            query += f" ORDER BY {sort_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        
        # 获取列名
        columns = [col[0] for col in cursor.description]
        
        # 转换为字典列表
        results = []
        for row in cursor.fetchall():
            result = {}
            for i, col in enumerate(columns):
                result[col] = row[i]
            results.append(result)
        
        conn.close()
        
        return results
    except Exception as e:
        conn.close()
        print(f"查询数据失败: {e}")
        return []

def find_one(table, condition):
    """查询单条数据"""
    results = find(table, condition, limit=1)
    return results[0] if results else None

def count(table, condition={}):
    """统计数据条数"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 构建统计语句
        query = f"SELECT COUNT(*) FROM {table}"
        
        params = []
        
        if condition:
            condition_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
            query += f" WHERE {condition_clause}"
            params = list(condition.values())
        
        cursor.execute(query, params)
        result = cursor.fetchone()[0]
        
        conn.close()
        
        return result
    except Exception as e:
        conn.close()
        print(f"统计数据失败: {e}")
        return 0

# 创建数据库客户端类
class DBClient:
    """数据库客户端"""
    
    def connect(self):
        """连接数据库"""
        return connect_db()
    
    def create_tables(self):
        """创建表"""
        return create_tables()
    
    def execute_query(self, query, params=None):
        """执行查询"""
        return execute_query(query, params)
    
    def execute_transaction(self, queries):
        """执行事务"""
        return execute_transaction(queries)
    
    def insert(self, table, data):
        """插入数据"""
        return insert(table, data)
    
    def update(self, table, condition, data):
        """更新数据"""
        return update(table, condition, data)
    
    def delete(self, table, condition):
        """删除数据"""
        return delete(table, condition)
    
    def find(self, table, condition={}, sort_by=None, limit=None):
        """查询数据"""
        return find(table, condition, sort_by, limit)
    
    def find_one(self, table, condition):
        """查询单条数据"""
        return find_one(table, condition)
    
    def count(self, table, condition={}):
        """统计数据"""
        return count(table, condition)

# 创建全局数据库客户端实例
db_client = DBClient()

def add_category_column_to_holdings():
    """
    确保holdings表有category字段（用于现有数据库的迁移）
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 检查是否已有category字段
        cursor.execute("PRAGMA table_info(holdings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'category' not in columns:
            # 添加category字段
            cursor.execute("ALTER TABLE holdings ADD COLUMN category TEXT DEFAULT ''")
            conn.commit()
            print("已为holdings表添加category字段")
    except Exception as e:
        print(f"添加category字段失败: {e}")
    finally:
        conn.close()

# 初始化数据库
try:
    create_tables()
except Exception as e:
    print(f"初始化数据库失败: {e}")
