# 八方策金融座舱 - 前端文档

## 1. 前端技术栈

### 核心框架

- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **构建工具**: Vite

### UI 组件库

- **组件库**: Element Plus / Ant Design Vue
- **图表库**: ECharts / Chart.js
- **样式方案**: SCSS / CSS Modules

### 状态管理与路由

- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios

## 2. 项目结构

```
frontend/
├── src/
│   ├── main.ts                  # 应用入口
│   ├── App.vue                  # 根组件
│   ├── router/
│   │   └── index.ts             # 路由配置
│   ├── store/
│   │   ├── user.ts              # 用户状态
│   │   ├── assets.ts            # 资产状态
│   │   ├── portfolio.ts         # 投资组合状态
│   │   └── assetCategories.ts   # 资产分类状态（新增）
│   ├── views/
│   │   ├── Login.vue            # 登录页
│   │   ├── Dashboard.vue        # 仪表盘
│   │   ├── Assets.vue           # 资产管理页
│   │   ├── Portfolio.vue        # 投资组合页
│   │   ├── Strategies.vue       # 策略管理页
│   │   └── AIAdvisor.vue        # AI建议页
│   ├── components/
│   │   ├── AssetCard.vue        # 资产卡片组件
│   │   ├── StrategyPanel.vue    # 策略面板组件
│   │   ├── ChartContainer.vue   # 图表容器组件
│   │   ├── AssetCategorySelector.vue  # 资产分类选择器（新增）
│   │   ├── StrategyDistributionChart.vue  # 策略分布图表（新增）
│   │   └── BulkCategoryDialog.vue        # 批量分类设置对话框（新增）
│   ├── api/
│   │   ├── index.ts             # API客户端配置
│   │   ├── auth.ts              # 认证API
│   │   ├── assets.ts            # 资产API
│   │   ├── assetCategories.ts   # 资产分类API（新增）
│   │   └── ai.ts                # AI API
│   ├── utils/
│   │   ├── categoryMapping.ts   # 分类映射工具函数（新增）
│   │   └── constants.ts         # 常量定义（新增）
│   └── types/
│       └── index.ts             # TypeScript类型定义
├── package.json                 # 前端依赖
├── vite.config.ts               # Vite配置
└── tsconfig.json                # TypeScript配置
```

## 3. 核心页面

### 3.1 登录页 (Login.vue)

用户认证入口页面

**功能**:
- 用户名/密码登录
- 记住密码功能
- 密码找回链接
- 注册链接

**主要组件**:
- 登录表单
- 记住我复选框
- 登录按钮

### 3.2 仪表盘 (Dashboard.vue)

数据概览和主要指标展示

**功能**:
- 总资产显示
- 日收益/亏损
- 持仓分布图表
- 策略分类分布图表（新增）
- 近期策略执行状态
- 重要告警通知

**主要组件**:
- 资产卡片（总资产、日收益、持仓数）
- 资产配置饼图
- 策略分类分布雷达图（新增）
- 收益曲线图
- 告警列表
- 策略状态面板

### 3.3 资产管理页 (Assets.vue)

资产管理主界面

**功能**:
- 资产列表展示（表格）
- 资产添加/编辑/删除
- 批量操作
- 资产搜索和筛选
- 策略分类管理（新增）
- 用户自定义分类覆盖（新增）
- 导出功能

**主要组件**:
- 资产表格（支持排序、分页）
- 添加资产对话框
- 编辑资产对话框（包含策略分类选择）
- 批量策略分类设置对话框（新增）
- 搜索框
- 筛选器（按类型、策略分类等）
- 导出按钮

**策略分类管理功能**:
- 显示资产的当前策略分类
- 标识系统自动映射 vs 用户自定义覆盖
- 支持单个或批量修改资产策略分类
- 提供恢复默认分类选项

### 3.4 投资组合页 (Portfolio.vue)

投资组合管理和分析

**功能**:
- 投资组合创建/编辑
- 组合资产配置
- 组合收益分析
- 风险评估
- 策略分类分布分析（新增）
- 历史对比

**主要组件**:
- 组合列表
- 组合编辑表单
- 资产配置调整
- 策略分类分布可视化（新增）
- 收益图表
- 风险指标展示

