import akshare as ak

# 定义要查询的场内基金代码列表
# fund_codes = ["513880", "510300", "159981", "518880"]

# 513880 is OK 华安日经225ETF
# 510300 is OK 沪深300ETF
# 159981 is OK 能源化工ETF
# 518880 is OK 华安黄金ETF 

fund_codes = ["501018", "161226"]

print("正在获取场内基金行情数据...")
print(f"{'='*80}")

try:
    # 获取所有场内基金行情数据
    fund_etf_fund_daily_em_df = ak.fund_etf_fund_daily_em()

    # 遍历查询的基金代码，从结果中筛选出对应的基金
    for code in fund_codes:
        print(f"\n场内基金代码: {code}")
        print(f"{'-'*50}")

        # 筛选出对应代码的基金信息
        fund_info = fund_etf_fund_daily_em_df[fund_etf_fund_daily_em_df['基金代码'] == code]

        if not fund_info.empty:
            print(fund_info)
        else:
            print(f"未找到代码为 {code} 的场内基金")

    # 可选：显示数据列名以便了解数据结构
    print(f"\n\n数据字段:")
    print(fund_etf_fund_daily_em_df.columns.tolist())

except Exception as e:
    print(f"获取场内基金数据时出错: {e}")



# 场内基金代码: 513880
# --------------------------------------------------
#        基金代码        基金简称        类型 2026-02-09-单位净值 2026-02-09-累计净值 2026-02-06-单位净值 2026-02-06-累计净值     增长值    增长率      市价     折价率
# 247  513880  华安日经225ETF  指数型-海外股票          1.8002          1.8002          1.7405          1.7405  0.0597  3.43%  1.8140  -0.77%

# 数据字段:
# ['基金代码', '基金简称', '类型', '2026-02-09-单位净值', '2026-02-09-累计净值', '2026-02-06-单位净值', '2026-02-06-累计净值', '增长值', '增长率', '市价', '折价率']