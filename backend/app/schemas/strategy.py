"""
策略相关schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StrategyCondition(BaseModel):
    """策略条件"""
    id: int
    strategy_id: int
    field: str
    operator: str
    value: str
    logical_operator: str = "AND"
    order: int = 0

    class Config:
        from_attributes = True


class StrategyConditionCreate(BaseModel):
    """策略条件创建"""
    field: str
    operator: str
    value: str
    logical_operator: str = "AND"
    order: int = 0


class StrategyBase(BaseModel):
    """策略基础信息"""
    name: str = Field(..., min_length=1, max_length=100)
    type: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = False


class StrategyCreate(StrategyBase):
    """策略创建"""
    conditions: Optional[list[StrategyConditionCreate]] = []


class StrategyUpdate(BaseModel):
    """策略更新"""
    name: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None


class Strategy(StrategyBase):
    """策略信息"""
    id: int
    user_id: int
    last_execution: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
