# 八方策金融座舱 - 项目概述

## 1. 项目简介

一个用于个人投资管理的Python工具，通过akshare获取金融产品实时数据，并计算持仓成本与现值的Web应用。支持多用户、全天候策略监控、AI持仓建议等功能。

## 2. 系统架构

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

## 3. 技术栈选择

### 3.1 后端技术栈

- **核心语言**: Python 3.10+
- **Web框架**: FastAPI
- **数据库**: PostgreSQL (生产环境) / SQLite (开发环境)
- **ORM**: SQLAlchemy
- **认证**: JWT + OAuth2
- **数据获取**: AkShare
- **任务调度**: APScheduler / Celery
- **AI集成**: Claude API / OpenAI API
- **依赖管理**: uv

### 3.2 前端技术栈

- **核心框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件**: Element Plus / Ant Design Vue
- **路由**: Vue Router
- **状态管理**: Pinia
- **HTTP客户端**: Axios

## 4. 项目结构

### 4.1 后端目录结构

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
│   │   ├── portfolio.py     # 投资组合相关模式
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

### 4.2 前端目录结构

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
│   │   ├── portfolio.ts     # 投资组合API
│   │   └── ai.ts            # AI API
│   └── types/
│       └── index.ts         # TypeScript类型定义
├── package.json             # 前端依赖
├── vite.config.ts           # Vite配置
└── tsconfig.json            # TypeScript配置
```

## 5. 核心功能模块

### 5.1 用户认证与授权

- JWT Token 认证机制
- 用户注册、登录、密码找回
- 数据隔离：每个用户只能访问自己的数据
- 可选：管理员角色和权限管理

### 5.2 资产管理

- 支持多种资产类型：股票、基金、债券、现金
- AkShare 实时数据同步
- 自动更新持仓市值
- 历史数据存储和查询
- 成本与收益计算
- **策略分类管理**：在资产管理页面中直接为资产设置策略分类

### 5.3 投资组合管理

- 支持创建多个投资组合
- 将持有资产添加到投资组合中
- **资产分配约束**：每项资产只能被一个组合持有
- 组合资产权重配置（目标权重 vs 当前权重）
- 组合收益分析（总市值、总成本、总盈亏、收益率）
- 组合策略分类分布分析
- 资产在组合间的转移管理
- 批量资产操作
- **策略分类显示**：资产表格中展示每项资产的当前策略分类（只读，如需修改请前往资产管理页面）

### 5.4 策略监控

- 全天候策略配置（阈值、条件）
- 定时任务执行监控
- 实时告警通知（邮件、短信、App通知）
- 策略历史执行记录
- 策略回测功能

### 5.5 AI 持仓建议

- API集成：调用Claude / OpenAI API
- 功能模块：
  - 投资组合分析
  - 风险评估
  - 调仓建议
  - 市场趋势分析
- 上下文管理：用户历史数据 + 实时市场数据
- 建议历史记录和评价

### 5.6 数据可视化

- 资产配置饼图
- 收益曲线图
- 风险指标仪表盘
- 策略执行状态监控
- 实时市场行情展示
- 组合策略分类分布可视化

## 6. 数据库设计

### 核心表结构

- `users`: 用户信息表
- `assets`: 资产明细表
- `portfolios`: 投资组合表
- `portfolio_assets`: 投资组合资产关联表（实现资产与组合的多对多关系，约束每项资产只能在一个组合中）
- `strategies`: 策略配置表
- `strategy_executions`: 策略执行记录表
- `alerts`: 告警记录表
- `ai_suggestions`: AI建议记录表
- `market_data`: 市场数据缓存表

## 7. 部署方案

### 7.1 传统部署

```
Nginx
  ├── /api  → FastAPI (Uvicorn + Gunicorn)
  └── /     → Vue (静态文件)
       ↓
  PostgreSQL
  Redis (可选，用于缓存和队列)
```

### 7.2 Docker 容器化部署 (推荐)

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

## 8. 开发计划

### Phase 1: 基础框架搭建

- [ ] FastAPI + Vue 基础项目搭建
- [ ] 数据库设计和连接
- [ ] 用户认证系统实现

### Phase 2: 核心功能开发

- [ ] AkShare 数据集成
- [ ] 资产管理 CRUD 功能
- [ ] 基础数据可视化

### Phase 3: 高级功能开发

- [ ] 策略监控引擎
- [ ] 告警系统
- [ ] AI API 集成

### Phase 4: 优化与部署

- [ ] 性能优化
- [ ] 容器化部署
- [ ] 监控日志系统

## 9. 技术优势

- **简洁高效**: FastAPI + Vue 都是轻量级、高性能框架
- **类型安全**: 全链路 TypeScript 支持，减少运行时错误
- **易于扩展**: 模块化设计便于功能扩展和维护
- **部署灵活**: 支持传统部署和容器化部署
- **成本可控**: 全开源技术栈，普通云服务器即可部署
- **开发体验**: FastAPI 自动生成API文档，Vue 热重载开发
- **社区活跃**: 两个框架都有活跃的社区支持

## 10. 快速开始

### 后端启动

```bash
cd backend
uv pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### Docker 部署

```bash
docker-compose up -d
```
