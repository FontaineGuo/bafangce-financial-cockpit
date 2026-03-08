import apiClient from './index'
import type { StrategyGroup, StrategyGroupCreate, StrategyGroupUpdate, ApiResponse } from '@/types'

export const strategyGroupsApi = {
  // 获取策略组列表
  getStrategyGroups: () => {
    return apiClient.get<ApiResponse<StrategyGroup[]>>('/strategy-groups')
  },

  // 获取单个策略组
  getStrategyGroup: (id: number) => {
    return apiClient.get<ApiResponse<StrategyGroup>>(`/strategy-groups/${id}`)
  },

  // 创建策略组
  createStrategyGroup: (data: StrategyGroupCreate) => {
    return apiClient.post<ApiResponse<StrategyGroup>>('/strategy-groups', data)
  },

  // 更新策略组
  updateStrategyGroup: (id: number, data: StrategyGroupUpdate) => {
    return apiClient.put<ApiResponse<StrategyGroup>>(`/strategy-groups/${id}`, data)
  },

  // 删除策略组
  deleteStrategyGroup: (id: number) => {
    return apiClient.delete<ApiResponse<null>>(`/strategy-groups/${id}`)
  }
}
