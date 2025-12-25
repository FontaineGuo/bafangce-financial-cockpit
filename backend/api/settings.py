# 系统设置相关API
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# 导入设置管理功能
from backend.config.settings import load_settings, save_settings

router = APIRouter(prefix="", tags=["settings"])

# 定义设置数据模型
class SettingsModel(BaseModel):
    """设置数据模型"""
    settings: Dict[str, Any]

@router.get("/settings")
def get_settings():
    """
    获取系统设置
    
    Returns:
        dict: 系统设置信息
    """
    try:
        settings = load_settings()
        return {"settings": settings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设置失败: {str(e)}")

@router.put("/settings")
def update_settings(settings_data: SettingsModel):
    """
    更新系统设置
    
    Args:
        settings_data: 设置数据，包含settings字典
    
    Returns:
        dict: 更新结果信息
    """
    try:
        save_settings(settings_data.settings)
        return {"message": "设置更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新设置失败: {str(e)}")
