# 八方策金融座舱 - 后端文档

## 1. 后端技术栈

### 核心框架

- **Web框架**: FastAPI
- **语言**: Python 3.10+
- **异步支持**: asyncio

### 数据库与存储

- **主数据库**: PostgreSQL (生产环境) / SQLite (开发环境)
- **ORM**: SQLAlchemy 2.0 (async)
- **缓存**: Redis
- **迁移工具**: Alembic

### 认证与安全

- **认证**: JWT (JSON Web Tokens)
- **密码加密**: bcrypt
- **协议**: OAuth2 (可选)

### 数据获取

- **金融数据**: AkShare
- **任务调度**: APScheduler / Celery

### AI 集成

- **API**: Claude API / OpenAI API
- **框架**: 可集成 LangChain

### 开发工具

- **依赖管理**: uv / pip
- **代码格式化**: black
- **类型检查**: mypy
- **测试**: pytest + pytest-asyncio

## 2. 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── models/              # SQLAlchemy 数据模型
│   │   ├── user.py          # 用户模型
│   │   ├── asset.py         # 资产模型
│   │   ├── portfolio.py     # 投资组合模型
│   │   └── strategy.py      # 策略模型
│   ├── schemas/             # Pydantic 数据模式
│   │   ├── user.py
│   │   ├── asset.py
│   │   └── strategy.py
│   ├── api/                 # API 路由
│   │   ├── auth.py          # 认证相关接口
│   │   ├── assets.py        # 资产管理接口
│   │   ├── portfolio.py     # 投资组合接口
│   │   ├── strategies.py    # 策略管理接口
│   │   └── ai.py            # AI建议接口
│   ├── services/            # 业务逻辑层
│   │   ├── auth_service.py  # 认证服务
│   │   ├── data_service.py  # AkShare数据获取
│   │   ├── strategy_service.py  # 策略监控服务
│   │   ├── alert_service.py # 告警服务
│   │   └── ai_service.py    # AI建议服务
│   ├── tasks/               # 定时任务
│   │   ├── market_monitor.py    # 市场监控任务
│   │   └── strategy_executor.py # 策略执行任务
│   └── db/
│       ├── database.py      # 数据库连接
│       └── session.py       # 数据库会话管理
├── requirements.txt         # Python依赖
├── .env                     # 环境变量配置
└── alembic/                 # 数据库迁移脚本
```

## 3. 数据库设计

### 3.1 用户表 (users)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3.2 资产表 (assets)

```sql
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL,  -- stock, lof_fund, etf_fund, open_fund, cash
                              -- 注：债券通过基金持有（lof_fund, etf_fund, open_fund）
    market VARCHAR(10) NOT NULL,  -- CN, US, EU, HK
    quantity DECIMAL(20, 8) NOT NULL,
    cost_price DECIMAL(15, 4) NOT NULL,
    current_price DECIMAL(15, 4),
    market_value DECIMAL(20, 4),
    profit DECIMAL(20, 4),
    profit_percent DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, code)
);
```

### 3.3 投资组合表 (portfolios)

```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3.4 策略表 (strategies)

```sql
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    conditions JSONB NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3.5 策略执行记录表 (strategy_executions)

```sql
CREATE TABLE strategy_executions (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id) ON DELETE CASCADE,
    executed_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) NOT NULL,  -- success, failed, triggered
    result JSONB,
    error_message TEXT
);
```

### 3.6 市场数据表 (market_data)

```sql
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    asset_code VARCHAR(50) NOT NULL,
    asset_type VARCHAR(20) NOT NULL,
    price DECIMAL(15, 4) NOT NULL,
    price_change DECIMAL(10, 4),
    price_change_pct DECIMAL(8, 4),
    volume BIGINT,
    turnover DECIMAL(20, 4),
    market_date DATE NOT NULL,
    trade_time TIME,
    is_latest BOOLEAN DEFAULT TRUE,
    data_source VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(asset_code, market_date, trade_time)
);

CREATE INDEX idx_market_asset_latest ON market_data(asset_code, is_latest);
CREATE INDEX idx_market_date ON market_data(market_date);
```

### 3.7 缓存元数据表 (cache_metadata)

```sql
CREATE TABLE cache_metadata (
    id SERIAL PRIMARY KEY,
    asset_code VARCHAR(50) NOT NULL,
    last_update_time TIMESTAMP NOT NULL,
    last_market_status VARCHAR(20) NOT NULL,
    update_count INT DEFAULT 0,
    api_call_count INT DEFAULT 0,
    api_error_count INT DEFAULT 0,
    last_error_message TEXT,
    UNIQUE(asset_code)
);
```

## 4. 资产类型定义

基于 AkShare 的实际 API 情况，系统支持以下资产类型：

**重要说明**：本系统中所有债券投资均通过基金持有（开放式基金、ETF基金、LOF基金），因此不设置独立的BOND资产类型。债券类基金根据其持仓特点通过策略分类系统进行归类。

### 4.1 资产类型枚举

```python
from enum import Enum

class AssetType(Enum):
    """资产类型枚举"""
    STOCK = "stock"                    # 股票（包括普通股票、通过股票API查询的ETF）
    LOF_FUND = "lof_fund"            # LOF基金（上市型开放式基金，使用fund_lof_spot_em）
    ETF_FUND = "etf_fund"            # ETF基金（交易型开放式指数基金，使用fund_etf_fund_daily_em）
    OPEN_FUND = "open_fund"          # 开放式基金（场外基金，使用fund_open_fund_daily_em）
                                      # 注：债券通过基金持有，包含在以上基金类型中
    CASH = "cash"                    # 现金
```

### 4.2 各类型资产说明

| 资产类型 | 说明 | AkShare API | 交易时间 | 数据更新频率 |
| --------- | ------ | ------------ | --------- | ------------ |
| STOCK | 普通股票、部分ETF/LOF | `stock_individual_info_em` | 9:30-11:30, 13:00-15:00 | 实时 |
| LOF_FUND | LOF基金（场内交易） | `fund_lof_spot_em` | 9:30-11:30, 13:00-15:00 | 实时 |
| ETF_FUND | ETF基金（场内交易） | `fund_etf_fund_daily_em` | 9:30-11:30, 13:00-15:00 | 实时 |
| OPEN_FUND | 开放式基金（场外） | `fund_open_fund_daily_em` | 不在交易所交易 | 每日更新（通常21:00后） |
| CASH | 现金 | - | - | 实时 |

**债券类基金说明**：

- 债券通过基金持有，包括：
  - 债券型ETF：通过ETF_FUND类型管理，策略分类为LONG_BOND/SHORT_BOND/CREDIT_BOND
  - 债券型LOF：通过LOF_FUND类型管理，策略分类为LONG_BOND/SHORT_BOND/CREDIT_BOND
  - 开放式债券基金：通过OPEN_FUND类型管理，策略分类为LONG_BOND/SHORT_BOND/CREDIT_BOND

### 4.3 资产类型选择策略

根据资产代码前缀和特征自动判断资产类型：

```python
def detect_asset_type(code: str) -> AssetType:
    """
    根据代码特征自动检测资产类型
    """
    # 股票代码规则
    if code.startswith(('60', '00', '30')):
        return AssetType.STOCK

    # LOF基金代码规则（通常以50、16开头）
    if code.startswith(('50', '16')):
        return AssetType.LOF_FUND

    # ETF基金代码规则（通常以51、15开头，且是5或6位）
    if code.startswith(('51', '15')):
        return AssetType.ETF_FUND

    # 开放式基金代码规则（6位数字）
    if len(code) == 6 and code.isdigit():
        return AssetType.OPEN_FUND

    # 默认返回股票类型
    return AssetType.STOCK
```

**注**：本系统不设置独立的债券资产类型。债券通过以下基金类型持有：

- 开放式债券基金（OPEN_FUND）：如纯债基金、信用债基金、可转债基金等
- 债券型ETF（ETF_FUND）：如国债ETF、信用债ETF等
- 债券型LOF（LOF_FUND）：场内交易的债券基金

### 4.4 策略分类定义

在策略监控和风险分析中，资产需要按照投资分类进行分组管理：

```python
from enum import Enum

class StrategyCategory(Enum):
    """策略分类枚举 - 用于策略执行和投资分析"""
    CASH = "cash"                           # 现金
    CN_STOCK_ETF = "cn_stock_etf"           # 中国市场股票与ETF
    OVERSEAS_STOCK_ETF = "overseas_stock_etf"  # 海外市场股票与ETF
    COMMODITY = "commodity"                 # 大宗商品
    CREDIT_BOND = "credit_bond"             # 信用债
    LONG_BOND = "long_bond"                 # 长债
    SHORT_BOND = "short_bond"                # 短债
    GOLD = "gold"                           # 黄金
    OTHER = "other"                          # 其他
```

### 4.5 资产到策略分类的映射

系统提供自动映射机制，同时支持用户手动覆盖：

#### 4.5.1 默认映射规则

```python
DEFAULT_ASSET_TO_STRATEGY_MAPPING = {
    # 现金类
    AssetType.CASH: StrategyCategory.CASH,

    # 中国市场股票与ETF
    AssetType.STOCK: StrategyCategory.CN_STOCK_ETF,
    AssetType.ETF_FUND: StrategyCategory.CN_STOCK_ETF,
    AssetType.LOF_FUND: StrategyCategory.CN_STOCK_ETF,

    # 开放式基金需要根据实际持仓判断
    AssetType.OPEN_FUND: None,  # 需要特殊处理

    # 注：债券通过基金持有，不设置独立的BOND资产类型
}
```

#### 4.5.2 基金细分映射规则

```python
FUND_STRATEGY_MAPPING = {
    # 股票型基金
    "股票型": StrategyCategory.CN_STOCK_ETF,
    "指数型": StrategyCategory.CN_STOCK_ETF,
    "混合型": StrategyCategory.CN_STOCK_ETF,

    # 债券型基金细分
    "债券型-纯债": StrategyCategory.LONG_BOND,
    "债券型-信用债": StrategyCategory.CREDIT_BOND,
    "债券型-可转债": StrategyCategory.SHORT_BOND,
    "债券型-中短债": StrategyCategory.SHORT_BOND,

    # 商品型基金
    "商品型-黄金": StrategyCategory.GOLD,
    "商品型-原油": StrategyCategory.COMMODITY,
    "商品型-白银": StrategyCategory.COMMODITY,

    # QDII基金（海外投资）
    "QDII": StrategyCategory.OVERSEAS_STOCK_ETF,
    "QDII-股票": StrategyCategory.OVERSEAS_STOCK_ETF,
    "QDII-债券": StrategyCategory.OVERSEAS_STOCK_ETF,

    # REITs基金
    "REITs": StrategyCategory.CN_STOCK_ETF,
}