**策略分类分析功能**:
- 显示按策略分类的资产分布
- 提供目标权重 vs 当前权重对比
- 支持按策略分类查看详细资产列表

### 3.5 策略管理页 (Strategies.vue)

交易策略配置和监控

**功能**:
- 策略创建/编辑/删除
- 策略参数配置（阈值、条件）
- 策略分类关联（新增）
- 策略启用/禁用
- 策略执行历史查看
- 告警设置

**主要组件**:
- 策略列表
- 策略配置表单
- 策略分类选择器（新增）
- 阈值设置组件
- 条件逻辑编辑器
- 执行历史表格
- 告警设置对话框

**策略分类功能**:
- 为策略关联特定策略分类
- 支持按策略分类筛选和查看策略
- 显示策略对特定资产分类的影响

### 3.6 AI建议页 (AIAdvisor.vue)

AI持仓建议和分析

**功能**:
- 投资组合AI分析
- 风险评估
- 调仓建议
- 策略分类优化建议（新增）
- 市场趋势分析
- 建议历史记录

**主要组件**:
- AI分析面板
- 风险评估图表
- 调仓建议列表
- 策略分类优化建议面板（新增）
- 市场趋势展示
- 建议历史表格

**策略分类优化功能**:
- 基于策略分类提供资产配置建议
- 分析当前策略分布的风险暴露
- 提供策略分类调整建议

## 4. 核心组件

### 4.1 AssetCard.vue

资产卡片组件，用于展示单个资产的摘要信息

**Props**:
- `asset`: 资产对象
- `showActions`: 是否显示操作按钮
- `showCategory`: 是否显示策略分类（新增）

**Events**:
- `edit`: 编辑事件
- `delete`: 删除事件
- `changeCategory`: 修改策略分类（新增）

### 4.2 StrategyPanel.vue

策略面板组件，用于展示策略状态和执行情况

**Props**:
- `strategy`: 策略对象
- `lastExecution`: 最后执行信息

**Events**:
- `toggle`: 切换启用状态
- `edit`: 编辑策略

### 4.3 ChartContainer.vue

图表容器组件，用于封装各种图表

**Props**:
- `chartType`: 图表类型（pie、line、bar等）
- `chartData`: 图表数据
- `chartOptions`: 图表配置选项

### 4.4 AssetCategorySelector.vue（新增）

资产策略分类选择器组件

**Props**:
- `assetCode`: 资产代码
- `assetType`: 资产类型
- `currentCategory`: 当前策略分类
- `isUserOverride`: 是否为用户自定义覆盖
- `disabled`: 是否禁用

**Events**:
- `change`: 策略分类变更事件
- `reset`: 重置为默认分类事件

**功能**:
- 显示当前策略分类
- 提供策略分类下拉选择
- 区分系统自动映射和用户自定义
- 支持重置为系统默认分类

### 4.5 StrategyDistributionChart.vue（新增）

策略分类分布图表组件

**Props**:
- `distribution`: 策略分布数据
- `chartType`: 图表类型（pie、bar、radar）
- `showLabels`: 是否显示标签

**功能**:
- 可视化展示按策略分类的资产分布
- 支持多种图表类型切换
- 交互式显示分类详情

### 4.6 BulkCategoryDialog.vue（新增）

批量设置策略分类对话框组件

**Props**:
- `visible`: 是否显示对话框
- `selectedAssets`: 选中的资产列表
- `targetCategory`: 目标策略分类

**Events**:
- `confirm`: 确认批量设置
- `cancel`: 取消操作

**功能**:
- 显示选中资产列表
- 选择目标策略分类
- 预览变更影响
- 确认或取消批量操作

## 5. 状态管理 (Pinia)

### 5.1 user.ts

用户相关状态管理

**State**:
- `user`: 当前用户信息
- `token`: 认证令牌
- `isAuthenticated`: 是否已认证

**Actions**:
- `login()`: 用户登录
- `logout()`: 用户登出
- `updateUser()`: 更新用户信息

### 5.2 assets.ts

资产相关状态管理

