"""
投资组合相关schemas
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class PortfolioAssetBase(BaseModel):
    """组合资产基础信息"""
    pass

class PortfolioAssetCreate(PortfolioAssetBase):
    """组合资产创建"""
    asset_id: int = Field(..., description="资产ID")

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

    model_config = ConfigDict(from_attributes=True)

class StrategyDistributionItem(BaseModel):
    """策略分类分布项"""
    category: str
    count: int
    total_value: float
    percentage: float

class StrategyDistributionStatus(BaseModel):
    """策略分布对比状态"""
    perfect: str = "perfect"
    normal: str = "normal"
    warning: str = "warning"
    danger: str = "danger"
    missing: str = "missing"

class StrategyComparisonItem(BaseModel):
    """策略分布对比项"""
    category: str
    current_percentage: float
    target_percentage: Optional[float] = None
    deviation: Optional[float] = None
    deviation_threshold: Optional[float] = None
    status: str  # perfect, normal, warning, danger, missing
    is_over_threshold: bool = False

class StrategyComparisonSummary(BaseModel):
    """策略分布对比摘要"""
    categories_over_threshold: int = 0
    categories_missing: int = 0
    max_deviation: float = 0.0
    total_deviation: float = 0.0

class StrategyComparison(BaseModel):
    """策略分布对比"""
    current_distribution: list[StrategyComparisonItem] = []
    summary: StrategyComparisonSummary = StrategyComparisonSummary()

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
    strategy_group_id: Optional[int] = None

class Portfolio(PortfolioBase):
    """组合信息"""
    id: int
    user_id: int
    total_value: float
    total_cost: float
    total_profit: float
    total_profit_percent: float
    strategy_group_id: Optional[int] = None
    assets: list[PortfolioAssetResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
