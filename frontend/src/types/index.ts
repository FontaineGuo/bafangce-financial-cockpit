// ==================== 基础枚举类型 ====================

export enum AssetType {
  /**
   * 资产类型枚举

   * 注：债券通过基金持有，不设置独立的BOND资产类型。
   * 债券通过以下基金类型持有：
   * - OPEN_FUND: 开放式债券基金（纯债、信用债、可转债等）
   * - ETF_FUND: 债券型ETF（国债ETF、信用债ETF等）
   * - LOF_FUND: 债券型LOF（场内交易的债券基金）
   */
  STOCK = 'STOCK',
  LOF_FUND = 'LOF_FUND',
  ETF_FUND = 'ETF_FUND',
  OPEN_FUND = 'OPEN_FUND',
  CASH = 'CASH'
}

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
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

// ==================== 资产相关类型 ====================

export interface MarketData {
  price: number
  change_amount?: number
  change_percent?: number
  volume?: number
  turnover?: number
  open_price?: number
  high_price?: number
  low_price?: number
  prev_close?: number
  turnover_rate?: number
  circulating_market_cap?: number
  total_market_cap?: number
  unit_net_value?: number
  accumulated_net_value?: number
  discount_rate?: number
}

export interface Asset {
  id: number
  user_id: number
  code: string
  name: string
  type: AssetType
  market: string
  quantity: number
  cost_price: number
  current_price?: number
  market_value?: number
  profit?: number
  profit_percent?: number
  market_data?: MarketData
  strategy_category?: string
  created_at: string
  updated_at: string
}

export interface AssetCreate {
  code: string
  name?: string
  type: AssetType
  market?: string
  quantity: number
  cost_price: number
}

export interface AssetUpdate {
  name?: string
  type?: AssetType
  market?: string
  quantity?: number
  cost_price?: number
}

// ==================== 资产分类映射相关类型 ====================

export interface AssetCategoryMapping {
  id: number
  user_id: number
  asset_code: string
  asset_type: AssetType
  strategy_category: StrategyCategory
  is_user_override: boolean
  auto_mapped: boolean
  created_at: string
  updated_at: string
}

export interface AssetCategoryMappingCreate {
  asset_code: string
  asset_type: AssetType
  strategy_category: StrategyCategory
  is_user_override?: boolean
}

export interface AssetCategoryMappingUpdate {
  strategy_category?: StrategyCategory
  is_user_override?: boolean
}

// ==================== 投资组合相关类型 ====================

export interface PortfolioAsset {
  id: number
  portfolio_id: number
  asset_id: number
  current_weight: number
  allocation_amount: number
  asset_code?: string
  asset_name?: string
  strategy_category?: string
  asset_market_value?: number
  asset_cost?: number
  asset_profit?: number
  asset_profit_percent?: number
  created_at: string
  updated_at: string
}

export interface Portfolio {
  id: number
  user_id: number
  name: string
  description?: string
  total_value: number
  total_cost: number
  total_profit: number
  total_profit_percent: number
  assets: PortfolioAsset[]
  created_at: string
  updated_at: string
}

export interface PortfolioCreate {
  name: string
  description?: string
  assets?: PortfolioAssetCreate[]
}

export interface PortfolioAssetCreate {
  asset_id: number
}

export interface PortfolioAssetBase {
  asset_id: number
}

export interface PortfolioUpdate {
  name?: string
  description?: string
}


export interface AssetStrategyCategoryUpdate {
  strategy_category: StrategyCategory
}

export interface StrategyDistributionItem {
  category: string
  count: number
  total_value: number
  percentage: number
}

export interface BatchAddAssetsResult {
  added_count: number
  conflict_count: number
  conflicts: Array<{
    asset_id: number
    asset_code?: string
    reason: string
  }>
}

// ==================== 策略组相关类型 ====================

export interface StrategyCategoryAllocation {
  id: number
  strategy_group_id: number
  category: StrategyCategory
  percentage: number
  deviation_threshold?: number
  created_at: string
  updated_at: string
}

export interface StrategyCategoryAllocationCreate {
  category: StrategyCategory
  percentage: number
  deviation_threshold?: number
}

export interface StrategyGroup {
  id: number
  user_id: number
  name: string
  description?: string
  created_at: string
  updated_at: string
  category_allocations: StrategyCategoryAllocation[]
}

export interface StrategyGroupCreate {
  name: string
  description?: string
  category_allocations: StrategyCategoryAllocationCreate[]
}

export interface StrategyGroupUpdate {
  name?: string
  description?: string
  category_allocations?: StrategyCategoryAllocationCreate[]
}

// ==================== AI建议相关类型 ====================

export interface AISuggestion {
  id: number
  portfolio_id: number
  type: string
  title: string
  content: string
  priority: string
  status: string
  created_at: string
  applied_at?: string
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
  page_size: number
  total_pages: number
}

export interface StrategyDistribution {
  category: string
  count: number
  totalValue: number
  targetWeight: number
  currentWeight: number
}
