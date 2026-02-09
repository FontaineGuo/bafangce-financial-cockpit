## 八方策金融座舱


1. 项目概述
一个用于个人投资管理的Python工具，通过akshare获取金融产品实时数据，并计算持仓成本与现值的桌面应用。支持CLI界面和HTML报表导出功能。

2. 技术栈选择
核心语言: Python 3.14+
数据获取: akshare
数据存储: SQLite（轻量级，适合个人使用）
前端框架: Vue
后端框架：FastAPI
数据处理: pandas
配置文件: JSON/YAML
依赖管理: uv

3. 项目结构
bafangce-financial-cockpit/
backend/
├── .python-version          # 锁定 Python 版本，uv 会读取这个
├── pyproject.toml           # 核心配置：依赖、元数据、构建配置。单一事实来源。
├── uv.lock                  # 依赖锁定文件（类似 package-lock.json）。别手动改它。
├── README.md
├── .gitignore
├── src/
│   └── finance_backend/     # 你的实际代码包
│       ├── __init__.py
│       ├── main.py          # FastAPI 入口
│       ├── api/             # 路由层
│       ├── core/            # 配置、安全
│       ├── models/          # 数据库模型
│       ├── services/        # 业务逻辑（akshare 集成放这里）
│       └── db/              # 数据库会话管理
├── tests/                   # 测试代码。和源代码分离，这是常识。
│   ├── __init__.py
│   └── test_main.py
├── scripts/                 # 脚本工具，比如数据初始化
│   └── init_db.py
└── alembic/                 # 如果用 Alembic 做数据库迁移（虽然你可以放 src 里，但根目录更干净）
    └── versions/
frontend/
├── index.html               # 入口 HTML，别动它，除非你知道自己在干嘛
├── package.json             # 依赖管理（对应后端的 pyproject.toml）
├── vite.config.js           # Vite 配置，通常不需要动
├── .gitignore
└── src/
    ├── main.js              # 应用入口，挂载 Vue 实例
    ├── App.vue              # 根组件
    ├── assets/              # 静态资源：图片、全局样式
    │   └── main.css
    ├── api/                 # 【重点】所有后端 API 调用集中在这里
    │   ├── index.js         # axios 实例配置（baseURL, 拦截器）
    │   ├── auth.js          # 登录、注册接口
    │   ├── portfolio.js     # 持仓数据接口
    │   └── ai.js            # AI 建议接口
    ├── components/          # 通用组件
    │   ├── PortfolioChart.vue
    │   └── LoadingSpinner.vue
    ├── composables/         # Vue 3 的 "好品味"：逻辑复用
    │   ├── useAuth.js       # 处理登录状态、Token 刷新
    │   └── usePortfolio.js  # 处理持仓数据的获取和缓存
    ├── router/              # 路由配置
    │   └── index.js
    ├── stores/              # 状态管理
    │   ├── user.js          # 用户信息
    │   └── portfolio.js     # 持仓状态
    └── views/               # 页面组件
        ├── Login.vue
        ├── Dashboard.vue
        └── Settings.vue