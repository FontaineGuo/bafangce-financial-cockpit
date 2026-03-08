<template>
  <div class="assets-content">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>资产管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="showAddDialog = true">添加资产</el-button>
            <el-button type="success" @click="handleBatchRefresh" :loading="loading" :disabled="assets.length === 0">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="assets" v-loading="loading" stripe>
        <el-table-column prop="code" label="代码" width="120" />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            {{ formatAssetType(row.type) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="cost_price" label="成本价" width="100" />
        <el-table-column prop="current_price" label="现价" width="150">
          <template #default="{ row }">
            <div v-if="row.current_price" class="price-cell">
              <span :class="{
                'manual-price': row.is_manually_set,
                'api-price': !row.is_manually_set
              }">
                {{ row.current_price.toFixed(4) }}
              </span>
              <el-tag v-if="row.is_manually_set" type="warning" size="small" class="price-tag">
                手动
              </el-tag>
              <span v-if="row.manual_set_at" class="manual-set-time">
                {{ formatDateTime(row.manual_set_at) }}
              </span>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="market_value" label="市值" width="100" />
        <el-table-column prop="profit" label="盈亏" width="100">
          <template #default="{ row }">
            <span :class="{ positive: row.profit > 0, negative: row.profit < 0 }">
              {{ row.profit ? row.profit.toFixed(2) : '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_percent" label="盈亏%" width="100">
          <template #default="{ row }">
            <span :class="{ positive: row.profit_percent > 0, negative: row.profit_percent < 0 }">
              {{ row.profit_percent ? row.profit_percent.toFixed(2) + '%' : '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="strategy_category" label="策略分类" width="150">
          <template #default="{ row }">
            <el-select
              v-model="row.strategy_category"
              @change="(value: string) => handleStrategyCategoryChange(row, value)"
              size="small"
              placeholder="未分类"
            >
              <el-option label="现金" value="CASH" />
              <el-option label="中国股票/ETF" value="CN_STOCK_ETF" />
              <el-option label="海外股票/ETF" value="OVERSEAS_STOCK_ETF" />
              <el-option label="大宗商品" value="COMMODITY" />
              <el-option label="信用债" value="CREDIT_BOND" />
              <el-option label="长债" value="LONG_BOND" />
              <el-option label="短债" value="SHORT_BOND" />
              <el-option label="黄金" value="GOLD" />
              <el-option label="其他" value="OTHER" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" @click="handleEdit(row)">编辑</el-button>
              <el-button size="small" type="primary" @click="handleEditPrice(row)">
                <el-icon><Edit /></el-icon>
                设置价格
              </el-button>
              <el-button size="small" type="success" @click="handleRefreshSingle(row)" :loading="loading">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑资产对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingAsset ? '编辑资产' : '添加资产'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="代码" prop="code">
          <el-input v-model="form.code" :disabled="!!editingAsset" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="可选：未填写时将自动从API获取"
          />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择资产类型">
            <el-option label="股票" value="STOCK" />
            <el-option label="LOF基金" value="LOF_FUND" />
            <el-option label="ETF基金" value="ETF_FUND" />
            <el-option label="开放式基金" value="OPEN_FUND" />
            <el-option label="现金" value="CASH" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="0" :precision="4" />
        </el-form-item>
        <el-form-item label="成本价" prop="cost_price">
          <el-input-number v-model="form.cost_price" :min="0" :precision="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 手动设置价格对话框 -->
    <el-dialog
      v-model="showPriceDialog"
      title="手动设置价格"
      width="500px"
    >
      <div v-if="editingPriceAsset">
        <el-form :model="priceForm" :rules="priceRules" ref="priceFormRef" label-width="100px">
          <el-form-item label="资产代码">
            <el-input v-model="editingPriceAsset.code" disabled />
          </el-form-item>
          <el-form-item label="资产名称">
            <el-input v-model="editingPriceAsset.name" disabled />
          </el-form-item>
          <el-form-item label="当前价格" v-if="editingPriceAsset.current_price">
            <el-input :value="formatPrice(editingPriceAsset.current_price)" disabled>
              <template #append>
                <span v-if="editingPriceAsset.is_manually_set" class="manual-price-badge">
                  <el-tag type="warning" size="small">手动</el-tag>
                </span>
                <span v-else class="api-price-badge">
                  <el-tag type="success" size="small">API</el-tag>
                </span>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="手动价格" prop="manual_set_price">
            <el-input-number
              v-model="priceForm.manual_set_price"
              :min="0.01"
              :precision="4"
              :step="0.01"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item v-if="editingPriceAsset.manual_set_at" label="手动设置时间">
            <el-input :value="formatDateTime(editingPriceAsset.manual_set_at)" disabled />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="closePriceDialog">取消</el-button>
        <el-button type="primary" @click="handleSubmitPrice" :loading="loading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Edit } from '@element-plus/icons-vue'
import { useAssetsStore } from '@/store/assets'
import type { Asset, AssetType, StrategyCategory, AssetStrategyCategoryUpdate, AssetUpdate } from '@/types'
import { ASSET_TYPE_NAMES, STRATEGY_CATEGORY_NAMES } from '@/utils/constants'

const assetsStore = useAssetsStore()

const showAddDialog = ref(false)
const editingAsset = ref<Asset | null>(null)
const formRef = ref()
const loading = computed(() => assetsStore.loading)
const assets = computed(() => assetsStore.assets)

// 价格设置相关
const showPriceDialog = ref(false)
const editingPriceAsset = ref<Asset | null>(null)
const priceFormRef = ref()
const priceForm = reactive({
  manual_set_price: 0
})

const priceRules = {
  manual_set_price: [
    { required: true, message: '请输入价格', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '价格必须大于0', trigger: 'blur' }
  ]
}

const form = reactive({
  code: '',
  name: '',
  type: 'STOCK' as AssetType,
  quantity: 0,
  cost_price: 0
})

const rules = {
  code: [{ required: true, message: '请输入资产代码', trigger: 'blur' }],
  name: [], // 名称可选，如果未提供会从API自动获取
  type: [{ required: true, message: '请选择资产类型', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  cost_price: [{ required: true, message: '请输入成本价', trigger: 'blur' }]
}

function resetForm() {
  form.code = ''
  form.name = ''
  form.type = 'STOCK'
  form.quantity = 0
  form.cost_price = 0
}

function closeDialog() {
  showAddDialog.value = false
  editingAsset.value = null
  resetForm()
}

function handleEdit(asset: Asset) {
  editingAsset.value = asset
  form.code = asset.code
  form.name = asset.name
  form.type = asset.type
  form.quantity = asset.quantity
  form.cost_price = asset.cost_price
  showAddDialog.value = true
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这个资产吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const result = await assetsStore.deleteAsset(id)
    if (result.success) {
      ElMessage.success('删除成功')
    } else {
      ElMessage.error(result.error || '删除失败')
    }
  } catch (error) {
    // 用户取消删除
  }
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      let result
      if (editingAsset.value) {
        const updateData = {
          name: form.name,
          type: form.type,
          quantity: form.quantity,
          cost_price: form.cost_price
        }
        result = await assetsStore.updateAsset(editingAsset.value.id, updateData)
        if (result.success) {
          ElMessage.success('更新成功')
          closeDialog()
        } else {
          ElMessage.error(result.error || '更新失败')
        }
      } else {
        result = await assetsStore.addAsset(form)
        if (result.success) {
          ElMessage.success('添加成功')
          closeDialog()
        } else {
          ElMessage.error(result.error || '添加失败')
        }
      }
    }
  })
}

async function handleStrategyCategoryChange(row: Asset, category: StrategyCategory) {
  try {
    const result = await assetsStore.updateAssetStrategyCategory(row.id, {
      strategy_category: category
    })
    if (result.success) {
      ElMessage.success('策略分类更新成功')
    } else {
      ElMessage.error(result.error || '更新失败')
    }
  } catch (error) {
    console.error('Update strategy category failed:', error)
  }
}

async function handleRefreshSingle(asset: Asset) {
  try {
    ElMessage.info(`正在刷新资产 ${asset.name} 的市场数据...`)
    const result = await assetsStore.refreshAsset(asset.id)
    if (result.success) {
      ElMessage.success('刷新成功')
    } else {
      ElMessage.error(result.error || '刷新失败')
    }
  } catch (error) {
    console.error('Refresh asset failed:', error)
  }
}

async function handleBatchRefresh() {
  try {
    ElMessage.info('正在批量刷新所有资产的市场数据...')
    const result = await assetsStore.batchRefreshAssets()
    if (result.success) {
      if (result.data && result.data.failed_count > 0) {
        ElMessage.warning(
          `刷新完成：成功 ${result.data.success_count} 个，失败 ${result.data.failed_count} 个`,
          { duration: 5000 }
        )
        if (result.data.failed_assets && result.data.failed_assets.length > 0) {
          const failedNames = result.data.failed_assets.map(a => a.name).join('、')
          ElMessage.warning(`失败资产：${failedNames}`, { duration: 5000 })
        }
      } else {
        ElMessage.success(`刷新成功！共刷新 ${result.data.success_count} 个资产`)
      }
    } else {
      ElMessage.error(result.error || '批量刷新失败')
    }
  } catch (error) {
    console.error('Batch refresh failed:', error)
  }
}

function formatAssetType(type: AssetType): string {
  return ASSET_TYPE_NAMES[type] || type
}

function formatStrategyCategory(category?: string): string {
  if (!category) return '-'
  return STRATEGY_CATEGORY_NAMES[category as keyof typeof STRATEGY_CATEGORY_NAMES] || category
}

function formatPrice(price: number): string {
  return price.toFixed(4)
}

function formatDateTime(dateStr?: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function handleEditPrice(asset: Asset) {
  editingPriceAsset.value = asset
  priceForm.manual_set_price = asset.current_price || asset.manual_set_price || 0
  showPriceDialog.value = true
}

function closePriceDialog() {
  showPriceDialog.value = false
  editingPriceAsset.value = null
  priceForm.manual_set_price = 0
}

async function handleSubmitPrice() {
  if (!priceFormRef.value || !editingPriceAsset.value) return

  await priceFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      const result = await assetsStore.setCurrentPrice(editingPriceAsset.value.id, {
        current_price: priceForm.manual_set_price
      })
      if (result.success) {
        ElMessage.success('价格设置成功')
        closePriceDialog()
      } else {
        ElMessage.error(result.error || '设置价格失败')
      }
    }
  })
}

onMounted(() => {
  assetsStore.fetchAssets()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.positive {
  color: #67c23a;
}

.negative {
  color: #f56c6c;
}

.price-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.manual-price {
  font-weight: bold;
  color: #e6a23c;
}

.api-price {
  color: #67c23a;
}

.price-tag {
  margin-left: 4px;
}

.manual-set-time {
  font-size: 11px;
  color: #909399;
}
</style>
