import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Asset, AssetCreate, AssetUpdate, AssetStrategyCategoryUpdate } from '@/types'
import { assetsApi } from '@/api/assets'

export const useAssetsStore = defineStore('assets', () => {
  const assets = ref<Asset[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAssets() {
    loading.value = true
    error.value = null
    try {
      const response = await assetsApi.getAssets()
      assets.value = response.data.data || []
    } catch (err) {
      error.value = '获取资产列表失败'
      console.error('Fetch assets failed:', err)
    } finally {
      loading.value = false
    }
  }

  async function addAsset(data: AssetCreate) {
    try {
      const response = await assetsApi.createAsset(data)
      assets.value.push(response.data.data!)
      return { success: true }
    } catch (err: any) {
      console.error('Add asset failed:', err)
      // 提取backend返回的错误信息
      const errorMessage = err.response?.data?.detail || '添加资产失败'
      return { success: false, error: errorMessage }
    }
  }

  async function updateAsset(id: number, data: AssetUpdate) {
    try {
      const response = await assetsApi.updateAsset(id, data)
      const index = assets.value.findIndex(a => a.id === id)
      if (index !== -1) {
        assets.value[index] = response.data.data!
      }
      return { success: true }
    } catch (err: any) {
      console.error('Update asset failed:', err)
      // 提取backend返回的错误信息
      const errorMessage = err.response?.data?.detail || '更新资产失败'
      return { success: false, error: errorMessage }
    }
  }

  async function deleteAsset(id: number) {
    try {
      await assetsApi.deleteAsset(id)
      assets.value = assets.value.filter(a => a.id !== id)
      return { success: true }
    } catch (err: any) {
      console.error('Delete asset failed:', err)
      // 提取backend返回的错误信息
      const errorMessage = err.response?.data?.detail || '删除资产失败'
      return { success: false, error: errorMessage }
    }
  }

  async function updateAssetStrategyCategory(id: number, data: AssetStrategyCategoryUpdate) {
    try {
      const response = await assetsApi.updateAssetStrategyCategory(id, data)
      const index = assets.value.findIndex(a => a.id === id)
      if (index !== -1) {
        assets.value[index] = response.data.data!
      }
      return { success: true }
    } catch (err: any) {
      console.error('Update asset strategy category failed:', err)
      const errorMessage = err.response?.data?.detail || '更新策略分类失败'
      return { success: false, error: errorMessage }
    }
  }

  async function refreshAsset(id: number) {
    try {
      const response = await assetsApi.refreshAsset(id)
      const index = assets.value.findIndex(a => a.id === id)
      if (index !== -1) {
        assets.value[index] = response.data.data!
      }
      return { success: true }
    } catch (err: any) {
      console.error('Refresh asset failed:', err)
      const errorMessage = err.response?.data?.detail || '刷新资产失败'
      return { success: false, error: errorMessage }
    }
  }

  async function batchRefreshAssets() {
    loading.value = true
    error.value = null
    try {
      const response = await assetsApi.batchRefreshAssets()
      // 重新获取所有资产
      await fetchAssets()
      return {
        success: true,
        data: response.data.data
      }
    } catch (err: any) {
      console.error('Batch refresh assets failed:', err)
      const errorMessage = err.response?.data?.detail || '批量刷新资产失败'
      error.value = errorMessage
      loading.value = false
      return { success: false, error: errorMessage }
    }
  }

  async function refreshAssets() {
    await fetchAssets()
  }

  return {
    assets,
    loading,
    error,
    fetchAssets,
    addAsset,
    updateAsset,
    deleteAsset,
    updateAssetStrategyCategory,
    refreshAsset,
    batchRefreshAssets,
    refreshAssets
  }
})
