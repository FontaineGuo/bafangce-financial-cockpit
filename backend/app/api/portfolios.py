"""
投资组合API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.user import User
from ..models.portfolio import Portfolio, PortfolioAsset
from ..schemas.portfolio import (
    Portfolio as PortfolioSchema,
    PortfolioCreate,
    PortfolioUpdate,
)
from ..schemas.common import Response
from ..utils.auth import get_current_active_user

router = APIRouter(prefix="/portfolios", tags=["投资组合"])


@router.get("", response_model=Response[List[PortfolioSchema]])
async def get_portfolios(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取投资组合列表"""
    portfolios = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).all()
    return Response.success_response(data=portfolios)


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

    return Response.success_response(data=portfolio)


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

    return Response.success_response(data=db_portfolio)


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
    return Response.success_response(data=db_portfolio)


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
