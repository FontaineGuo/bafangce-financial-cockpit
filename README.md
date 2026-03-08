# 八方策金融座舱

基于 FastAPI + Vue 3 + TypeScript 的个人金融资产管理平台

## 📋 项目概述

一个用于个人投资管理的Web应用，支持多种资产类型（股票、基金、债券等）的管理和策略分析。

## 🎯 功能特性

- ✅ 用户认证系统（JWT）
- ✅ 资产管理（股票、基金、债券等）
- ✅ 资产分类映射（自动分类 + 用户自定义覆盖）
- ✅ 投资组合管理
- ✅ 策略管理框架
- ✅ Mock数据服务（替代akshare）
- 🚧 AI建议分析（待实现）

## 📁 项目结构

### 1. 项目概述

一个用于个人投资管理的Python工具，通过akshare获取金融产品实时数据，并计算持仓成本与现值的Web应用。支持多用户、全天候策略监控、AI持仓建议等功能。

### 2. 系统架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Vue 3     │────▶│   FastAPI   │────▶│  PostgreSQL │
│   前端       │     │   后端       │     │   数据库     │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ├─────────────────────────┐
                           ▼                         ▼
                    ┌─────────────┐         ┌─────────────┐
                    │  AkShare    │         │   AI API    │
                    │  数据接口    │         │  (可选)      │
                    └─────────────┘         └─────────────┘
```

### 3. 技术栈选择

#### 3.1 后端技术栈
- **核心语言**: Python 3.10+
- **Web框架**: FastAPI
- **数据库**: PostgreSQL (生产环境) / SQLite (开发环境)
- **ORM**: SQLAlchemy
- **认证**: JWT + OAuth2
- **数据获取**: AkShare
- **任务调度**: APScheduler / Celery
- **AI集成**: Claude API / OpenAI API
- **依赖管理**: uv

#### 3.2 前端技术栈
- **核心框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件**: Element Plus / Ant Design Vue
- **路由**: Vue Router
- **状态管理**: Pinia
- **HTTP客户端**: Axios

### 4. 项目结构

#### 4.1 后端目录结构
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

#### 4.2 前端目录结构
```
frontend/
├── src/
│   ├── main.ts              # 应用入口
│   ├── App.vue              # 根组件
│   ├── router/
│   │   └── index.ts         # 路由配置
│   ├── store/
│   │   ├── user.ts          # 用户状态
│   │   ├── assets.ts        # 资产状态
│   │   └── portfolio.ts     # 投资组合状态
│   ├── views/
│   │   ├── Login.vue        # 登录页
│   │   ├── Dashboard.vue    # 仪表盘
│   │   ├── Assets.vue       # 资产管理页
│   │   ├── Portfolio.vue    # 投资组合页
│   │   ├── Strategies.vue   # 策略管理页
│   │   └── AIAdvisor.vue    # AI建议页
│   ├── components/
│   │   ├── AssetCard.vue    # 资产卡片组件
│   │   ├── StrategyPanel.vue    # 策略面板组件
│   │   └── ChartContainer.vue   # 图表容器组件
│   ├── api/
│   │   ├── index.ts         # API客户端配置
│   │   ├── auth.ts          # 认证API
│   │   ├── assets.ts        # 资产API
│   │   └── ai.ts            # AI API
│   └── types/
│       └── index.ts         # TypeScript类型定义
├── package.json             # 前端依赖
├── vite.config.ts           # Vite配置
└── tsconfig.json            # TypeScript配置
```

### 5. 核心功能模块

#### 5.1 用户认证与授权
- JWT Token 认证机制
- 用户注册、登录、密码找回
- 数据隔离：每个用户只能访问自己的数据
- 可选：管理员角色和权限管理

#### 5.2 资产管理
- 支持多种资产类型：股票、基金、债券、现金
- AkShare 实时数据同步
- 自动更新持仓市值
- 历史数据存储和查询
- 成本与收益计算

#### 5.3 策略监控
- 全天候策略配置（阈值、条件）
- 定时任务执行监控
- 实时告警通知（邮件、短信、App通知）
- 策略历史执行记录
- 策略回测功能

#### 5.4 AI 持仓建议
- API集成：调用Claude / OpenAI API
- 功能模块：
  - 投资组合分析
  - 风险评估
  - 调仓建议
  - 市场趋势分析
- 上下文管理：用户历史数据 + 实时市场数据
- 建议历史记录和评价

#### 5.5 数据可视化
- 资产配置饼图
- 收益曲线图
- 风险指标仪表盘
- 策略执行状态监控
- 实时市场行情展示

### 6. 数据缓存与更新策略

#### 6.1 设计原则
- **API 限制处理**: AkShare 部分 API 存在使用频率限制，避免频繁调用
- **缓存优先**: 优先使用本地缓存数据，减少外部 API 调用
- **时效性保障**: 确保数据的时效性和准确性
- **智能更新**: 根据市场状态和资产类型选择合适的更新策略

#### 6.2 缓存架构
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

#### 6.3 市场状态判断
```python
# 市场状态分类
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
```

#### 6.4 数据更新策略

##### 6.4.1 按资产类型分类
```python
ASSET_UPDATE_RULES = {
    "stock_cn": {
        "market": "CN",
        "trading_hours": ["09:30-11:30", "13:00-15:00"],
        "update_interval_trading": 300,      # 交易时：5分钟
        "update_interval_non_trading": 86400, # 非交易时：24小时
        "fallback_days": 1,                  # 回退天数
    },
    "fund_cn": {
        "market": "CN",
        "update_interval": 3600,             # 基金：1小时（净值更新频率低）
        "update_time": "21:00",              # 通常晚间更新净值
        "fallback_days": 1,
    },
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
    "bond": {
        "market": "CN",
        "update_interval": 1800,             # 债券：30分钟
        "fallback_days": 1,
    },
}
```

##### 6.4.2 智能更新逻辑
```python
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
    if not should_update_data(cache_info, market_status, rules):
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
        return cache_info

    # 6. 缓存也没有，从数据库历史数据获取
    return await get_historical_fallback(asset_code, rules["fallback_days"])
