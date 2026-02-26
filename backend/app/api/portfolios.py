"""
投资组合API路由
"""
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.user import User
from ..models.portfolio import Portfolio, PortfolioAsset
from ..models.asset import Asset
from ..models.enums import StrategyCategory
from ..schemas.portfolio import (
    Portfolio as PortfolioSchema,
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioAssetCreate,
    PortfolioAssetResponse,
    StrategyDistributionItem,
)
from ..schemas.common import Response
from ..utils.auth import get_current_active_user

router = APIRouter(prefix="/portfolios", tags=["投资组合"])


def _calculate_portfolio_stats(db: Session, portfolio_id: int) -> None:
    """计算投资组合的统计数据"""
    # 获取所有组合资产
    portfolio_assets = db.query(PortfolioAsset).filter(
        PortfolioAsset.portfolio_id == portfolio_id
    ).all()

    total_value = 0
    total_cost = 0

    for pa in portfolio_assets:
        asset = db.query(Asset).filter(Asset.id == pa.asset_id).first()
        if asset:
            market_value = asset.market_value or (asset.quantity * asset.cost_price)
            cost = asset.quantity * asset.cost_price

            total_value += market_value
            total_cost += cost

            # 更新权重
            pa.current_weight = (market_value / total_value * 100) if total_value > 0 else 0
            pa.allocation_amount = market_value

    # 更新组合统计
    total_profit = total_value - total_cost
    total_profit_percent = (total_profit / total_cost * 100) if total_cost > 0 else 0

    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if portfolio:
        portfolio.total_value = total_value
        portfolio.total_cost = total_cost
        portfolio.total_profit = total_profit
        portfolio.total_profit_percent = total_profit_percent

    db.commit()


def _portfolio_asset_to_response(pa: PortfolioAsset, asset: Optional[Asset] = None) -> PortfolioAssetResponse:
    """将PortfolioAsset转换为响应格式"""
    asset_data = {}
    if asset:
        asset_data = {
            "asset_code": asset.code,
            "asset_name": asset.name,
            "strategy_category": asset.strategy_category,
            "asset_market_value": asset.market_value,
            "asset_cost": asset.quantity * asset.cost_price if asset.quantity and asset.cost_price else None,
            "asset_profit": asset.profit,
            "asset_profit_percent": asset.profit_percent,
        }

    return PortfolioAssetResponse(
        id=pa.id,
        portfolio_id=pa.portfolio_id,
        asset_id=pa.asset_id,
        target_weight=pa.target_weight,
        current_weight=pa.current_weight,
        allocation_amount=pa.allocation_amount,
        created_at=pa.created_at,
        updated_at=pa.updated_at,
        **asset_data
    )


@router.get("", response_model=Response[List[PortfolioSchema]])
async def get_portfolios(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取投资组合列表"""
    portfolios = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).all()

    # 转换资产为响应格式
    result = []
    for portfolio in portfolios:
        assets_data = []
        for pa in portfolio.assets:
            asset = db.query(Asset).filter(Asset.id == pa.asset_id).first()
            assets_data.append(_portfolio_asset_to_response(pa, asset))

        portfolio_dict = {
            "id": portfolio.id,
            "user_id": portfolio.user_id,
            "name": portfolio.name,
            "description": portfolio.description,
            "total_value": portfolio.total_value,
            "total_cost": portfolio.total_cost,
            "total_profit": portfolio.total_profit,
            "total_profit_percent": portfolio.total_profit_percent,
            "assets": assets_data,
            "created_at": portfolio.created_at,
            "updated_at": portfolio.updated_at,
        }
        result.append(PortfolioSchema(**portfolio_dict))

    return Response.success_response(data=result)


@router.get("/{portfolio_id}", response_model=Response[PortfolioSchema])
async def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取单个投资组合"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投资组合不存在"
        )

    # 转换资产为响应格式
    assets_data = []
    for pa in portfolio.assets:
        asset = db.query(Asset).filter(Asset.id == pa.asset_id).first()
        assets_data.append(_portfolio_asset_to_response(pa, asset))

    portfolio_dict = {
        "id": portfolio.id,
        "user_id": portfolio.user_id,
        "name": portfolio.name,
        "description": portfolio.description,
        "total_value": portfolio.total_value,
        "total_cost": portfolio.total_cost,
        "total_profit": portfolio.total_profit,
        "total_profit_percent": portfolio.total_profit_percent,
        "assets": assets_data,
        "created_at": portfolio.created_at,
        "updated_at": portfolio.updated_at,
    }

    return Response.success_response(data=PortfolioSchema(**portfolio_dict))


@router.post("", response_model=Response[PortfolioSchema])
async def create_portfolio(
    portfolio: PortfolioCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建投资组合"""
    db_portfolio = Portfolio(
        user_id=current_user.id,
        name=portfolio.name,
        description=portfolio.description,
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)

    # 如果有资产，添加关联
    if portfolio.assets:
        for asset_data in portfolio.assets:
            # 验证资产存在且属于当前用户
            db_asset = db.query(Asset).filter(
                Asset.id == asset_data.asset_id,
                Asset.user_id == current_user.id
            ).first()

            if not db_asset:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"资产ID {asset_data.asset_id} 不存在"
                )

            # 检查资产是否已在其他组合中
            existing = db.query(PortfolioAsset).filter(
                PortfolioAsset.asset_id == asset_data.asset_id
            ).first()

            if existing:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"资产 {db_asset.code} 已在其他组合中"
                )

            portfolio_asset = PortfolioAsset(
                portfolio_id=db_portfolio.id,
                asset_id=asset_data.asset_id,
                target_weight=asset_data.target_weight,
            )
            db.add(portfolio_asset)

        # 计算组合统计
        _calculate_portfolio_stats(db, db_portfolio.id)
        db.refresh(db_portfolio)

    # 转换资产为响应格式
    assets_data = []
    for pa in db_portfolio.assets:
        asset = db.query(Asset).filter(Asset.id == pa.asset_id).first()
        assets_data.append(_portfolio_asset_to_response(pa, asset))

    portfolio_dict = {
        "id": db_portfolio.id,
        "user_id": db_portfolio.user_id,
        "name": db_portfolio.name,
        "description": db_portfolio.description,
        "total_value": db_portfolio.total_value,
        "total_cost": db_portfolio.total_cost,
        "total_profit": db_portfolio.total_profit,
        "total_profit_percent": db_portfolio.total_profit_percent,
        "assets": assets_data,
        "created_at": db_portfolio.created_at,
        "updated_at": db_portfolio.updated_at,
    }

    return Response.success_response(data=PortfolioSchema(**portfolio_dict))