def get_fund_strategy_category(fund_type: str, fund_code: str = "") -> StrategyCategory:
    """
    根据基金类型和代码获取策略分类

    Args:
        fund_type: 基金类型（如"指数型-海外股票"）
        fund_code: 基金代码（用于特殊判断）

    Returns:
        对应的策略分类
    """
    # 精确匹配
    if fund_type in FUND_STRATEGY_MAPPING:
        return FUND_STRATEGY_MAPPING[fund_type]

    # 模糊匹配
    for pattern, category in FUND_STRATEGY_MAPPING.items():
        if pattern in fund_type:
            return category

    # 根据代码前缀判断（如QDII基金）
    if fund_code.startswith(('5', '9')):
        # 5xx系列通常是海外基金
        return StrategyCategory.OVERSEAS_STOCK_ETF

    return StrategyCategory.OTHER
```

#### 4.5.3 债券基金细分映射规则

**注**：本系统不设置独立的债券资产类型。债券通过基金持有，包括债券型ETF、债券型LOF和开放式债券基金。

债券基金通过基金名称关键字映射到对应的策略分类：

```python
BOND_FUND_KEYWORD_MAPPING = {
    # 长债类基金
    "国债": StrategyCategory.LONG_BOND,
    "国开": StrategyCategory.LONG_BOND,
    "纯债": StrategyCategory.LONG_BOND,
    "长久期": StrategyCategory.LONG_BOND,

    # 信用债类基金
    "信用": StrategyCategory.CREDIT_BOND,
    "企业债": StrategyCategory.CREDIT_BOND,
    "信用债": StrategyCategory.CREDIT_BOND,

    # 短债类基金
    "转债": StrategyCategory.SHORT_BOND,
    "可转债": StrategyCategory.SHORT_BOND,
    "短融": StrategyCategory.SHORT_BOND,
    "短债": StrategyCategory.SHORT_BOND,
    "中短债": StrategyCategory.SHORT_BOND,
}

def get_bond_fund_strategy_category(fund_name: str, fund_code: str = "") -> StrategyCategory:
    """
    根据债券基金名称获取策略分类

    Args:
        fund_name: 债券基金名称
        fund_code: 基金代码

    Returns:
        对应的策略分类
    """
    for pattern, category in BOND_FUND_KEYWORD_MAPPING.items():
        if pattern in fund_name:
            return category

    return StrategyCategory.OTHER
```

**债券基金映射说明**：

- 债券ETF（ETF_FUND）：根据ETF名称关键字使用上述映射规则
- 债券LOF（LOF_FUND）：根据LOF名称关键字使用上述映射规则
- 开放式债券基金（OPEN_FUND）：根据基金名称关键字使用上述映射规则
- 所有债券基金统一归类到策略分类：LONG_BOND、CREDIT_BOND、SHORT_BOND

#### 4.5.4 统一的分类映射服务

```python
from typing import Optional
from app.models.asset import Asset
from app.schemas.asset import AssetUpdate

class AssetCategoryMappingService:
    """资产分类映射服务"""

    @staticmethod
    def get_strategy_category(
        asset: Asset,
        user_mapping: Optional[dict] = None
    ) -> StrategyCategory:
        """
        获取资产的策略分类

        Args:
            asset: 资产对象
            user_mapping: 用户自定义映射（如果有）

        Returns:
            策略分类
        """
        # 1. 优先使用用户自定义映射
        if user_mapping and asset.code in user_mapping:
            custom_category = user_mapping[asset.code]
            try:
                return StrategyCategory(custom_category)
            except ValueError:
                pass

        # 2. 现金直接返回
        if asset.type == AssetType.CASH.value:
            return StrategyCategory.CASH

        # 3. 股票、ETF、LOF直接映射到中国市场股票与ETF
        if asset.type in [AssetType.STOCK.value, AssetType.ETF_FUND.value, AssetType.LOF_FUND.value]:
            # 判断是否为海外市场（根据market字段）
            if asset.market in ['US', 'EU', 'HK']:
                return StrategyCategory.OVERSEAS_STOCK_ETF
            return StrategyCategory.CN_STOCK_ETF

        # 4. 开放式基金需要根据基金类型判断
        if asset.type == AssetType.OPEN_FUND.value:
            # 从数据库或缓存中获取基金类型
            fund_type = AssetCategoryMappingService._get_fund_type(asset.code)
            return get_fund_strategy_category(fund_type, asset.code)

        # 5. 默认返回其他
        # 注：债券通过基金持有（ETF_FUND、LOF_FUND、OPEN_FUND），已在上述规则中处理
        return StrategyCategory.OTHER

    @staticmethod
    def _get_fund_type(code: str) -> str:
        """
        获取基金类型
        从市场数据缓存中查询，避免重复API调用
        """
        # 从Redis缓存或数据库查询基金类型信息
        # ...
        return "未知类型"

    @staticmethod
    def batch_update_user_mappings(user_id: int, mappings: dict):
        """
        批量更新用户的自定义映射

        Args:
            user_id: 用户ID
            mappings: 映射字典 {code: strategy_category}
        """
        # 保存到用户配置表或用户资产表
        # ...
        pass
```

### 4.6 数据库表设计调整

需要在 `assets` 表中添加策略分类相关字段：

```sql
-- 添加策略分类字段
ALTER TABLE assets ADD COLUMN strategy_category VARCHAR(30);

-- 添加是否使用自定义映射标志
ALTER TABLE assets ADD COLUMN use_custom_mapping BOOLEAN DEFAULT FALSE;

-- 创建索引
CREATE INDEX idx_assets_strategy_category ON assets(strategy_category);
CREATE INDEX idx_assets_user_category ON assets(user_id, strategy_category);
```

新增用户资产分类配置表：

```sql
CREATE TABLE user_asset_category_mappings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    asset_code VARCHAR(50) NOT NULL,
    strategy_category VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, asset_code)
);
```

### 4.7 API 接口扩展

新增用户自定义分类映射的API：

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.asset import AssetCategoryMapping, AssetStrategyCategoryUpdate
from app.models.asset import Asset
from app.services.asset_category_mapping_service import AssetCategoryMappingService
from app.core.auth import get_current_user
from app.db.session import async_session

router = APIRouter()

@router.get("/category-mappings")
async def get_user_category_mappings(
    current_user = Depends(get_current_user),
    mapping_service: AssetCategoryMappingService = Depends()
):
    """获取用户的所有自定义分类映射"""
    return await mapping_service.get_user_mappings(current_user.id)

@router.post("/category-mappings")
async def update_category_mappings(
    mappings: Dict[str, str],  # {asset_code: strategy_category}
    current_user = Depends(get_current_user),
    mapping_service: AssetCategoryMappingService = Depends()
):
    """
    更新用户的自定义分类映射

    示例:
    {
        "005827": "cn_stock_etf",  # 指定某个基金为中国股票ETF
        "518880": "gold",             # 指定某个ETF为黄金类
        "161726": "overseas_stock_etf"  # 指定某个LOF为海外股票ETF
    }
    """
    await mapping_service.batch_update_user_mappings(current_user.id, mappings)
    return {"message": "Category mappings updated successfully"}

@router.get("/{asset_id}/strategy-category")
async def get_asset_strategy_category(
    asset_id: int,
    current_user = Depends(get_current_user)
):
    """获取单个资产的策略分类"""
    async with async_session() as session:
        asset = await session.execute(
            select(Asset).where(
                Asset.id == asset_id,
                Asset.user_id == current_user.id
            )
        )
        asset = asset.scalar_one_or_none()
        if not asset:
            raise HTTPException(
                status_code=404,
                detail="资产不存在"
            )
        return {"asset_id": asset_id, "strategy_category": asset.strategy_category}

@router.put("/{asset_id}/strategy-category")
async def update_asset_strategy_category(
    asset_id: int,
    strategy_data: AssetStrategyCategoryUpdate,
    current_user = Depends(get_current_user)
):
    """
    手动设置单个资产的策略分类

    此接口直接更新资产表（assets.strategy_category）中的策略分类。
    策略分类是资产的全局属性，不是组合特定的。

    Args:
        asset_id: 资产ID
        strategy_data: 包含 strategy_category 的请求体

    Raises:
        HTTPException: 资产不存在或无权访问时抛出错误

    Returns:
        更新后的资产数据
    """
    async with async_session() as session:
        asset = await session.execute(
            select(Asset).where(
                Asset.id == asset_id,
                Asset.user_id == current_user.id
            )
        )
        asset = asset.scalar_one_or_none()
        if not asset:
            raise HTTPException(
                status_code=404,
                detail="资产不存在"
            )

        asset.strategy_category = strategy_data.strategy_category
        await session.commit()
        await session.refresh(asset)
        return asset
```

#### Pydantic Schema: AssetStrategyCategoryUpdate

```python
from pydantic import BaseModel, Field

class AssetStrategyCategoryUpdate(BaseModel):
    """更新资产策略分类"""
    strategy_category: str = Field(..., description="策略分类（参考 StrategyCategory 枚举）")
```

**策略分类枚举值：**

| 枚举值 | 名称 | 说明 |
| ------ | ------ | ------ |
| CASH | 现金 | 现金及现金等价物 |
| CN_STOCK_ETF | 中国股票/ETF | 中国A股及中国市场的股票、ETF、LOF基金 |
| OVERSEAS_STOCK_ETF | 海外股票/ETF | 海外市场的股票、ETF基金 |
| COMMODITY | 大宗商品 | 大宗商品类资产 |
| CREDIT_BOND | 信用债 | 信用类债券基金 |
| LONG_BOND | 长债 | 长期债券基金 |
| SHORT_BOND | 短债 | 短期债券基金 |
| GOLD | 黄金 | 黄金及贵金属类资产 |
| OTHER | 其他 | 其他类资产 |

### 4.8 策略分类统计接口