**State**:
- `assets`: 资产列表
- `totalAssets`: 总资产
- `loading`: 加载状态

**Actions**:
- `fetchAssets()`: 获取资产列表
- `addAsset()`: 添加资产
- `updateAsset()`: 更新资产
- `deleteAsset()`: 删除资产
- `refreshAssets()`: 刷新资产数据

### 5.3 portfolio.ts

投资组合相关状态管理

**State**:
- `portfolios`: 投资组合列表
- `currentPortfolio`: 当前选中的组合
- `loading`: 加载状态

**Actions**:
- `fetchPortfolios()`: 获取投资组合列表
- `selectPortfolio()`: 选择投资组合
- `createPortfolio()`: 创建投资组合
- `updatePortfolio()`: 更新投资组合
- `deletePortfolio()`: 删除投资组合

### 5.4 assetCategories.ts

资产策略分类管理状态管理

**State**:
- `mappings`: 资产分类映射列表
- `strategyCategories`: 策略分类列表
- `distribution`: 当前组合的策略分布
- `loading`: 加载状态

**Actions**:
- `fetchAssetCategoryMappings()`: 获取所有资产分类映射
- `getAssetCategoryMapping(assetCode)`: 获取指定资产的分类映射
- `createAssetCategoryMapping(data)`: 创建资产分类映射
- `updateAssetCategoryMapping(id, data)`: 更新资产分类映射
- `deleteAssetCategoryMapping(id)`: 删除资产分类映射
- `fetchStrategyCategories()`: 获取策略分类列表
- `getDefaultAssetCategory(assetType)`: 获取资产类型的默认分类
- `fetchPortfolioStrategyDistribution(portfolioId)`: 获取组合策略分布
- `bulkUpdateAssetCategories(updates)`: 批量更新资产分类

**示例使用**:

```typescript
// 获取资产的策略分类
const store = useAssetCategoriesStore()
const mapping = await store.getAssetCategoryMapping('501018')
console.log(mapping.strategyCategory) // 'COMMODITY'

// 用户自定义覆盖资产分类
await store.createAssetCategoryMapping({
  assetCode: '501018',
  assetType: AssetType.LOF_FUND,
  strategyCategory: StrategyCategory.CN_STOCK_ETF,
  isUserOverride: true
})

// 获取组合的策略分布
const distribution = await store.fetchPortfolioStrategyDistribution(1)
// 返回按策略分类统计的资产分布情况
```

## 6. API 集成

### 6.1 API 客户端配置 (api/index.ts)

```typescript
import axios from 'axios'
import { useUserStore } from '@/store/user'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

### 6.2 认证API (api/auth.ts)

用户认证相关API

**Methods**:
- `login(username, password)`: 用户登录
- `register(userData)`: 用户注册
- `logout()`: 用户登出
- `refreshToken()`: 刷新令牌

### 6.3 资产API (api/assets.ts)

资产管理相关API

**Methods**:
- `getAssets(params)`: 获取资产列表
- `getAsset(id)`: 获取单个资产
- `createAsset(data)`: 创建资产
- `updateAsset(id, data)`: 更新资产
- `deleteAsset(id)`: 删除资产
- `getAssetPrices(codes)`: 批量获取资产价格

### 6.4 AI API (api/ai.ts)

AI建议相关API

**Methods**:
- `analyzePortfolio(portfolioId)`: 分析投资组合
- `getRiskAssessment(portfolioId)`: 获取风险评估
- `getRebalancingSuggestions(portfolioId)`: 获取调仓建议
- `getMarketTrend()`: 获取市场趋势

### 6.5 资产分类管理 API (api/assetCategories.ts)

资产策略分类管理相关API

**Methods**:
- `getAssetCategoryMappings()`: 获取用户所有资产分类映射
- `getAssetCategoryMapping(assetCode)`: 获取指定资产的分类映射
- `createAssetCategoryMapping(data)`: 创建资产分类映射
- `updateAssetCategoryMapping(id, data)`: 更新资产分类映射
- `deleteAssetCategoryMapping(id)`: 删除资产分类映射
- `getStrategyCategories()`: 获取所有策略分类列表
- `getDefaultAssetCategories(assetType)`: 根据资产类型获取默认策略分类
- `getPortfolioStrategyDistribution(portfolioId)`: 获取投资组合的策略分类分布

**示例请求**:

```typescript
// 创建资产分类映射（用户自定义覆盖）
const mappingData = {
  assetCode: "501018",
  assetType: AssetType.LOF_FUND,
  strategyCategory: StrategyCategory.COMMODITY,
  isUserOverride: true
}
createAssetCategoryMapping(mappingData)

