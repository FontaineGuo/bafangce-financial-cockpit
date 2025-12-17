# 计算模块

import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def calculate_position_value(holding, current_price):
    """计算持仓市值"""
    if holding and current_price:
        return holding.quantity * current_price
    return 0.0

def calculate_profit_loss(holding, current_price):
    """计算盈亏"""
    if holding and current_price:
        position_value = calculate_position_value(holding, current_price)
        cost_value = holding.quantity * holding.purchase_price
        return position_value - cost_value
    return 0.0

def calculate_total_value(holdings):
    """计算总资产价值"""
    total = 0.0
    if holdings:
        for holding in holdings:
            if holding.current_price:
                total += holding.quantity * holding.current_price
    return total

def calculate_total_profit_loss(holdings):
    """计算总盈亏"""
    total_profit = 0.0
    if holdings:
        for holding in holdings:
            if holding.current_price:
                profit = calculate_profit_loss(holding, holding.current_price)
                total_profit += profit
    return total_profit