```python
@router.get("/portfolio/by-strategy-category")
async def get_portfolio_by_strategy_category(
    current_user = Depends(get_current_user),
    asset_service: AssetService = Depends()
):
    """
    按策略分类统计投资组合

    返回格式:
    {
        "cash": {"total_value": 100000, "count": 2, "percentage": 10.5},
        "cn_stock_etf": {"total_value": 500000, "count": 15, "percentage": 52.6},
        "overseas_stock_etf": {"total_value": 200000, "count": 8, "percentage": 21.1},
        ...
    }
    """
    return await asset_service.get_portfolio_by_strategy_category(current_user.id)
```

在资产管理服务中添加按策略分类统计的方法：

```python
from typing import Dict
from app.enums.asset_type import StrategyCategory
from app.services.asset_category_mapping_service import AssetCategoryMappingService

class AssetService:
    # ... 其他方法 ...

    async def get_portfolio_by_strategy_category(self, user_id: int) -> Dict[str, Dict]:
        """
        按策略分类统计投资组合

        Args:
            user_id: 用户ID

        Returns:
            按策略分类分组统计的字典
        """
        async with async_session() as session:
            # 获取用户所有资产
            assets = await session.execute(
                select(Asset).where(Asset.user_id == user_id)
            )
            assets = assets.scalars().all()

            # 获取用户自定义映射
            mapping_service = AssetCategoryMappingService()
            user_mappings = await mapping_service.get_user_mappings(user_id)

            # 按策略分类分组
            category_stats = {}
            total_value = 0

            for asset in assets:
                # 获取策略分类
                category = mapping_service.get_strategy_category(
                    asset, user_mappings
                )
                category_key = category.value

                # 计算市值（如果当前价格为空，使用成本价）
                market_value = asset.market_value or (asset.quantity * asset.cost_price)

                # 统计
                if category_key not in category_stats:
                    category_stats[category_key] = {
                        "total_value": 0,
                        "count": 0,
                        "assets": []
                    }

                category_stats[category_key]["total_value"] += market_value
                category_stats[category_key]["count"] += 1
                category_stats[category_key]["assets"].append({
                    "code": asset.code,
                    "name": asset.name,
                    "market_value": market_value
                })

                total_value += market_value

            # 计算百分比
            for category_data in category_stats.values():
                if total_value > 0:
                    category_data["percentage"] = (
                        category_data["total_value"] / total_value * 100
                    )
                else:
                    category_data["percentage"] = 0

            return category_stats
```

## 5. 数据缓存与更新策略

### 5.1 设计原则

- **API 限制处理**: AkShare 部分 API 存在使用频率限制，避免频繁调用
- **缓存优先**: 优先使用本地缓存数据，减少外部 API 调用
- **时效性保障**: 确保数据的时效性和准确性
- **智能更新**: 根据市场状态和资产类型选择合适的更新策略
- **批量优化**: 对同类资产使用批量API，减少API调用次数

### 5.2 缓存架构

```
Redis (内存缓存)
  ├── 热点数据 (TTL: 5-15分钟)
  └── 会话数据 (TTL: 30分钟)
       ↓
PostgreSQL (持久化存储)
  ├── market_data (市场数据表)
  ├── price_history (价格历史表)
  └── cache_metadata (缓存元数据表)
```

### 5.3 市场状态判断

```python
from enum import Enum
from datetime import datetime
import pytz

class MarketStatus(Enum):
    # 中国市场
    CN_TRADING = "cn_trading"      # 中国交易时间 (9:30-11:30, 13:00-15:00)
    CN_PRE_MARKET = "cn_pre_market"  # 中国交易前
    CN_AFTER_MARKET = "cn_after_market" # 中国交易后

    # 海外市场
    US_TRADING = "us_trading"      # 美国交易时间
    US_PRE_MARKET = "us_pre_market"
    EU_TRADING = "eu_trading"      # 欧洲交易时间
    HK_TRADING = "hk_trading"      # 香港交易时间

    # 非交易时间
    WEEKEND = "weekend"            # 周末
    HOLIDAY = "holiday"            # 法定节假日

def get_market_status(market: str = "CN") -> MarketStatus:
    """获取当前市场状态"""
    tz = {
        "CN": "Asia/Shanghai",
        "US": "America/New_York",
        "EU": "Europe/London",
        "HK": "Asia/Hong_Kong"
    }.get(market, "Asia/Shanghai")

    now = datetime.now(pytz.timezone(tz))
    weekday = now.weekday()

    # 周末检查
    if weekday >= 5:  # 5=周六, 6=周日
        return MarketStatus.WEEKEND

    # 中国市场交易时间
    if market == "CN":
        time = now.time()
        if datetime.strptime("09:30", "%H:%M").time() <= time <= datetime.strptime("11:30", "%H:%M").time():
            return MarketStatus.CN_TRADING
        elif datetime.strptime("13:00", "%H:%M").time() <= time <= datetime.strptime("15:00", "%H:%M").time():
            return MarketStatus.CN_TRADING
        elif time < datetime.strptime("09:30", "%H:%M").time():
            return MarketStatus.CN_PRE_MARKET
        else:
            return MarketStatus.CN_AFTER_MARKET

    # 其他市场的交易时间判断...

    return MarketStatus.WEEKEND
```

### 5.4 数据更新规则

```python
ASSET_UPDATE_RULES = {
    # 股票类（包含ETF、LOF等场内交易品种）
    "stock_cn": {
        "market": "CN",
        "api": "stock_individual_info_em",
        "trading_hours": ["09:30-11:30", "13:00-15:00"],
        "update_interval_trading": 300,      # 交易时：5分钟
        "update_interval_non_trading": 86400, # 非交易时：24小时
        "fallback_days": 1,                  # 回退天数
    },

    # LOF基金（场内交易型开放式基金）
    "lof_fund_cn": {
        "market": "CN",
        "api": "fund_lof_spot_em",
        "trading_hours": ["09:30-11:30", "13:00-15:00"],
        "update_interval_trading": 300,
        "update_interval_non_trading": 86400,
        "fallback_days": 1,
    },

    # ETF基金（场内交易型指数基金）
    "etf_fund_cn": {
        "market": "CN",
        "api": "fund_etf_fund_daily_em",
        "trading_hours": ["09:30-11:30", "13:00-15:00"],
        "update_interval_trading": 300,
        "update_interval_non_trading": 86400,
        "fallback_days": 1,
    },

    # 开放式基金（场外基金）
    "open_fund_cn": {
        "market": "CN",
        "api": "fund_open_fund_daily_em",
        "update_interval": 3600,             # 基金：1小时（净值更新频率低）
        "update_time": "21:00",              # 通常晚间更新净值
        "fallback_days": 1,
    },

    # 海外市场
    "stock_us": {
        "market": "US",
        "trading_hours": ["21:30-04:00"],     # 中国时区下的美股时间
        "update_interval_trading": 300,
        "update_interval_non_trading": 86400,
        "fallback_days": 1,
    },
    "fund_us": {
        "market": "US",
        "update_interval": 86400,             # 美股基金：24小时
        "fallback_days": 2,                  # 时差可能导致多日延迟
    },
    "fund_eu": {
        "market": "EU",
        "update_interval": 86400,
        "fallback_days": 2,
    },

    # 债券
    "bond_cn": {
        "market": "CN",
        "update_interval": 1800,             # 债券：30分钟
        "fallback_days": 1,
    },
}
```

### 5.5 智能更新逻辑

```python
import json
from datetime import datetime, timedelta
from app.services.redis_service import redis
from app.services.data_service import fetch_from_akshare

async def get_asset_price(asset_code: str, asset_type: str) -> dict:
    """
    获取资产价格（智能缓存策略）

    Args:
        asset_code: 资产代码
        asset_type: 资产类型

    Returns:
        包含价格、时间戳等信息的字典
    """
    rules = ASSET_UPDATE_RULES.get(asset_type)
    if not rules:
        raise ValueError(f"Unknown asset type: {asset_type}")

    # 1. 检查缓存
    cached_data = await redis.get(f"price:{asset_code}")
    if cached_data:
        cache_info = json.loads(cached_data)
        if not is_data_expired(cache_info, rules):
            return cache_info

    # 2. 判断市场状态
    market_status = get_market_status(rules["market"])

    # 3. 确定是否需要更新
    if not should_update_data(cached_data, market_status, rules):
        # 非交易时间或周末，使用缓存数据
        return cache_info

    # 4. 尝试从 AkShare 获取最新数据
    try:
        new_data = await fetch_from_akshare(asset_code, asset_type)
        if new_data:
            # 更新缓存和数据库
            await update_cache_and_db(asset_code, new_data)
            return new_data
    except Exception as e:
        logger.warning(f"AkShare fetch failed: {e}")

    # 5. API 调用失败，使用缓存数据
    if cached_data:
        return cached_data

    # 6. 缓存也没有，从数据库历史数据获取
    return await get_historical_fallback(asset_code, rules["fallback_days"])

def is_data_expired(cache_data: dict, rules: dict) -> bool:
    """检查缓存数据是否过期"""
    if not cache_data:
        return True

    cache_time = datetime.fromisoformat(cache_data.get("updated_at"))
    now = datetime.now()
    elapsed = (now - cache_time).total_seconds()

    # 根据规则判断是否过期
    interval = rules.get("update_interval_trading", 3600)
    return elapsed > interval

def should_update_data(cache_data: dict, market_status: MarketStatus, rules: dict) -> bool:
    """判断是否需要更新数据"""
    if not cache_data:
        return True

    # 非交易时间不更新
    if market_status in [MarketStatus.WEEKEND, MarketStatus.HOLIDAY]:
        return False

    # 根据市场状态确定更新频率
    if market_status.value.endswith("_trading"):
        interval = rules.get("update_interval_trading", 300)
    else:
        interval = rules.get("update_interval_non_trading", 3600)

    cache_time = datetime.fromisoformat(cache_data.get("updated_at"))
    elapsed = (datetime.now() - cache_time).total_seconds()

    return elapsed >= interval
```

### 5.6 海外基金特殊处理

