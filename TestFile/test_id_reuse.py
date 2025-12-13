#!/usr/bin/env python3
# 测试删除持仓后ID重用功能

import sys
import os
import sqlite3

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import connect_db, create_tables
from core.holdings_manager import add_holding, delete_holding, get_all_holdings
from models.holding import Holding
from config.constants import DB_PATH

def reset_database():
    """重置数据库，删除并重新创建表"""
    print("=== 重置数据库 ===")
    # 删除数据库文件
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"删除数据库文件: {DB_PATH}")
    
    # 创建新表
    create_tables()
    print("创建新表")

def test_id_reuse():
    """测试ID重用功能"""
    print("\n=== 测试ID重用功能 ===")
    
    # 1. 添加第一个持仓
    print("1. 添加第一个持仓")
    holding1 = Holding(
        product_code="515080",
        product_name="招商中证红利ETF",
        product_type="etf",
        quantity=1000,
        purchase_price=1.50,
        current_price=1.55
    )
    holding1_id = add_holding(holding1)
    print(f"   添加成功，持仓ID: {holding1_id}")
    
    # 2. 添加第二个持仓
    print("2. 添加第二个持仓")
    holding2 = Holding(
        product_code="515030",
        product_name="华夏中证500ETF",
        product_type="etf",
        quantity=2000,
        purchase_price=5.00,
        current_price=5.10
    )
    holding2_id = add_holding(holding2)
    print(f"   添加成功，持仓ID: {holding2_id}")
    
    # 3. 查看当前所有持仓
    print("\n3. 当前所有持仓:")
    holdings = get_all_holdings()
    for h in holdings:
        print(f"   ID: {h.id}, 代码: {h.product_code}, 名称: {h.product_name}")
    
    # 4. 删除第一个持仓
    print(f"\n4. 删除持仓ID: {holding1_id}")
    delete_holding(holding1_id)
    print(f"   删除成功")
    
    # 5. 查看删除后的持仓
    print("5. 删除后的持仓:")
    holdings = get_all_holdings()
    for h in holdings:
        print(f"   ID: {h.id}, 代码: {h.product_code}, 名称: {h.product_name}")
    
    # 6. 添加新持仓，验证ID是否重用
    print("\n6. 添加新持仓，验证ID是否重用")
    holding3 = Holding(
        product_code="159915",
        product_name="易方达创业板ETF",
        product_type="etf",
        quantity=1500,
        purchase_price=2.80,
        current_price=2.90
    )
    holding3_id = add_holding(holding3)
    print(f"   添加成功，持仓ID: {holding3_id}")
    
    # 7. 查看最终所有持仓
    print("\n7. 最终所有持仓:")
    holdings = get_all_holdings()
    for h in holdings:
        print(f"   ID: {h.id}, 代码: {h.product_code}, 名称: {h.product_name}")
    
    # 8. 验证结果
    if holding3_id == holding1_id:
        print(f"\n✅ 测试成功！新持仓ID {holding3_id} 重用了已删除的持仓ID {holding1_id}")
        return True
    else:
        print(f"\n❌ 测试失败！新持仓ID {holding3_id} 没有重用已删除的持仓ID {holding1_id}")
        return False

def main():
    """主函数"""
    try:
        # 重置数据库
        reset_database()
        
        # 测试ID重用
        test_id_reuse()
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
