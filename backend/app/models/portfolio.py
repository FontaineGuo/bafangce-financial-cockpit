"""
投资组合数据模型
"""
from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .user import User
    from .asset import Asset


class Portfolio(Base):
    """投资组合表"""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    name = Column(String(100), nullable=False, comment="组合名称")
    description = Column(Text, comment="组合描述")
    total_value = Column(Float, default=0, comment="总市值")
    total_cost = Column(Float, default=0, comment="总成本")
    total_profit = Column(Float, default=0, comment="总盈亏")
    total_profit_percent = Column(Float, default=0, comment="总盈亏百分比")
    strategy_group_id = Column(Integer, ForeignKey("strategy_groups.id"), nullable=True, index=True, comment="应用的策略组ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="portfolios")
    assets = relationship("PortfolioAsset", back_populates="portfolio", cascade="all, delete-orphan")
    strategy_group = relationship("StrategyGroup", backref="portfolios")

    def __repr__(self):
        return f"<Portfolio {self.name}>"


class PortfolioAsset(Base):
    """投资组合资产关联表"""
    __tablename__ = "portfolio_assets"
    __table_args__ = (
        UniqueConstraint('asset_id', name='uq_portfolio_asset_asset_id'),
        {'comment': '投资组合资产关联表，每项资产只能被一个组合持有'}
    )

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True, comment="组合ID")
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True, comment="资产ID")
    current_weight = Column(Float, default=0, comment="当前权重（百分比）")
    allocation_amount = Column(Float, default=0, comment="分配金额")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    portfolio = relationship("Portfolio", back_populates="assets")
    asset = relationship("Asset", backref="portfolio_association")

    def __repr__(self):
        return f"<PortfolioAsset portfolio_id={self.portfolio_id} asset_id={self.asset_id}>"
