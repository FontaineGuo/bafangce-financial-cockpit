"""
资产相关schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from ..models.enums import AssetType


class MarketData(BaseModel):
    """市场数据"""
    price: float
    change_amount: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[float] = None
    turnover: Optional[float] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    prev_close: Optional[float] = None
    turnover_rate: Optional[float] = None
    circulating_market_cap: Optional[float] = None
    total_market_cap: Optional[float] = None
    unit_net_value: Optional[float] = None
    accumulated_net_value: Optional[float] = None
    discount_rate: Optional[float] = None


class AssetBase(BaseModel):
    """资产基础信息"""
    code: str = Field(..., min_length=1, max_length=20)
    name: Optional[str] = Field(None, max_length=100)
    type: AssetType
    market: str = "CN"
    quantity: float = Field(..., ge=0)
    cost_price: float = Field(..., ge=0)


class AssetCreate(AssetBase):
    """
    资产创建

    说明：
    - name字段为可选，如果未提供将从市场数据自动获取
    - 代码、类型、数量、成本价是必填项
    - 其他字段有默认值
    """
    pass


class AssetUpdate(BaseModel):
    """资产更新"""
    name: Optional[str] = None
    type: Optional[AssetType] = None
    market: Optional[str] = None
    quantity: Optional[float] = None
    cost_price: Optional[float] = None


class AssetStrategyCategoryUpdate(BaseModel):
    """更新资产策略分类"""
    strategy_category: str = Field(..., description="策略分类（参考 StrategyCategory 枚举）")


class Asset(AssetBase):
    """资产信息"""
    id: int
    user_id: int
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    profit: Optional[float] = None
    profit_percent: Optional[float] = None
    market_data: Optional[MarketData] = None
    strategy_category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