// 获取投资组合策略分布
getPortfolioStrategyDistribution(1)
// 返回:
// {
//   distribution: [
//     { category: StrategyCategory.CN_STOCK_ETF, count: 5, totalValue: 50000, targetWeight: 40, currentWeight: 45 },
//     { category: StrategyCategory.COMMODITY, count: 3, totalValue: 30000, targetWeight: 30, currentWeight: 27 },
//     // ...
//   ]
// }
```

## 7. 路由配置

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/assets',
    name: 'Assets',
    component: () => import('@/views/Assets.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/portfolio',
    name: 'Portfolio',
    component: () => import('@/views/Portfolio.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/strategies',
    name: 'Strategies',
    component: () => import('@/views/Strategies.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-advisor',
    name: 'AIAdvisor',
    component: () => import('@/views/AIAdvisor.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && userStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
```

## 8. 工具函数和常量 (utils/)

### 8.1 constants.ts

项目常量定义

```typescript
// 策略分类显示名称映射
export const STRATEGY_CATEGORY_NAMES: Record<StrategyCategory, string> = {
  [StrategyCategory.CASH]: '现金',
  [StrategyCategory.CN_STOCK_ETF]: '国内股票ETF',
  [StrategyCategory.OVERSEAS_STOCK_ETF]: '海外股票ETF',
  [StrategyCategory.COMMODITY]: '商品',
  [StrategyCategory.CREDIT_BOND]: '信用债',
  [StrategyCategory.LONG_BOND]: '长债',
  [StrategyCategory.SHORT_BOND]: '短债',
  [StrategyCategory.GOLD]: '黄金',
  [StrategyCategory.OTHER]: '其他'
}

// 策略分类颜色映射（用于图表）
export const STRATEGY_CATEGORY_COLORS: Record<StrategyCategory, string> = {
  [StrategyCategory.CASH]: '#909399',
  [StrategyCategory.CN_STOCK_ETF]: '#409EFF',
  [StrategyCategory.OVERSEAS_STOCK_ETF]: '#67C23A',
  [StrategyCategory.COMMODITY]: '#E6A23C',
  [StrategyCategory.CREDIT_BOND]: '#F56C6C',
  [StrategyCategory.LONG_BOND]: '#FF6B6B',
  [StrategyCategory.SHORT_BOND]: '#FFB74D',
  [StrategyCategory.GOLD]: '#FFD700',
  [StrategyCategory.OTHER]: '#C0C4CC'
}

// 资产类型显示名称
export const ASSET_TYPE_NAMES: Record<AssetType, string> = {
  [AssetType.STOCK]: '股票',
  [AssetType.LOF_FUND]: 'LOF基金',
  [AssetType.ETF_FUND]: 'ETF基金',
  [AssetType.OPEN_FUND]: '开放式基金',
  [AssetType.BOND]: '债券',
  [AssetType.CASH]: '现金'
}
```

### 8.2 categoryMapping.ts

分类映射工具函数

