"""
策略API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.user import User
from ..models.strategy import Strategy
from ..schemas.strategy import (
    Strategy as StrategySchema,
    StrategyCreate,
    StrategyUpdate,
)
from ..schemas.common import Response
from ..utils.auth import get_current_active_user

router = APIRouter(prefix="/strategies", tags=["策略"])


@router.get("", response_model=Response[List[StrategySchema]])
async def get_strategies(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取策略列表"""
    strategies = db.query(Strategy).filter(
        Strategy.user_id == current_user.id
    ).all()
    return Response.success_response(data=strategies)


@router.get("/{strategy_id}", response_model=Response[StrategySchema])
async def get_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取单个策略"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()

    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="策略不存在"
        )

    return Response.success_response(data=strategy)


@router.post("", response_model=Response[StrategySchema])
async def create_strategy(
    strategy: StrategyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建策略"""
    db_strategy = Strategy(
        user_id=current_user.id,
        name=strategy.name,
        type=strategy.type,
        category=strategy.category,
        description=strategy.description,
        enabled=strategy.enabled,
    )
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)

    # 添加策略条件
    if strategy.conditions:
        from ..models.strategy import StrategyCondition
        for i, condition_data in enumerate(strategy.conditions):
            condition = StrategyCondition(
                strategy_id=db_strategy.id,
                field=condition_data.field,
                operator=condition_data.operator,
                value=condition_data.value,
                logical_operator=condition_data.logical_operator,
                order=i,
            )
            db.add(condition)

    db.commit()
    return Response.success_response(data=db_strategy)


@router.put("/{strategy_id}", response_model=Response[StrategySchema])
async def update_strategy(
    strategy_id: int,
    strategy: StrategyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新策略"""
    db_strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()

    if not db_strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="策略不存在"
        )

    for field, value in strategy.model_dump(exclude_unset=True).items():
        setattr(db_strategy, field, value)

    db.commit()
    db.refresh(db_strategy)
    return Response.success_response(data=db_strategy)


@router.delete("/{strategy_id}", response_model=Response[None])
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除策略"""
    db_strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()

    if not db_strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="策略不存在"
        )

    db.delete(db_strategy)
    db.commit()
    return Response.success_response(message="删除成功")
