"""
数据服务工厂 - 根据配置选择真实数据或Mock数据

该模块提供统一的数据服务接口，根据配置自动选择数据源。
"""
from typing import Optional

from ..core.config import settings
from .real_data import MarketDataService, RealMarketDataService
from .mock_data import MockDataService


def get_market_data_service() -> MarketDataService:
    """
    获取市场数据服务实例

    根据配置文件中的USE_REAL_DATA设置选择数据源：
    - USE_REAL_DATA = True: 使用真实数据服务（需要实现）
    - USE_REAL_DATA = False: 使用Mock数据服务（当前默认）

    Returns:
        MarketDataService: 市场数据服务实例
    """
    if settings.USE_REAL_DATA and RealMarketDataService:
        # 使用真实数据服务
        return RealMarketDataService()
    else:
        # 使用Mock数据服务（默认）
        return MockDataService()


# 创建全局数据服务实例
market_data_service = get_market_data_service()


def refresh_market_data_service() -> None:
    """
    刷新数据服务实例

    在配置变更后调用此方法重新创建服务实例。
    主要用于开发和测试场景。
    """
    global market_data_service
    market_data_service = get_market_data_service()


def get_data_source_info() -> dict:
    """
    获取当前数据源信息

    Returns:
        dict: 包含数据源类型和状态的字典
    """
    is_using_real_data = settings.USE_REAL_DATA and RealMarketDataService is not None

    return {
        "source": "real_api" if is_using_real_data else "mock_data",
        "service_type": "RealMarketDataService" if is_using_real_data else "MockDataService",
        "config_setting": settings.USE_REAL_DATA,
        "description": "使用真实金融API数据" if is_using_real_data else "使用Mock测试数据"
    }
