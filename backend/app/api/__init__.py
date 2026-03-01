"""
API路由模块
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .assets import router as assets_router
from .portfolios import router as portfolios_router
from .strategy_groups import router as strategy_groups_router
from .asset_categories import router as asset_categories_router
from .ai import router as ai_router

# 创建主路由
router = APIRouter(prefix="/api", tags=["API"])

# 注册子路由
router.include_router(auth_router)
router.include_router(assets_router)
router.include_router(portfolios_router)
router.include_router(strategy_groups_router)
router.include_router(asset_categories_router)
router.include_router(ai_router)