```typescript
import { AssetType, StrategyCategory } from '@/types'

// 资产类型到默认策略分类的映射（与后端保持一致）
const DEFAULT_CATEGORY_MAPPING: Partial<Record<AssetType, StrategyCategory>> = {
  [AssetType.STOCK]: StrategyCategory.CN_STOCK_ETF,
  [AssetType.LOF_FUND]: StrategyCategory.COMMODITY, // 需要根据具体基金名称二次判断
  [AssetType.ETF_FUND]: StrategyCategory.CN_STOCK_ETF, // 需要根据具体ETF名称二次判断
  [AssetType.OPEN_FUND]: StrategyCategory.CN_STOCK_ETF, // 需要根据具体基金名称二次判断
  [AssetType.BOND]: StrategyCategory.CREDIT_BOND,
  [AssetType.CASH]: StrategyCategory.CASH
}

// 基金名称关键字到策略分类的映射（LOF基金）
const LOF_KEYWORD_MAPPING: Record<string, StrategyCategory> = {
  '原油': StrategyCategory.COMMODITY,
  '白银': StrategyCategory.COMMODITY,
  '豆粕': StrategyCategory.COMMODITY,
  '能源': StrategyCategory.COMMODITY,
  '有色': StrategyCategory.COMMODITY,
  '黄金': StrategyCategory.GOLD,
  '日经': StrategyCategory.OVERSEAS_STOCK_ETF,
  '纳指': StrategyCategory.OVERSEAS_STOCK_ETF,
  '恒生': StrategyCategory.CN_STOCK_ETF,
  '沪深': StrategyCategory.CN_STOCK_ETF,
  '中证': StrategyCategory.CN_STOCK_ETF,
  '标普': StrategyCategory.OVERSEAS_STOCK_ETF,
  '美元': StrategyCategory.CASH,
  '债券': StrategyCategory.CREDIT_BOND
}

// 基金名称关键字到策略分类的映射（ETF基金）
const ETF_KEYWORD_MAPPING: Record<string, StrategyCategory> = {
  '能源': StrategyCategory.COMMODITY,
  '化工': StrategyCategory.COMMODITY,
  '有色': StrategyCategory.COMMODITY,
  '豆粕': StrategyCategory.COMMODITY,
  '黄金': StrategyCategory.GOLD,
  '白银': StrategyCategory.COMMODITY,
  '原油': StrategyCategory.COMMODITY,
  '日经': StrategyCategory.OVERSEAS_STOCK_ETF,
  '纳指': StrategyCategory.OVERSEAS_STOCK_ETF,
  '标普': StrategyCategory.OVERSEAS_STOCK_ETF,
  '沪深': StrategyCategory.CN_STOCK_ETF,
  '中证': StrategyCategory.CN_STOCK_ETF,
  '科创': StrategyCategory.CN_STOCK_ETF,
  '创业': StrategyCategory.CN_STOCK_ETF,
  '国债': StrategyCategory.LONG_BOND,
  '信用': StrategyCategory.CREDIT_BOND,
  '可转债': StrategyCategory.SHORT_BOND
}

// 开放式基金关键字映射
const OPEN_FUND_KEYWORD_MAPPING: Record<string, StrategyCategory> = {
  '黄金': StrategyCategory.GOLD,
  '债券': StrategyCategory.CREDIT_BOND,
  '国债': StrategyCategory.LONG_BOND,
  '短债': StrategyCategory.SHORT_BOND,
  '可转债': StrategyCategory.SHORT_BOND,
  '原油': StrategyCategory.COMMODITY,
  '美元': StrategyCategory.CASH,
  '货币': StrategyCategory.CASH,
  '商品': StrategyCategory.COMMODITY
}

/**
 * 根据资产类型和名称获取默认策略分类
 */
export function getDefaultStrategyCategory(
  assetType: AssetType,
  assetName: string = ''
): StrategyCategory {
  // 首先使用资产类型的默认映射
  let category = DEFAULT_CATEGORY_MAPPING[assetType] || StrategyCategory.OTHER

  // 对于基金类型，根据基金名称关键字进行二次判断
  if (assetType === AssetType.LOF_FUND && assetName) {
    category = categorizeFundByName(assetName, LOF_KEYWORD_MAPPING, category)
  } else if (assetType === AssetType.ETF_FUND && assetName) {
    category = categorizeFundByName(assetName, ETF_KEYWORD_MAPPING, category)
  } else if (assetType === AssetType.OPEN_FUND && assetName) {
    category = categorizeFundByName(assetName, OPEN_FUND_KEYWORD_MAPPING, category)
  }

  return category
}

/**
 * 根据基金名称关键字进行分类
 */
function categorizeFundByName(
  fundName: string,
  keywordMapping: Record<string, StrategyCategory>,
  defaultCategory: StrategyCategory
): StrategyCategory {
  for (const [keyword, category] of Object.entries(keywordMapping)) {
    if (fundName.includes(keyword)) {
      return category
    }
  }
  return defaultCategory
}

/**
 * 判断分类是否为用户自定义覆盖
 */
export function isUserOverrideMapping(mapping?: AssetCategoryMapping): boolean {
  return mapping?.isUserOverride ?? false
}

/**
 * 格式化策略分类显示名称
 */
export function formatStrategyCategoryName(category: StrategyCategory): string {
  return STRATEGY_CATEGORY_NAMES[category] || category
}

/**
 * 获取策略分类颜色
 */
export function getStrategyCategoryColor(category: StrategyCategory): string {
  return STRATEGY_CATEGORY_COLORS[category] || '#C0C4CC'
}
```

