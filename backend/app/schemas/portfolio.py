"""
投资组合相关schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PortfolioAssetBase(BaseModel):
    """组合资产基础信息"""
    target_weight: float = Field(..., ge=0, le=100)


class PortfolioAsset(PortfolioAssetBase):
    """组合资产信息"""
    id: int
    portfolio_id: int
    asset_id: int
    current_weight: float
    allocation_amount: float

    class Config:
        from_attributes = True


class PortfolioBase(BaseModel):
    """组合基础信息"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class PortfolioCreate(PortfolioBase):
    """组合创建"""
    assets: Optional[list[PortfolioAssetBase]] = None


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
    assets: list[PortfolioAsset] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
