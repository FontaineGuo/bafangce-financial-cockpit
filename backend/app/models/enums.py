"""
枚举类型定义
"""
from enum import Enum


class AssetType(str, Enum):
    """
    资产类型枚举

    注：债券通过基金持有，不设置独立的BOND资产类型。
    债券通过以下基金类型持有：
    - OPEN_FUND: 开放式债券基金（纯债、信用债、可转债等）
    - ETF_FUND: 债券型ETF（国债ETF、信用债ETF等）
    - LOF_FUND: 债券型LOF（场内交易的债券基金）
    """
    STOCK = "STOCK"
    LOF_FUND = "LOF_FUND"
    ETF_FUND = "ETF_FUND"
    OPEN_FUND = "OPEN_FUND"
    CASH = "CASH"


class StrategyCategory(str, Enum):
    """策略分类枚举"""
    CASH = "CASH"
    CN_STOCK_ETF = "CN_STOCK_ETF"
    OVERSEAS_STOCK_ETF = "OVERSEAS_STOCK_ETF"
    COMMODITY = "COMMODITY"
    CREDIT_BOND = "CREDIT_BOND"
    LONG_BOND = "LONG_BOND"
    SHORT_BOND = "SHORT_BOND"
    GOLD = "GOLD"
    OTHER = "OTHER"


class StrategyConditionOperator(str, Enum):
    """策略条件操作符"""
    EQ = "eq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"


class LogicalOperator(str, Enum):
    """逻辑操作符"""
    AND = "AND"
    OR = "OR"


class AISuggestionType(str, Enum):
    """AI建议类型"""
    RISK = "risk"
    REBALANCING = "rebalancing"
    TREND = "trend"


class AISuggestionPriority(str, Enum):
    """AI建议优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AISuggestionStatus(str, Enum):
    """AI建议状态"""
    PENDING = "pending"
    APPLIED = "applied"
    DISMISSED = "dismissed"
