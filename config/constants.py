# 常量定义

# 数据库配置
DB_PATH = "data/portfolio.db"

# Akshare配置
AKSHARE_TIMEOUT = 10

# 界面配置
WINDOW_TITLE = "八方策金融座舱"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

# 资产配置策略常量
# 全天候策略：包含balance-function.md中定义的8个资产品类
DEFAULT_ASSET_ALLOCATION_STRATEGY = {
    'china_stock_etf': {'target_ratio': 0.10, 'max_deviation': 0.03},    # 中国股票或指数ETF 10%，最大偏离3%
    'foreign_stock_etf': {'target_ratio': 0.10, 'max_deviation': 0.03},  # 海外股票或指数ETF 10%，最大偏离3%
    'commodity': {'target_ratio': 0.10, 'max_deviation': 0.02},         # 大宗商品 10%，最大偏离3%
    'gold': {'target_ratio': 0.10, 'max_deviation': 0.02},              # 黄金 10%，最大偏离3%
    'long_bond': {'target_ratio': 0.3, 'max_deviation': 0.015},         # 长债 30%，最大偏离3%
    'short_bond': {'target_ratio': 0.198, 'max_deviation': 0.015},        # 短债 19.8%，最大偏离3%
    'credit_bond': {'target_ratio': 0.102, 'max_deviation': 0.015},       # 信用债 10.2%，最大偏离3%
    'cash': {'target_ratio': 0.0, 'max_deviation': 0.00}               # 现金 0%，最大偏离0%
}

# 资产类别映射
ASSET_CATEGORY_MAP = {
    # 股票类别映射
    'stock': {
        'china_stock': 'china_stock_etf',    # 中国股票
        'foreign_stock': 'foreign_stock_etf' # 海外股票
    },
    # 基金类别映射
    'fund': {
        'china_stock_fund': 'china_stock_etf',    # 中国股票型基金
        'foreign_stock_fund': 'foreign_stock_etf',  # 海外股票型基金
        'commodity_fund': 'commodity',         # 大宗商品型基金
        'gold_fund': 'gold',                   # 黄金型基金
        'long_bond_fund': 'long_bond',         # 长债型基金
        'short_bond_fund': 'short_bond',       # 短债型基金
        'credit_bond_fund': 'credit_bond',     # 信用债型基金
        'money_fund': 'cash'                   # 货币型基金
    },
    # ETF类别映射
    'etf': {
        'china_stock_etf': 'china_stock_etf',    # 中国股票或指数ETF
        'foreign_stock_etf': 'foreign_stock_etf',  # 海外股票或指数ETF
        'commodity_etf': 'commodity',         # 大宗商品ETF
        'gold_etf': 'gold',                   # 黄金ETF
        'long_bond_etf': 'long_bond',         # 长债ETF
        'short_bond_etf': 'short_bond',       # 短债ETF
        'credit_bond_etf': 'credit_bond',     # 信用债ETF
        'money_etf': 'cash'                   # 货币ETF
    }
}
