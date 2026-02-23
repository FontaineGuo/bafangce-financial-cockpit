"""
Pydantic schemas模块
"""
from .user import User, UserCreate, UserLogin, Token
from .asset import Asset, AssetCreate, AssetUpdate, MarketData
from .portfolio import Portfolio, PortfolioCreate, PortfolioUpdate, PortfolioAsset
from .strategy import Strategy, StrategyCreate, StrategyUpdate, StrategyCondition
from .asset_category_mapping import AssetCategoryMapping, AssetCategoryMappingCreate, AssetCategoryMappingUpdate
from .ai_suggestion import AISuggestion
from .common import Response

__all__ = [
    "User", "UserCreate", "UserLogin", "Token",
    "Asset", "AssetCreate", "AssetUpdate", "MarketData",
    "Portfolio", "PortfolioCreate", "PortfolioUpdate", "PortfolioAsset",
    "Strategy", "StrategyCreate", "StrategyUpdate", "StrategyCondition",
    "AssetCategoryMapping", "AssetCategoryMappingCreate", "AssetCategoryMappingUpdate",
    "AISuggestion",
    "Response",
]