```python
async def handle_overseas_fund(asset_code: str, fund_type: str) -> dict:
    """
    处理海外基金（考虑时差和净值发布延迟）

    Args:
        asset_code: 基金代码
        fund_type: 基金类型（US, EU, HK 等）

    Returns:
        基金净值数据
    """
    # 1. 获取当前中国时间
    china_time = datetime.now(pytz.timezone('Asia/Shanghai'))

    # 2. 根据基金类型确定目标市场时区
    market_timezones = {
        "US": "America/New_York",
        "EU": "Europe/London",
        "HK": "Asia/Hong_Kong",
    }

    target_tz = pytz.timezone(market_timezones.get(fund_type, "Asia/Shanghai"))

    # 3. 判断目标市场是否已开盘
    market_time = datetime.now(target_tz)
    market_hour = market_time.hour

    # 4. 确定应该使用的日期
    if fund_type == "US":
        # 美股通常在中国晚上开盘，所以早晨可能还没有当日净值
        if market_hour < 9:  # 美股还没开盘（对应中国时间）
            target_date = (china_time - timedelta(days=1)).date()
        else:
            target_date = china_time.date()
    elif fund_type == "EU":
        # 欧股开盘较早
        if market_hour < 15:  # 欧股还没收盘
            target_date = (china_time - timedelta(days=1)).date()
        else:
            target_date = china_time.date()
    else:
        target_date = china_time.date()

    # 5. 尝试获取当日净值
    current_data = await get_fund_net_value(asset_code, target_date)

    # 6. 如果当日净值不存在，尝试前一日
    if not current_data:
        target_date = (target_date - timedelta(days=1)).date()
        current_data = await get_fund_net_value(asset_code, target_date)
        if current_data:
            current_data["note"] = "使用前一日净值（当日净值未发布）"

    # 7. 如果还是没有，使用最新可用数据
    if not current_data:
        current_data = await get_latest_fund_data(asset_code)
        if current_data:
            current_data["note"] = "使用历史最新净值"

    return current_data
```

### 5.7 定时任务策略

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 定时任务配置
SCHEDULED_TASKS = {
    "price_update_trading": {
        "trigger": "interval",
        "seconds": 300,  # 5分钟
        "description": "交易时间内价格更新",
        "market_filter": ["CN_TRADING", "US_TRADING", "EU_TRADING", "HK_TRADING"],
    },
    "price_update_non_trading": {
        "trigger": "cron",
        "hour": 22,  # 晚上10点
        "minute": 0,
        "description": "非交易时间价格更新（周末等）",
    },
    "fund_net_value_update": {
        "trigger": "cron",
        "hour": 21,
        "minute": 30,  # 晚上9:30（基金净值发布时间）
        "description": "基金净值更新",
    },
    "overseas_fund_check": {
        "trigger": "cron",
        "hour": 8,
        "minute": 0,   # 早上8点检查海外基金
        "description": "海外基金净值检查",
    },
    "cache_cleanup": {
        "trigger": "cron",
        "hour": 2,
        "minute": 0,   # 凌晨2点清理过期缓存
        "description": "Redis 缓存清理",
    },
}

scheduler = AsyncIOScheduler()

async def price_update_trading():
    """交易时间内价格更新任务"""
    market_status = get_market_status("CN")
    if market_status == MarketStatus.CN_TRADING:
        # 更新所有资产价格
        await update_all_assets_price()

async def fund_net_value_update():
    """基金净值更新任务"""
    # 更新所有基金净值
    await update_all_fund_net_values()

# 添加定时任务
scheduler.add_job(price_update_trading, 'interval', minutes=5)
scheduler.add_job(fund_net_value_update, 'cron', hour=21, minute=30)

scheduler.start()
```

### 5.8 数据一致性保障

```python
# 数据一致性检查机制
class DataConsistencyChecker:
    async def check_data_integrity(self, asset_code: str) -> bool:
        """检查数据完整性"""
        # 1. 检查缓存和数据库一致性
        cache_data = await redis.get(f"price:{asset_code}")
        db_data = await self.get_db_data(asset_code)

        if cache_data and db_data:
            # 比较关键指标
            cache_info = json.loads(cache_data)
            if abs(cache_info["price"] - db_data["price"]) > 0.01:
                logger.warning(f"Data inconsistency for {asset_code}")
                return False

        return True

    async def force_refresh(self, asset_code: str) -> dict:
        """强制刷新数据"""
        # 1. 清除缓存
        await redis.delete(f"price:{asset_code}")

        # 2. 从 AkShare 获取最新数据
        new_data = await fetch_from_akshare(asset_code, asset_type)

        # 3. 更新数据库
        if new_data:
            await self.update_database(asset_code, new_data)

        return new_data
```

### 5.9 性能优化建议

1. **批量查询**: 对于多个资产，使用批量查询减少 API 调用
2. **请求队列**: 使用消息队列（Redis Stream / Celery）管理 API 请求
3. **限流控制**: 实现 Token Bucket 或 Leaky Bucket 算法
4. **异步并发**: 使用 async/await 并发处理多个数据请求
5. **缓存预热**: 在非高峰期预加载热门资产数据
6. **监控告警**: 监控 API 调用频率和错误率，及时调整策略

## 6. API 接口设计

### 6.1 认证接口 (api/auth.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, auth_service: AuthService = Depends()):
    """用户注册"""
    return await auth_service.register(user_data)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends()):
    """用户登录"""
    return await auth_service.authenticate(form_data.username, form_data.password)

@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """用户登出"""
    # 清除 Token（如果使用 Redis 存储）
    await auth_service.logout(current_user.id)
    return {"message": "Successfully logged out"}

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, auth_service: AuthService = Depends()):
    """刷新访问令牌"""
    return await auth_service.refresh_token(refresh_token)
```

### 6.2 资产接口 (api/assets.py)

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse, AssetStrategyCategoryUpdate
from app.models.asset import Asset
from app.services.asset_service import AssetService
from app.core.auth import get_current_user
from app.db.session import async_session

router = APIRouter()

@router.get("", response_model=List[AssetResponse])
async def get_assets(
    skip: int = 0,
    limit: int = 100,
    asset_type: str = None,
    current_user = Depends(get_current_user),
    asset_service: AssetService = Depends()
):
    """获取资产列表"""
    return await asset_service.get_user_assets(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        asset_type=asset_type
    )

@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate,
    current_user = Depends(get_current_user),
    asset_service: AssetService = Depends()
):
    """创建资产"""
    return await asset_service.create_asset(user_id=current_user.id, asset_data=asset_data)

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    current_user = Depends(get_current_user),
    asset_service: AssetService = Depends()
):
    """获取单个资产"""
    return await asset_service.get_asset(asset_id=asset_id, user_id=current_user.id)

@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    current_user = Depends(get_current_user),
    asset_service: AssetService = Depends()
):
    """更新资产"""
    return await asset_service.update_asset(
        asset_id=asset_id,
        user_id=current_user.id,
        asset_data=asset_data
    )

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    current_user = Depends(get_current_user),
    asset_service: AssetService = Depends()
):
    """删除资产"""
    await asset_service.delete_asset(asset_id=asset_id, user_id=current_user.id)

@router.post("/batch-update")
async def batch_update_assets(
    codes: List[str],
    current_user = Depends(get_current_user),
    asset_service: AssetService = Depends()
):
    """批量更新资产价格"""
    return await asset_service.batch_update_prices(user_id=current_user.id, codes=codes)

@router.get("/category-mappings")
async def get_user_category_mappings(
    current_user = Depends(get_current_user),
    mapping_service: AssetCategoryMappingService = Depends()
):
    """获取用户的所有自定义分类映射"""
    return await mapping_service.get_user_mappings(current_user.id)

@router.post("/category-mappings")
async def update_category_mappings(
    mappings: Dict[str, str],  # {asset_code: strategy_category}
    current_user = Depends(get_current_user),
    mapping_service: AssetCategoryMappingService = Depends()
):
    """
    更新用户的自定义分类映射

    示例:
    {
        "005827": "cn_stock_etf",  # 指定某个基金为中国股票ETF
        "518880": "gold",             # 指定某个ETF为黄金类
        "161726": "overseas_stock_etf"  # 指定某个LOF为海外股票ETF
    }
    """
    await mapping_service.batch_update_user_mappings(current_user.id, mappings)
    return {"message": "Category mappings updated successfully"}

@router.get("/{asset_id}/strategy-category")
async def get_asset_strategy_category(
    asset_id: int,
    current_user = Depends(get_current_user)
):
    """获取单个资产的策略分类"""
    async with async_session() as session:
        asset = await session.execute(
            select(Asset).where(
                Asset.id == asset_id,
                Asset.user_id == current_user.id
            )
        )
        asset = asset.scalar_one_or_none()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="资产不存在"
            )
        return {"asset_id": asset_id, "strategy_category": asset.strategy_category}

@router.put("/{asset_id}/strategy-category")
async def update_asset_strategy_category(
    asset_id: int,
    strategy_data: AssetStrategyCategoryUpdate,
    current_user = Depends(get_current_user)
):
    """
    手动设置单个资产的策略分类

    此接口直接更新资产表（assets.strategy_category）中的策略分类。
    策略分类是资产的全局属性，不是组合特定的。

    Args:
        asset_id: 资产ID
        strategy_data: 包含 strategy_category 的请求体

    Raises:
        HTTPException: 资产不存在或无权访问时抛出错误

    Returns:
        更新后的资产数据
    """
    async with async_session() as session:
        asset = await session.execute(
            select(Asset).where(
                Asset.id == asset_id,
                Asset.user_id == current_user.id
            )
        )
        asset = asset.scalar_one_or_none()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="资产不存在"
            )

        asset.strategy_category = strategy_data.strategy_category
        await session.commit()
        await session.refresh(asset)
        return asset

@router.get("/portfolio/by-strategy-category")
async def get_portfolio_by_strategy_category(
    current_user = Depends(get_current_user),
    asset_service: AssetService = Depends()
):
    """
    按策略分类统计投资组合

    返回格式:
    {
        "cash": {"total_value": 100000, "count": 2, "percentage": 10.5},
        "cn_stock_etf": {"total_value": 500000, "count": 15, "percentage": 52.6},
        "overseas_stock_etf": {"total_value": 200000, "count": 8, "percentage": 21.1},
        ...
    }
    """
    return await asset_service.get_portfolio_by_strategy_category(current_user.id)
```

在资产管理服务中添加按策略分类统计的方法：

```python
from typing import Dict
from app.enums.asset_type import StrategyCategory
from app.services.asset_category_mapping_service import AssetCategoryMappingService

