"""
策略相关schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class StrategyCategoryAllocation(BaseModel):
    """策略分类配置"""
    id: int
    strategy_group_id: int
    category: str
    percentage: float
    deviation_threshold: float | None = None

    class Config:
        from_attributes = True


class StrategyCategoryAllocationCreate(BaseModel):
    """策略分类配置创建"""
    category: str
    percentage: float = Field(..., ge=0, le=100)
    deviation_threshold: float | None = Field(None, ge=0)

    @field_validator('percentage')
    def validate_percentage(cls, v):
        if v < 0 or v > 100:
            raise ValueError('百分比必须在0到100之间')
        return v


class StrategyGroupBase(BaseModel):
    """策略组基础信息"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class StrategyGroupCreate(StrategyGroupBase):
    """策略组创建"""
    category_allocations: list[StrategyCategoryAllocationCreate] = []

    @field_validator('category_allocations')
    def validate_total_percentage(cls, v):
        total = sum(item.percentage for item in v)
        if total > 100:
            raise ValueError(f'所有策略分类的百分比总和不能超过100%，当前为{total}%')
        return v


class StrategyGroupUpdate(BaseModel):
    """策略组更新"""
    name: Optional[str] = None
    description: Optional[str] = None
    category_allocations: Optional[list[StrategyCategoryAllocationCreate]] = None

    @field_validator('category_allocations')
    def validate_total_percentage(cls, v):
        if v is not None:
            total = sum(item.percentage for item in v)
            if total > 100:
                raise ValueError(f'所有策略分类的百分比总和不能超过100%，当前为{total}%')
        return v


class StrategyGroup(StrategyGroupBase):
    """策略组信息"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    category_allocations: list[StrategyCategoryAllocation] = []

    class Config:
        from_attributes = True
