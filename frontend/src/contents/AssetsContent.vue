<template>
  <div class="assets-content">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>资产管理</span>
          <el-button type="primary" @click="showAddDialog = true">添加资产</el-button>
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
        <el-table-column prop="current_price" label="现价" width="100" />
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
            {{ formatStrategyCategory(row.strategy_category) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAssetsStore } from '@/store/assets'
import type { Asset, AssetType } from '@/types'
import { ASSET_TYPE_NAMES, STRATEGY_CATEGORY_NAMES } from '@/utils/constants'

const assetsStore = useAssetsStore()

const showAddDialog = ref(false)
const editingAsset = ref<Asset | null>(null)
const formRef = ref()
const loading = computed(() => assetsStore.loading)
const assets = computed(() => assetsStore.assets)

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

function formatAssetType(type: AssetType): string {
  return ASSET_TYPE_NAMES[type] || type
}

function formatStrategyCategory(category?: string): string {
  if (!category) return '-'
  return STRATEGY_CATEGORY_NAMES[category as keyof typeof STRATEGY_CATEGORY_NAMES] || category
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

.positive {
  color: #67c23a;
}

.negative {
  color: #f56c6c;
}
</style>
