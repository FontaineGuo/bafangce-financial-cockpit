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
      destroy-on-close
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
      width="1300px"
      destroy-on-close
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

        <!-- 策略组应用 -->
        <div class="detail-section">
          <div class="section-header">
            <h4>策略组配置</h4>
          </div>
          <div class="strategy-group-selector">
            <el-select
              v-model="selectedStrategyGroupId"
              placeholder="选择策略组"
              clearable
              @change="handleStrategyGroupChange"
              style="width: 300px"
            >
              <el-option
                v-for="group in strategyGroups"
                :key="group.id"
                :label="group.name"
                :value="group.id"
              />
            </el-select>
            <el-button
              v-if="currentPortfolio.strategy_group_id"
              type="danger"
              size="small"
              @click="handleRemoveStrategyGroup"
            >
              移除策略组
            </el-button>
          </div>
        </div>

        <!-- 策略分布对比 -->
        <div class="detail-section" v-if="strategyComparison">
          <div class="section-header">
            <h4>策略分布对比</h4>
            <div v-if="strategyComparison.summary.categories_over_threshold > 0" class="warning-badge">
              <el-tag type="warning" size="small">
                ⚠️ {{ strategyComparison.summary.categories_over_threshold }} 个分类超出阈值
              </el-tag>
            </div>
          </div>
          <div class="strategy-comparison-table">
            <el-table :data="strategyComparison.current_distribution" stripe>
              <el-table-column prop="category" label="策略分类" width="150">
                <template #default="{ row }">
                  {{ formatStrategyCategoryName(row.category) }}
                </template>
              </el-table-column>
              <el-table-column prop="current_percentage" label="当前分布" width="120">
                <template #default="{ row }">
                  {{ row.current_percentage.toFixed(2) }}%
                </template>
              </el-table-column>
              <el-table-column prop="target_percentage" label="目标分布" width="120">
                <template #default="{ row }">
                  {{ row.target_percentage ? row.target_percentage.toFixed(2) + '%' : '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="deviation" label="偏离值" width="120">
                <template #default="{ row }">
                  <span
                    v-if="row.deviation !== null && row.deviation !== undefined"
                    :style="{
                      color: row.deviation > 0 ? '#f56c6c' : (row.deviation < 0 ? '#67c23a' : '#303133'),
                      fontWeight: '500'
                    }"
                  >
                    {{ row.deviation >= 0 ? '+' : '' }}{{ row.deviation.toFixed(2) }}%
                  </span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="150">
                <template #default="{ row }">
                  <el-tag
                    :type="getStatusTagType(row.status)"
                    size="small"
                  >
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="deviation_threshold" label="偏离阈值" width="120">
                <template #default="{ row }">
                  {{ row.deviation_threshold ? row.deviation_threshold + '%' : '-' }}
                </template>
              </el-table-column>
            </el-table>
          </div>
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

          <el-table :data="sortedAssets" stripe v-if="currentPortfolio.assets && currentPortfolio.assets.length > 0" @sort-change="handleAssetSortChange">
            <el-table-column prop="asset_code" label="资产代码" width="120" sortable="custom" />
            <el-table-column prop="asset_name" label="资产名称" width="150" sortable="custom" />
            <el-table-column prop="current_weight" label="当前权重(%)" width="120" sortable="custom">
              <template #default="{ row }">
                {{ (row.current_weight || 0).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column prop="asset_market_value" label="资产市值" width="150" sortable="custom">
              <template #default="{ row }">
                ¥{{ row.asset_market_value !== undefined && row.asset_market_value !== null ? Number(row.asset_market_value).toFixed(3) : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="profit" label="盈亏" width="120" sortable="custom">
              <template #default="{ row }">
                <span v-if="row.asset_profit !== undefined" :class="{ positive: row.asset_profit > 0, negative: row.asset_profit < 0 }">
                  ¥{{ formatNumber(row.asset_profit) }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="profit_percent" label="收益率" width="100" sortable="custom">
              <template #default="{ row }">
                <span v-if="row.asset_profit_percent !== undefined" :class="{ positive: row.asset_profit_percent > 0, negative: row.asset_profit_percent < 0 }">
                  {{ row.asset_profit_percent?.toFixed(2) || 0 }}%
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="strategy_category" label="策略分类" width="120" sortable="custom">
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
      destroy-on-close
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
      destroy-on-close
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
import { useStrategyGroupsStore } from '@/store/strategy-groups'
import { STRATEGY_CATEGORY_NAMES } from '@/utils/constants'
import type { Portfolio, PortfolioCreate, PortfolioUpdate, PortfolioAssetCreate } from '@/types'

const portfoliosStore = usePortfoliosStore()
const assetsStore = useAssetsStore()
const strategyGroupsStore = useStrategyGroupsStore()

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
  asset_id: undefined as number | undefined
})

const assetRules = {
  asset_id: [{ required: true, message: '请选择资产', trigger: 'change' }]
}

const batchForm = reactive({})

const batchRules = {}

const batchSelectedAssets = ref<number[]>([])

// 策略组相关
const selectedStrategyGroupId = ref<number | undefined>(undefined)
const strategyGroups = computed(() => strategyGroupsStore.strategyGroups)
const strategyComparison = ref<any>(null)

// 资产排序相关
const assetSortColumn = ref<string | null>(null)
const assetSortOrder = ref<'ascending' | 'descending' | null>(null)

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

// 排序后的资产列表
const sortedAssets = computed(() => {
  if (!currentPortfolio.value || !currentPortfolio.value.assets) return []

  const assets = [...currentPortfolio.value.assets]

  if (!assetSortColumn.value || !assetSortOrder.value) return assets

  return assets.sort((a, b) => {
    let valueA: any
    let valueB: any

    // 根据排序列获取值
    switch (assetSortColumn.value) {
      case 'asset_code':
        valueA = a.asset_code || ''
        valueB = b.asset_code || ''
        break
      case 'asset_name':
        valueA = a.asset_name || ''
        valueB = b.asset_name || ''
        break
      case 'current_weight':
        valueA = a.current_weight || 0
        valueB = b.current_weight || 0
        break
      case 'profit':
        valueA = a.asset_profit || 0
        valueB = b.asset_profit || 0
        break
      case 'profit_percent':
        valueA = a.asset_profit_percent || 0
        valueB = b.asset_profit_percent || 0
        break
      case 'strategy_category':
        valueA = formatStrategyCategoryName(a.strategy_category || 'OTHER')
        valueB = formatStrategyCategoryName(b.strategy_category || 'OTHER')
        break
      default:
        return 0
    }

    // 字符串比较
    if (typeof valueA === 'string' && typeof valueB === 'string') {
      return assetSortOrder.value === 'ascending'
        ? valueA.localeCompare(valueB, 'zh-CN')
        : valueB.localeCompare(valueA, 'zh-CN')
    }

    // 数值比较
    return assetSortOrder.value === 'ascending'
      ? valueA - valueB
      : valueB - valueA
  })
})

// 处理排序变化
function handleAssetSortChange({ prop, order }: { prop: string; order: 'ascending' | 'descending' | null }) {
  assetSortColumn.value = prop
  assetSortOrder.value = order
}

function resetForm() {
  form.name = ''
  form.description = ''
}

function resetAssetForm() {
  assetForm.asset_id = undefined
}

function resetBatchForm() {
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
    // 设置选中的策略组
    if (currentPortfolio.value.strategy_group_id) {
      selectedStrategyGroupId.value = currentPortfolio.value.strategy_group_id
    } else {
      selectedStrategyGroupId.value = undefined
    }
    // 加载策略对比数据
    await loadStrategyComparison()
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
        asset_id: assetForm.asset_id!
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
        asset_id: assetId
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

async function loadStrategyComparison() {
  if (!currentPortfolio.value) return
  strategyComparison.value = await portfoliosStore.getStrategyComparison(currentPortfolio.value.id)
}

async function handleStrategyGroupChange(strategyGroupId: number) {
  if (!currentPortfolio.value) return
  const result = await portfoliosStore.applyStrategyGroupToPortfolio(currentPortfolio.value.id, strategyGroupId)
  if (result.success) {
    ElMessage.success('策略组应用成功')
    await loadStrategyComparison()
  } else {
    ElMessage.error(result.error || '应用策略组失败')
    // 恢复选择
    selectedStrategyGroupId.value = currentPortfolio.value.strategy_group_id
  }
}

async function handleRemoveStrategyGroup() {
  if (!currentPortfolio.value) return
  try {
    await ElMessageBox.confirm('确定要移除当前策略组吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const result = await portfoliosStore.removeStrategyGroupFromPortfolio(currentPortfolio.value.id)
    if (result.success) {
      ElMessage.success('策略组已移除')
      selectedStrategyGroupId.value = undefined
      await loadStrategyComparison()
    } else {
      ElMessage.error(result.error || '移除失败')
    }
  } catch (error) {
    // 用户取消移除
  }
}

function getStatusTagType(status: string): 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'perfect':
      return 'success'
    case 'normal':
      return 'success'
    case 'warning':
      return 'warning'
    case 'danger':
      return 'danger'
    case 'missing':
      return 'info'
    default:
      return 'info'
  }
}

function getStatusText(status: string): string {
  switch (status) {
    case 'perfect':
      return '完美匹配'
    case 'normal':
      return '正常'
    case 'warning':
      return '轻微偏离'
    case 'danger':
      return '严重偏离'
    case 'missing':
      return '待配置'
    default:
      return '-'
  }
}

onMounted(async () => {
  await portfoliosStore.fetchPortfolios()
  await assetsStore.fetchAssets()
  await strategyGroupsStore.fetchStrategyGroups()
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
  color: #f56c6c !important;
}

.stat-value.negative {
  color: #67c23a !important;
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

/* 策略组相关样式 */
.strategy-group-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.warning-badge {
  margin-left: auto;
}

.strategy-comparison-table {
  margin-top: 15px;
}

.positive-deviation {
  color: #f56c6c !important;
  font-weight: 500;
}

.negative-deviation {
  color: #67c23a !important;
  font-weight: 500;
}

</style>
