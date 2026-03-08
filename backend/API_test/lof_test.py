import akshare as ak

# 定义要查询的LOF基金代码列表
lof_codes = ["501018", "161226"]

# 501018 is OK 南方原油LOF
# 161226 is OK 国投白银 (use LOF api)

print("正在获取LOF基金实时行情数据...")
print(f"{'='*80}")

try:
    # 获取所有LOF基金实时行情
    fund_lof_spot_em_df = ak.fund_lof_spot_em()

    # 遍历查询的LOF代码，从结果中筛选出对应的基金
    for code in lof_codes:
        print(f"\nLOF基金代码: {code}")
        print(f"{'-'*50}")

        # 筛选出对应代码的基金信息
        fund_info = fund_lof_spot_em_df[fund_lof_spot_em_df['代码'] == code]

        if not fund_info.empty:
            print(fund_info)
        else:
            print(f"未找到代码为 {code} 的LOF基金")

    # 显示数据列名以便了解数据结构
    print(f"\n\n数据字段:")
    print(fund_lof_spot_em_df.columns.tolist())
    print(f"数据类型:")
    print(fund_lof_spot_em_df.dtypes)
    print(f"数据形状: {fund_lof_spot_em_df.shape}")

except Exception as e:
    print(f"获取LOF基金数据时出错: {e}")


# LOF基金代码: 501018
# --------------------------------------------------
#         代码       名称    最新价    涨跌额   涨跌幅        成交量          成交额    开盘价    最高价    最低价     昨收    换手率       流通市值        总市值
# 12  501018  南方原油LOF  1.314  0.046  3.63  2926603.0  385592522.0  1.296  1.345  1.272  1.268  39.84  965320913  965320913