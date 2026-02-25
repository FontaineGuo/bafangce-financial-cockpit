import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Portfolio, PortfolioCreate, PortfolioUpdate, PortfolioAssetBase, PortfolioAssetCreate, BatchAddAssetsResult, PortfolioAssetStrategyCategoryUpdate } from '@/types'
import { portfoliosApi } from '@/api/portfolios'

export const usePortfoliosStore = defineStore('portfolios', () => {
  const portfolios = ref<Portfolio[]>([])
  const currentPortfolio = ref<Portfolio | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchPortfolios() {
    loading.value = true
    error.value = null
    try {
      const response = await portfoliosApi.getPortfolios()
      portfolios.value = response.data.data || []
    } catch (err) {
      error.value = '获取投资组合列表失败'
      console.error('Fetch portfolios failed:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchPortfolio(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await portfoliosApi.getPortfolio(id)
      currentPortfolio.value = response.data.data || null
      return currentPortfolio.value
    } catch (err) {
      error.value = '获取投资组合失败'
      console.error('Fetch portfolio failed:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function createPortfolio(data: PortfolioCreate) {
    try {
      const response = await portfoliosApi.createPortfolio(data)
      portfolios.value.push(response.data.data!)
      return { success: true }
    } catch (err: any) {
      console.error('Create portfolio failed:', err)
      const errorMessage = err.response?.data?.detail || '创建投资组合失败'
      return { success: false, error: errorMessage }
    }
  }

  async function updatePortfolio(id: number, data: PortfolioUpdate) {
    try {
      const response = await portfoliosApi.updatePortfolio(id, data)
      const index = portfolios.value.findIndex(p => p.id === id)
      if (index !== -1) {
        portfolios.value[index] = response.data.data!
      }
      if (currentPortfolio.value?.id === id) {
        currentPortfolio.value = response.data.data!
      }
      return { success: true }
    } catch (err: any) {
      console.error('Update portfolio failed:', err)
      const errorMessage = err.response?.data?.detail || '更新投资组合失败'
      return { success: false, error: errorMessage }
    }
  }

  async function deletePortfolio(id: number) {
    try {
      await portfoliosApi.deletePortfolio(id)
      portfolios.value = portfolios.value.filter(p => p.id !== id)
      if (currentPortfolio.value?.id === id) {
        currentPortfolio.value = null
      }
      return { success: true }
    } catch (err: any) {
      console.error('Delete portfolio failed:', err)
      const errorMessage = err.response?.data?.detail || '删除投资组合失败'
      return { success: false, error: errorMessage }
    }
  }

  async function addAssetToPortfolio(portfolioId: number, assetData: PortfolioAssetCreate) {
    try {
      const response = await portfoliosApi.addAssetToPortfolio(portfolioId, assetData)
      const index = portfolios.value.findIndex(p => p.id === portfolioId)
      if (index !== -1) {
        portfolios.value[index] = response.data.data!
      }
      if (currentPortfolio.value?.id === portfolioId) {
        currentPortfolio.value = response.data.data!
      }
      return { success: true }
    } catch (err: any) {
      console.error('Add asset to portfolio failed:', err)
      const errorMessage = err.response?.data?.detail || '添加资产失败'
      return { success: false, error: errorMessage }
    }
  }

  async function batchAddAssetsToPortfolio(portfolioId: number, assetList: PortfolioAssetCreate[]) {
    try {
      const response = await portfoliosApi.batchAddAssetsToPortfolio(portfolioId, assetList)
      const result = response.data.data as BatchAddAssetsResult
      // 刷新当前投资组合数据
      if (currentPortfolio.value?.id === portfolioId) {
        await fetchPortfolio(portfolioId)
      }
      return { success: true, data: result }
    } catch (err: any) {
      console.error('Batch add assets to portfolio failed:', err)
      const errorMessage = err.response?.data?.detail || '批量添加资产失败'
      return { success: false, error: errorMessage }
    }
  }

  async function removeAssetFromPortfolio(portfolioId: number, assetId: number) {
    try {
      await portfoliosApi.removeAssetFromPortfolio(portfolioId, assetId)
      // 刷新当前投资组合数据
      if (currentPortfolio.value?.id === portfolioId) {
        await fetchPortfolio(portfolioId)
      }
      return { success: true }
    } catch (err: any) {
      console.error('Remove asset from portfolio failed:', err)
      const errorMessage = err.response?.data?.detail || '移除资产失败'
      return { success: false, error: errorMessage }
    }
  }

  async function updateAssetStrategyCategory(portfolioId: number, assetId: number, strategyData: PortfolioAssetStrategyCategoryUpdate) {
    try {
      const response = await portfoliosApi.updateAssetStrategyCategory(portfolioId, assetId, strategyData)
      // 刷新当前投资组合数据
      if (currentPortfolio.value?.id === portfolioId) {
        currentPortfolio.value = response.data.data!
      }
      return { success: true }
    } catch (err: any) {
      console.error('Update asset strategy category failed:', err)
      const errorMessage = err.response?.data?.detail || '更新策略分类失败'
      return { success: false, error: errorMessage }
    }
  }

  async function fetchPortfolioStrategyDistribution(portfolioId: number) {
    try {
      const response = await portfoliosApi.getPortfolioStrategyDistribution(portfolioId)
      return response.data.data || []
    } catch (err) {
      console.error('Fetch portfolio strategy distribution failed:', err)
      return []
    }
  }

  function selectPortfolio(portfolio: Portfolio) {
    currentPortfolio.value = portfolio
  }

  function clearCurrentPortfolio() {
    currentPortfolio.value = null
  }

  async function refreshPortfolios() {
    await fetchPortfolios()
  }

  return {
    portfolios,
    currentPortfolio,
    loading,
    error,
    fetchPortfolios,
    fetchPortfolio,
    createPortfolio,
    updatePortfolio,
    deletePortfolio,
    addAssetToPortfolio,
    batchAddAssetsToPortfolio,
    removeAssetFromPortfolio,
    updateAssetStrategyCategory,
    fetchPortfolioStrategyDistribution,
    selectPortfolio,
    clearCurrentPortfolio,
    refreshPortfolios
  }
})
