"""
资产分类映射服务

债券分类说明：
本系统不设置独立的BOND资产类型。所有债券投资均通过基金持有，包括：

1. 开放式债券基金 (OPEN_FUND)
   - 纯债基金：策略分类为 LONG_BOND
   - 信用债基金：策略分类为 CREDIT_BOND
   - 可转债基金：策略分类为 SHORT_BOND
   - 短债/中短债基金：策略分类为 SHORT_BOND

2. 债券型ETF (ETF_FUND)
   - 国债ETF：策略分类为 LONG_BOND
   - 信用债ETF：策略分类为 CREDIT_BOND
   - 可转债ETF：策略分类为 SHORT_BOND

3. 债券型LOF (LOF_FUND)
   - 国债LOF：策略分类为 LONG_BOND
   - 信用债LOF：策略分类为 CREDIT_BOND
   - 可转债LOF：策略分类为 SHORT_BOND

分类逻辑：
- 基金首先通过基金类型（LOF_FUND、ETF_FUND、OPEN_FUND）进行基础分类
- 然后通过基金名称中的关键字进行二次分类，确定债券基金的具体策略分类
- 用户可以通过自定义映射覆盖系统默认分类
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session

from ..models.enums import AssetType, StrategyCategory
from ..models.asset_category_mapping import AssetCategoryMapping as AssetCategoryMappingModel
from ..schemas.asset_category_mapping import AssetCategoryMappingCreate, AssetCategoryMappingUpdate


class AssetCategoryMappingService:
    """
    资产分类映射服务

    注：债券通过基金持有，不设置独立的BOND资产类型。
    债券通过以下基金类型持有，并通过基金名称关键字进行分类：
    - OPEN_FUND: 开放式债券基金（纯债、信用债、可转债等）
    - ETF_FUND: 债券型ETF（国债ETF、信用债ETF等）
    - LOF_FUND: 债券型LOF（场内交易的债券基金）
    """

    # 默认分类映射规则
    DEFAULT_CATEGORY_MAPPING: Dict[AssetType, StrategyCategory] = {
        AssetType.STOCK: StrategyCategory.CN_STOCK_ETF,
        AssetType.LOF_FUND: StrategyCategory.COMMODITY,
        AssetType.ETF_FUND: StrategyCategory.CN_STOCK_ETF,
        AssetType.OPEN_FUND: StrategyCategory.CN_STOCK_ETF,
        AssetType.CASH: StrategyCategory.CASH,
    }

    # LOF基金名称关键字映射
    LOF_KEYWORD_MAPPING: Dict[str, StrategyCategory] = {
        "原油": StrategyCategory.COMMODITY,
        "白银": StrategyCategory.COMMODITY,
        "豆粕": StrategyCategory.COMMODITY,
        "能源": StrategyCategory.COMMODITY,
        "有色": StrategyCategory.COMMODITY,
        "黄金": StrategyCategory.GOLD,
        "日经": StrategyCategory.OVERSEAS_STOCK_ETF,
        "纳指": StrategyCategory.OVERSEAS_STOCK_ETF,
        "恒生": StrategyCategory.CN_STOCK_ETF,
        "沪深": StrategyCategory.CN_STOCK_ETF,
        "中证": StrategyCategory.CN_STOCK_ETF,
        "标普": StrategyCategory.OVERSEAS_STOCK_ETF,
        "美元": StrategyCategory.CASH,
        # 债券类LOF基金
        "债券": StrategyCategory.CREDIT_BOND,
        "国债": StrategyCategory.LONG_BOND,
        "信用": StrategyCategory.CREDIT_BOND,
        "可转债": StrategyCategory.SHORT_BOND,
        "短债": StrategyCategory.SHORT_BOND,
        "纯债": StrategyCategory.LONG_BOND,
    }

    # ETF基金名称关键字映射
    ETF_KEYWORD_MAPPING: Dict[str, StrategyCategory] = {
        "能源": StrategyCategory.COMMODITY,
        "化工": StrategyCategory.COMMODITY,
        "有色": StrategyCategory.COMMODITY,
        "豆粕": StrategyCategory.COMMODITY,
        "黄金": StrategyCategory.GOLD,
        "白银": StrategyCategory.COMMODITY,
        "原油": StrategyCategory.COMMODITY,
        "日经": StrategyCategory.OVERSEAS_STOCK_ETF,
        "纳指": StrategyCategory.OVERSEAS_STOCK_ETF,
        "标普": StrategyCategory.OVERSEAS_STOCK_ETF,
        "沪深": StrategyCategory.CN_STOCK_ETF,
        "中证": StrategyCategory.CN_STOCK_ETF,
        "科创": StrategyCategory.CN_STOCK_ETF,
        "创业": StrategyCategory.CN_STOCK_ETF,
        # 债券类ETF基金
        "国债": StrategyCategory.LONG_BOND,
        "信用": StrategyCategory.CREDIT_BOND,
        "可转债": StrategyCategory.SHORT_BOND,
        "短债": StrategyCategory.SHORT_BOND,
        "纯债": StrategyCategory.LONG_BOND,
        "长久期": StrategyCategory.LONG_BOND,
    }

    # 开放式基金关键字映射
    OPEN_FUND_KEYWORD_MAPPING: Dict[str, StrategyCategory] = {
        "黄金": StrategyCategory.GOLD,
        # 债券类开放式基金
        "债券": StrategyCategory.CREDIT_BOND,
        "国债": StrategyCategory.LONG_BOND,
        "短债": StrategyCategory.SHORT_BOND,
        "可转债": StrategyCategory.SHORT_BOND,
        "中短债": StrategyCategory.SHORT_BOND,
        "纯债": StrategyCategory.LONG_BOND,
        "长久期": StrategyCategory.LONG_BOND,
        "信用": StrategyCategory.CREDIT_BOND,
        "信用债": StrategyCategory.CREDIT_BOND,
        "企业债": StrategyCategory.CREDIT_BOND,
        "短融": StrategyCategory.SHORT_BOND,
        # 其他类型
        "原油": StrategyCategory.COMMODITY,
        "美元": StrategyCategory.CASH,
        "货币": StrategyCategory.CASH,
        "商品": StrategyCategory.COMMODITY,
    }

    @classmethod
    def get_default_strategy_category(
        cls,
        asset_type: AssetType,
        asset_name: str = ""
    ) -> StrategyCategory:
        """获取默认策略分类"""
        # 首先使用资产类型的默认映射
        category = cls.DEFAULT_CATEGORY_MAPPING.get(asset_type, StrategyCategory.OTHER)

        # 对于基金类型，根据基金名称关键字进行二次判断
        if asset_type == AssetType.LOF_FUND and asset_name:
            category = cls._categorize_fund_by_name(asset_name, cls.LOF_KEYWORD_MAPPING, category)
        elif asset_type == AssetType.ETF_FUND and asset_name:
            category = cls._categorize_fund_by_name(asset_name, cls.ETF_KEYWORD_MAPPING, category)
        elif asset_type == AssetType.OPEN_FUND and asset_name:
            category = cls._categorize_fund_by_name(asset_name, cls.OPEN_FUND_KEYWORD_MAPPING, category)

        return category

    @classmethod
    def _categorize_fund_by_name(
        cls,
        fund_name: str,
        keyword_mapping: Dict[str, StrategyCategory],
        default_category: StrategyCategory
    ) -> StrategyCategory:
        """根据基金名称关键字进行分类"""
        for keyword, category in keyword_mapping.items():
            if keyword in fund_name:
                return category
        return default_category

    @classmethod
    def get_user_mapping(
        cls,
        db: Session,
        user_id: int,
        asset_code: str
    ) -> Optional[AssetCategoryMappingModel]:
        """获取用户的资产分类映射"""
        return db.query(AssetCategoryMappingModel).filter(
            AssetCategoryMappingModel.user_id == user_id,
            AssetCategoryMappingModel.asset_code == asset_code
        ).first()

    @classmethod
    def create_mapping(
        cls,
        db: Session,
        user_id: int,
        mapping: AssetCategoryMappingCreate
    ) -> AssetCategoryMappingModel:
        """创建资产分类映射"""
        db_mapping = AssetCategoryMappingModel(
            user_id=user_id,
            asset_code=mapping.asset_code,
            asset_type=mapping.asset_type,
            strategy_category=mapping.strategy_category,
            is_user_override=mapping.is_user_override,
            auto_mapped=not mapping.is_user_override,
        )
        db.add(db_mapping)
        db.commit()
        db.refresh(db_mapping)
        return db_mapping

    @classmethod
    def update_mapping(
        cls,
        db: Session,
        mapping_id: int,
        mapping: AssetCategoryMappingUpdate
    ) -> Optional[AssetCategoryMappingModel]:
        """更新资产分类映射"""
        db_mapping = db.query(AssetCategoryMappingModel).filter(
            AssetCategoryMappingModel.id == mapping_id
        ).first()
        if db_mapping:
            for field, value in mapping.model_dump(exclude_unset=True).items():
                setattr(db_mapping, field, value)
            if mapping.is_user_override:
                db_mapping.auto_mapped = False
            db.commit()
            db.refresh(db_mapping)
        return db_mapping

    @classmethod
    def delete_mapping(cls, db: Session, mapping_id: int) -> bool:
        """删除资产分类映射"""
        db_mapping = db.query(AssetCategoryMappingModel).filter(
            AssetCategoryMappingModel.id == mapping_id
        ).first()
        if db_mapping:
            db.delete(db_mapping)
            db.commit()
            return True
        return False

    @classmethod
    def get_all_mappings(cls, db: Session, user_id: int) -> list[AssetCategoryMappingModel]:
        """获取用户的所有资产分类映射"""
        return db.query(AssetCategoryMappingModel).filter(
            AssetCategoryMappingModel.user_id == user_id
        ).all()

    @classmethod
    def get_effective_strategy_category(
        cls,
        db: Session,
        user_id: int,
        asset_code: str,
        asset_type: AssetType,
        asset_name: str = ""
    ) -> StrategyCategory:
        """获取有效的策略分类（优先使用用户自定义覆盖）"""
        # 首先查找用户自定义映射
        user_mapping = cls.get_user_mapping(db, user_id, asset_code)
        if user_mapping and user_mapping.is_user_override:
            return user_mapping.strategy_category

        # 如果没有用户自定义，返回默认分类
        return cls.get_default_strategy_category(asset_type, asset_name)


asset_category_mapping_service = AssetCategoryMappingService()
