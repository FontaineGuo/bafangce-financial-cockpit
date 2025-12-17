# 持仓相关API路由
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入核心功能模块
from backend.core.portfolio import PortfolioManager
from backend.models.holding import Holding

# 创建路由器
router = APIRouter()

# 实例化PortfolioManager（在实际项目中，这应该通过依赖注入来管理）
portfolio_manager = PortfolioManager()

@router.get("/holdings", response_model=List[Dict[str, Any]])
async def get_all_holdings():
    """获取所有持仓"""
    try:
        holdings = portfolio_manager.get_all_holdings()
        # 将Holding对象转换为字典
        return [holding.to_dict() for holding in holdings]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取持仓失败: {str(e)}")

@router.post("/holdings", response_model=Dict[str, Any])
async def add_holding(holding_data: Dict[str, Any]):
    """添加新持仓"""
    try:
        # 验证必要字段
        required_fields = ["product_code", "product_name", "product_type", "quantity", "purchase_price"]
        for field in required_fields:
            if field not in holding_data:
                raise HTTPException(status_code=400, detail=f"缺少必要字段: {field}")

        success, result = portfolio_manager.add_holding(holding_data)
        if not success:
            raise HTTPException(status_code=400, detail=result.get("message", "添加持仓失败"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加持仓失败: {str(e)}")

@router.put("/holdings/{holding_id}", response_model=Dict[str, Any])
async def update_holding(holding_id: int, update_data: Dict[str, Any]):
    """更新持仓信息"""
    try:
        success, result = portfolio_manager.update_holding(holding_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail=result.get("message", "持仓不存在或更新失败"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新持仓失败: {str(e)}")

@router.delete("/holdings/{holding_id}", response_model=Dict[str, Any])
async def delete_holding(holding_id: int):
    """删除持仓"""
    try:
        success, message = portfolio_manager.delete_holding(holding_id)
        if not success:
            raise HTTPException(status_code=404, detail=message)
        return {"message": message}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除持仓失败: {str(e)}")

@router.get("/asset-allocation", response_model=Dict[str, Any])
async def get_asset_allocation():
    """获取资产配置信息"""
    try:
        allocation = portfolio_manager.calculate_asset_allocation()
        return allocation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算资产配置失败: {str(e)}")

@router.get("/search/{keyword}", response_model=List[Dict[str, Any]])
async def search_holdings(keyword: str):
    """搜索持仓"""
    try:
        results = portfolio_manager.search_holdings(keyword)
        return [holding.to_dict() for holding in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索持仓失败: {str(e)}")
