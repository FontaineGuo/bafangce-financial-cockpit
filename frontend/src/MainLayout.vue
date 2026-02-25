<template>
  <div class="main-layout">
    <el-container>
      <!-- 顶部头部 -->
      <el-header class="header">
        <div class="header-content">
          <h1 class="app-title">八方策金融座舱</h1>
          <el-button @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>

      <el-container>
        <!-- 侧边栏 -->
        <el-aside class="sidebar">
          <el-menu
            :default-active="activeTab"
            @select="handleSelectTab"
            class="sidebar-menu"
          >
            <el-menu-item index="dashboard">
              <el-icon><HomeFilled /></el-icon>
              <span>仪表盘</span>
            </el-menu-item>
            <el-menu-item index="assets">
              <el-icon><Wallet /></el-icon>
              <span>资产管理</span>
            </el-menu-item>
            <el-menu-item index="portfolios">
              <el-icon><DataLine /></el-icon>
              <span>投资组合</span>
            </el-menu-item>
            <el-menu-item index="strategies">
              <el-icon><TrendCharts /></el-icon>
              <span>策略管理</span>
            </el-menu-item>
            <el-menu-item index="ai-advisor">
              <el-icon><MagicStick /></el-icon>
              <span>AI建议</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 内容区域 -->
        <el-main class="main-content">
          <DashboardContent v-if="activeTab === 'dashboard'" />
          <AssetsContent v-if="activeTab === 'assets'" />
          <PortfoliosContent v-if="activeTab === 'portfolios'" />
          <StrategiesContent v-if="activeTab === 'strategies'" />
          <AIAdvisorContent v-if="activeTab === 'ai-advisor'" />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { HomeFilled, Wallet, DataLine, TrendCharts, MagicStick } from '@element-plus/icons-vue'
import { useUserStore } from './store/user'
import DashboardContent from './contents/DashboardContent.vue'
import AssetsContent from './contents/AssetsContent.vue'
import PortfoliosContent from './contents/PortfoliosContent.vue'
import StrategiesContent from './contents/StrategiesContent.vue'
import AIAdvisorContent from './contents/AIAdvisorContent.vue'

const router = useRouter()
const userStore = useUserStore()
const activeTab = ref('dashboard')

function handleSelectTab(index: string) {
  activeTab.value = index
}

function handleLogout() {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #545c64;
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.app-title {
  margin: 0;
  font-size: 20px;
}

.sidebar {
  width: 220px;
  background: #545c64;
  height: calc(100vh - 60px);
  overflow-y: auto;
  padding-top: 20px;
}

.sidebar-menu {
  border: none;
}

.main-content {
  background: #f5f5f5;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}

:deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 0 10px;
  border-radius: 8px;
  transition: all 0.3s;
}

:deep(.el-menu-item:hover) {
  background: rgba(64, 158, 255, 0.1);
}

:deep(.el-menu-item.is-active) {
  background: #409eff;
  color: #fff;
}
</style>
