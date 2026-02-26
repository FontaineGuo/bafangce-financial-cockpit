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
      width="1000px"
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

        <!-- 资产操作 -->
        <div class="detail-section">
          <div class="section-header">
            <h4>组合资产 ({{ currentPortfolio.assets?.length || 0 }})</h4>
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="handleShowAddAssetDialog">添加资产</el-button>
              <el-button type="primary" size="small" @click="handleShowBatchAddAssetDialog">批量添加</el-button>
            </div>
          </div>

          <el-table :data="currentPortfolio.assets" stripe v-if="currentPortfolio.assets && currentPortfolio.assets.length > 0">
            <el-table-column prop="asset_code" label="资产代码" width="120" />
            <el-table-column prop="asset_name" label="资产名称" width="150" />
            <el-table-column prop="target_weight" label="目标权重(%)" width="120" />
            <el-table-column prop="current_weight" label="当前权重(%)" width="120" />
            <el-table-column prop="allocation_amount" label="分配金额" width="150">
              <template #default="{ row }">
                ¥{{ formatNumber(row.allocation_amount) }}
              </template>
            </el-table-column>
            <el-table-column label="盈亏" width="120">
              <template #default="{ row }">
                <span v-if="row.asset_profit !== undefined" :class="{ positive: row.asset_profit > 0, negative: row.asset_profit < 0 }">
                  ¥{{ formatNumber(row.asset_profit) }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="收益率" width="100">
              <template #default="{ row }">
                <span v-if="row.asset_profit_percent !== undefined" :class="{ positive: row.asset_profit_percent > 0, negative: row.asset_profit_percent < 0 }">
                  {{ row.asset_profit_percent?.toFixed(2) || 0 }}%
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="策略分类" width="120">
              <template #default="{ row }">
                <span>{{ formatStrategyCategoryName(row.strategy_category || 'OTHER') }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="handleRemoveAsset(row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-else description="暂无资产，请点击右上角添加" />
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
      </div>
    </el-dialog>

    <!-- 添加资产对话框 -->
    <el-dialog
      v-model="showAddAssetDialog"
      title="添加资产到组合"
      width="600px"
    >
      <el-form :model="assetForm" :rules="assetRules" ref="assetFormRef" label-width="120px">
        <el-form-item label="选择资产" prop="asset_id">
          <el-select
            v-model="assetForm.asset_id"
            placeholder="请选择要添加的资产"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="asset in availableAssets"
              :key="asset.id"
              :label="`${asset.code} - ${asset.name}`"
              :value="asset.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="目标权重(%)" prop="target_weight">
          <el-input-number
            v-model="assetForm.target_weight"
            :min="0"
            :max="100"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeAddAssetDialog">取消</el-button>
        <el-button type="primary" @click="handleAddAsset" :loading="loading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量添加资产对话框 -->
    <el-dialog
      v-model="showBatchAddAssetDialog"
      title="批量添加资产到组合"
      width="800px"
    >
      <div class="batch-add-header">
        <el-alert
          title="注意：每项资产只能被一个组合持有"
          type="warning"
          :closable="false"
          show-icon
        />
      </div>
      <el-transfer
        v-model="batchSelectedAssets"
        :data="availableAssetsForTransfer"
        :titles="['可用资产', '已选择']"
        filterable
        filter-placeholder="搜索资产"
      />
      <el-form :model="batchForm" :rules="batchRules" ref="batchFormRef" label-width="120px" style="margin-top: 20px">
        <el-form-item label="默认权重(%)" prop="default_weight">
          <el-input-number
            v-model="batchForm.default_weight"
            :min="0"
            :max="100"
            :precision="2"
            style="width: 100%"
          />
          <div class="form-tip">所有选中资产将使用相同的目标权重，添加后可单独调整</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeBatchAddAssetDialog">取消</el-button>
        <el-button type="primary" @click="handleBatchAddAssets" :loading="loading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePortfoliosStore } from '@/store/portfolios'
import { useAssetsStore } from '@/store/assets'
import { STRATEGY_CATEGORY_NAMES } from '@/utils/constants'
import type { Portfolio, PortfolioCreate, PortfolioUpdate, PortfolioAssetCreate } from '@/types'

const portfoliosStore = usePortfoliosStore()
const assetsStore = useAssetsStore()

const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showAddAssetDialog = ref(false)
const showBatchAddAssetDialog = ref(false)
const editingPortfolio = ref<Portfolio | null>(null)
const currentPortfolio = ref<Portfolio | null>(null)
const formRef = ref()
const assetFormRef = ref()
const batchFormRef = ref()
const loading = computed(() => portfoliosStore.loading)
const assetsLoading = computed(() => assetsStore.loading)

const portfolios = computed(() => portfoliosStore.portfolios)
const assets = computed(() => assetsStore.assets)

const form = reactive({
  name: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入组合名称', trigger: 'blur' }]
}

const assetForm = reactive({
  asset_id: undefined as number | undefined,
  target_weight: 0
})

const assetRules = {
  asset_id: [{ required: true, message: '请选择资产', trigger: 'change' }],
  target_weight: [
    { required: true, message: '请输入目标权重', trigger: 'blur' },
    { type: 'number', min: 0, max: 100, message: '权重必须在0-100之间', trigger: 'blur' }
  ]
}

const batchForm = reactive({
  default_weight: 0
})

const batchRules = {
  default_weight: [
    { required: true, message: '请输入默认权重', trigger: 'blur' },
    { type: 'number', min: 0, max: 100, message: '权重必须在0-100之间', trigger: 'blur' }
  ]
}

const batchSelectedAssets = ref<number[]>([])

// 可用资产：未在当前组合中的资产
const availableAssets = computed(() => {
  if (!currentPortfolio.value) return assets.value

  const portfolioAssetIds = new Set(currentPortfolio.value.assets.map(a => a.asset_id))
  return assets.value.filter(a => !portfolioAssetIds.has(a.id))
})

// 批量添加用的资产列表
const availableAssetsForTransfer = computed(() => {
  return availableAssets.value.map(asset => ({
    key: asset.id,
    label: `${asset.code} - ${asset.name}`,
    disabled: false
  }))
})

const strategyDistribution = ref<any[]>([])

function resetForm() {
  form.name = ''
  form.description = ''
}

function resetAssetForm() {
  assetForm.asset_id = undefined
  assetForm.target_weight = 0
}

function resetBatchForm() {
  batchForm.default_weight = 0
  batchSelectedAssets.value = []
}

function closeDialog() {
  showCreateDialog.value = false
  editingPortfolio.value = null
  resetForm()
}

function closeAddAssetDialog() {
  showAddAssetDialog.value = false
  resetAssetForm()
}

function closeBatchAddAssetDialog() {
  showBatchAddAssetDialog.value = false
  resetBatchForm()
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

function handleShowAddAssetDialog() {
  showAddAssetDialog.value = true
}

async function handleAddAsset() {
  if (!assetFormRef.value || !currentPortfolio.value) return

  await assetFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      const assetData: PortfolioAssetCreate = {
        asset_id: assetForm.asset_id!,
        target_weight: assetForm.target_weight
      }

      const result = await portfoliosStore.addAssetToPortfolio(currentPortfolio.value!.id, assetData)
      if (result.success) {
        ElMessage.success('添加成功')
        closeAddAssetDialog()
        // 刷新当前组合
        await handleViewPortfolio(currentPortfolio.value!)
      } else {
        ElMessage.error(result.error || '添加失败')
      }
    }
  })
}

function handleShowBatchAddAssetDialog() {
  showBatchAddAssetDialog.value = true
}

async function handleBatchAddAssets() {
  if (!batchFormRef.value || !currentPortfolio.value) return

  await batchFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      if (batchSelectedAssets.value.length === 0) {
        ElMessage.warning('请选择至少一个资产')
        return
      }

      const assetList: PortfolioAssetCreate[] = batchSelectedAssets.value.map(assetId => ({
        asset_id: assetId,
        target_weight: batchForm.default_weight
      }))

      const result = await portfoliosStore.batchAddAssetsToPortfolio(currentPortfolio.value!.id, assetList)
      if (result.success) {
        const { added_count, conflict_count, conflicts } = result.data!
        if (added_count > 0) {
          ElMessage.success(`成功添加 ${added_count} 项资产`)
        }
        if (conflict_count > 0) {
          ElMessage.warning(`${conflict_count} 项资产添加失败（已存在于其他组合）`)
          // 显示冲突详情
          console.log('Conflicts:', conflicts)
        }
        closeBatchAddAssetDialog()
        // 刷新当前组合
        await handleViewPortfolio(currentPortfolio.value!)
      } else {
        ElMessage.error(result.error || '批量添加失败')
      }
    }
  })
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

onMounted(async () => {
  await portfoliosStore.fetchPortfolios()
  await assetsStore.fetchAssets()
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h4 {
  color: #303133;
  border-left: 4px solid #409eff;
  padding-left: 10px;
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: 8px;
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

.batch-add-header {
  margin-bottom: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
