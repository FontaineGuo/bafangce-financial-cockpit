#!/usr/bin/env python3
# 测试CLI修复后的ETF数据处理功能

import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.cli import get_product_info

# 测试数据
TEST_ETF_CODE = "515080"

def test_product_info():
    """测试获取产品信息功能"""
    print(f"=== 测试获取产品信息功能: {TEST_ETF_CODE} ===")
    
    # 获取产品信息
    product_type, product_info = get_product_info(TEST_ETF_CODE)
    
    if product_info:
        print(f"✅ 成功获取产品信息")
        print(f"产品类型: {product_type}")
        print(f"产品信息键名: {list(product_info.keys())}")
        print(f"产品名称: {product_info.get('etf_name', product_info.get('fund_name', product_info.get('stock_name')))}")
        return True
    else:
        print(f"❌ 无法获取产品信息")
        return False

def main():
    """主测试函数"""
    test_product_info()

if __name__ == "__main__":
    main()
