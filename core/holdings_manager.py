# 持仓管理模块
from core.database import (
    add_holding_to_db, 
    get_all_holdings_from_db, 
    update_holding_in_db, 
    delete_holding_from_db
)
from models.holding import Holding

def get_all_holdings():
    """获取所有持仓
    
    Returns:
        list: Holding对象列表
    """
    return get_all_holdings_from_db()

def add_holding(holding):
    """添加持仓
    
    Args:
        holding (Holding): 持仓对象
    
    Returns:
        int: 插入记录的ID
    """
    # 验证输入参数类型
    if not isinstance(holding, Holding):
        raise TypeError("参数必须是Holding类型")
    
    # 添加到数据库
    return add_holding_to_db(holding)

def update_holding(holding_id, holding):
    """更新持仓
    
    Args:
        holding_id (int): 持仓记录ID
        holding (Holding): 更新后的持仓对象
    
    Returns:
        bool: 更新是否成功
    """
    # 验证输入参数类型
    if not isinstance(holding, Holding):
        raise TypeError("参数必须是Holding类型")
    
    # 更新数据库记录
    return update_holding_in_db(holding_id, holding)

def delete_holding(holding_id):
    """删除持仓
    
    Args:
        holding_id (int): 持仓记录ID
    
    Returns:
        bool: 删除是否成功
    """
    # 删除数据库记录
    return delete_holding_from_db(holding_id)
