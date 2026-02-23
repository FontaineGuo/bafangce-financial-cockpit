"""
策略数据模型
"""
from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..core.database import Base
from .enums import StrategyCategory

if TYPE_CHECKING:
    from .user import User


class Strategy(Base):
    """交易策略表"""
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    name = Column(String(100), nullable=False, comment="策略名称")
    type = Column(String(50), comment="策略类型")
    category = Column(String(50), comment="关联的策略分类")
    description = Column(Text, comment="策略描述")
    enabled = Column(Boolean, default=False, comment="是否启用")
    last_execution = Column(DateTime, comment="最后执行时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="strategies")
    conditions = relationship("StrategyCondition", back_populates="strategy", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Strategy {self.name}>"


class StrategyCondition(Base):
    """策略条件表"""
    __tablename__ = "strategy_conditions"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False, index=True, comment="策略ID")
    field = Column(String(50), nullable=False, comment="字段")
    operator = Column(String(20), nullable=False, comment="操作符")
    value = Column(String(100), comment="值")
    logical_operator = Column(String(10), default="AND", comment="逻辑操作符")
    order = Column(Integer, default=0, comment="执行顺序")

    # 关系
    strategy = relationship("Strategy", back_populates="conditions")

    def __repr__(self):
        return f"<StrategyCondition {self.field} {self.operator} {self.value}>"
