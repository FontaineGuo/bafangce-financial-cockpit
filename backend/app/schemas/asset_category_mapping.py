"""
资产分类映射相关schemas
"""
from datetime import datetime
from pydantic import BaseModel, Field
from ..models.enums import AssetType, StrategyCategory


class AssetCategoryMappingBase(BaseModel):
    """资产分类映射基础信息"""
    asset_code: str = Field(..., min_length=1, max_length=20)
    asset_type: AssetType
    strategy_category: StrategyCategory
    is_user_override: bool = False


class AssetCategoryMappingCreate(AssetCategoryMappingBase):
    """资产分类映射创建"""
    pass


class AssetCategoryMappingUpdate(BaseModel):
    """资产分类映射更新"""
    strategy_category: Optional[StrategyCategory] = None
    is_user_override: Optional[bool] = None


class AssetCategoryMapping(AssetCategoryMappingBase):
    """资产分类映射信息"""
    id: int
    user_id: int
    auto_mapped: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
