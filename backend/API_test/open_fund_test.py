import akshare as ak

# 定义要查询的开放式基金代码列表
# fund_codes = ["003376", "006848", "007194", "006484", "000216", "007492", "000614"]

# fund_codes = ["007280", "017641", "021539", "016452", "007721", "018043", "016532", "019172"]
fund_codes = ["021539"]


# All test OK

print("正在获取开放式基金实时数据...")
print(f"{'='*80}")

try:
    # 获取所有开放式基金实时数据
    fund_open_fund_daily_em_df = ak.fund_open_fund_daily_em()

    # 遍历查询的基金代码，从结果中筛选出对应的基金
    for code in fund_codes:
        print(f"\n开放式基金代码: {code}")
        print(f"{'-'*50}")

        # 筛选出对应代码的基金信息
        fund_info = fund_open_fund_daily_em_df[fund_open_fund_daily_em_df['基金代码'] == code]

        if not fund_info.empty:
            print(fund_info)
        else:
            print(f"未找到代码为 {code} 的开放式基金")

    # 可选：显示数据列名以便了解数据结构
    print(f"\n\n数据字段:")
    print(fund_open_fund_daily_em_df.columns.tolist())

except Exception as e:
    print(f"获取开放式基金数据时出错: {e}")


# 数据字段:
# ['基金代码', '基金简称', '2026-02-09-单位净值', '2026-02-09-累计净值', '2026-02-06-单位净值', '2026-02-06-累计净值', '日增长值', '日增长率', '申购状态', '赎回状态', '手续费']