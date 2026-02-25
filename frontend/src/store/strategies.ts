import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Strategy, StrategyCreate, StrategyUpdate } from '@/types'
import { strategiesApi } from '@/api/strategies'

export const useStrategiesStore = defineStore('strategies', () => {
  const strategies = ref<Strategy[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchStrategies() {
    loading.value = true
    error.value = null
    try {
      const response = await strategiesApi.getStrategies()
      strategies.value = response.data.data || []
    } catch (err) {
      error.value = '获取策略列表失败'
      console.error('Fetch strategies failed:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchStrategy(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await strategiesApi.getStrategy(id)
      return response.data.data || null
    } catch (err) {
      error.value = '获取策略失败'
      console.error('Fetch strategy failed:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function createStrategy(data: StrategyCreate) {
    try {
      const response = await strategiesApi.createStrategy(data)
      strategies.value.push(response.data.data!)
      return { success: true }
    } catch (err: any) {
      console.error('Create strategy failed:', err)
      const errorMessage = err.response?.data?.detail || '创建策略失败'
      return { success: false, error: errorMessage }
    }
  }

  async function updateStrategy(id: number, data: StrategyUpdate) {
    try {
      const response = await strategiesApi.updateStrategy(id, data)
      const index = strategies.value.findIndex(s => s.id === id)
      if (index !== -1) {
        strategies.value[index] = response.data.data!
      }
      return { success: true }
    } catch (err: any) {
      console.error('Update strategy failed:', err)
      const errorMessage = err.response?.data?.detail || '更新策略失败'
      return { success: false, error: errorMessage }
    }
  }

  async function deleteStrategy(id: number) {
    try {
      await strategiesApi.deleteStrategy(id)
      strategies.value = strategies.value.filter(s => s.id !== id)
      return { success: true }
    } catch (err: any) {
      console.error('Delete strategy failed:', err)
      const errorMessage = err.response?.data?.detail || '删除策略失败'
      return { success: false, error: errorMessage }
    }
  }

  async function toggleStrategy(id: number, enabled: boolean) {
    try {
      const response = await strategiesApi.updateStrategy(id, { enabled })
      const index = strategies.value.findIndex(s => s.id === id)
      if (index !== -1) {
        strategies.value[index] = response.data.data!
      }
      return { success: true }
    } catch (err: any) {
      console.error('Toggle strategy failed:', err)
      const errorMessage = err.response?.data?.detail || '切换策略状态失败'
      return { success: false, error: errorMessage }
    }
  }

  async function refreshStrategies() {
    await fetchStrategies()
  }

  return {
    strategies,
    loading,
    error,
    fetchStrategies,
    fetchStrategy,
    createStrategy,
    updateStrategy,
    deleteStrategy,
    toggleStrategy,
    refreshStrategies
  }
})
