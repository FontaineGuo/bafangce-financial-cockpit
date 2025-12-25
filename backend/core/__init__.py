# 后端核心模块导出

# 投资组合管理
from .portfolio import (
    PortfolioManager,
    portfolio_manager,
    get_all_holdings,
    add_holding,
    update_holding,
    delete_holding,
    calculate_portfolio_stats,
    calculate_asset_allocation
)

# 数据获取
from .data_fetcher import (
    get_stock_data,
    get_etf_data,
    get_fund_data,
    get_realtime_data,
    get_product_info
)

# 持仓管理
from .holdings_manager import (
    get_all_holdings as db_get_all_holdings,
    add_holding as db_add_holding,
    update_holding as db_update_holding,
    delete_holding as db_delete_holding,
    get_holding_by_id,
    get_holdings_by_category
)

# AKSHARE客户端
from .akshare_client import (
    get_stock_individual_info,
    get_fund_open_fund_daily,
    get_fund_etf_fund_daily
)

# 资产配置监控
from .asset_allocation import AssetAllocationMonitor

# 计算工具
from .calculator import (
    calculate_position_value,
    calculate_profit_loss,
    calculate_total_value,
    calculate_total_profit_loss
)

# 数据库工具
from .database import (
    db_client,
    create_tables,
    connect_db,
    execute_query,
    execute_transaction,
    insert,
    update,
    delete,
    find,
    find_one,
    count
)

__all__ = [
    # PortfolioManager
    'PortfolioManager',
    'portfolio_manager',
    'get_all_holdings',
    'add_holding',
    'update_holding',
    'delete_holding',
    'calculate_portfolio_stats',
    'calculate_asset_allocation',
    
    # Data Fetcher
    'get_stock_data',
    'get_etf_data',
    'get_fund_data',
    'get_realtime_data',
    'get_product_info',
    
    # Holdings Manager
    'db_get_all_holdings',
    'db_add_holding',
    'db_update_holding',
    'db_delete_holding',
    'get_holding_by_id',
    'get_holdings_by_category',
    
    # AKSHARE Client
    'get_stock_individual_info',
    'get_fund_open_fund_daily',
    'get_fund_etf_fund_daily',
    
    # Asset Allocation
    'AssetAllocationMonitor',
    
    # Calculator
    'calculate_position_value',
    'calculate_profit_loss',
    'calculate_total_value',
    'calculate_total_profit_loss',
    
    # Database
    'db_client',
    'create_tables',
    'connect_db',
    'execute_query',
    'execute_transaction',
    'insert',
    'update',
    'delete',
    'find',
    'find_one',
    'count'
]