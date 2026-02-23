import apiClient from './index'
import type { Strategy, StrategyCreate, StrategyUpdate, ApiResponse } from '@/types'

export const strategiesApi = {
  // 获取策略列表
  getStrategies: () => {
    return apiClient.get<ApiResponse<Strategy[]>>('/strategies')
  },

  // 获取单个策略
  getStrategy: (id: number) => {
    return apiClient.get<ApiResponse<Strategy>>(`/strategies/${id}`)
  },

  // 创建策略
  createStrategy: (data: StrategyCreate) => {
    return apiClient.post<ApiResponse<Strategy>>('/strategies', data)
  },

  // 更新策略
  updateStrategy: (id: number, data: StrategyUpdate) => {
    return apiClient.put<ApiResponse<Strategy>>(`/strategies/${id}`, data)
  },

  // 删除策略
  deleteStrategy: (id: number) => {
    return apiClient.delete<ApiResponse<null>>(`/strategies/${id}`)
  }
}