## 9. 类型定义 (types/index.ts)

```typescript
// ==================== 基础枚举类型 ====================

// 资产类型枚举（匹配后端 AssetType）
export enum AssetType {
  STOCK = 'STOCK',
  LOF_FUND = 'LOF_FUND',
  ETF_FUND = 'ETF_FUND',
  OPEN_FUND = 'OPEN_FUND',
  BOND = 'BOND',
  CASH = 'CASH'
}

// 策略分类枚举（匹配后端 StrategyCategory）
export enum StrategyCategory {
  CASH = 'CASH',
  CN_STOCK_ETF = 'CN_STOCK_ETF',
  OVERSEAS_STOCK_ETF = 'OVERSEAS_STOCK_ETF',
  COMMODITY = 'COMMODITY',
  CREDIT_BOND = 'CREDIT_BOND',
  LONG_BOND = 'LONG_BOND',
  SHORT_BOND = 'SHORT_BOND',
  GOLD = 'GOLD',
  OTHER = 'OTHER'
}

// ==================== 用户相关类型 ====================

export interface User {
  id: number
  username: string
  email: string
  createdAt: string
}

// ==================== 资产相关类型 ====================

// 市场数据接口
export interface MarketData {
  price: number                      // 最新价
  changeAmount?: number              // 涨跌额
  changePercent?: number            // 涨跌幅
  volume?: number                   // 成交量
  turnover?: number                 // 成交额
  openPrice?: number                // 开盘价
  highPrice?: number                // 最高价
  lowPrice?: number                 // 最低价
  prevClose?: number                // 昨收价
  turnoverRate?: number             // 换手率
  circulatingMarketCap?: number    // 流通市值
  totalMarketCap?: number           // 总市值
  unitNetValue?: number             // 单位净值（基金）
  accumulatedNetValue?: number      // 累计净值（基金）
  discountRate?: number             // 折价率（基金）
}

// 资产接口
export interface Asset {
  id: number
  code: string
  name: string
  type: AssetType
  market: 'CN' | 'US' | 'EU' | 'HK'
  quantity: number
  costPrice: number
  currentPrice: number
  marketValue: number
  profit: number
  profitPercent: number
  marketData?: MarketData           // 市场数据
  strategyCategory?: StrategyCategory // 策略分类（用户可覆盖）
}

// 资产分类映射接口
export interface AssetCategoryMapping {
  id: number
  userId: number
  assetCode: string
  assetType: AssetType
  strategyCategory: StrategyCategory
  isUserOverride: boolean           // 是否为用户自定义覆盖
  autoMapped: boolean               // 是否为系统自动映射
  createdAt: string
  updatedAt: string
}

// ==================== 投资组合相关类型 ====================

// 投资组合资产配置
export interface PortfolioAsset {
  asset: Asset
  targetWeight: number            // 目标权重（百分比）
  currentWeight: number           // 当前权重
  allocationAmount: number        // 分配金额
}

// 投资组合接口
export interface Portfolio {
  id: number
  userId: number
  name: string
  description: string
  assets: PortfolioAsset[]
  strategyDistribution?: StrategyDistribution // 策略分类分布
  totalValue: number
  totalCost: number
  totalProfit: number
  totalProfitPercent: number
  createdAt: string
  updatedAt: string
}

// 策略分类分布
export interface StrategyDistribution {
  category: StrategyCategory
  count: number
  totalValue: number
  targetWeight: number
  currentWeight: number
}

// ==================== 策略相关类型 ====================

export interface Strategy {
  id: number
  userId: number
  name: string
  type: string
  category?: StrategyCategory      // 关联的策略分类
  conditions: StrategyCondition[]
  enabled: boolean
  lastExecution?: string
  createdAt: string
  updatedAt: string
}

export interface StrategyCondition {
  id: number
  field: string
  operator: string
  value: number
  logicalOperator?: 'AND' | 'OR'   // 多条件逻辑关系
}

// ==================== AI建议相关类型 ====================

export interface AISuggestion {
  id: number
  portfolioId: number
  type: 'risk' | 'rebalancing' | 'trend'
  title: string
  content: string
  priority: 'low' | 'medium' | 'high'
  status: 'pending' | 'applied' | 'dismissed'
  createdAt: string
  appliedAt?: string
}

// ==================== 缓存相关类型 ====================

export interface CacheMetadata {
  dataType: string                 // 数据类型（如 'stock', 'lof_fund' 等）
  code: string                     // 资产代码
  cachedAt: string                 // 缓存时间
  expiresAt: string                // 过期时间
  dataSize: number                 // 数据大小（字节）
}

// ==================== API响应类型 ====================

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}
```

