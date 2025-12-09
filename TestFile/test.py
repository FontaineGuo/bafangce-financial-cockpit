import akshare as ak
import pandas as pd
def get_today_fund_nav(fund_code):
    """
    获取指定基金的当日净值数据
    :param fund_code: 基金代码，字符串类型，例如 "000001"
    :return: 包含该基金当日净值信息的 pandas Series，如果未找到则返回 None
    """
    try:
        # 获取所有开放式基金的当日净值数据[citation:10]
        df = ak.fund_open_fund_daily_em()
        
        # 根据基金代码筛选
        fund_data = df[df['基金代码'] == fund_code]
        
        if not fund_data.empty:
            # 通常第一列就是最新的净值数据，取第一条记录
            return fund_data.iloc[0]
        else:
            print(f"未找到基金代码为 {fund_code} 的当日数据。")
            return None
            
    except Exception as e:
        print(f"获取数据时出现错误：{e}")
        return None

# 示例：获取华夏成长混合(000001)的当日净值
fund_code = "000001"
result = get_today_fund_nav(fund_code)

if result is not None:
    print(f"基金代码: {result['基金代码']}")
    print(f"基金简称: {result['基金简称']}")
    print(f"单位净值: {result.get('单位净值', '列名可能已更新')}")
    print(f"日增长率: {result.get('日增长率', '列名可能已更新')}")
    # 注意：DataFrame的列名可能包含日期，例如“2020-12-28-单位净值”[citation:10]
    # 打印所有信息以便查看实际结构
    print("\n获取到的所有字段：")
    print(result)