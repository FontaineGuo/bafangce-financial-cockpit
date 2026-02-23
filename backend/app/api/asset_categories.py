"""
资产分类映射API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.user import User
from ..models.enums import AssetType, StrategyCategory
from ..schemas.asset_category_mapping import (
    AssetCategoryMapping as MappingSchema,
    AssetCategoryMappingCreate,
    AssetCategoryMappingUpdate,
)
from ..schemas.common import Response
from ..utils.auth import get_current_active_user
from ..services.asset_category_mapping import asset_category_mapping_service

router = APIRouter(prefix="/asset-categories", tags=["资产分类"])


@router.get("", response_model=Response[List[MappingSchema]])
async def get_asset_category_mappings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户所有资产分类映射"""
    mappings = asset_category_mapping_service.get_all_mappings(db, current_user.id)
    return Response.success_response(data=mappings)


@router.get("/{asset_code}", response_model=Response[MappingSchema])
async def get_asset_category_mapping(
    asset_code: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取指定资产的分类映射"""
    mapping = asset_category_mapping_service.get_user_mapping(db, current_user.id, asset_code)

    if not mapping:
        # 如果没有用户自定义映射，返回基于默认规则的信息
        from ..models.asset import Asset
        asset = db.query(Asset).filter(Asset.code == asset_code).first()
        if asset:
            default_category = asset_category_mapping_service.get_default_strategy_category(
                asset.type, asset.name
            )
            # 返回一个临时映射对象（不保存到数据库）
            from ..models.asset_category_mapping import AssetCategoryMapping
            temp_mapping = AssetCategoryMapping(
                id=0,
                user_id=current_user.id,
                asset_code=asset.code,
                asset_type=asset.type,
                strategy_category=default_category,
                is_user_override=False,
                auto_mapped=True,
            )
            return Response.success_response(data=temp_mapping)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="资产不存在"
            )

    return Response.success_response(data=mapping)


@router.post("", response_model=Response[MappingSchema])
async def create_asset_category_mapping(
    mapping: AssetCategoryMappingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建资产分类映射（用户自定义覆盖）"""
    # 检查是否已存在映射
    existing = asset_category_mapping_service.get_user_mapping(db, current_user.id, mapping.asset_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该资产已存在分类映射，请使用更新接口"
        )

    db_mapping = asset_category_mapping_service.create_mapping(db, current_user.id, mapping)
    return Response.success_response(data=db_mapping, message="创建成功")


@router.put("/{mapping_id}", response_model=Response[MappingSchema])
async def update_asset_category_mapping(
    mapping_id: int,
    mapping: AssetCategoryMappingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新资产分类映射"""
    # 验证映射是否属于当前用户
    from ..models.asset_category_mapping import AssetCategoryMapping as MappingModel
    db_mapping = db.query(MappingModel).filter(
        MappingModel.id == mapping_id,
        MappingModel.user_id == current_user.id
    ).first()

    if not db_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="映射不存在"
        )

    updated_mapping = asset_category_mapping_service.update_mapping(db, mapping_id, mapping)
    return Response.success_response(data=updated_mapping, message="更新成功")


@router.delete("/{mapping_id}", response_model=Response[None])
async def delete_asset_category_mapping(
    mapping_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除资产分类映射（恢复默认分类）"""
    # 验证映射是否属于当前用户
    from ..models.asset_category_mapping import AssetCategoryMapping as MappingModel
    db_mapping = db.query(MappingModel).filter(
        MappingModel.id == mapping_id,
        MappingModel.user_id == current_user.id
    ).first()

    if not db_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="映射不存在"
        )

    asset_category_mapping_service.delete_mapping(db, mapping_id)
    return Response.success_response(message="删除成功，已恢复默认分类")


@router.get("/strategy-categories/list", response_model=Response[List[str]])
async def get_strategy_categories(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取所有策略分类列表"""
    categories = [category.value for category in StrategyCategory]
    return Response.success_response(data=categories)


@router.get("/default/{asset_type}", response_model=Response[str])
async def get_default_asset_category(
    asset_type: AssetType,
    asset_name: str = "",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """根据资产类型获取默认策略分类"""
    default_category = asset_category_mapping_service.get_default_strategy_category(
        asset_type, asset_name
    )
    return Response.success_response(data=default_category.value)


@router.get("/portfolio/{portfolio_id}/distribution")
async def get_portfolio_strategy_distribution(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取投资组合的策略分类分布"""
    # 获取组合的资产
    from ..models.portfolio import Portfolio, PortfolioAsset
    from sqlalchemy import func

    # 验证组合是否属于当前用户
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投资组合不存在"
        )

    # 获取组合中的资产
    portfolio_assets = db.query(PortfolioAsset).filter(
        PortfolioAsset.portfolio_id == portfolio_id
    ).all()

    distribution = []

    for pa in portfolio_assets:
        asset = db.query(Asset).filter(Asset.id == pa.asset_id).first()
        if asset:
            category = asset_category_mapping_service.get_effective_strategy_category(
                db, current_user.id, asset.code, asset.type, asset.name
            )

            # 查找或创建分布条目
            dist_item = next((d for d in distribution if d["category"] == category.value), None)
            if dist_item:
                dist_item["count"] += 1
                dist_item["totalValue"] += asset.market_value or 0
            else:
                distribution.append({
                    "category": category.value,
                    "count": 1,
                    "totalValue": asset.market_value or 0,
                })

    # 计算权重
    total_value = sum(d["totalValue"] for d in distribution) or 1
    for d in distribution:
        d["currentWeight"] = round((d["totalValue"] / total_value) * 100, 2)
        d["targetWeight"] = 0  # 这里可以根据业务逻辑设置目标权重

    return Response.success_response(data={"distribution": distribution})
