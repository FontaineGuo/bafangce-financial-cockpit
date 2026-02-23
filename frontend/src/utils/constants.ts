import { AssetType, StrategyCategory } from '@/types'

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
  [AssetType.CASH]: '现金'
}

// 注：债券通过基金持有，不设置独立的BOND资产类型
// 债券通过以下基金类型持有：
// - OPEN_FUND: 开放式债券基金（纯债、信用债、可转债等）
// - ETF_FUND: 债券型ETF（国债ETF、信用债ETF等）
// - LOF_FUND: 债券型LOF（场内交易的债券基金）

// 资产类型到默认策略分类的映射
const DEFAULT_CATEGORY_MAPPING: Partial<Record<AssetType, StrategyCategory>> = {
  [AssetType.STOCK]: StrategyCategory.CN_STOCK_ETF,
  [AssetType.LOF_FUND]: StrategyCategory.COMMODITY,
  [AssetType.ETF_FUND]: StrategyCategory.CN_STOCK_ETF,
  [AssetType.OPEN_FUND]: StrategyCategory.CN_STOCK_ETF,
  [AssetType.CASH]: StrategyCategory.CASH
  // 注：债券通过基金持有，不设置独立的BOND资产类型
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
  // 债券类LOF基金
  '债券': StrategyCategory.CREDIT_BOND,
  '国债': StrategyCategory.LONG_BOND,
  '信用': StrategyCategory.CREDIT_BOND,
  '可转债': StrategyCategory.SHORT_BOND,
  '短债': StrategyCategory.SHORT_BOND,
  '纯债': StrategyCategory.LONG_BOND
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
  // 债券类ETF基金
  '国债': StrategyCategory.LONG_BOND,
  '信用': StrategyCategory.CREDIT_BOND,
  '可转债': StrategyCategory.SHORT_BOND,
  '短债': StrategyCategory.SHORT_BOND,
  '纯债': StrategyCategory.LONG_BOND,
  '长久期': StrategyCategory.LONG_BOND
}

// 开放式基金关键字映射
const OPEN_FUND_KEYWORD_MAPPING: Record<string, StrategyCategory> = {
  '黄金': StrategyCategory.GOLD,
  // 债券类开放式基金
  '债券': StrategyCategory.CREDIT_BOND,
  '国债': StrategyCategory.LONG_BOND,
  '短债': StrategyCategory.SHORT_BOND,
  '可转债': StrategyCategory.SHORT_BOND,
  '中短债': StrategyCategory.SHORT_BOND,
  '纯债': StrategyCategory.LONG_BOND,
  '长久期': StrategyCategory.LONG_BOND,
  '信用': StrategyCategory.CREDIT_BOND,
  '信用债': StrategyCategory.CREDIT_BOND,
  '企业债': StrategyCategory.CREDIT_BOND,
  '短融': StrategyCategory.SHORT_BOND,
  // 其他类型
  '原油': StrategyCategory.COMMODITY,
  '美元': StrategyCategory.CASH,
  '货币': StrategyCategory.CASH,
  '商品': StrategyCategory.COMMODITY
}

export function getDefaultStrategyCategory(
  assetType: AssetType,
  assetName: string = ''
): StrategyCategory {
  let category = DEFAULT_CATEGORY_MAPPING[assetType] || StrategyCategory.OTHER

  if (assetType === AssetType.LOF_FUND && assetName) {
    category = categorizeFundByName(assetName, LOF_KEYWORD_MAPPING, category)
  } else if (assetType === AssetType.ETF_FUND && assetName) {
    category = categorizeFundByName(assetName, ETF_KEYWORD_MAPPING, category)
  } else if (assetType === AssetType.OPEN_FUND && assetName) {
    category = categorizeFundByName(assetName, OPEN_FUND_KEYWORD_MAPPING, category)
  }

  return category
}

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

export function isUserOverrideMapping(mapping?: AssetCategoryMapping): boolean {
  return mapping?.is_user_override ?? false
}

export function formatStrategyCategoryName(category: StrategyCategory): string {
  return STRATEGY_CATEGORY_NAMES[category] || category
}

export function getStrategyCategoryColor(category: StrategyCategory): string {
  return STRATEGY_CATEGORY_COLORS[category] || '#C0C4CC'
}
