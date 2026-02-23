"""
AI建议API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.user import User
from ..models.ai_suggestion import AISuggestion
from ..schemas.ai_suggestion import AISuggestion as SuggestionSchema
from ..schemas.common import Response
from ..utils.auth import get_current_active_user

router = APIRouter(prefix="/ai", tags=["AI建议"])


@router.get("/suggestions", response_model=Response[List[SuggestionSchema]])
async def get_suggestions(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取AI建议列表"""
    suggestions = db.query(AISuggestion).filter(
        AISuggestion.portfolio_id == portfolio_id
    ).order_by(AISuggestion.created_at.desc()).all()
    return Response.success_response(data=suggestions)


@router.get("/suggestions/{suggestion_id}", response_model=Response[SuggestionSchema])
async def get_suggestion(
    suggestion_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取单个AI建议"""
    suggestion = db.query(AISuggestion).filter(
        AISuggestion.id == suggestion_id
    ).first()

    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="建议不存在"
        )

    return Response.success_response(data=suggestion)


@router.post("/analyze/{portfolio_id}")
async def analyze_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分析投资组合（生成AI建议）"""
    # 这里是mock实现，实际应该调用AI服务
    # 创建一些mock建议
    from datetime import datetime

    mock_suggestions = [
        AISuggestion(
            portfolio_id=portfolio_id,
            type="rebalancing",
            title="建议增加权益类资产配置",
            content="当前组合中债券类资产占比过高，建议适当增加权益类资产配置以提高收益。",
            priority="medium",
            status="pending",
            created_at=datetime.utcnow(),
        ),
        AISuggestion(
            portfolio_id=portfolio_id,
            type="risk",
            title="注意大宗商品价格波动风险",
            content="近期大宗商品价格波动较大，注意相关资产的风险管理。",
            priority="high",
            status="pending",
            created_at=datetime.utcnow(),
        ),
    ]

    for suggestion in mock_suggestions:
        db.add(suggestion)

    db.commit()

    return Response.success_response(
        data={"message": "分析完成", "suggestions_created": len(mock_suggestions)},
        message="分析完成"
    )
