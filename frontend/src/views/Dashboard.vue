<template>
  <div class="dashboard">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>八方策金融座舱</h1>
          <el-button @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>

      <el-container>
        <el-aside width="200px">
          <el-menu
            :default-active="$route.path"
            router
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <span>仪表盘</span>
            </el-menu-item>
            <el-menu-item index="/assets">
              <el-icon><Wallet /></el-icon>
              <span>资产管理</span>
            </el-menu-item>
            <el-menu-item index="/portfolios">
              <el-icon><DataLine /></el-icon>
              <span>投资组合</span>
            </el-menu-item>
            <el-menu-item index="/strategies">
              <el-icon><TrendCharts /></el-icon>
              <span>策略管理</span>
            </el-menu-item>
            <el-menu-item index="/ai-advisor">
              <el-icon><MagicStick /></el-icon>
              <span>AI建议</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main>
          <h2>仪表盘</h2>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-value">{{ totalAssets }}</div>
                <div class="stat-label">总资产</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-value positive">{{ totalProfit }}</div>
                <div class="stat-label">总收益</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-value">{{ assetCount }}</div>
                <div class="stat-label">持仓数量</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-value">{{ strategyCount }}</div>
                <div class="stat-label">启用策略</div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" style="margin-top: 20px">
            <el-col :span="12">
              <el-card>
                <template #header>
                  <span>资产分布</span>
                </template>
                <div class="chart-placeholder">
                  资产分布图表（待实现）
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>
                  <span>策略分布</span>
                </template>
                <div class="chart-placeholder">
                  策略分布图表（待实现）
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { HomeFilled, Wallet, DataLine, TrendCharts, MagicStick } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { useAssetsStore } from '@/store/assets'

const router = useRouter()
const userStore = useUserStore()
const assetsStore = useAssetsStore()

const strategyCount = ref(0)

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

function handleLogout() {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(async () => {
  await assetsStore.fetchAssets()
})
</script>

<style scoped>
.dashboard {
  height: 100vh;
}

.el-header {
  background-color: #545c64;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-content h1 {
  margin: 0;
  font-size: 20px;
}

.el-aside {
  background-color: #f5f5f5;
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
  color: #f56c6c !important;
}

.stat-value.negative {
  color: #67c23a !important;
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