## 10. 环境配置

### .env.development

```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000/ws
```

### .env.production

```
VITE_API_BASE_URL=https://your-domain.com/api
VITE_WS_BASE_URL=wss://your-domain.com/ws
```

## 11. 开发指南

### 10.1 安装依赖

```bash
cd frontend
npm install
```

### 10.2 启动开发服务器

```bash
npm run dev
```

### 10.3 构建生产版本

```bash
npm run build
```

### 10.4 预览生产构建

```bash
npm run preview
```

## 12. 最佳实践

1. **组件命名**: 使用 PascalCase 命名组件文件和组件名
2. **样式隔离**: 使用 scoped CSS 或 CSS Modules
3. **类型检查**: 充分利用 TypeScript 类型检查
4. **错误处理**: 统一的错误处理机制
5. **代码分割**: 使用路由懒加载优化性能
6. **状态管理**: 合理使用 Pinia store，避免过度全局化
7. **API调用**: 封装 API 调用，统一处理错误和加载状态
8. **策略分类管理**:
   - 优先使用系统自动映射，避免过度自定义
   - 用户自定义覆盖应清晰标注，便于后续维护
   - 批量修改策略分类前应提供预览功能
   - 定期审查策略分类分布，确保配置合理性
9. **数据一致性**:
   - 资产类型和策略分类应与后端保持一致
   - 使用枚举类型而非字符串，避免拼写错误
   - 关键业务逻辑放在后端，前端只负责展示和交互
10. **用户体验**:
    - 策略分类变更应提供撤销功能
    - 加载状态应有明确提示
    - 错误信息应清晰友好，指导用户操作

## 13. 策略分类管理实施指南

### 13.1 实施步骤

1. **初始化阶段**:
   - 从后端加载所有资产和现有分类映射
   - 为未分类资产应用默认分类规则
   - 建立前端分类映射工具函数

2. **用户引导**:
   - 在资产管理页添加分类管理入口
   - 提供分类管理帮助文档
   - 展示当前分类分布概览

3. **功能实现**:
   - 实现单个资产分类修改功能
   - 实现批量分类设置功能
   - 实现分类重置为默认功能
   - 实现策略分布可视化

4. **优化迭代**:
   - 根据用户反馈优化分类映射规则
   - 持续完善基金名称关键字识别
   - 提供更多分类选项和自定义能力

### 13.2 关键注意事项

- **性能考虑**: 批量操作时应使用后端批量接口，避免多次单条请求
- **数据验证**: 前端应验证资产代码和分类的有效性
- **冲突处理**: 处理用户自定义与系统自动映射的冲突
- **审计追踪**: 记录分类变更历史，支持回滚操作

### 13.3 测试建议

- 测试各种资产类型的默认分类映射
- 测试基金名称关键字识别准确性
- 测试用户自定义覆盖功能
- 测试批量操作性能
- 测试错误场景和边界条件
