"""
资产API路由

说明：
- 创建资产时，name字段为可选
- 如果未提供name，系统会从mock数据/akshare API获取资产名称
- 这样可以简化用户操作，只需输入代码和基本信息即可
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.user import User
from ..models.asset import Asset
from ..models.enums import AssetType
from ..schemas.asset import (
    Asset as AssetSchema,
    AssetCreate,
    AssetUpdate,
    AssetStrategyCategoryUpdate,
    MarketData
)
from ..schemas.common import Response, PaginatedResponse
from ..utils.auth import get_current_active_user
from ..services.mock_data import mock_data_service
from ..services.asset_category_mapping import asset_category_mapping_service

router = APIRouter(prefix="/assets", tags=["资产"])


@router.get("", response_model=Response[List[AssetSchema]])
async def get_assets(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取资产列表"""
    assets = db.query(Asset).filter(Asset.user_id == current_user.id).offset(skip).limit(limit).all()

    # 更新资产的市场数据和策略分类
    for asset in assets:
        # 获取市场数据
        market_data = mock_data_service.get_market_data(asset.code, asset.type)
        if market_data:
            asset.current_price = market_data["price"]
            asset.market_value = asset.quantity * market_data["price"]
            asset.profit = (market_data["price"] - asset.cost_price) * asset.quantity
            asset.profit_percent = ((market_data["price"] - asset.cost_price) / asset.cost_price) * 100

        # 获取策略分类
        asset.strategy_category = asset_category_mapping_service.get_effective_strategy_category(
            db, current_user.id, asset.code, asset.type, asset.name
        )

    db.commit()
    return Response.success_response(data=assets)


@router.get("/{asset_id}", response_model=Response[AssetSchema])
async def get_asset(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取单个资产"""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )

    # 更新市场数据
    market_data = mock_data_service.get_market_data(asset.code, asset.type)
    if market_data:
        asset.current_price = market_data["price"]
        asset.market_value = asset.quantity * market_data["price"]
        asset.profit = (market_data["price"] - asset.cost_price) * asset.quantity
        asset.profit_percent = ((market_data["price"] - asset.cost_price) / asset.cost_price) * 100

    # 更新策略分类
    asset.strategy_category = asset_category_mapping_service.get_effective_strategy_category(
        db, current_user.id, asset.code, asset.type, asset.name
    )

    db.commit()
    return Response.success_response(data=asset)


@router.post("", response_model=Response[AssetSchema])
async def create_asset(
    asset: AssetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建资产"""
    # 检查资产代码是否已存在
    existing_asset = db.query(Asset).filter(Asset.code == asset.code).first()
    if existing_asset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="资产代码已存在"
        )

    # 获取初始市场数据并验证代码是否有效
    market_data = mock_data_service.get_market_data(asset.code, asset.type)

    # 验证代码是否存在（市场数据或名称至少有一个存在）
    if not market_data and not mock_data_service.get_asset_name(asset.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的资产代码 '{asset.code}'：未找到对应的金融产品"
        )

    # 如果未提供名称，从市场数据中获取
    asset_name = asset.name
    if not asset_name:
        asset_name = mock_data_service.get_asset_name(asset.code)
        if not asset_name and market_data:
            # 如果mock数据中没有，尝试从market_data中获取
            asset_name = market_data.get("name")
        # 如果还是没有，使用代码作为名称
        if not asset_name:
            asset_name = asset.code

    db_asset = Asset(
        user_id=current_user.id,
        code=asset.code,
        name=asset_name,
        type=asset.type,
        market=asset.market,
        quantity=asset.quantity,
        cost_price=asset.cost_price,
        current_price=market_data["price"] if market_data else asset.cost_price,
        market_value=asset.quantity * (market_data["price"] if market_data else asset.cost_price),
    )

    if market_data:
        db_asset.profit = (market_data["price"] - asset.cost_price) * asset.quantity
        db_asset.profit_percent = ((market_data["price"] - asset.cost_price) / asset.cost_price) * 100

    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    # 自动创建分类映射
    # 使用最终保存的资产名称进行分类
    default_category = asset_category_mapping_service.get_default_strategy_category(asset.type, asset_name)
    from ..models.asset_category_mapping import AssetCategoryMapping
    mapping = AssetCategoryMapping(
        user_id=current_user.id,
        asset_code=asset.code,
        asset_type=asset.type,
        strategy_category=default_category,
        is_user_override=False,
        auto_mapped=True,
    )
    db.add(mapping)
    db.commit()

    return Response.success_response(data=db_asset)


@router.put("/{asset_id}", response_model=Response[AssetSchema])
async def update_asset(
    asset_id: int,
    asset: AssetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新资产"""
    db_asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()

    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )

    for field, value in asset.model_dump(exclude_unset=True).items():
        setattr(db_asset, field, value)

    # 重新计算市值
    if db_asset.current_price:
        db_asset.market_value = db_asset.quantity * db_asset.current_price
        db_asset.profit = (db_asset.current_price - db_asset.cost_price) * db_asset.quantity
        db_asset.profit_percent = ((db_asset.current_price - db_asset.cost_price) / db_asset.cost_price) * 100

    db.commit()
    db.refresh(db_asset)
    return Response.success_response(data=db_asset)


@router.delete("/{asset_id}", response_model=Response[None])
async def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除资产"""
    db_asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()

    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )

    db.delete(db_asset)
    db.commit()
    return Response.success_response(message="删除成功")


@router.put("/{asset_id}/strategy-category", response_model=Response[AssetSchema])
async def update_asset_strategy_category(
    asset_id: int,
    strategy_data: AssetStrategyCategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新资产的策略分类"""
    db_asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()

    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )

    # 更新策略分类
    db_asset.strategy_category = strategy_data.strategy_category
    db.commit()

    return Response.success_response(data=db_asset)


@router.get("/{asset_code}/market-data", response_model=Response[MarketData])
async def get_asset_market_data(
    asset_code: str,
    asset_type: AssetType,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取资产市场数据"""
    market_data = mock_data_service.get_market_data(asset_code, asset_type)

    if not market_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无法获取市场数据"
        )

    return Response.success_response(data=MarketData(**market_data))
