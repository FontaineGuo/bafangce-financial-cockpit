import akshare as ak

def get_stock_info(stock_code: str):
    """
    使用AKSHARE库获取A股股票信息
    
    Args:
        stock_code (str): A股股票代码，例如 "000001"
    
    Returns:
        dict: 股票信息
    """
    try:
        # 获取股票基本信息
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        return stock_info
    except Exception as e:
        print(f"获取股票信息时出错: {e}")
        return None

def test_get_stock_info():
    """
    测试方法：获取A股股票信息
    """
    # 测试股票代码，例如平安银行(000001)
    test_stock_code = "515080"
    
    print(f"正在获取股票 {test_stock_code} 的信息...")
    stock_info = get_stock_info(test_stock_code)
    
    if stock_info is not None:
        print("股票信息获取成功:")
        print(stock_info)
    else:
        print("股票信息获取失败")

if __name__ == "__main__":
    test_get_stock_info()
