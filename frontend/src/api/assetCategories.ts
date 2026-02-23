import apiClient from './index'
import type {
  AssetCategoryMapping,
  AssetCategoryMappingCreate,
  AssetCategoryMappingUpdate,
  ApiResponse,
  AssetType,
  StrategyDistribution
} from '@/types'

export const assetCategoriesApi = {
  // 获取用户所有资产分类映射
  getMappings: () => {
    return apiClient.get<ApiResponse<AssetCategoryMapping[]>>('/asset-categories')
  },

  // 获取指定资产的分类映射
  getMapping: (assetCode: string) => {
    return apiClient.get<ApiResponse<AssetCategoryMapping>>(`/asset-categories/${assetCode}`)
  },

  // 创建资产分类映射
  createMapping: (data: AssetCategoryMappingCreate) => {
    return apiClient.post<ApiResponse<AssetCategoryMapping>>('/asset-categories', data)
  },

  // 更新资产分类映射
  updateMapping: (id: number, data: AssetCategoryMappingUpdate) => {
    return apiClient.put<ApiResponse<AssetCategoryMapping>>(`/asset-categories/${id}`, data)
  },

  // 删除资产分类映射
  deleteMapping: (id: number) => {
    return apiClient.delete<ApiResponse<null>>(`/asset-categories/${id}`)
  },

  // 获取所有策略分类列表
  getStrategyCategories: () => {
    return apiClient.get<ApiResponse<string[]>>('/asset-categories/strategy-categories/list')
  },

  // 根据资产类型获取默认策略分类
  getDefaultCategory: (assetType: AssetType, assetName: string = '') => {
    return apiClient.get<ApiResponse<string>>(`/asset-categories/default/${assetType}`, {
      params: { asset_name: assetName }
    })
  },

  // 获取投资组合的策略分类分布
  getPortfolioDistribution: (portfolioId: number) => {
    return apiClient.get<ApiResponse<{ distribution: StrategyDistribution[] }>>(
      `/asset-categories/portfolio/${portfolioId}/distribution`
    )
  }
}
