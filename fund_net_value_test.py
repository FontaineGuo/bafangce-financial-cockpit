import akshare as ak

def get_fund_net_value(fund_code: str):
    """
    获取指定基金的最新净值信息
    
    Args:
        fund_code (str): 基金代码
    
    Returns:
        dict: 基金净值信息
    """
    try:
        # 使用akshare获取基金净值信息
        fund_net_value_df = ak.fund_open_fund_info_em(fund=fund_code, indicator="单位净值走势")
        
        if not fund_net_value_df.empty:
            # 获取最新净值记录
            latest_record = fund_net_value_df.iloc[-1]
            return {
                "fund_code": fund_code,
                "date": latest_record['净值日期'],
                "net_value": latest_record['单位净值'],
                "growth_rate": latest_record.get('日增长率', 'N/A')
            }
        else:
            return {"error": f"未找到基金 {fund_code} 的数据"}
    except Exception as e:
        return {"error": f"获取基金 {fund_code} 数据时出错: {str(e)}"}

if __name__ == "__main__":
    # 测试基金代码，以易方达蓝筹精选混合(005827)为例
    test_fund_code = "005827"
    
    print(f"正在获取基金 {test_fund_code} 的最新净值信息...")
    result = get_fund_net_value(test_fund_code)
    
    if "error" in result:
        print(result["error"])
    else:
        print(f"基金代码: {result['fund_code']}")
        print(f"净值日期: {result['date']}")
        print(f"单位净值: {result['net_value']}")
        print(f"日增长率: {result['growth_rate']}")
