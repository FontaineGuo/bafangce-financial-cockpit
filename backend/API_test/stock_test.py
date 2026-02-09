import akshare as ak

# 定义要查询的股票代码列表
stock_codes = ["518880"]

# 161226 is OK 国投白银 (use LOF api)
# 159985 is OK 豆粕ETF
# 159981 is OK 能源化工ETF
# 159980 is OK 有色ETF大成
# 501018 is failed 南方原油LOF
# 518880 is failed 华安黄金ETF (use ETF api)

# 遍历查询每个股票的信息
for code in stock_codes:
    print(f"\n{'='*50}")
    print(f"股票代码: {code}")
    print(f"{'='*50}")

    try:
        stock_info = ak.stock_individual_info_em(symbol=code)
        print(stock_info)

        # 显示数据列名以便了解数据结构
        if not stock_info.empty:
            print(f"\n数据字段:")
            print(stock_info.columns.tolist())
            print(f"数据类型:")
            print(stock_info.dtypes)
            print(f"数据形状: {stock_info.shape}")
    except Exception as e:
        print(f"查询股票 {code} 时出错: {e}")

# sample
# ==================================================
# 股票代码: 159985
# ==================================================
#    item          value
# 0    最新          1.985
# 1  股票代码         159985
# 2  股票简称          豆粕ETF
# 3   总股本   1399924064.0
# 4   流通股   1399924064.0
# 5   总市值  2778849267.04
# 6  流通市值  2778849267.04
# 7    行业              -
# 8  上市时间       20191205


# 数据字段:
# ['item', 'value']
# 数据类型:
# item     object
# value    object
# dtype: object
# 数据形状: (9, 2)