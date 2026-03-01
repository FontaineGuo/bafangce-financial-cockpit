<template>
  <div class="dashboard-content">
    <h2>仪表盘</h2>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-value">{{ totalAssets }}</div>
          <div class="stat-label">总资产</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-value positive">{{ totalProfit }}</div>
          <div class="stat-label">总收益</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-value">{{ assetCount }}</div>
          <div class="stat-label">持仓数量</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>资产分布</span>
          </template>
          <div class="chart-placeholder">
            资产分布图表（待实现）
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { useAssetsStore } from '@/store/assets'

const userStore = useUserStore()
const assetsStore = useAssetsStore()

const totalAssets = computed(() => {
  return assetsStore.assets
    .reduce((sum, asset) => sum + (asset.market_value || 0), 0)
    .toFixed(2)
})

const totalProfit = computed(() => {
  const profit = assetsStore.assets
    .reduce((sum, asset) => sum + (asset.profit || 0), 0)
  return (profit >= 0 ? '+' : '') + profit.toFixed(2)
})

const assetCount = computed(() => assetsStore.assets.length)

onMounted(async () => {
  await assetsStore.fetchAssets()
})
</script>

<style scoped>
.dashboard-content {
  padding: 20px;
}

h2 {
  margin: 0 0 20px 0;
  color: #303133;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 10px;
}

.stat-value.positive {
  color: #67c23a;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}
</style>