class AssetService:
    # ... 其他方法 ...

    async def get_portfolio_by_strategy_category(self, user_id: int) -> Dict[str, Dict]:
        """
        按策略分类统计投资组合

        Args:
            user_id: 用户ID

        Returns:
            按策略分类分组统计的字典
        """
        async with async_session() as session:
            # 获取用户所有资产
            assets = await session.execute(
                select(Asset).where(Asset.user_id == user_id)
            )
            assets = assets.scalars().all()

            # 获取用户自定义映射
            mapping_service = AssetCategoryMappingService()
            user_mappings = await mapping_service.get_user_mappings(user_id)

            # 按策略分类分组
            category_stats = {}
            total_value = 0

            for asset in assets:
                # 获取策略分类
                category = mapping_service.get_strategy_category(
                    asset, user_mappings
                )
                category_key = category.value

                # 计算市值（如果当前价格为空，使用成本价）
                market_value = asset.market_value or (asset.quantity * asset.cost_price)

                # 统计
                if category_key not in category_stats:
                    category_stats[category_key] = {
                        "total_value": 0,
                        "count": 0,
                        "assets": []
                    }

                category_stats[category_key]["total_value"] += market_value
                category_stats[category_key]["count"] += 1
                category_stats[category_key]["assets"].append({
                    "code": asset.code,
                    "name": asset.name,
                    "market_value": market_value
                })

                total_value += market_value

            # 计算百分比
            for category_data in category_stats.values():
                if total_value > 0:
                    category_data["percentage"] = (
                        category_data["total_value"] / total_value * 100
                    )
                else:
                    category_data["percentage"] = 0

            return category_stats
```

### 6.3 投资组合接口 (api/portfolio.py)

投资组合接口管理用户的投资组合，支持创建、更新、删除投资组合，以及将资产添加到投资组合中。

**重要约束**：
- 每项资产只能被一个组合持有
- 用户可以创建多个投资组合
- 资产在添加到新组合前必须从原组合移除

#### 6.3.1 数据模型调整

投资组合与资产的关联通过 `portfolio_assets` 中间表实现：

```sql
-- 投资组合资产关联表
CREATE TABLE portfolio_assets (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    target_weight DECIMAL(5, 2) DEFAULT 0,      -- 目标权重（百分比）
    current_weight DECIMAL(5, 2) DEFAULT 0,     -- 当前权重（百分比，自动计算）
    allocation_amount DECIMAL(20, 4),              -- 分配金额（自动计算）
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(portfolio_id, asset_id)  -- 确保资产只能在一个组合中
);

-- 创建索引
CREATE INDEX idx_portfolio_assets_portfolio ON portfolio_assets(portfolio_id);
CREATE INDEX idx_portfolio_assets_asset ON portfolio_assets(asset_id);
```

#### 6.3.2 Pydantic Schemas

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PortfolioAssetBase(BaseModel):
    """投资组合资产基础模型"""
    asset_id: int = Field(..., description="资产ID")
    target_weight: float = Field(default=0, ge=0, le=100, description="目标权重（0-100）")

class PortfolioAssetCreate(PortfolioAssetBase):
    """创建投资组合资产"""
    pass

class PortfolioAssetResponse(BaseModel):
    """投资组合资产响应模型"""
    id: int
    asset_id: int
    target_weight: float
    current_weight: float
    allocation_amount: float
    asset_code: Optional[str] = Field(None, description="资产代码")
    asset_name: Optional[str] = Field(None, description="资产名称")
    strategy_category: Optional[str] = Field(None, description="策略分类")
    asset_market_value: Optional[float] = Field(None, description="资产市值")
    asset_profit: Optional[float] = Field(None, description="资产盈亏")
    asset_profit_percent: Optional[float] = Field(None, description="资产收益率(%)")
    created_at: datetime
    updated_at: datetime

class PortfolioBase(BaseModel):
    """投资组合基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="投资组合名称")
    description: Optional[str] = Field(None, description="投资组合描述")
    assets: Optional[List[PortfolioAssetCreate]] = Field(default=[], description="初始资产列表")

class PortfolioCreate(PortfolioBase):
    """创建投资组合"""
    pass

class PortfolioUpdate(BaseModel):
    """更新投资组合"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

class PortfolioResponse(PortfolioBase):
    """投资组合响应模型"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    total_value: float = Field(default=0, description="总市值")
    total_cost: float = Field(default=0, description="总成本")
    total_profit: float = Field(default=0, description="总盈亏")
    total_profit_percent: float = Field(default=0, description="收益率（%）")
    assets: List[PortfolioAssetResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

class StrategyDistributionItem(BaseModel):
    """策略分类分布项"""
    category: str = Field(..., description="策略分类")
    count: int = Field(default=0, description="资产数量")
    total_value: float = Field(default=0, description="总市值")
    percentage: float = Field(default=0, description="占比（%）")
```

#### 6.3.3 API 端点

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.portfolio import (
    PortfolioCreate, PortfolioUpdate, PortfolioResponse,
    PortfolioAssetCreate, PortfolioAssetResponse,
    StrategyDistributionItem
)
from app.models.portfolio import Portfolio, PortfolioAsset
from app.models.asset import Asset
from app.core.auth import get_current_user
from app.db.session import async_session

router = APIRouter()

@router.get("", response_model=List[PortfolioResponse])
async def get_portfolios(
    current_user = Depends(get_current_user)
):
    """
    获取用户的所有投资组合
    """
    async with async_session() as session:
        portfolios = await session.execute(
            select(Portfolio).where(Portfolio.user_id == current_user.id)
        )
        portfolios = portfolios.scalars().all()

        # 为每个组合加载资产并计算统计数据
        result = []
        for portfolio in portfolios:
            result.append(await _calculate_portfolio_stats(session, portfolio))
        return result

@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user = Depends(get_current_user)
):
    """
    创建投资组合

    Args:
        portfolio_data: 投资组合数据（可包含初始资产列表）

    Raises:
        HTTPException: 资产已在其他组合中时抛出400错误
    """
    async with async_session() as session:
        # 创建投资组合
        portfolio = Portfolio(
            user_id=current_user.id,
            name=portfolio_data.name,
            description=portfolio_data.description
        )
        session.add(portfolio)
        await session.flush()

        # 如果有初始资产列表，添加资产
        if portfolio_data.assets:
            for asset_data in portfolio_data.assets:
                # 检查资产是否已在其他组合中
                existing = await session.execute(
                    select(PortfolioAsset).where(
                        PortfolioAsset.asset_id == asset_data.asset_id
                    )
                )
                if existing.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"资产 {asset_data.asset_id} 已在其他组合中，请先从原组合移除"
                    )

                # 验证资产所有权
                asset = await session.execute(
                    select(Asset).where(
                        Asset.id == asset_data.asset_id,
                        Asset.user_id == current_user.id
                    )
                )
                asset = asset.scalar_one_or_none()
                if not asset:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"资产 {asset_data.asset_id} 不存在"
                    )

                # 创建关联
                portfolio_asset = PortfolioAsset(
                    portfolio_id=portfolio.id,
                    asset_id=asset_data.asset_id,
                    target_weight=asset_data.target_weight
                )
                session.add(portfolio_asset)

        await session.commit()
        return await _calculate_portfolio_stats(session, portfolio)

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: int,
    current_user = Depends(get_current_user)
):
    """
    获取单个投资组合详情
    """
    async with async_session() as session:
        portfolio = await session.execute(
            select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == current_user.id
            )
        )
        portfolio = portfolio.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="投资组合不存在"
            )
        return await _calculate_portfolio_stats(session, portfolio)

@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: int,
    portfolio_data: PortfolioUpdate,
    current_user = Depends(get_current_user)
):
    """
    更新投资组合信息（不包括资产列表）
    """
    async with async_session() as session:
        portfolio = await session.execute(
            select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == current_user.id
            )
        )
        portfolio = portfolio.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="投资组合不存在"
            )

        if portfolio_data.name is not None:
            portfolio.name = portfolio_data.name
        if portfolio_data.description is not None:
            portfolio.description = portfolio_data.description

        portfolio.updated_at = datetime.utcnow()
        await session.commit()

        return await _calculate_portfolio_stats(session, portfolio)

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: int,
    current_user = Depends(get_current_user)
):
    """
    删除投资组合
    """
    async with async_session() as session:
        portfolio = await session.execute(
            select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == current_user.id
            )
        )
        portfolio = portfolio.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="投资组合不存在"
            )

        await session.delete(portfolio)
        await session.commit()

@router.post("/{portfolio_id}/assets", response_model=PortfolioResponse)
async def add_asset_to_portfolio(
    portfolio_id: int,
    asset_data: PortfolioAssetCreate,
    current_user = Depends(get_current_user)
):
    """
    向投资组合添加资产

    Raises:
        HTTPException: 资产已在其他组合中时抛出400错误
    """
    async with async_session() as session:
        # 验证投资组合
        portfolio = await session.execute(
            select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == current_user.id
            )
        )
        portfolio = portfolio.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="投资组合不存在"
            )

        # 检查资产是否已在其他组合中
        existing = await session.execute(
            select(PortfolioAsset).where(
                PortfolioAsset.asset_id == asset_data.asset_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"资产 {asset_data.asset_id} 已在其他组合中，请先从原组合移除"
            )

        # 验证资产所有权
        asset = await session.execute(
            select(Asset).where(
                Asset.id == asset_data.asset_id,
                Asset.user_id == current_user.id
            )
        )
        asset = asset.scalar_one_or_none()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"资产 {asset_data.asset_id} 不存在"
            )

        # 创建关联
        portfolio_asset = PortfolioAsset(
            portfolio_id=portfolio.id,
            asset_id=asset_data.asset_id,
            target_weight=asset_data.target_weight
        )
        session.add(portfolio_asset)

        await session.commit()
        return await _calculate_portfolio_stats(session, portfolio)

@router.delete("/{portfolio_id}/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_asset_from_portfolio(
    portfolio_id: int,
    asset_id: int,
    current_user = Depends(get_current_user)
):
    """
    从投资组合移除资产
    """
    async with async_session() as session:
        # 验证投资组合
        portfolio = await session.execute(
            select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == current_user.id
            )
        )
        portfolio = portfolio.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="投资组合不存在"
            )

        # 查找关联
        portfolio_asset = await session.execute(
            select(PortfolioAsset).where(
                PortfolioAsset.portfolio_id == portfolio_id,
                PortfolioAsset.asset_id == asset_id
            )
        )
        portfolio_asset = portfolio_asset.scalar_one_or_none()
        if not portfolio_asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="资产不在此投资组合中"
            )

        await session.delete(portfolio_asset)
        await session.commit()

