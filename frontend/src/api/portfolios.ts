import apiClient from './index'
import type {
  Portfolio,
  PortfolioCreate,
  PortfolioUpdate,
  ApiResponse,
  PortfolioAssetBase,
  PortfolioAssetCreate,
  StrategyDistributionItem,
  BatchAddAssetsResult,
  StrategyComparison
} from '@/types'

export const portfoliosApi = {
  // 获取投资组合列表
  getPortfolios: () => {
    return apiClient.get<ApiResponse<Portfolio[]>>('/portfolios')
  },

  // 获取单个投资组合
  getPortfolio: (id: number) => {
    return apiClient.get<ApiResponse<Portfolio>>(`/portfolios/${id}`)
  },

  // 创建投资组合
  createPortfolio: (data: PortfolioCreate) => {
    return apiClient.post<ApiResponse<Portfolio>>('/portfolios', data)
  },

  // 更新投资组合
  updatePortfolio: (id: number, data: PortfolioUpdate) => {
    return apiClient.put<ApiResponse<Portfolio>>(`/portfolios/${id}`, data)
  },

  // 删除投资组合
  deletePortfolio: (id: number) => {
    return apiClient.delete<ApiResponse<null>>(`/portfolios/${id}`)
  },

  // 向投资组合添加资产
  addAssetToPortfolio: (portfolioId: number, assetData: PortfolioAssetCreate) => {
    return apiClient.post<ApiResponse<Portfolio>>(`/portfolios/${portfolioId}/assets`, assetData)
  },

  // 批量向投资组合添加资产
  batchAddAssetsToPortfolio: (portfolioId: number, assetList: PortfolioAssetCreate[]) => {
    return apiClient.post<ApiResponse<BatchAddAssetsResult>>(`/portfolios/${portfolioId}/assets/batch`, assetList)
  },

  // 从投资组合移除资产
  removeAssetFromPortfolio: (portfolioId: number, assetId: number) => {
    return apiClient.delete<ApiResponse<null>>(`/portfolios/${portfolioId}/assets/${assetId}`)
  },

  // 获取投资组合的策略分类分布
  getPortfolioStrategyDistribution: (portfolioId: number) => {
    return apiClient.get<ApiResponse<StrategyDistributionItem[]>>(`/portfolios/${portfolioId}/strategy-distribution`)
  },

  // 应用策略组到投资组合
  applyStrategyGroupToPortfolio: (portfolioId: number, strategyGroupId: number) => {
    return apiClient.post<ApiResponse<Portfolio>>(`/portfolios/${portfolioId}/strategy-group`, { strategy_group_id: strategyGroupId })
  },

  // 移除投资组合的策略组
  removeStrategyGroupFromPortfolio: (portfolioId: number) => {
    return apiClient.delete<ApiResponse<null>>(`/portfolios/${portfolioId}/strategy-group`)
  },

  // 获取策略分布对比
  getStrategyComparison: (portfolioId: number) => {
    return apiClient.get<ApiResponse<StrategyComparison>>(`/portfolios/${portfolioId}/strategy-comparison`)
  }
}
