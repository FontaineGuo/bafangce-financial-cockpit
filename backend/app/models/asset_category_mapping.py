"""
资产分类映射数据模型
"""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..core.database import Base
from .enums import AssetType, StrategyCategory

if TYPE_CHECKING:
    from .user import User


class AssetCategoryMapping(Base):
    """资产分类映射表"""
    __tablename__ = "asset_category_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    asset_code = Column(String(20), nullable=False, index=True, comment="资产代码")
    asset_type = Column(String(20), nullable=False, comment="资产类型")
    strategy_category = Column(String(50), nullable=False, comment="策略分类")
    is_user_override = Column(Boolean, default=False, comment="是否为用户自定义覆盖")
    auto_mapped = Column(Boolean, default=False, comment="是否为系统自动映射")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="category_mappings")

    def __repr__(self):
        return f"<AssetCategoryMapping {self.asset_code} -> {self.strategy_category}>"