@router.get("/{portfolio_id}/strategy-distribution", response_model=List[StrategyDistributionItem])
async def get_portfolio_strategy_distribution(
    portfolio_id: int,
    current_user = Depends(get_current_user)
):
    """
    获取投资组合的策略分类分布

    Returns:
        按策略分类统计的资产分布，包括每个分类的资产数量、总市值和占比
    """
    async with async_session() as session:
        # 验证投资组合
        portfolio = await session.execute(
            select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == current_user.id
            )
        )
        portfolio = portfolio.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="投资组合不存在"
            )

        # 获取组合中的所有资产
        portfolio_assets = await session.execute(
            select(PortfolioAsset).where(PortfolioAsset.portfolio_id == portfolio_id)
        )
        portfolio_assets = portfolio_assets.scalars().all()

        # 获取资产信息（包括策略分类）
        distribution = {}
        total_value = 0

        for pa in portfolio_assets:
            asset = await session.execute(
                select(Asset).where(Asset.id == pa.asset_id)
            )
            asset = asset.scalar_one()

            # 获取策略分类（使用资产表中的strategy_category字段）
            category = asset.strategy_category or 'other'

            # 计算市值
            market_value = asset.market_value or (asset.quantity * asset.cost_price)

            # 统计
            if category not in distribution:
                distribution[category] = {
                    "count": 0,
                    "total_value": 0
                }

            distribution[category]["count"] += 1
            distribution[category]["total_value"] += market_value
            total_value += market_value

        # 计算百分比
        result = []
        for category, data in distribution.items():
            percentage = (data["total_value"] / total_value * 100) if total_value > 0 else 0
            result.append(StrategyDistributionItem(
                category=category,
                count=data["count"],
                total_value=data["total_value"],
                percentage=round(percentage, 2)
            ))

        return result

@router.post("/{portfolio_id}/assets/batch", response_model=PortfolioResponse)
async def batch_add_assets_to_portfolio(
    portfolio_id: int,
    assets_data: List[PortfolioAssetCreate],
    current_user = Depends(get_current_user)
):
    """
    批量向投资组合添加资产

    Raises:
        HTTPException: 任何资产已在其他组合中时抛出400错误，并返回详细错误信息
    """
    async with async_session() as session:
        # 验证投资组合
        portfolio = await session.execute(
            select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == current_user.id
            )
        )
        portfolio = portfolio.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="投资组合不存在"
            )

        # 检查所有资产是否可用
        conflicts = []
        for asset_data in assets_data:
            existing = await session.execute(
                select(PortfolioAsset).where(
                    PortfolioAsset.asset_id == asset_data.asset_id
                )
            )
            if existing.scalar_one_or_none():
                conflicts.append(asset_data.asset_id)

        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "部分资产已在其他组合中",
                    "conflicts": conflicts
                }
            )

        # 验证所有资产所有权
        for asset_data in assets_data:
            asset = await session.execute(
                select(Asset).where(
                    Asset.id == asset_data.asset_id,
                    Asset.user_id == current_user.id
                )
            )
            if not asset.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"资产 {asset_data.asset_id} 不存在"
                )

        # 批量创建关联
        for asset_data in assets_data:
            portfolio_asset = PortfolioAsset(
                portfolio_id=portfolio.id,
                asset_id=asset_data.asset_id,
                target_weight=asset_data.target_weight
            )
            session.add(portfolio_asset)

        await session.commit()
        return await _calculate_portfolio_stats(session, portfolio)

async def _calculate_portfolio_stats(
    session: AsyncSession,
    portfolio: Portfolio
) -> PortfolioResponse:
    """
    计算投资组合统计数据
    """
    # 获取组合中的所有资产
    portfolio_assets = await session.execute(
        select(PortfolioAsset).where(PortfolioAsset.portfolio_id == portfolio.id)
    )
    portfolio_assets = portfolio_assets.scalars().all()

    # 计算统计
    total_value = 0
    total_cost = 0
    total_market_value = 0  # 用于计算当前权重

    for pa in portfolio_assets:
        asset = await session.execute(
            select(Asset).where(Asset.id == pa.asset_id)
        )
        asset = asset.scalar_one()

        # 累加
        total_cost += asset.quantity * asset.cost_price
        market_value = asset.market_value or (asset.quantity * asset.cost_price)
        total_value += market_value

        # 更新分配金额和当前权重
        pa.allocation_amount = market_value
        total_market_value += market_value

    # 计算当前权重
    for pa in portfolio_assets:
        if total_market_value > 0:
            pa.current_weight = (pa.allocation_amount / total_market_value) * 100
        else:
            pa.current_weight = 0

    total_profit = total_value - total_cost
    total_profit_percent = (total_profit / total_cost * 100) if total_cost > 0 else 0

    portfolio.total_value = total_value
    portfolio.total_cost = total_cost
    portfolio.total_profit = total_profit
    portfolio.total_profit_percent = total_profit_percent

    return PortfolioResponse.model_validate(portfolio)
```

#### 6.3.4 接口说明

| 方法 | 路径 | 描述 | 请求体 | 响应 |
| ----- | ------ | ------ | ------- | ----- |
| GET | /portfolios | 获取所有投资组合 | - | List[PortfolioResponse] |
| POST | /portfolios | 创建投资组合 | PortfolioCreate | PortfolioResponse |
| GET | /portfolios/{id} | 获取单个投资组合 | - | PortfolioResponse |
| PUT | /portfolios/{id} | 更新投资组合 | PortfolioUpdate | PortfolioResponse |
| DELETE | /portfolios/{id} | 删除投资组合 | - | 204 No Content |
| POST | /portfolios/{id}/assets | 向组合添加资产 | PortfolioAssetCreate | PortfolioResponse |
| DELETE | /portfolios/{id}/assets/{asset_id} | 从组合移除资产 | - | 204 No Content |
| GET | /portfolios/{id}/strategy-distribution | 获取策略分布 | - | List[StrategyDistributionItem] |
| POST | /portfolios/{id}/assets/batch | 批量添加资产 | List[PortfolioAssetCreate] | PortfolioResponse |

#### 6.3.5 约束与错误处理

**约束**：
1. 资产唯一性：通过 `UNIQUE(portfolio_id, asset_id)` 约束确保每项资产只能在一个组合中
2. 用户隔离：所有操作都验证 `user_id`，确保用户只能操作自己的数据
3. 级联删除：删除投资组合时，自动删除组合中的所有资产关联

**错误响应示例**：

```json
// 资产已在其他组合中
{
  "detail": "资产 123 已在其他组合中，请先从原组合移除"
}

// 批量添加时的冲突
{
  "detail": {
    "message": "部分资产已在其他组合中",
    "conflicts": [123, 456, 789]
  }
}

// 投资组合不存在
{
  "detail": "投资组合不存在"
}

// 资产不存在或无权访问
{
  "detail": "资产 123 不存在"
}
```

### 6.4 AI 接口 (api/ai.py)

```python
from fastapi import APIRouter, Depends
from app.schemas.ai import PortfolioAnalysisResponse, RiskAssessmentResponse
from app.services.ai_service import AIService
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/analyze-portfolio/{portfolio_id}", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio(
    portfolio_id: int,
    current_user = Depends(get_current_user),
    ai_service: AIService = Depends()
):
    """AI 分析投资组合"""
    return await ai_service.analyze_portfolio(
        user_id=current_user.id,
        portfolio_id=portfolio_id
    )

@router.get("/risk-assessment/{portfolio_id}", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    portfolio_id: int,
    current_user = Depends(get_current_user),
    ai_service: AIService = Depends()
):
    """获取风险评估"""
    return await ai_service.get_risk_assessment(
        user_id=current_user.id,
        portfolio_id=portfolio_id
    )

@router.get("/rebalancing-suggestions/{portfolio_id}")
async def get_rebalancing_suggestions(
    portfolio_id: int,
    current_user = Depends(get_current_user),
    ai_service: AIService = Depends()
):
    """获取调仓建议"""
    return await ai_service.get_rebalancing_suggestions(
        user_id=current_user.id,
        portfolio_id=portfolio_id
    )