```

#### 6.5 数据库表设计优化

##### 6.5.1 market_data 表
```sql
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    asset_code VARCHAR(50) NOT NULL,      -- 资产代码
    asset_type VARCHAR(20) NOT NULL,      -- 资产类型
    price DECIMAL(15, 4) NOT NULL,       -- 当前价格
    price_change DECIMAL(10, 4),          -- 价格变动
    price_change_pct DECIMAL(8, 4),       -- 价格变动百分比
    volume BIGINT,                        -- 成交量
    turnover DECIMAL(20, 4),              -- 成交额
    market_date DATE NOT NULL,            -- 市场日期
    trade_time TIME,                      -- 交易时间（用于实时数据）
    is_latest BOOLEAN DEFAULT TRUE,       -- 是否最新数据
    data_source VARCHAR(20),              -- 数据来源
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(asset_code, market_date, trade_time)
);

CREATE INDEX idx_market_asset_latest ON market_data(asset_code, is_latest);
CREATE INDEX idx_market_date ON market_data(market_date);
```

##### 6.5.2 cache_metadata 表
```sql
CREATE TABLE cache_metadata (
    id SERIAL PRIMARY KEY,
    asset_code VARCHAR(50) NOT NULL,
    last_update_time TIMESTAMP NOT NULL,
    last_market_status VARCHAR(20) NOT NULL,  -- 上次更新时的市场状态
    update_count INT DEFAULT 0,                -- 更新次数
    api_call_count INT DEFAULT 0,              -- API 调用次数
    api_error_count INT DEFAULT 0,             -- API 错误次数
    last_error_message TEXT,
    UNIQUE(asset_code)
);
```

#### 6.6 定时任务策略

```python
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
```

#### 6.7 海外基金特殊处理

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

#### 6.8 数据一致性保障

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

#### 6.9 性能优化建议

1. **批量查询**: 对于多个资产，使用批量查询减少 API 调用
2. **请求队列**: 使用消息队列（Redis Stream / Celery）管理 API 请求
3. **限流控制**: 实现 Token Bucket 或 Leaky Bucket 算法
4. **异步并发**: 使用 async/await 并发处理多个数据请求
5. **缓存预热**: 在非高峰期预加载热门资产数据
6. **监控告警**: 监控 API 调用频率和错误率，及时调整策略

### 7. 数据库设计

#### 核心表结构
- `users`: 用户信息表
- `assets`: 资产明细表
- `portfolios`: 投资组合表
- `strategies`: 策略配置表
- `strategy_executions`: 策略执行记录表
- `alerts`: 告警记录表
- `ai_suggestions`: AI建议记录表
- `market_data`: 市场数据缓存表

### 7. 部署方案

#### 7.1 传统部署
```
Nginx
  ├── /api  → FastAPI (Uvicorn + Gunicorn)
  └── /     → Vue (静态文件)
       ↓
  PostgreSQL
  Redis (可选，用于缓存和队列)
```

#### 7.2 Docker 容器化部署 (推荐)
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
    depends_on:
      - db
      - redis
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=...
  redis:
    image: redis:7
```

### 8. 开发计划

#### Phase 1: 基础框架搭建
- [ ] FastAPI + Vue 基础项目搭建
- [ ] 数据库设计和连接
- [ ] 用户认证系统实现

#### Phase 2: 核心功能开发
- [ ] AkShare 数据集成
- [ ] 资产管理 CRUD 功能
- [ ] 基础数据可视化

#### Phase 3: 高级功能开发
- [ ] 策略监控引擎
- [ ] 告警系统
- [ ] AI API 集成

#### Phase 4: 优化与部署
- [ ] 性能优化
- [ ] 容器化部署
- [ ] 监控日志系统

### 9. 技术优势

- **简洁高效**: FastAPI + Vue 都是轻量级、高性能框架
- **类型安全**: 全链路 TypeScript 支持，减少运行时错误
- **易于扩展**: 模块化设计便于功能扩展和维护
- **部署灵活**: 支持传统部署和容器化部署
- **成本可控**: 全开源技术栈，普通云服务器即可部署
- **开发体验**: FastAPI 自动生成API文档，Vue 热重载开发
- **社区活跃**: 两个框架都有活跃的社区支持

### 10. 快速开始

#### 后端启动
```bash
cd backend
uv pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端启动
```bash
cd frontend
npm install
npm run dev
```

#### Docker 部署
```bash
docker-compose up -d
```

