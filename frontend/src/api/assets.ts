import apiClient from './index'
import type { Asset, AssetCreate, AssetUpdate, AssetStrategyCategoryUpdate, MarketData, AssetType, ApiResponse, ManualPriceUpdate } from '@/types'

export const assetsApi = {
  // 获取资产列表
  getAssets: (params?: { skip?: number; limit?: number }) => {
    return apiClient.get<ApiResponse<Asset[]>>('/assets', { params })
  },

  // 获取单个资产
  getAsset: (id: number) => {
    return apiClient.get<ApiResponse<Asset>>(`/assets/${id}`)
  },

  // 创建资产
  createAsset: (data: AssetCreate) => {
    return apiClient.post<ApiResponse<Asset>>('/assets', data)
  },

  // 更新资产
  updateAsset: (id: number, data: AssetUpdate) => {
    return apiClient.put<ApiResponse<Asset>>(`/assets/${id}`, data)
  },

  // 删除资产
  deleteAsset: (id: number) => {
    return apiClient.delete<ApiResponse<null>>(`/assets/${id}`)
  },

  // 更新资产策略分类
  updateAssetStrategyCategory: (id: number, data: AssetStrategyCategoryUpdate) => {
    return apiClient.put<ApiResponse<Asset>>(`/assets/${id}/strategy-category`, data)
  },

  // 获取资产市场数据
  getMarketData: (code: string, type: AssetType) => {
    return apiClient.get<ApiResponse<MarketData>>(`/assets/${code}/market-data`, {
      params: { asset_type: type }
    })
  },

  // 强制刷新单个资产的市场数据
  refreshAsset: (id: number) => {
    return apiClient.post<ApiResponse<Asset>>(`/assets/${id}/refresh`)
  },

  // 批量刷新所有资产的市场数据
  batchRefreshAssets: () => {
    return apiClient.post<ApiResponse<{
      total_count: number
      success_count: number
      failed_count: number
      failed_assets: Array<{ code: string; name: string }>
    }>>('/assets/batch-refresh')
  },

  // 手动设置资产当前价格
  setCurrentPrice: (id: number, data: ManualPriceUpdate) => {
    return apiClient.put<ApiResponse<Asset>>(`/assets/${id}/current-price`, data)
  }
}
