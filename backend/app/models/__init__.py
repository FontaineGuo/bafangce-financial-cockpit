"""
数据模型模块
"""
from .enums import AssetType, StrategyCategory
from .asset import Asset, MarketData, CacheMetadata
from .user import User
from .portfolio import Portfolio, PortfolioAsset
from .strategy import StrategyGroup, StrategyCategoryAllocation
from .asset_category_mapping import AssetCategoryMapping
from .ai_suggestion import AISuggestion

__all__ = [
    "AssetType",
    "StrategyCategory",
    "Asset",
    "MarketData",
    "CacheMetadata",
    "User",
    "Portfolio",
    "PortfolioAsset",
    "StrategyGroup",
    "StrategyCategoryAllocation",
    "AssetCategoryMapping",
    "AISuggestion",
]
