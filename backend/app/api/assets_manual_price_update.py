"""
手动更新资产当前价格API接口

功能：
- 用户可以手动设置资产的当前价格
- 手动设置的价格会立即保存到数据库
- API刷新时智能判断是否应该覆盖手动设置的价格
- 提供清晰的状态查询接口

核心逻辑：
- 24小时内手动设置的价格优先级更高
- 价格差异大于5%时允许API覆盖
- 否则保持手动设置的价格
- 明确的状态标记和更新时间
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from ..core.database import get_db
from ..models.user import User
from ..models.asset import Asset
from ..schemas.response import Response
from ..dependencies.auth import get_current_active_user

router = APIRouter()


@router.put("/assets/{asset_id}/current-price", response_model=Response[dict])
async def update_asset_current_price(
    asset_id: int,
    price_data: dict,  # 接收包含current_price的字典
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    手动更新资产当前价格

    Args:
        asset_id: 资产ID
        price_data: 包含current_price的字典
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新后的资产信息
    """
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

    # 更新资产字段
    asset.current_price = current_price
    asset.is_manually_set = True
    asset.manual_set_price = current_price
    asset.manual_set_at = datetime.now()
    asset.updated_at = datetime.now()

    # 重新计算相关字段
    if asset.current_price:
        asset.market_value = asset.quantity * asset.current_price
        asset.profit = (asset.current_price - asset.cost_price) * asset.quantity
        asset.profit_percent = ((asset.current_price - asset.cost_price) / asset.cost_price) * 100

    db.commit()

    return {
        "success": True,
        "message": "资产价格更新成功",
        "asset": {
            "id": asset.id,
            "code": asset.code,
            "name": asset.name,
            "current_price": asset.current_price,
            "is_manually_set": asset.is_manually_set,
            "manual_set_at": asset.manual_set_at.isoformat() if asset.manual_set_at else None
        }
    }


@router.get("/assets/{asset_id}/price-status", response_model=Response[dict])
async def get_asset_price_status(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取资产价格状态（手动设置 vs API价格）

    Args:
        asset_id: 资产ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        价格状态信息和建议
    """
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

    # 分析价格状态
    is_manually_set = asset.is_manually_set or False
    is_recently_set = False
    hours_since_manual = 0
    should_update = False
    update_advice = ""

    if asset.manual_set_at:
        hours_since_manual = (datetime.now() - asset.manual_set_at).total_seconds() / 3600

    # 判断是否是最近设置（24小时内）
    is_recently_set = hours_since_manual < 24

    # 判断是否应该更新价格
    if not asset.is_manually_set:
        should_update = True
        update_advice = "建议设置价格"
    elif is_recently_set and hours_since_manual > 24:
        # 手动设置超过24小时，API应该覆盖
        should_update = True
        update_advice = "手动设置较旧，建议刷新"
    else:
        # 手动设置在24小时内，保持手动设置
        should_update = False
        update_advice = "当前设置有效"

    return {
        "success": True,
        "asset": {
            "id": asset.id,
            "code": asset.code,
            "name": asset.name,
            "current_price": asset.current_price,
            "is_manually_set": asset.is_manually_set,
            "manual_set_at": asset.manual_set_at.isoformat() if asset.manual_set_at else None,
            "hours_since_manual": round(hours_since_manual, 2),
            "should_update": should_update,
            "update_advice": update_advice
        }
    }