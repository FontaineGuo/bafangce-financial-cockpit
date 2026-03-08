"""
策略数据模型
"""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Float
from sqlalchemy.orm import relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .user import User


class StrategyGroup(Base):
    """策略组表"""
    __tablename__ = "strategy_groups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    name = Column(String(100), nullable=False, comment="策略组名称")
    description = Column(Text, comment="策略组描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="strategy_groups")
    category_allocations = relationship("StrategyCategoryAllocation", back_populates="strategy_group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<StrategyGroup {self.name}>"


class StrategyCategoryAllocation(Base):
    """策略分类配置表"""
    __tablename__ = "strategy_category_allocations"

    id = Column(Integer, primary_key=True, index=True)
    strategy_group_id = Column(Integer, ForeignKey("strategy_groups.id"), nullable=False, index=True, comment="策略组ID")
    category = Column(String(50), nullable=False, comment="策略分类")
    percentage = Column(Numeric(5, 2), nullable=False, comment="配置百分比(0-100)")
    deviation_threshold = Column(Float, comment="编辑偏离阈值(%)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    strategy_group = relationship("StrategyGroup", back_populates="category_allocations")

    def __repr__(self):
        return f"<StrategyCategoryAllocation {self.category}: {self.percentage}%>"
