<template>
  <div class="portfolios">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>投资组合</span>
          <el-button type="primary" @click="showCreateDialog = true">创建组合</el-button>
        </div>
      </template>

      <!-- 投资组合列表 -->
      <el-empty v-if="!loading && portfolios.length === 0" description="暂无投资组合，点击右上角创建" />

      <div v-else class="portfolio-list">
        <el-card
          v-for="portfolio in portfolios"
          :key="portfolio.id"
          class="portfolio-card"
          shadow="hover"
          @click="handleViewPortfolio(portfolio)"
        >
          <template #header>
            <div class="portfolio-header">
              <span class="portfolio-name">{{ portfolio.name }}</span>
              <div class="portfolio-actions">
                <el-button size="small" @click.stop="handleEditPortfolio(portfolio)">编辑</el-button>
                <el-button size="small" type="danger" @click.stop="handleDeletePortfolio(portfolio)">删除</el-button>
              </div>
            </div>
          </template>

          <div class="portfolio-stats">
            <div class="stat-item">
              <span class="stat-label">总市值</span>
              <span class="stat-value">¥{{ formatNumber(portfolio.total_value) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总成本</span>
              <span class="stat-value">¥{{ formatNumber(portfolio.total_cost) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总盈亏</span>
              <span
                class="stat-value"
                :class="{ positive: portfolio.total_profit > 0, negative: portfolio.total_profit < 0 }"
              >
                ¥{{ formatNumber(portfolio.total_profit) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">收益率</span>
              <span
                class="stat-value"
                :class="{ positive: portfolio.total_profit_percent > 0, negative: portfolio.total_profit_percent < 0 }"
              >
                {{ portfolio.total_profit_percent?.toFixed(2) || 0 }}%
              </span>
            </div>
          </div>

          <div class="portfolio-description" v-if="portfolio.description">
            {{ portfolio.description }}
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 创建/编辑组合对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingPortfolio ? '编辑组合' : '创建组合'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="组合名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入组合名称" />
        </el-form-item>
        <el-form-item label="组合描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入组合描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 投资组合详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`${currentPortfolio?.name} - 详情`"
      width="900px"
    >
      <div v-if="currentPortfolio" class="portfolio-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="组合名称">{{ currentPortfolio.name }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(currentPortfolio.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="总市值">¥{{ formatNumber(currentPortfolio.total_value) }}</el-descriptions-item>
            <el-descriptions-item label="总成本">¥{{ formatNumber(currentPortfolio.total_cost) }}</el-descriptions-item>
            <el-descriptions-item label="总盈亏">
              <span :class="{ positive: currentPortfolio.total_profit > 0, negative: currentPortfolio.total_profit < 0 }">
                ¥{{ formatNumber(currentPortfolio.total_profit) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="收益率">
              <span :class="{ positive: currentPortfolio.total_profit_percent > 0, negative: currentPortfolio.total_profit_percent < 0 }">
                {{ currentPortfolio.total_profit_percent?.toFixed(2) || 0 }}%
              </span>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 策略分类分布 -->
        <div class="detail-section" v-if="strategyDistribution.length > 0">
          <h4>策略分类分布</h4>
          <div class="strategy-distribution">
            <div
              v-for="item in strategyDistribution"
              :key="item.category"
              class="distribution-item"
            >
              <div class="distribution-header">
                <span class="category-name">{{ formatStrategyCategoryName(item.category) }}</span>
                <span class="category-percentage">{{ item.percentage.toFixed(1) }}%</span>
              </div>
              <div class="distribution-body">
                <div class="distribution-stats">
                  <span class="stat">资产数: {{ item.count }}</span>
                  <span class="stat">市值: ¥{{ formatNumber(item.total_value) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 资产列表 -->
        <div class="detail-section" v-if="currentPortfolio.assets && currentPortfolio.assets.length > 0">
          <h4>组合资产 ({{ currentPortfolio.assets.length }})</h4>
          <el-table :data="currentPortfolio.assets" stripe>
            <el-table-column prop="asset_id" label="资产ID" width="80" />
            <el-table-column prop="current_weight" label="当前权重(%)" width="120" />
            <el-table-column prop="allocation_amount" label="分配金额" width="150">
              <template #default="{ row }">
                ¥{{ formatNumber(row.allocation_amount) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="handleRemoveAsset(row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePortfoliosStore } from '@/store/portfolios'
import { useAssetsStore } from '@/store/assets'
import { ASSET_TYPE_NAMES, STRATEGY_CATEGORY_NAMES } from '@/utils/constants'
import type { Portfolio, PortfolioCreate, PortfolioUpdate } from '@/types'

const portfoliosStore = usePortfoliosStore()
const assetsStore = useAssetsStore()

const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const editingPortfolio = ref<Portfolio | null>(null)
const currentPortfolio = ref<Portfolio | null>(null)
const formRef = ref()
const loading = computed(() => portfoliosStore.loading)

const portfolios = computed(() => portfoliosStore.portfolios)

const form = reactive({
  name: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入组合名称', trigger: 'blur' }]
}

const strategyDistribution = ref<any[]>([])

function resetForm() {
  form.name = ''
  form.description = ''
}

function closeDialog() {
  showCreateDialog.value = false
  editingPortfolio.value = null
  resetForm()
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      if (editingPortfolio.value) {
        const result = await portfoliosStore.updatePortfolio(editingPortfolio.value.id, form)
        if (result.success) {
          ElMessage.success('更新成功')
          closeDialog()
        } else {
          ElMessage.error(result.error || '更新失败')
        }
      } else {
        const result = await portfoliosStore.createPortfolio(form)
        if (result.success) {
          ElMessage.success('创建成功')
          closeDialog()
        } else {
          ElMessage.error(result.error || '创建失败')
        }
      }
    }
  })
}

function handleEditPortfolio(portfolio: Portfolio) {
  editingPortfolio.value = portfolio
  form.name = portfolio.name
  form.description = portfolio.description || ''
  showCreateDialog.value = true
}

async function handleDeletePortfolio(portfolio: Portfolio) {
  try {
    await ElMessageBox.confirm('确定要删除这个投资组合吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const result = await portfoliosStore.deletePortfolio(portfolio.id)
    if (result.success) {
      ElMessage.success('删除成功')
    } else {
      ElMessage.error(result.error || '删除失败')
    }
  } catch (error) {
    // 用户取消删除
  }
}

async function handleViewPortfolio(portfolio: Portfolio) {
  currentPortfolio.value = await portfoliosStore.fetchPortfolio(portfolio.id)
  if (currentPortfolio.value) {
    strategyDistribution.value = await portfoliosStore.fetchPortfolioStrategyDistribution(portfolio.id)
    showDetailDialog.value = true
  }
}

async function handleRemoveAsset(row: any) {
  if (!currentPortfolio.value) return

  try {
    await ElMessageBox.confirm('确定要移除这个资产吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const result = await portfoliosStore.removeAssetFromPortfolio(currentPortfolio.value.id, row.asset_id)
    if (result.success) {
      ElMessage.success('移除成功')
      // 刷新当前组合
      if (currentPortfolio.value) {
        await handleViewPortfolio(currentPortfolio.value)
      }
    } else {
      ElMessage.error(result.error || '移除失败')
    }
  } catch (error) {
    // 用户取消移除
  }
}

function formatNumber(num: number | undefined): string {
  if (num === undefined) return '0'
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString('zh-CN')
}

function formatStrategyCategoryName(category: string): string {
  return STRATEGY_CATEGORY_NAMES[category as keyof typeof STRATEGY_CATEGORY_NAMES] || category
}

onMounted(() => {
  portfoliosStore.fetchPortfolios()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.portfolio-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.portfolio-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.portfolio-card:hover {
  transform: translateY(-4px);
}

.portfolio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.portfolio-name {
  font-weight: bold;
  font-size: 16px;
}

.portfolio-actions {
  display: flex;
  gap: 8px;
}

.portfolio-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin: 15px 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.stat-value.positive {
  color: #67c23a;
}

.stat-value.negative {
  color: #f56c6c;
}

.portfolio-description {
  margin-top: 15px;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.portfolio-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section h4 {
  margin-bottom: 15px;
  color: #303133;
  border-left: 4px solid #409eff;
  padding-left: 10px;
}

.strategy-distribution {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.distribution-item {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
}

.distribution-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.category-name {
  font-weight: bold;
  color: #303133;
}

.category-percentage {
  font-size: 14px;
  color: #409eff;
  font-weight: bold;
}

.distribution-stats {
  display: flex;
  gap: 20px;
  color: #606266;
  font-size: 13px;
}

.distribution-stats .stat {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
