import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.data_fetcher import get_etf_data
from core.database import create_tables


def test_etf_data():
    """测试ETF数据获取功能"""
    print("=== ETF数据获取测试 ===")
    
    # 确保数据库表已创建
    create_tables()
    
    # 测试的ETF代码
    etf_codes = ["515080"]  # 招商中证红利ETF
    
    for code in etf_codes:
        print(f"\n测试获取ETF代码 {code} 的数据...")
        try:
            etf_data = get_etf_data(code, force_update=True)
            
            if etf_data:
                print(f"✅ 成功获取ETF数据:")
                print(f"   代码: {etf_data['etf_code']}")
                print(f"   名称: {etf_data['etf_name']}")
                print(f"   类型: {etf_data['type']}")
                print(f"   当前净值: {etf_data['net_value']}")
                print(f"   累计净值: {etf_data['total_net_value']}")
                print(f"   前一日净值: {etf_data['prev_net_value']}")
                print(f"   前一日累计净值: {etf_data['prev_total_net_value']}")
                print(f"   增长值: {etf_data['growth_value']}")
                print(f"   增长率: {etf_data['growth_rate']}")
                print(f"   市价: {etf_data['market_price']}")
                print(f"   折价率: {etf_data['discount_rate']}")
            else:
                print(f"❌ 无法获取ETF {code} 的数据")
                
        except Exception as e:
            print(f"❌ 获取ETF {code} 数据失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_etf_data()
