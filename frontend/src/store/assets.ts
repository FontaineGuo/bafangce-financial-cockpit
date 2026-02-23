import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Asset, AssetCreate, AssetUpdate } from '@/types'
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
      return true
    } catch (err) {
      console.error('Add asset failed:', err)
      return false
    }
  }

  async function updateAsset(id: number, data: AssetUpdate) {
    try {
      const response = await assetsApi.updateAsset(id, data)
      const index = assets.value.findIndex(a => a.id === id)
      if (index !== -1) {
        assets.value[index] = response.data.data!
      }
      return true
    } catch (err) {
      console.error('Update asset failed:', err)
      return false
    }
  }

  async function deleteAsset(id: number) {
    try {
      await assetsApi.deleteAsset(id)
      assets.value = assets.value.filter(a => a.id !== id)
      return true
    } catch (err) {
      console.error('Delete asset failed:', err)
      return false
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
    refreshAssets
  }
})