@router.put("/{portfolio_id}", response_model=Response[PortfolioSchema])
async def update_portfolio(
    portfolio_id: int,
    portfolio: PortfolioUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新投资组合"""
    db_portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not db_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投资组合不存在"
        )

    for field, value in portfolio.model_dump(exclude_unset=True).items():
        setattr(db_portfolio, field, value)

    db.commit()
    db.refresh(db_portfolio)

    # 转换资产为响应格式
    assets_data = []
    for pa in db_portfolio.assets:
        asset = db.query(Asset).filter(Asset.id == pa.asset_id).first()
        assets_data.append(_portfolio_asset_to_response(pa, asset))

    portfolio_dict = {
        "id": db_portfolio.id,
        "user_id": db_portfolio.user_id,
        "name": db_portfolio.name,
        "description": db_portfolio.description,
        "total_value": db_portfolio.total_value,
        "total_cost": db_portfolio.total_cost,
        "total_profit": db_portfolio.total_profit,
        "total_profit_percent": db_portfolio.total_profit_percent,
        "assets": assets_data,
        "created_at": db_portfolio.created_at,
        "updated_at": db_portfolio.updated_at,
    }

    return Response.success_response(data=PortfolioSchema(**portfolio_dict))


@router.delete("/{portfolio_id}", response_model=Response[None])
async def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除投资组合"""
    db_portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not db_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投资组合不存在"
        )

    db.delete(db_portfolio)
    db.commit()
    return Response.success_response(message="删除成功")


@router.post("/{portfolio_id}/assets", response_model=Response[PortfolioSchema])
async def add_asset_to_portfolio(
    portfolio_id: int,
    asset_data: PortfolioAssetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """向投资组合添加资产"""
    # 验证投资组合
    db_portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not db_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投资组合不存在"
        )

    # 验证资产存在且属于当前用户
    db_asset = db.query(Asset).filter(
        Asset.id == asset_data.asset_id,
        Asset.user_id == current_user.id
    ).first()

    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )

    # 检查资产是否已在其他组合中（唯一约束冲突检测）
    existing = db.query(PortfolioAsset).filter(
        PortfolioAsset.asset_id == asset_data.asset_id
    ).first()

    if existing:
        if existing.portfolio_id == portfolio_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"资产 {db_asset.code} 已在此组合中"
            )
        else:
            # 获取现有组合名称
            existing_portfolio = db.query(Portfolio).filter(
                Portfolio.id == existing.portfolio_id
            ).first()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"资产 {db_asset.code} 已在组合 '{existing_portfolio.name}' 中，请先从该组合移除"
            )

    # 添加关联
    portfolio_asset = PortfolioAsset(
        portfolio_id=portfolio_id,
        asset_id=asset_data.asset_id,
        target_weight=asset_data.target_weight,
    )
    db.add(portfolio_asset)
    db.commit()

    # 计算组合统计
    _calculate_portfolio_stats(db, portfolio_id)
    db.refresh(db_portfolio)

    # 转换资产为响应格式
    assets_data = []
    for pa in db_portfolio.assets:
        asset = db.query(Asset).filter(Asset.id == pa.asset_id).first()
        assets_data.append(_portfolio_asset_to_response(pa, asset))

    portfolio_dict = {
        "id": db_portfolio.id,
        "user_id": db_portfolio.user_id,
        "name": db_portfolio.name,
        "description": db_portfolio.description,
        "total_value": db_portfolio.total_value,
        "total_cost": db_portfolio.total_cost,
        "total_profit": db_portfolio.total_profit,
        "total_profit_percent": db_portfolio.total_profit_percent,
        "assets": assets_data,
        "created_at": db_portfolio.created_at,
        "updated_at": db_portfolio.updated_at,
    }

    return Response.success_response(data=PortfolioSchema(**portfolio_dict))


