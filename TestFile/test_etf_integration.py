import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.data_fetcher import get_realtime_data
from core.database import create_tables
from ui.cli import get_product_info


def test_etf_integration():
    """测试ETF数据获取与UI集成功能"""
    print("=== ETF数据获取与UI集成测试 ===")
    
    # 确保数据库表已创建
    create_tables()
    
    # 测试的代码列表（包含股票、ETF、基金）
    test_codes = ["515080", "600000", "000001"]  # ETF, 股票, 基金
    
    for code in test_codes:
        print(f"\n测试代码 {code}:")
        
        # 测试get_realtime_data函数（自动判断类型）
        print("1. 测试get_realtime_data函数（自动判断类型）:")
        try:
            realtime_data = get_realtime_data(code)
            if realtime_data:
                product_type, product_data = realtime_data
                print(f"   ✅ 成功获取数据:")
                print(f"      类型: {product_type}")
                # 根据类型获取名称和价格
                if product_type == 'stock':
                    print(f"      名称: {product_data.get('stock_name')}")
                    print(f"      当前价格: {product_data.get('current_price')}")
                elif product_type == 'etf':
                    print(f"      名称: {product_data.get('etf_name')}")
                    print(f"      当前价格: {product_data.get('net_value')}")
                elif product_type == 'fund':
                    print(f"      名称: {product_data.get('fund_name')}")
                    print(f"      当前价格: {product_data.get('net_value')}")
            else:
                print(f"   ❌ 无法获取数据")
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试UI的get_product_info函数
        print("2. 测试UI的get_product_info函数:")
        try:
            product_info = get_product_info(code)
            if product_info:
                product_type, product_data = product_info
                print(f"   ✅ 成功获取产品信息:")
                print(f"      类型: {product_type}")
                # 根据类型获取名称和价格
                if product_type == 'stock':
                    print(f"      名称: {product_data.get('stock_name')}")
                    print(f"      当前价格: {product_data.get('current_price')}")
                elif product_type == 'etf':
                    print(f"      名称: {product_data.get('etf_name')}")
                    print(f"      当前价格: {product_data.get('net_value')}")
                elif product_type == 'fund':
                    print(f"      名称: {product_data.get('fund_name')}")
                    print(f"      当前价格: {product_data.get('net_value')}")
            else:
                print(f"   ❌ 无法获取产品信息")
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_etf_integration()
