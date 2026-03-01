"""
用户数据模型
"""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .asset import Asset
    from .portfolio import Portfolio
    from .strategy import StrategyGroup
    from .asset_category_mapping import AssetCategoryMapping


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    hashed_password = Column(String(200), nullable=False, comment="哈希密码")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_superuser = Column(Boolean, default=False, comment="是否超级管理员")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    assets = relationship("Asset", back_populates="user", cascade="all, delete-orphan")
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    strategy_groups = relationship("StrategyGroup", back_populates="user", cascade="all, delete-orphan")
    category_mappings = relationship("AssetCategoryMapping", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"
