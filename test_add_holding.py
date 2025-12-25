#!/usr/bin/env python3
# 测试添加持仓功能

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.portfolio import PortfolioManager

# 实例化PortfolioManager
portfolio_manager = PortfolioManager()

# 测试添加持仓（不包含product_name，使用category作为product_type）
test_data = {
    "product_code": "000001",
    "category": "stock",
    "quantity": 100,
    "purchase_price": 10.0
}

print("测试添加持仓（不包含product_name）...")
success, result = portfolio_manager.add_holding(test_data)

if success:
    print(f"添加成功: {result}")
else:
    print(f"添加失败: {result}")
