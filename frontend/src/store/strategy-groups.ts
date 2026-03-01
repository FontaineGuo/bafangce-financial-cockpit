import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { StrategyGroup, StrategyGroupCreate, StrategyGroupUpdate } from '@/types'
import { strategyGroupsApi } from '@/api/strategy-groups'

export const useStrategyGroupsStore = defineStore('strategy-groups', () => {
  const strategyGroups = ref<StrategyGroup[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchStrategyGroups() {
    loading.value = true
    error.value = null
    try {
      const response = await strategyGroupsApi.getStrategyGroups()
      strategyGroups.value = response.data.data || []
    } catch (err) {
      error.value = '获取策略组列表失败'
      console.error('Fetch strategy groups failed:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchStrategyGroup(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await strategyGroupsApi.getStrategyGroup(id)
      return response.data.data || null
    } catch (err) {
      error.value = '获取策略组失败'
      console.error('Fetch strategy group failed:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function createStrategyGroup(data: StrategyGroupCreate) {
    try {
      const response = await strategyGroupsApi.createStrategyGroup(data)
      strategyGroups.value.push(response.data.data!)
      return { success: true }
    } catch (err: any) {
      console.error('Create strategy group failed:', err)
      const errorMessage = err.response?.data?.detail || '创建策略组失败'
      return { success: false, error: errorMessage }
    }
  }

  async function updateStrategyGroup(id: number, data: StrategyGroupUpdate) {
    try {
      const response = await strategyGroupsApi.updateStrategyGroup(id, data)
      const index = strategyGroups.value.findIndex(sg => sg.id === id)
      if (index !== -1) {
        strategyGroups.value[index] = response.data.data!
      }
      return { success: true }
    } catch (err: any) {
      console.error('Update strategy group failed:', err)
      const errorMessage = err.response?.data?.detail || '更新策略组失败'
      return { success: false, error: errorMessage }
    }
  }

  async function deleteStrategyGroup(id: number) {
    try {
      await strategyGroupsApi.deleteStrategyGroup(id)
      strategyGroups.value = strategyGroups.value.filter(sg => sg.id !== id)
      return { success: true }
    } catch (err: any) {
      console.error('Delete strategy group failed:', err)
      const errorMessage = err.response?.data?.detail || '删除策略组失败'
      return { success: false, error: errorMessage }
    }
  }

  async function refreshStrategyGroups() {
    await fetchStrategyGroups()
  }

  // 计算策略组的总百分比
  function getTotalPercentage(groupId: number): number {
    const group = strategyGroups.value.find(sg => sg.id === groupId)
    if (!group) return 0
    return group.category_allocations.reduce((sum, allocation) => sum + allocation.percentage, 0)
  }

  // 检查策略组是否有效（总百分比不超过100%）
  function isGroupValid(groupId: number): boolean {
    return getTotalPercentage(groupId) <= 100
  }

  return {
    strategyGroups,
    loading,
    error,
    fetchStrategyGroups,
    fetchStrategyGroup,
    createStrategyGroup,
    updateStrategyGroup,
    deleteStrategyGroup,
    refreshStrategyGroups,
    getTotalPercentage,
    isGroupValid
  }
})
