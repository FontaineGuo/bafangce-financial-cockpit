# 持仓数据管理模块 - 封装与数据库的交互
import sys
import os
import json

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.database import db_client
from backend.models.holding import Holding

# 数据库表名
HOLDINGS_TABLE = 'holdings'

def get_all_holdings(user_id=None):
    """
    获取所有持仓
    
    Args:
        user_id (str/int, optional): 用户ID，用于多用户场景
        
    Returns:
        list: Holding对象列表
    """
    try:
        # 构建查询条件
        query = {} if user_id is None else {'user_id': user_id}
        
        # 从数据库获取所有持仓记录
        holdings_data = db_client.find(HOLDINGS_TABLE, query)
        
        # 转换为Holding对象列表
        holdings = []
        for data in holdings_data:
            # 确保purchase_date是字符串格式
            if 'purchase_date' in data and data['purchase_date'] and not isinstance(data['purchase_date'], str):
                data['purchase_date'] = str(data['purchase_date'])
            
            # 创建Holding对象
            holding = Holding.from_dict(data)
            holdings.append(holding)
        
        return holdings
    except Exception as e:
        print(f"获取持仓数据失败: {e}")
        return []

def add_holding(holding, user_id=None):
    """
    添加新持仓
    
    Args:
        holding (Holding): Holding对象
        user_id (str/int, optional): 用户ID
        
    Returns:
        int: 新增持仓的ID
    """
    try:
        # 只提取数据库表中实际存在的字段
        holding_data = {
            'product_code': holding.product_code,
            'product_name': holding.product_name,
            'product_type': holding.product_type,
            'category': holding.category,
            'quantity': holding.quantity,
            'purchase_price': holding.purchase_price,
            'current_price': holding.current_price,
            'purchase_date': getattr(holding, 'purchase_date', None)  # 可选字段
        }
        
        # 添加用户ID（如果提供）
        if user_id is not None:
            holding_data['user_id'] = user_id
        
        # 插入数据库
        holding_id = db_client.insert(HOLDINGS_TABLE, holding_data)
        
        return holding_id
    except Exception as e:
        print(f"添加持仓数据失败: {e}")
        return None

def update_holding(holding_id, holding):
    """
    更新持仓信息
    
    Args:
        holding_id (int): 持仓ID
        holding (Holding): 更新后的Holding对象
        
    Returns:
        bool: 更新是否成功
    """
    try:
        # 转换为字典格式（排除ID）
        holding_data = holding.to_dict()
        del holding_data['id']
        
        # 更新数据库
        success = db_client.update(HOLDINGS_TABLE, {'id': holding_id}, holding_data)
        
        return success
    except Exception as e:
        print(f"更新持仓数据失败: {e}")
        return False

def delete_holding(holding_id):
    """
    删除持仓
    
    Args:
        holding_id (int): 持仓ID
        
    Returns:
        bool: 删除是否成功
    """
    try:
        # 从数据库删除
        success = db_client.delete(HOLDINGS_TABLE, {'id': holding_id})
        
        return success
    except Exception as e:
        print(f"删除持仓数据失败: {e}")
        return False

def get_holding_by_id(holding_id):
    """
    根据ID获取持仓
    
    Args:
        holding_id (int): 持仓ID
        
    Returns:
        Holding: Holding对象
    """
    try:
        # 从数据库获取
        holding_data = db_client.find_one(HOLDINGS_TABLE, {'id': holding_id})
        
        if not holding_data:
            return None
        
        # 创建Holding对象
        holding = Holding.from_dict(holding_data)
        
        return holding
    except Exception as e:
        print(f"获取持仓数据失败: {e}")
        return None

def get_holdings_by_category(category, user_id=None):
    """
    根据资产类别获取持仓
    
    Args:
        category (str): 资产类别
        user_id (str/int, optional): 用户ID
        
    Returns:
        list: Holding对象列表
    """
    try:
        # 构建查询条件
        query = {'category': category}
        if user_id is not None:
            query['user_id'] = user_id
        
        # 从数据库获取
        holdings_data = db_client.find(HOLDINGS_TABLE, query)
        
        # 转换为Holding对象列表
        holdings = []
        for data in holdings_data:
            holding = Holding.from_dict(data)
            holdings.append(holding)
        
        return holdings
    except Exception as e:
        print(f"获取持仓数据失败: {e}")
        return []
