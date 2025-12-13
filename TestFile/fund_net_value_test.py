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
        # 使用akshare获取所有场内基金数据
        fund_etf_df = ak.fund_etf_fund_daily_em()
        
        if not fund_etf_df.empty:
            # 过滤出指定基金代码的数据
            fund_data = fund_etf_df[fund_etf_df['基金代码'] == fund_code]
            
            if not fund_data.empty:
                # 获取指定基金的数据
                fund_info = fund_data.iloc[0]
                
                # 获取包含日期的字段名
                date_fields = [col for col in fund_etf_df.columns if '单位净值' in col or '累计净值' in col]
                
                # 初始化结果字典
                result = {
                    "fund_code": fund_info['基金代码'],
                    "fund_name": fund_info['基金简称'],
                    "type": fund_info['类型'],
                    "growth_value": fund_info['增长值'],
                    "growth_rate": fund_info['增长率'],
                    "market_price": fund_info['市价'],
                    "discount_rate": fund_info['折价率']
                }
                
                # 添加带日期的净值字段
                for field in date_fields:
                    result[field] = fund_info[field]
                
                return result
            else:
                return {"error": f"未找到基金 {fund_code} 的数据"}
        else:
            return {"error": "未获取到任何基金数据"}
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
        print(f"基金简称: {result['fund_name']}")
        print(f"类型: {result['type']}")
        
        # 打印所有带日期的净值字段
        for key, value in result.items():
            if '单位净值' in key or '累计净值' in key:
                print(f"{key}: {value}")
        
        print(f"增长值: {result['growth_value']}")
        print(f"增长率: {result['growth_rate']}")
        print(f"市价: {result['market_price']}")
        print(f"折价率: {result['discount_rate']}")
