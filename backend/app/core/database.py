"""
数据库配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    import os
    from ..models import (
        User,
        Asset,
        MarketData,
        CacheMetadata,
        Portfolio,
        PortfolioAsset,
        Strategy,
        StrategyCondition,
        AssetCategoryMapping,
        AISuggestion,
    )

    # 确保数据库目录存在
    db_dir = os.path.join(os.path.dirname(__file__), "db")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"[INFO] Created database directory: {db_dir}")

    Base.metadata.create_all(bind=engine)
    print("[INFO] Database tables initialized successfully")
