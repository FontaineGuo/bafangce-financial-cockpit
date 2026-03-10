"""
资产API路由

说明：
- 创建资产时，name字段为可选
- 如果未提供name，系统会从数据服务获取资产名称
- 数据服务根据配置选择真实API或Mock数据
"""
from datetime import datetime, timedelta
from typing import List, Optional
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
from ..services.data_service import market_data_service
from ..services.asset_category_mapping import asset_category_mapping_service

router = APIRouter(prefix="/assets", tags=["资产"])


@router.get("", response_model=Response[List[AssetSchema]])
async def get_assets(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取资产列表（纯读取操作，不触发任何更新）

    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
    """
    assets = db.query(Asset).filter(Asset.user_id == current_user.id).offset(skip).limit(limit).all()
    return Response.success_response(data=assets)


@router.get("/{asset_id}", response_model=Response[AssetSchema])
async def get_asset(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取单个资产（纯读取操作，不触发任何更新）"""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )

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
    market_data = market_data_service.get_market_data(asset.code, asset.type)

    # 验证代码是否存在（市场数据或名称至少有一个存在）
    if not market_data and not market_data_service.get_asset_name(asset.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的资产代码 '{asset.code}'：未找到对应的金融产品"
        )

    # 如果未提供名称，从数据服务中获取
    asset_name = asset.name
    if not asset_name:
        asset_name = market_data_service.get_asset_name(asset.code)
        if not asset_name and market_data:
            # 如果数据服务中没有，尝试从market_data中获取
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

    # 移除自动策略分类映射逻辑，完全交给用户手动管理
    # 用户可以通过专门的分类映射接口手动设置策略分类

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
    market_data = market_data_service.get_market_data(asset_code, asset_type)

    if not market_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无法获取市场数据"
        )

    return Response.success_response(data=MarketData(**market_data))


@router.post("/{asset_id}/refresh", response_model=Response[AssetSchema])
async def refresh_asset_data(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """强制刷新资产的市场数据"""
    # 查询资产
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )

    # 强制刷新数据
    refresh_success = market_data_service.force_refresh_asset(asset.code, asset.type)

    if not refresh_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刷新市场数据失败"
        )

    # 更新资产的市场数据
    market_data = market_data_service.get_market_data(asset.code, asset.type)
    if market_data:
        api_price = market_data["price"]

        # 检查是否应该覆盖手动设置的价格（强制刷新时不覆盖，除非满足条件）
        should_use_api_price = should_override_manual_price(asset, api_price)

        if should_use_api_price:
            # 使用API价格
            asset.current_price = api_price
            asset.market_value = asset.quantity * api_price
            asset.profit = (api_price - asset.cost_price) * asset.quantity
            asset.profit_percent = ((api_price - asset.cost_price) / asset.cost_price) * 100
        else:
            # 保持手动价格
            asset.current_price = asset.manual_set_price
            asset.market_value = asset.quantity * asset.manual_set_price
            asset.profit = (asset.manual_set_price - asset.cost_price) * asset.quantity
            asset.profit_percent = ((asset.manual_set_price - asset.cost_price) / asset.cost_price) * 100

    # 更新策略分类
    asset.strategy_category = asset_category_mapping_service.get_effective_strategy_category(
        db, current_user.id, asset.code, asset.type, asset.name
    )

    db.commit()
    db.refresh(asset)

    return Response.success_response(data=asset)


