"""
投资组合相关schemas
"""
from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field


class PortfolioAssetBase(BaseModel):
    """组合资产基础信息"""
    target_weight: float = Field(..., ge=0, le=100)


class PortfolioAssetCreate(PortfolioAssetBase):
    """组合资产创建"""
    asset_id: int = Field(..., description="资产ID")


class PortfolioAssetStrategyCategoryUpdate(BaseModel):
    """更新投资组合资产策略分类"""
    strategy_category: str = Field(..., description="策略分类（参考 StrategyCategory 枚举）")


class PortfolioAssetResponse(PortfolioAssetBase):
    """组合资产响应"""
    id: int
    portfolio_id: int
    asset_id: int
    current_weight: float
    allocation_amount: float
    asset_code: Optional[str] = Field(None, description="资产代码")
    asset_name: Optional[str] = Field(None, description="资产名称")
    strategy_category: Optional[str] = Field(None, description="策略分类")
    asset_market_value: Optional[float] = Field(None, description="资产市值")
    asset_cost: Optional[float] = Field(None, description="资产成本")
    asset_profit: Optional[float] = Field(None, description="资产盈亏")
    asset_profit_percent: Optional[float] = Field(None, description="资产收益率(%)")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PortfolioAsset(PortfolioAssetBase):
    """组合资产信息（兼容旧代码）"""
    id: int
    portfolio_id: int
    asset_id: int
    current_weight: float
    allocation_amount: float

    class Config:
        from_attributes = True


class StrategyDistributionItem(BaseModel):
    """策略分类分布项"""
    category: str
    count: int
    total_value: float
    percentage: float


class PortfolioBase(BaseModel):
    """组合基础信息"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class PortfolioCreate(PortfolioBase):
    """组合创建"""
    assets: Optional[list[PortfolioAssetCreate]] = None


class PortfolioUpdate(BaseModel):
    """组合更新"""
    name: Optional[str] = None
    description: Optional[str] = None


class Portfolio(PortfolioBase):
    """组合信息"""
    id: int
    user_id: int
    total_value: float
    total_cost: float
    total_profit: float
    total_profit_percent: float
    assets: list[PortfolioAssetResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
