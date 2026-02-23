"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用设置"""

    # 应用基础配置
    APP_NAME: str = "八方策金融座舱"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./db/bafangce.db"

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis配置（可选，用于缓存）
    REDIS_URL: Optional[str] = None

    # CORS配置
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # 数据缓存配置
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 3600  # 1小时

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