@router.post("/batch-refresh", response_model=Response[dict])
async def batch_refresh_assets(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """批量刷新所有资产的市场数据"""
    # 查询用户所有资产
    assets = db.query(Asset).filter(Asset.user_id == current_user.id).all()

    success_count = 0
    failed_count = 0
    failed_assets = []

    # 逐个刷新
    for asset in assets:
        refresh_success = market_data_service.force_refresh_asset(asset.code, asset.type)
        if refresh_success:
            success_count += 1
            # 更新资产的市场数据
            market_data = market_data_service.get_market_data(asset.code, asset.type)
            if market_data:
                api_price = market_data["price"]

                # 检查是否应该覆盖手动设置的价格
                should_use_api_price = should_override_manual_price(asset, api_price)

                if should_use_api_price:
                    # 使用API价格
                    asset.current_price = api_price
                    asset.market_value = asset.quantity * api_price
                    asset.profit = (api_price - asset.cost_price) * asset.quantity
                    asset.profit_percent = ((api_price - asset.cost_price) / asset.cost_price) * 100
                else:
                    # 保持手动价格
                    asset.current_price = asset.manual_set_price
                    asset.market_value = asset.quantity * asset.manual_set_price
                    asset.profit = (asset.manual_set_price - asset.cost_price) * asset.quantity
                    asset.profit_percent = ((asset.manual_set_price - asset.cost_price) / asset.cost_price) * 100

            # 更新策略分类
            asset.strategy_category = asset_category_mapping_service.get_effective_strategy_category(
                db, current_user.id, asset.code, asset.type, asset.name
            )
        else:
            failed_count += 1
            failed_assets.append({
                'code': asset.code,
                'name': asset.name
            })

    db.commit()

    return Response.success_response(data={
        'total_count': len(assets),
        'success_count': success_count,
        'failed_count': failed_count,
        'failed_assets': failed_assets,
        'sync_status': 'completed'  # 数据同步状态
    })


@router.get("/assets/sync-status", response_model=Response[dict])
async def get_assets_sync_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取资产数据同步状态"""
    # 查询用户资产，检查最后更新时间
    assets = db.query(Asset).filter(Asset.user_id == current_user.id).all()

    if not assets:
        return Response.success_response(data={
            'has_assets': False,
            'total_assets': 0,
            'last_update_time': None,
            'sync_status': 'no_data'
        })

    # 找到最近更新的资产
    latest_asset = max(assets, key=lambda a: a.updated_at or datetime.min)
    last_update_time = latest_asset.updated_at if latest_asset.updated_at else None

    return Response.success_response(data={
        'has_assets': True,
        'total_assets': len(assets),
        'last_update_time': last_update_time,
        'sync_status': 'completed' if last_update_time else 'pending',
        'message': '数据已同步' if last_update_time else '等待首次数据更新'
    })


def should_override_manual_price(asset: Asset, api_price: float) -> bool:
    """
    判断是否应该用手动价格覆盖API价格

    逻辑：
    - 如果资产没有手动设置价格，返回True（使用API价格）
    - 如果手动价格设置时间超过24小时，返回True（覆盖）
    - 如果API价格与手动价格差异超过5%，返回True（覆盖）
    - 否则返回False（保持手动价格）

    Args:
        asset: 资产对象
        api_price: API返回的价格

    Returns:
        bool: 是否应该用手动价格覆盖API价格
    """
    # 如果没有手动设置价格，使用API价格
    if not asset.is_manually_set or not asset.manual_set_price or not asset.manual_set_at:
        return True

    # 如果手动价格设置时间超过24小时，使用API价格
    if datetime.utcnow() - asset.manual_set_at > timedelta(hours=24):
        return True

    # 如果价格差异超过5%，使用API价格
    price_diff_percent = abs(api_price - asset.manual_set_price) / asset.manual_set_price * 100
    if price_diff_percent > 5:
        return True

    # 保持手动价格
    return False


@router.put("/{asset_id}/current-price", response_model=Response[AssetSchema])
async def set_asset_current_price(
    asset_id: int,
    price_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """手动设置资产当前价格"""
    # 查询资产
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )

    # 验证价格数据
    current_price = price_data.get("current_price")
    if current_price is None or current_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前价格必须大于0"
        )

    # 更新手动价格字段
    asset.is_manually_set = True
    asset.manual_set_price = current_price
    asset.manual_set_at = datetime.utcnow()

    # 使用手动价格更新当前价格和相关字段
    asset.current_price = current_price
    asset.market_value = asset.quantity * current_price
    asset.profit = (current_price - asset.cost_price) * asset.quantity
    asset.profit_percent = ((current_price - asset.cost_price) / asset.cost_price) * 100

    db.commit()
    db.refresh(asset)

    # 更新策略分类
    asset.strategy_category = asset_category_mapping_service.get_effective_strategy_category(
        db, current_user.id, asset.code, asset.type, asset.name
    )

    db.commit()
    db.refresh(asset)

    return Response.success_response(data=asset)
