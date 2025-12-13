#!/usr/bin/env python3
# 直接测试持仓管理功能的脚本

import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.holdings_manager import add_holding, get_all_holdings, update_holding, delete_holding
from core.data_fetcher import get_etf_data
from models.holding import Holding
from core.database import create_tables

# 创建数据库表
create_tables()

# 测试数据
TEST_ETF_CODE = "515080"
TEST_QUANTITY = 1000
TEST_PURCHASE_PRICE = 1.5453
TEST_NEW_QUANTITY = 2000
TEST_NEW_PURCHASE_PRICE = 1.55

def test_add_holding():
    """测试添加持仓功能"""
    print("=== 测试添加持仓功能 ===")
    
    # 获取ETF数据
    etf_data = get_etf_data(TEST_ETF_CODE, force_update=True)
    
    if not etf_data:
        print(f"❌ 无法获取ETF数据: {TEST_ETF_CODE}")
        return None
    
    print(f"✅ 获取ETF数据成功: {etf_data['etf_name']}")
    
    # 创建持仓对象
    holding = Holding(
        product_code=TEST_ETF_CODE,
        product_name=etf_data['etf_name'],
        product_type="etf",
        quantity=TEST_QUANTITY,
        purchase_price=TEST_PURCHASE_PRICE,
        current_price=etf_data['net_value']
    )
    
    # 添加持仓
    try:
        holding_id = add_holding(holding)
        print(f"✅ 持仓添加成功！持仓ID: {holding_id}")
        return holding_id
    except Exception as e:
        print(f"❌ 持仓添加失败: {e}")
        return None

def test_view_holdings():
    """测试查看持仓功能"""
    print("\n=== 测试查看持仓功能 ===")
    
    try:
        # 获取所有持仓
        holdings = get_all_holdings()
        
        if not holdings:
            print("❌ 暂无持仓记录！")
            return None
        
        print(f"✅ 成功获取{len(holdings)}条持仓记录")
        
        # 打印持仓列表
        print("\n持仓列表:")
        print(f"{'ID':^5} {'类型':^6} {'代码':^12} {'名称':^18} {'份额':^12} {'成本价':^12} {'当前价':^12}")
        print("-" * 80)
        
        holding_objects = []
        for holding in holdings:
            if isinstance(holding, tuple):
                holding = Holding.from_dict({
                    'id': holding[0],
                    'product_code': holding[1],
                    'product_name': holding[2],
                    'product_type': holding[3],
                    'quantity': holding[4],
                    'purchase_price': holding[5],
                    'current_price': holding[6],
                    'update_time': holding[7]
                })
            holding_objects.append(holding)
            
            product_type_str = "股票" if holding.product_type == "stock" else "ETF" if holding.product_type == "etf" else "基金"
            print(f"{holding.id:^5} {product_type_str:^6} {holding.product_code:^12} {holding.product_name:^18} {holding.quantity:^12.2f} {holding.purchase_price:^12.2f} {holding.current_price:^12.2f}")
        
        return holding_objects
    except Exception as e:
        print(f"❌ 查看持仓失败: {e}")
        return None

def test_update_holding(holding_id):
    """测试更新持仓功能"""
    print(f"\n=== 测试更新持仓功能 (ID: {holding_id}) ===")
    
    try:
        # 获取所有持仓
        holdings = get_all_holdings()
        
        # 查找要更新的持仓
        target_holding = None
        for holding in holdings:
            if isinstance(holding, tuple) and holding[0] == holding_id:
                target_holding = Holding.from_dict({
                    'id': holding[0],
                    'product_code': holding[1],
                    'product_name': holding[2],
                    'product_type': holding[3],
                    'quantity': holding[4],
                    'purchase_price': holding[5],
                    'current_price': holding[6],
                    'update_time': holding[7]
                })
                break
            elif hasattr(holding, 'id') and holding.id == holding_id:
                target_holding = holding
                break
        
        if not target_holding:
            print(f"❌ 找不到ID为{holding_id}的持仓！")
            return False
        
        print(f"找到要更新的持仓: {target_holding.product_name}")
        print(f"原份额: {target_holding.quantity} → 新份额: {TEST_NEW_QUANTITY}")
        print(f"原成本价: {target_holding.purchase_price} → 新成本价: {TEST_NEW_PURCHASE_PRICE}")
        
        # 创建更新后的持仓对象
        updated_holding = Holding(
            id=target_holding.id,
            product_code=target_holding.product_code,
            product_name=target_holding.product_name,
            product_type=target_holding.product_type,
            quantity=TEST_NEW_QUANTITY,
            purchase_price=TEST_NEW_PURCHASE_PRICE,
            current_price=target_holding.current_price
        )
        
        # 更新持仓
        success = update_holding(holding_id, updated_holding)
        
        if success:
            print("✅ 持仓更新成功！")
            return True
        else:
            print("❌ 持仓更新失败！")
            return False
            
    except Exception as e:
        print(f"❌ 更新持仓失败: {e}")
        return False

def test_delete_holding(holding_id):
    """测试删除持仓功能"""
    print(f"\n=== 测试删除持仓功能 (ID: {holding_id}) ===")
    
    try:
        # 删除持仓
        success = delete_holding(holding_id)
        
        if success:
            print("✅ 持仓删除成功！")
            return True
        else:
            print("❌ 持仓删除失败！")
            return False
            
    except Exception as e:
        print(f"❌ 删除持仓失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试持仓管理功能...")
    
    # 1. 测试添加持仓
    holding_id = test_add_holding()
    
    if holding_id:
        # 2. 测试查看持仓
        test_view_holdings()
        
        # 3. 测试更新持仓
        if test_update_holding(holding_id):
            # 4. 再次查看持仓
            test_view_holdings()
            
            # 5. 测试删除持仓
            test_delete_holding(holding_id)
            
            # 6. 最后查看持仓
            test_view_holdings()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