```

## 7. 服务层设计

### 7.1 认证服务 (auth_service.py)

```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.user import User
from app.db.session import async_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def register(self, user_data: UserCreate) -> User:
        async with async_session() as session:
            # 检查用户是否存在
            existing_user = await session.execute(
                select(User).where(User.username == user_data.username)
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Username already registered")

            # 创建新用户
            hashed_password = self.get_password_hash(user_data.password)
            user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def authenticate(self, username: str, password: str) -> Token:
        async with async_session() as session:
            user = await session.execute(
                select(User).where(User.username == username)
            )
            user = user.scalar_one_or_none()

            if not user or not self.verify_password(password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password"
                )

            access_token = self.create_access_token(data={"sub": user.username})
            return Token(access_token=access_token, token_type="bearer")
```

### 7.2 数据服务 (data_service.py)

```python
import akshare as ak
from typing import List, Dict, Optional
from datetime import datetime, date
from app.db.session import async_session
from app.models.market_data import MarketData
import asyncio

class DataService:
    async def fetch_stock_info(self, code: str) -> Dict:
        """
        获取股票/ETF/LOF 信息
        使用 stock_individual_info_em API 获取单个股票的详细信息
        """
        try:
            # 使用 akshare 获取股票实时数据
            stock_info = ak.stock_individual_info_em(symbol=code)
            if stock_info.empty:
                return None

            # 转换为字典格式
            data_dict = {}
            for _, row in stock_info.iterrows():
                data_dict[row['item']] = row['value']

            return {
                "code": data_dict.get('股票代码'),
                "name": data_dict.get('股票简称'),
                "price": float(data_dict.get('最新', 0)),
                "total_shares": float(data_dict.get('总股本', 0)),
                "float_shares": float(data_dict.get('流通股', 0)),
                "market_cap": float(data_dict.get('总市值', 0)),
                "updated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching stock info for {code}: {e}")
            return None

    async def fetch_lof_fund_info(self, code: str) -> Dict:
        """
        获取 LOF 基金实时行情
        使用 fund_lof_spot_em API 获取所有 LOF 基金数据后筛选
        """
        try:
            # 获取所有 LOF 基金数据（批量获取，减少API调用）
            lof_data = ak.fund_lof_spot_em()
            fund_info = lof_data[lof_data['代码'] == code]

            if fund_info.empty:
                return None

            row = fund_info.iloc[0]
            return {
                "code": str(row['代码']),
                "name": row['名称'],
                "price": float(row['最新价']),
                "change": float(row['涨跌额']),
                "change_pct": float(row['涨跌幅']),
                "volume": int(row['成交量']),
                "turnover": float(row['成交额']),
                "open_price": float(row['开盘价']),
                "high_price": float(row['最高价']),
                "low_price": float(row['最低价']),
                "prev_close": float(row['昨收']),
                "turnover_rate": float(row['换手率']),
                "float_market_cap": float(row['流通市值']),
                "total_market_cap": float(row['总市值']),
                "updated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching LOF fund info for {code}: {e}")
            return None

    async def fetch_etf_fund_info(self, code: str) -> Dict:
        """
        获取 ETF 基金行情
        使用 fund_etf_fund_daily_em API 获取所有 ETF 基金数据后筛选
        """
        try:
            # 获取所有 ETF 基金数据（批量获取，减少API调用）
            etf_data = ak.fund_etf_fund_daily_em()
            fund_info = etf_data[etf_data['基金代码'] == code]

            if fund_info.empty:
                return None

            row = fund_info.iloc[0]
            # 获取最新的净值列（动态日期列名）
            net_value_cols = [col for col in fund_info.columns if '单位净值' in col]
            if net_value_cols:
                latest_net_value = float(row[net_value_cols[0]])
            else:
                latest_net_value = None

            return {
                "code": str(row['基金代码']),
                "name": row['基金简称'],
                "fund_type": row['类型'],
                "latest_net_value": latest_net_value,
                "market_price": float(row['市价']),
                "discount_rate": row['折价率'],  # 折价率百分比
                "growth_value": float(row['增长值']),
                "growth_rate": row['增长率'],  # 增长率百分比
                "updated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching ETF fund info for {code}: {e}")
            return None

    async def fetch_open_fund_info(self, code: str) -> Dict:
        """
        获取开放式基金净值
        使用 fund_open_fund_daily_em API 获取所有开放式基金数据后筛选
        """
        try:
            # 获取所有开放式基金数据（批量获取，减少API调用）
            fund_data = ak.fund_open_fund_daily_em()
            fund_info = fund_data[fund_data['基金代码'] == code]

            if fund_info.empty:
                return None

            row = fund_info.iloc[0]
            # 获取最新的净值列（动态日期列名）
            net_value_cols = [col for col in fund_data.columns if '单位净值' in col]
            accumulated_value_cols = [col for col in fund_data.columns if '累计净值' in col]

            return {
                "code": str(row['基金代码']),
                "name": row['基金简称'],
                "latest_net_value": float(row[net_value_cols[0]]) if net_value_cols else None,
                "latest_accumulated_value": float(row[accumulated_value_cols[0]]) if accumulated_value_cols else None,
                "daily_growth_value": float(row['日增长值']),
                "daily_growth_rate": row['日增长率'],
                "purchase_status": row['申购状态'],
                "redemption_status": row['赎回状态'],
                "fee": row['手续费'],
                "updated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching open fund info for {code}: {e}")
            return None

    async def fetch_asset_data(self, code: str, asset_type: str) -> Dict:
        """
        根据资产类型获取数据
        """
        if asset_type == "stock":
            return await self.fetch_stock_info(code)
        elif asset_type == "lof_fund":
            return await self.fetch_lof_fund_info(code)
        elif asset_type == "etf_fund":
            return await self.fetch_etf_fund_info(code)
        elif asset_type == "open_fund":
            return await self.fetch_open_fund_info(code)
        else:
            logger.warning(f"Unknown asset type: {asset_type}")
            return None

    async def batch_fetch_prices(self, codes: List[str], asset_types: List[str]) -> Dict[str, Dict]:
        """
        批量获取价格
        对于同一类型的资产，使用批量API减少调用次数
        """
        results = {}
        tasks = []

        for code, asset_type in zip(codes, asset_types):
            tasks.append(self.fetch_asset_data(code, asset_type))

        # 并发执行
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for code, response in zip(codes, responses):
            if not isinstance(response, Exception) and response:
                results[code] = response
            elif isinstance(response, Exception):
                logger.error(f"Failed to fetch data for {code}: {response}")

        return results

    async def update_market_data(self, code: str, data: Dict, asset_type: str):
        """
        更新市场数据到数据库
        """
        async with async_session() as session:
            # 检查是否已存在今日数据
            existing = await session.execute(
                select(MarketData).where(
                    MarketData.asset_code == code,
                    MarketData.market_date == date.today()
                )
            )
            existing = existing.scalar_one_or_none()

            if existing:
                # 更新现有记录
                existing.price = data.get('price') or data.get('market_price') or data.get('latest_net_value')
                existing.price_change = data.get('change') or data.get('daily_growth_value')
                existing.price_change_pct = data.get('change_pct') or data.get('daily_growth_rate')
                existing.volume = data.get('volume', 0)
                existing.turnover = data.get('turnover', 0)
                existing.trade_time = datetime.now().time()
                existing.updated_at = datetime.now()
            else:
                # 创建新记录
                price = data.get('price') or data.get('market_price') or data.get('latest_net_value')
                price_change = data.get('change') or data.get('daily_growth_value')
                price_change_pct = data.get('change_pct') or data.get('daily_growth_rate')

                market_data = MarketData(
                    asset_code=code,
                    asset_type=asset_type,
                    price=price,
                    price_change=price_change,
                    price_change_pct=price_change_pct,
                    volume=data.get('volume', 0),
                    turnover=data.get('turnover', 0),
                    market_date=date.today(),
                    trade_time=datetime.now().time(),
                    is_latest=True,
                    data_source="akshare"
                )
                session.add(market_data)

            await session.commit()
```

### 7.3 资产分类映射服务 (asset_category_mapping_service.py)

```python
from typing import Dict, Optional
from app.models.asset import Asset
from app.schemas.asset import AssetUpdate
from app.db.session import async_session
from sqlalchemy import select
from app.enums.asset_type import AssetType, StrategyCategory

class AssetCategoryMappingService:
    """资产分类映射服务"""

    # 默认映射规则
    DEFAULT_ASSET_TO_STRATEGY_MAPPING = {
        # 现金类
        AssetType.CASH: StrategyCategory.CASH,

        # 中国市场股票与ETF
        AssetType.STOCK: StrategyCategory.CN_STOCK_ETF,
        AssetType.ETF_FUND: StrategyCategory.CN_STOCK_ETF,
        AssetType.LOF_FUND: StrategyCategory.CN_STOCK_ETF,

        # 开放式基金需要根据实际持仓判断
        AssetType.OPEN_FUND: None,  # 需要特殊处理

        # 债券类需要细分
        AssetType.BOND: None,  # 需要特殊处理
    }

    # 基金细分映射规则
    FUND_STRATEGY_MAPPING = {
        # 股票型基金
        "股票型": StrategyCategory.CN_STOCK_ETF,
        "指数型": StrategyCategory.CN_STOCK_ETF,
        "混合型": StrategyCategory.CN_STOCK_ETF,

        # 债券型基金细分
        "债券型-纯债": StrategyCategory.LONG_BOND,
        "债券型-信用债": StrategyCategory.CREDIT_BOND,
        "债券型-可转债": StrategyCategory.SHORT_BOND,
        "债券型-中短债": StrategyCategory.SHORT_BOND,

        # 商品型基金
        "商品型-黄金": StrategyCategory.GOLD,
        "商品型-原油": StrategyCategory.COMMODITY,
        "商品型-白银": StrategyCategory.COMMODITY,

        # QDII基金（海外投资）
        "QDII": StrategyCategory.OVERSEAS_STOCK_ETF,
        "QDII-股票": StrategyCategory.OVERSEAS_STOCK_ETF,
        "QDII-债券": StrategyCategory.OVERSEAS_STOCK_ETF,

        # REITs基金
        "REITs": StrategyCategory.CN_STOCK_ETF,
    }

    # 债券基金细分映射规则（注：债券通过基金持有，不设置独立的BOND资产类型）
    BOND_FUND_KEYWORD_MAPPING = {
        "国债": StrategyCategory.LONG_BOND,
        "国开": StrategyCategory.LONG_BOND,
        "纯债": StrategyCategory.LONG_BOND,
        "长久期": StrategyCategory.LONG_BOND,
        "信用": StrategyCategory.CREDIT_BOND,
        "企业债": StrategyCategory.CREDIT_BOND,
        "信用债": StrategyCategory.CREDIT_BOND,
        "转债": StrategyCategory.SHORT_BOND,
        "可转债": StrategyCategory.SHORT_BOND,
        "短融": StrategyCategory.SHORT_BOND,
        "短债": StrategyCategory.SHORT_BOND,
        "中短债": StrategyCategory.SHORT_BOND,
    }

    async def get_user_mappings(self, user_id: int) -> Dict[str, str]:
        """获取用户的所有自定义映射"""
        async with async_session() as session:
            mappings = await session.execute(
                select(UserAssetCategoryMapping).where(
                    UserAssetCategoryMapping.user_id == user_id
                )
            )
            return {
                m.asset_code: m.strategy_category
                for m in mappings.scalars().all()
            }

    async def get_asset_category(
        self, user_id: int, asset_id: int
    ) -> StrategyCategory:
        """
        获取资产的策略分类

        Args:
            user_id: 用户ID
            asset_id: 资产ID

        Returns:
            策略分类
        """
        async with async_session() as session:
            # 获取资产信息
            asset = await session.execute(
                select(Asset).where(
                    Asset.id == asset_id,
                    Asset.user_id == user_id
                )
            )
            asset = asset.scalar_one_or_none()

            if not asset:
                raise ValueError(f"Asset not found: {asset_id}")

            # 1. 检查是否有用户自定义映射
            user_mapping = await session.execute(
                select(UserAssetCategoryMapping).where(
                    UserAssetCategoryMapping.user_id == user_id,
                    UserAssetCategoryMapping.asset_code == asset.code
                )
            )
            user_mapping = user_mapping.scalar_one_or_none()

            if user_mapping:
                return StrategyCategory(user_mapping.strategy_category)

            # 2. 现金直接返回
            if asset.type == AssetType.CASH.value:
                return StrategyCategory.CASH

            # 3. 股票、ETF、LOF根据市场判断
            if asset.type in [
                AssetType.STOCK.value,
                AssetType.ETF_FUND.value,
                AssetType.LOF_FUND.value
            ]:
                if asset.market in ['US', 'EU', 'HK']:
                    return StrategyCategory.OVERSEAS_STOCK_ETF
                return StrategyCategory.CN_STOCK_ETF

            # 4. 开放式基金需要根据基金类型判断
            if asset.type == AssetType.OPEN_FUND.value:
                fund_type = await self._get_fund_type(asset.code, session)
                return self.get_fund_strategy_category(fund_type, asset.code)

            # 5. 默认返回其他
            # 注：债券通过基金持有（ETF_FUND、LOF_FUND、OPEN_FUND），已在上述规则中处理
            return StrategyCategory.OTHER

    async def set_asset_category(
        self, user_id: int, asset_id: int, category: StrategyCategory
    ):
        """设置单个资产的策略分类"""
        async with async_session() as session:
            # 获取资产信息
            asset = await session.execute(
                select(Asset).where(
                    Asset.id == asset_id,
                    Asset.user_id == user_id
                )
            )
            asset = asset.scalar_one_or_none()

            if not asset:
                raise ValueError(f"Asset not found: {asset_id}")

            # 更新或创建用户映射
            mapping = await session.execute(
                select(UserAssetCategoryMapping).where(
                    UserAssetCategoryMapping.user_id == user_id,
                    UserAssetCategoryMapping.asset_code == asset.code
                )
            )
            mapping = mapping.scalar_one_or_none()

            if mapping:
                mapping.strategy_category = category.value
                mapping.updated_at = datetime.now()
            else:
                mapping = UserAssetCategoryMapping(
                    user_id=user_id,
                    asset_code=asset.code,
                    strategy_category=category.value
                )
                session.add(mapping)

            await session.commit()

    async def batch_update_user_mappings(
        self, user_id: int, mappings: Dict[str, str]
    ):
        """批量更新用户的自定义映射"""
        async with async_session() as session:
            for asset_code, category in mappings.items():
                # 验证分类是否有效
                try:
                    StrategyCategory(category)
                except ValueError:
                    logger.warning(f"Invalid strategy category: {category}")
                    continue

                # 更新或创建映射
                mapping = await session.execute(
                    select(UserAssetCategoryMapping).where(
                        UserAssetCategoryMapping.user_id == user_id,
                        UserAssetCategoryMapping.asset_code == asset_code
                    )
                )
                mapping = mapping.scalar_one_or_none()

                if mapping:
                    mapping.strategy_category = category
                    mapping.updated_at = datetime.now()
                else:
                    mapping = UserAssetCategoryMapping(
                        user_id=user_id,
                        asset_code=asset_code,
                        strategy_category=category
                    )
                    session.add(mapping)

            await session.commit()

    @staticmethod
    def get_fund_strategy_category(fund_type: str, fund_code: str = "") -> StrategyCategory:
        """
        根据基金类型和代码获取策略分类
        """
        # 精确匹配
        if fund_type in AssetCategoryMappingService.FUND_STRATEGY_MAPPING:
            return AssetCategoryMappingService.FUND_STRATEGY_MAPPING[fund_type]

        # 模糊匹配
        for pattern, category in AssetCategoryMappingService.FUND_STRATEGY_MAPPING.items():
            if pattern in fund_type:
                return category

        # 根据代码前缀判断
        if fund_code.startswith(('5', '9')):
            return StrategyCategory.OVERSEAS_STOCK_ETF

        return StrategyCategory.OTHER

    @staticmethod
    async def _get_fund_type(code: str, session) -> str:
        """
        获取基金类型
        从市场数据缓存中查询
        """
        # 从市场数据表查询基金类型
        fund_info = await session.execute(
            select(MarketData).where(
                MarketData.asset_code == code
            ).order_by(
                MarketData.created_at.desc()
            ).limit(1)
        )
        fund_info = fund_info.scalar_one_or_none()

        if fund_info and fund_info.extra_data:
            return fund_info.extra_data.get('fund_type', '未知类型')

        return '未知类型'
```

### 7.4 策略服务 (strategy_service.py)

```python
from typing import List
from app.models.strategy import Strategy, StrategyExecution
from app.db.session import async_session
from sqlalchemy import select

class StrategyService:
    async def check_strategies(self, user_id: int):
        """检查并执行用户的策略"""
        async with async_session() as session:
            # 获取用户的所有启用策略
            strategies = await session.execute(
                select(Strategy).where(
                    Strategy.user_id == user_id,
                    Strategy.enabled == True
                )
            )
            strategies = strategies.scalars().all()

            for strategy in strategies:
                await self._execute_strategy(session, strategy)

            await session.commit()

    async def _execute_strategy(self, session, strategy: Strategy):
        """执行单个策略"""
        try:
            # 解析策略条件
            conditions = strategy.conditions

            # 获取相关资产数据
            # ...

            # 检查条件是否满足
            triggered = self._check_conditions(conditions, asset_data)

            if triggered:
                # 创建执行记录
                execution = StrategyExecution(
                    strategy_id=strategy.id,
                    status="triggered",
                    result={"conditions": conditions}
                )
                session.add(execution)

                # 触发告警
                await self._send_alert(strategy, execution)

        except Exception as e:
            logger.error(f"Error executing strategy {strategy.id}: {e}")

    def _check_conditions(self, conditions: List[dict], asset_data: dict) -> bool:
        """检查策略条件"""
        for condition in conditions:
            field = condition['field']
            operator = condition['operator']
            value = condition['value']

            actual_value = asset_data.get(field)

            if operator == '>':
                if not (actual_value > value):
                    return False
            elif operator == '<':
                if not (actual_value < value):
                    return False
            elif operator == '>=':
                if not (actual_value >= value):
                    return False
            elif operator == '<=':
                if not (actual_value <= value):
                    return False
            elif operator == '==':
                if not (actual_value == value):
                    return False

        return True

    async def _send_alert(self, strategy: Strategy, execution: StrategyExecution):
        """发送告警通知"""
        # 实现邮件、短信或其他通知方式
        # ...
        pass
```

### 7.5 AI 服务 (ai_service.py)

```python
import anthropic
from app.core.config import settings

class AIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def analyze_portfolio(self, user_id: int, portfolio_id: int) -> dict:
        """AI 分析投资组合"""
        # 获取投资组合数据
        portfolio_data = await self._get_portfolio_data(user_id, portfolio_id)

        # 构建提示词
        prompt = self._build_analysis_prompt(portfolio_data)

        # 调用 AI API
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # 解析响应
        analysis = self._parse_analysis_response(response.content[0].text)

        return analysis

    def _build_analysis_prompt(self, portfolio_data: dict) -> str:
        """构建分析提示词"""
        prompt = f"""
        请分析以下投资组合：

        组合名称: {portfolio_data['name']}
        总资产: {portfolio_data['total_value']}
        总成本: {portfolio_data['total_cost']}
        总收益: {portfolio_data['total_profit']}
        收益率: {portfolio_data['total_profit_percent']}%

        资产明细:
        """
        for asset in portfolio_data['assets']:
            prompt += f"""
            - {asset['name']} ({asset['code']}): {asset['quantity']}股
              成本价: {asset['cost_price']}, 当前价: {asset['current_price']}
              盈亏: {asset['profit']} ({asset['profit_percent']}%)
            """

        prompt += """
        请提供以下分析：
        1. 投资组合风险评估
        2. 资产配置建议
        3. 潜在风险提示
        4. 调仓建议（如有必要）
        """

        return prompt

    async def get_risk_assessment(self, user_id: int, portfolio_id: int) -> dict:
        """获取风险评估"""
        portfolio_data = await self._get_portfolio_data(user_id, portfolio_id)

        prompt = f"""
        请评估以下投资组合的风险水平：

        {self._format_portfolio_data(portfolio_data)}

        请提供：
        1. 整体风险等级（低/中/高）
        2. 主要风险因素
        3. 风险分散程度评估
        4. 风险控制建议
        """

        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_risk_assessment(response.content[0].text)
```

## 8. 环境配置

### .env.example

```
# 应用配置
APP_NAME="八方策金融座舱"
APP_VERSION="1.0.0"
DEBUG=True

# 数据库配置
DATABASE_URL="postgresql://user:password@localhost:5432/financial_cockpit"
# 开发环境可使用 SQLite
# DATABASE_URL="sqlite+aiosqlite:///./financial_cockpit.db"

# Redis 配置
REDIS_URL="redis://localhost:6379/0"

# JWT 配置
SECRET_KEY="your-secret-key-here-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI API 配置
ANTHROPIC_API_KEY="your-anthropic-api-key"
# OPENAI_API_KEY="your-openai-api-key"

# CORS 配置
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# 日志配置
LOG_LEVEL="INFO"
LOG_FILE="app.log"
```

## 9. 部署配置

### requirements.txt

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
aiosqlite==0.19.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
hiredis==2.3.2
apscheduler==3.10.4
akshare==1.12.52
anthropic==0.18.1
openai==1.10.0
python-dotenv==1.0.0
alembic==1.13.1
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/financial_cockpit
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=financial_cockpit
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 10. 开发指南

### 10.1 安装依赖

```bash
cd backend
uv pip install -r requirements.txt
```

### 10.2 数据库迁移

```bash
# 初始化迁移
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 10.3 启动开发服务器

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 10.4 运行测试

```bash
pytest tests/
```

### 10.5 代码格式化

```bash
black app/
```

### 10.6 类型检查

```bash
mypy app/
```

## 11. 最佳实践

1. **异步优先**: 使用 async/await 进行所有 I/O 操作
2. **错误处理**: 统一的异常处理机制
3. **日志记录**: 使用结构化日志
4. **类型注解**: 充分使用 Python 类型注解
5. **依赖注入**: 使用 FastAPI 的依赖注入系统
6. **数据库事务**: 确保数据库操作的原子性
7. **API 限流**: 对外部 API 调用实现限流
8. **缓存策略**: 合理使用缓存减少数据库和外部 API 调用
9. **安全考虑**: 输入验证、SQL 注入防护、XSS 防护
10. **监控告警**: 实现应用监控和告警机制
