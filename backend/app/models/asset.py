"""
资产相关数据模型
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from ..core.database import Base
from .enums import AssetType, StrategyCategory


class MarketData(Base):
    """市场数据表"""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String(20), index=True, nullable=False, comment="资产代码")
    price = Column(Float, nullable=False, comment="最新价")
    change_amount = Column(Float, comment="涨跌额")
    change_percent = Column(Float, comment="涨跌幅")
    volume = Column(Float, comment="成交量")
    turnover = Column(Float, comment="成交额")
    open_price = Column(Float, comment="开盘价")
    high_price = Column(Float, comment="最高价")
    low_price = Column(Float, comment="最低价")
    prev_close = Column(Float, comment="昨收价")
    turnover_rate = Column(Float, comment="换手率")
    circulating_market_cap = Column(Float, comment="流通市值")
    total_market_cap = Column(Float, comment="总市值")
    unit_net_value = Column(Float, comment="单位净值")
    accumulated_net_value = Column(Float, comment="累计净值")
    discount_rate = Column(Float, comment="折价率")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def __repr__(self):
        return f"<MarketData {self.asset_code}>"


class CacheMetadata(Base):
    """缓存元数据表"""
    __tablename__ = "cache_metadata"

    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(50), nullable=False, index=True, comment="数据类型")
    code = Column(String(20), nullable=False, index=True, comment="资产代码")
    cached_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="缓存时间")
    expires_at = Column(DateTime, nullable=False, comment="过期时间")
    data_size = Column(Integer, comment="数据大小（字节）")

    def __repr__(self):
        return f"<CacheMetadata {self.data_type}:{self.code}>"


class Asset(Base):
    """资产表"""
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    code = Column(String(20), unique=True, nullable=False, index=True, comment="资产代码")
    name = Column(String(100), nullable=False, comment="资产名称")
    type = Column(String(20), nullable=False, comment="资产类型")
    strategy_category = Column(String(20), nullable=True, comment="策略分类")
    market = Column(String(10), nullable=False, default="CN", comment="市场")

    # 手动价格设置相关字段
    is_manually_set = Column(Boolean, default=False, comment="是否手动设置价格")
    manual_set_price = Column(Float, nullable=True, comment="手动设置的价格")
    manual_set_at = Column(DateTime, nullable=True, comment="手动设置时间")

    quantity = Column(Float, nullable=False, comment="持有数量")
    cost_price = Column(Float, nullable=False, comment="成本价")
    current_price = Column(Float, comment="当前价")
    market_value = Column(Float, comment="市值")
    profit = Column(Float, comment="盈亏")
    profit_percent = Column(Float, comment="盈亏百分比")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="assets")

    def __repr__(self):
        return f"<Asset {self.code} {self.name}>"