@router.post("/{portfolio_id}/assets/batch", response_model=Response[Dict])
async def batch_add_assets_to_portfolio(
    portfolio_id: int,
    asset_list: List[PortfolioAssetCreate],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """批量向投资组合添加资产"""
    # 验证投资组合
    db_portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not db_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投资组合不存在"
        )

    conflicts = []
    added_count = 0

    for asset_data in asset_list:
        # 验证资产存在且属于当前用户
        db_asset = db.query(Asset).filter(
            Asset.id == asset_data.asset_id,
            Asset.user_id == current_user.id
        ).first()

        if not db_asset:
            conflicts.append({
                "asset_id": asset_data.asset_id,
                "reason": "资产不存在"
            })
            continue

        # 检查资产是否已在其他组合中
        existing = db.query(PortfolioAsset).filter(
            PortfolioAsset.asset_id == asset_data.asset_id
        ).first()

        if existing:
            if existing.portfolio_id == portfolio_id:
                conflicts.append({
                    "asset_id": asset_data.asset_id,
                    "asset_code": db_asset.code,
                    "reason": "资产已在此组合中"
                })
            else:
                existing_portfolio = db.query(Portfolio).filter(
                    Portfolio.id == existing.portfolio_id
                ).first()
                conflicts.append({
                    "asset_id": asset_data.asset_id,
                    "asset_code": db_asset.code,
                    "reason": f"已在组合 '{existing_portfolio.name}' 中"
                })
            continue

        # 添加关联
        portfolio_asset = PortfolioAsset(
            portfolio_id=portfolio_id,
            asset_id=asset_data.asset_id,
            target_weight=asset_data.target_weight,
        )
        db.add(portfolio_asset)
        added_count += 1

    if added_count > 0:
        db.commit()
        # 计算组合统计
        _calculate_portfolio_stats(db, portfolio_id)
        db.refresh(db_portfolio)

    return Response.success_response(data={
        "added_count": added_count,
        "conflict_count": len(conflicts),
        "conflicts": conflicts
    })


@router.delete("/{portfolio_id}/assets/{asset_id}", response_model=Response[None])
async def remove_asset_from_portfolio(
    portfolio_id: int,
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """从投资组合移除资产"""
    # 验证投资组合
    db_portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not db_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投资组合不存在"
        )

    # 删除关联
    portfolio_asset = db.query(PortfolioAsset).filter(
        PortfolioAsset.portfolio_id == portfolio_id,
        PortfolioAsset.asset_id == asset_id
    ).first()

    if not portfolio_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产关联不存在"
        )

    db.delete(portfolio_asset)
    db.commit()

    # 重新计算组合统计
    _calculate_portfolio_stats(db, portfolio_id)

    return Response.success_response(message="资产移除成功")


@router.get("/{portfolio_id}/strategy-distribution", response_model=Response[List[StrategyDistributionItem]])
async def get_portfolio_strategy_distribution(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取投资组合的策略分类分布"""
    # 验证投资组合
    db_portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not db_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投资组合不存在"
        )

    # 获取所有关联的资产
    portfolio_assets = db.query(PortfolioAsset).filter(
        PortfolioAsset.portfolio_id == portfolio_id
    ).all()

    distribution = {}
    total_value = 0

    for pa in portfolio_assets:
        asset = db.query(Asset).filter(Asset.id == pa.asset_id).first()
        if asset:
            # 获取策略分类
            category = asset.strategy_category or StrategyCategory.OTHER.value
            value = asset.market_value or (asset.quantity * asset.cost_price)

            if category not in distribution:
                distribution[category] = {
                    "count": 0,
                    "total_value": 0.0,
                    "assets": []
                }

            distribution[category]["count"] += 1
            distribution[category]["total_value"] += value
            distribution[category]["assets"].append({
                "id": asset.id,
                "code": asset.code,
                "name": asset.name,
                "value": value
            })
            total_value += value

    # 计算百分比
    result = []
    for category, data in distribution.items():
        result.append({
            "category": category,
            "count": data["count"],
            "total_value": data["total_value"],
            "percentage": (data["total_value"] / total_value * 100) if total_value > 0 else 0
        })

    return Response.success_response(data=result)
