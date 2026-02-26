import apiClient from './index'
import type { Asset, AssetCreate, AssetUpdate, AssetStrategyCategoryUpdate, MarketData, AssetType, ApiResponse } from '@/types'

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
  }
}
