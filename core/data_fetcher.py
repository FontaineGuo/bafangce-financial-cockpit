# 数据获取模块
import akshare as ak
import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import normalize_number

def get_stock_data(stock_code):
    """
    使用AKSHARE库获取A股股票实时数据
    
    Args:
        stock_code (str): A股股票代码，例如 "000001"
    
    Returns:
        dict: 股票实时数据，数值已规范化到小数点后5位
    """
    try:
        # 获取股票实时买卖五档数据
        stock_data = ak.stock_bid_ask_em(symbol=stock_code)
        
        # 如果是DataFrame类型，转换为字典
        if hasattr(stock_data, 'to_dict'):
            # 将DataFrame转换为以'item'为键，'value'为值的字典
            stock_data = dict(zip(stock_data['item'], stock_data['value']))
        
        # 规范化数值格式
        normalized_data = {}
        for key, value in stock_data.items():
            try:
                normalized_data[key] = normalize_number(value)
            except Exception as e:
                # 如果无法转换，保留原始值
                normalized_data[key] = value
        
        return normalized_data
    except Exception as e:
        print(f"获取股票数据时出错: {e}")
        return None

def get_fund_data(fund_code):
    """获取基金实时数据"""
    pass

def get_realtime_data(product_type, code):
    """
    获取实时数据的统一接口
    
    Args:
        product_type (str): 产品类型，例如 "stock" 或 "fund"
        code (str): 产品代码
    
    Returns:
        dict: 产品实时数据
    """
    if product_type == "stock":
        return get_stock_data(code)
    elif product_type == "fund":
        return get_fund_data(code)
    else:
        print(f"不支持的产品类型: {product_type}")
        return None


def test_get_stock_data():
    """
    测试方法：获取A股股票实时数据
    """
    # 测试股票代码，例如平安银行(000001) 或常熟银行(601127)
    test_stock_code = "601127"
    
    print(f"正在获取股票 {test_stock_code} 的实时数据...")
    stock_data = get_stock_data(test_stock_code)
    
    if stock_data is not None:
        print("股票实时数据获取成功:")
        print(stock_data)
    else:
        print("股票实时数据获取失败")


if __name__ == "__main__":
    test_get_stock_data()
