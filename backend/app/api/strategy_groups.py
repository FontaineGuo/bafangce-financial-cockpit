"""
策略组API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.user import User
from ..models.strategy import StrategyGroup, StrategyCategoryAllocation
from ..schemas.strategy import (
    StrategyGroup as StrategyGroupSchema,
    StrategyGroupCreate,
    StrategyGroupUpdate,
)
from ..schemas.common import Response
from ..utils.auth import get_current_active_user

router = APIRouter(prefix="/strategy-groups", tags=["策略组"])


@router.get("", response_model=Response[List[StrategyGroupSchema]])
async def get_strategy_groups(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取策略组列表"""
    strategy_groups = db.query(StrategyGroup).filter(
        StrategyGroup.user_id == current_user.id
    ).all()
    return Response.success_response(data=strategy_groups)


@router.get("/{group_id}", response_model=Response[StrategyGroupSchema])
async def get_strategy_group(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取单个策略组"""
    strategy_group = db.query(StrategyGroup).filter(
        StrategyGroup.id == group_id,
        StrategyGroup.user_id == current_user.id
    ).first()

    if not strategy_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="策略组不存在"
        )

    return Response.success_response(data=strategy_group)


@router.post("", response_model=Response[StrategyGroupSchema])
async def create_strategy_group(
    group: StrategyGroupCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建策略组"""
    db_strategy_group = StrategyGroup(
        user_id=current_user.id,
        name=group.name,
        description=group.description,
    )
    db.add(db_strategy_group)
    db.commit()
    db.refresh(db_strategy_group)

    # 添加策略分类配置
    if group.category_allocations:
        for allocation_data in group.category_allocations:
            allocation = StrategyCategoryAllocation(
                strategy_group_id=db_strategy_group.id,
                category=allocation_data.category,
                percentage=allocation_data.percentage,
                deviation_threshold=allocation_data.deviation_threshold,
            )
            db.add(allocation)

    db.commit()
    db.refresh(db_strategy_group)
    return Response.success_response(data=db_strategy_group)


@router.put("/{group_id}", response_model=Response[StrategyGroupSchema])
async def update_strategy_group(
    group_id: int,
    group: StrategyGroupUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新策略组"""
    db_strategy_group = db.query(StrategyGroup).filter(
        StrategyGroup.id == group_id,
        StrategyGroup.user_id == current_user.id
    ).first()

    if not db_strategy_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="策略组不存在"
        )

    # 更新基本字段
    for field, value in group.model_dump(exclude_unset=True, exclude={'category_allocations'}).items():
        setattr(db_strategy_group, field, value)

    # 更新策略分类配置
    if group.category_allocations is not None:
        # 删除现有的配置
        db.query(StrategyCategoryAllocation).filter(
            StrategyCategoryAllocation.strategy_group_id == group_id
        ).delete()

        # 添加新的配置
        for allocation_data in group.category_allocations:
            allocation = StrategyCategoryAllocation(
                strategy_group_id=group_id,
                category=allocation_data.category,
                percentage=allocation_data.percentage,
                deviation_threshold=allocation_data.deviation_threshold,
            )
            db.add(allocation)

    db.commit()
    db.refresh(db_strategy_group)
    return Response.success_response(data=db_strategy_group)


@router.delete("/{group_id}", response_model=Response[None])
async def delete_strategy_group(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除策略组"""
    db_strategy_group = db.query(StrategyGroup).filter(
        StrategyGroup.id == group_id,
        StrategyGroup.user_id == current_user.id
    ).first()

    if not db_strategy_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="策略组不存在"
        )

    db.delete(db_strategy_group)
    db.commit()
    return Response.success_response(message="删除成功")
