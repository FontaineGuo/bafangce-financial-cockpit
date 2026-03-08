import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  AssetCategoryMapping,
  AssetCategoryMappingCreate,
  AssetCategoryMappingUpdate,
  StrategyDistribution
} from '@/types'
import { assetCategoriesApi } from '@/api/assetCategories'

export const useAssetCategoriesStore = defineStore('assetCategories', () => {
  const mappings = ref<AssetCategoryMapping[]>([])
  const distribution = ref<StrategyDistribution[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchMappings() {
    loading.value = true
    error.value = null
    try {
      const response = await assetCategoriesApi.getMappings()
      mappings.value = response.data.data || []
    } catch (err) {
      error.value = '获取分类映射失败'
      console.error('Fetch mappings failed:', err)
    } finally {
      loading.value = false
    }
  }

  async function getMapping(assetCode: string) {
    try {
      const response = await assetCategoriesApi.getMapping(assetCode)
      return response.data.data
    } catch (err) {
      console.error('Get mapping failed:', err)
      return null
    }
  }

  async function createMapping(data: AssetCategoryMappingCreate) {
    try {
      const response = await assetCategoriesApi.createMapping(data)
      mappings.value.push(response.data.data!)
      return true
    } catch (err) {
      console.error('Create mapping failed:', err)
      return false
    }
  }

  async function updateMapping(id: number, data: AssetCategoryMappingUpdate) {
    try {
      const response = await assetCategoriesApi.updateMapping(id, data)
      const index = mappings.value.findIndex(m => m.id === id)
      if (index !== -1) {
        mappings.value[index] = response.data.data!
      }
      return true
    } catch (err) {
      console.error('Update mapping failed:', err)
      return false
    }
  }

  async function deleteMapping(id: number) {
    try {
      await assetCategoriesApi.deleteMapping(id)
      mappings.value = mappings.value.filter(m => m.id !== id)
      return true
    } catch (err) {
      console.error('Delete mapping failed:', err)
      return false
    }
  }

  async function fetchPortfolioDistribution(portfolioId: number) {
    loading.value = true
    try {
      const response = await assetCategoriesApi.getPortfolioDistribution(portfolioId)
      distribution.value = response.data.data?.distribution || []
    } catch (err) {
      console.error('Fetch distribution failed:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    mappings,
    distribution,
    loading,
    error,
    fetchMappings,
    getMapping,
    createMapping,
    updateMapping,
    deleteMapping,
    fetchPortfolioDistribution
  }
})
