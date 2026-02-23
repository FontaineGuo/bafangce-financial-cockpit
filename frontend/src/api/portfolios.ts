import apiClient from './index'
import type { Portfolio, PortfolioCreate, PortfolioUpdate, ApiResponse } from '@/types'

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
  }
}
