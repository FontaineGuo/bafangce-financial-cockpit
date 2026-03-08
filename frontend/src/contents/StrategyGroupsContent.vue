<template>
  <div class="strategy-groups">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>策略组管理</span>
          <el-button type="primary" @click="showCreateDialog = true">创建策略组</el-button>
        </div>
      </template>

      <!-- 策略组列表 -->
      <el-empty v-if="!loading && strategyGroups.length === 0" description="暂无策略组，点击右上角创建" />

      <div v-else class="strategy-groups-list">
        <el-card
          v-for="group in strategyGroups"
          :key="group.id"
          class="strategy-group-card"
          shadow="hover"
        >
          <template #header>
            <div class="strategy-group-header">
              <span class="strategy-group-name">{{ group.name }}</span>
              <div class="strategy-group-actions">
                <el-button size="small" @click="handleViewGroup(group)">查看</el-button>
                <el-button size="small" @click="handleEditGroup(group)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteGroup(group)">删除</el-button>
              </div>
            </div>
          </template>

          <div class="strategy-group-content">
            <!-- 基本信息 -->
            <div class="strategy-group-info">
              <div class="info-row" v-if="group.description">
                <span class="label">描述：</span>
                <span class="value">{{ group.description }}</span>
              </div>
              <div class="info-row">
                <span class="label">创建时间：</span>
                <span class="value">{{ formatDateTime(group.created_at) }}</span>
              </div>
              <div class="info-row">
                <span class="label">更新时间：</span>
                <span class="value">{{ formatDateTime(group.updated_at) }}</span>
              </div>
            </div>

            <!-- 策略分类配置 -->
            <div class="category-allocations" v-if="group.category_allocations && group.category_allocations.length > 0">
              <h5>策略分类配置</h5>
              <div class="allocations-list">
                <div
                  v-for="(allocation, index) in group.category_allocations"
                  :key="allocation.id"
                  class="allocation-item"
                >
                  <span class="allocation-category">{{ getCategoryLabel(allocation.category) }}</span>
                  <div class="allocation-inputs">
                    <span class="input-label">百分比：</span>
                    <el-input-number
                      v-model="allocation.percentage"
                      :min="0"
                      :max="100"
                      :precision="2"
                      :step="0.1"
                      style="width: 150px"
                      size="small"
                    />
                    <span class="input-label">偏离值(%)：</span>
                    <el-input-number
                      v-model="allocation.deviation_threshold"
                      :min="0"
                      :max="100"
                      :precision="2"
                      :step="0.1"
                      style="width: 150px"
                      size="small"
                    />
                  </div>
                </div>
                <el-divider />
                <div class="allocation-total">
                  <span class="total-label">总计：</span>
                  <span class="total-value" :class="{ 'error': getTotalPercentage(group.id) > 100 }">
                  {{ getTotalPercentage(group.id) }}%
                </span>
                <el-tag v-if="getTotalPercentage(group.id) > 100" type="danger" size="small" class="error-tag">
                  超过100%
                </el-tag>
              </div>
            </div>
            </div>
            <el-empty v-else description="暂无策略分类配置" :image-size="60" />
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 创建/编辑策略组对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingGroup ? '编辑策略组' : '创建策略组'"
      width="800px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="策略组名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入策略组名称" />
        </el-form-item>
        <el-form-item label="策略组描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入策略组描述"
          />
        </el-form-item>

        <!-- 策略分类配置 -->
        <el-divider>策略分类配置</el-divider>
        <div class="allocations-section">
          <el-alert
            title="注意：所有策略分类的百分比总和不能超过100%，每个策略分类在一个策略组中只能使用一次"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 20px"
          />

          <div
            v-for="(allocation, index) in form.category_allocations"
            :key="index"
            class="allocation-form-item"
          >
            <el-form-item
              :label="`分类 ${index + 1}`"
              :prop="`category_allocations.${index}.category`"
              :rules="[
                { required: true, message: '请选择策略分类', trigger: 'change' },
                {
                  validator: (rule: any, value: string, callback: any) => {
                    if (!value) {
                      callback()
                      return
                    }
                    // 检查是否有重复分类
                    const duplicates = form.category_allocations.filter((a, i) =>
                      a.category === value && i !== index
                    )
                    if (duplicates.length > 0) {
                      callback(new Error('该策略分类已存在，请选择其他分类'))
                    } else {
                      callback()
                    }
                  },
                  trigger: 'change'
                }
              ]"
            >
              <el-select
                v-model="allocation.category"
                placeholder="选择策略分类"
                @change="(val: string) => handleCategoryChange(index, val)"
              >
                <el-option
                  v-for="category in getAvailableCategories(index)"
                  :key="category"
                  :label="getCategoryLabel(category)"
                  :value="category"
                />
              </el-select>
            </el-form-item>
            <el-form-item
              label="百分比"
              :prop="`category_allocations.${index}.percentage`"
              :rules="[
                { required: true, message: '请输入百分比', trigger: 'blur' },
                {
                  type: 'number',
                  min: 0,
                  max: 100,
                  message: '百分比必须在0到100之间',
                  trigger: 'blur'
                }
              ]"
            >
              <el-input-number
                v-model="allocation.percentage"
                :min="0"
                :max="100"
                :precision="2"
                :step="0.1"
                controls-position="right"
                style="width: 200px"
                @change="validateTotalPercentage"
              />
              <span class="percentage-unit">%</span>
            </el-form-item>
            <el-form-item
              label="偏离值"
              :prop="`category_allocations.${index}.deviation_threshold`"
              :rules="[
                {
                  type: 'number',
                  min: 0,
                  message: '偏离值不能小于0',
                  trigger: 'blur'
                }
              ]"
            >
              <el-input-number
                v-model="allocation.deviation_threshold"
                :min="0"
                :max="100"
                :precision="2"
                :step="0.1"
                controls-position="right"
                style="width: 200px"
                placeholder="选填"
              />
              <span class="percentage-unit">%</span>
            </el-form-item>
            <el-button
              size="small"
              type="danger"
              @click="removeAllocation(index)"
              v-if="form.category_allocations.length > 1"
            >
              删除
            </el-button>
            <el-divider v-if="index < form.category_allocations.length - 1" />
          </div>

          <el-button size="small" @click="addAllocation">
            添加策略分类
          </el-button>

          <!-- 总计显示 -->
          <div class="form-total" v-if="form.category_allocations.length > 0">
            <span class="total-label">总计：</span>
            <span class="total-value" :class="{ 'error': formTotalPercentage > 100 }">
              {{ formTotalPercentage }}%
            </span>
            <el-tag v-if="formTotalPercentage > 100" type="danger" size="small" class="error-tag">
              超过100%，请调整
            </el-tag>
          </div>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button
          type="primary"
          @click="handleSubmit"
          :loading="loading"
          :disabled="formTotalPercentage > 100"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看策略组详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`策略组详情 - ${currentGroup?.name}`"
      width="700px"
    >
      <div v-if="currentGroup" class="strategy-group-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="策略组名称">{{ currentGroup.name }}</el-descriptions-item>
          <el-descriptions-item label="策略组描述" v-if="currentGroup.description">
            {{ currentGroup.description }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentGroup.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDateTime(currentGroup.updated_at) }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>策略分类配置</el-divider>
        <div v-if="currentGroup.category_allocations && currentGroup.category_allocations.length > 0" class="detail-allocations">
          <el-table :data="currentGroup.category_allocations" border style="width: 100%">
            <el-table-column prop="category" label="策略分类" width="200">
              <template #default="{ row }">
                {{ getCategoryLabel(row.category) }}
              </template>
            </el-table-column>
            <el-table-column prop="percentage" label="百分比" width="150">
              <template #default="{ row }">
                {{ row.percentage }}%
              </template>
            </el-table-column>
            <el-table-column prop="deviation_threshold" label="偏离值(%)" width="150">
              <template #default="{ row }">
                {{ row.deviation_threshold ?? '-' }}
              </template>
            </el-table-column>
          </el-table>
          <el-divider />
          <div class="detail-total">
            <span class="total-label">总计：</span>
            <span class="total-value" :class="{ 'error': getTotalPercentage(currentGroup.id) > 100 }">
              {{ getTotalPercentage(currentGroup.id) }}%
            </span>
            <el-tag v-if="getTotalPercentage(currentGroup.id) > 100" type="danger" size="small" class="error-tag">
              超过100%
            </el-tag>
          </div>
        </div>
        <el-empty v-else description="暂无策略分类配置" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useStrategyGroupsStore } from '@/store/strategy-groups'
import type { StrategyGroup, StrategyGroupCreate, StrategyGroupUpdate, StrategyCategoryAllocationCreate } from '@/types'
import { StrategyCategory } from '@/types'

const strategyGroupsStore = useStrategyGroupsStore()

const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const editingGroup = ref<StrategyGroup | null>(null)
const currentGroup = ref<StrategyGroup | null>(null)
const formRef = ref()
const loading = computed(() => strategyGroupsStore.loading)

const strategyGroups = computed(() => strategyGroupsStore.strategyGroups)

const form = reactive({
  name: '',
  description: '',
  category_allocations: [] as StrategyCategoryAllocationCreate[]
})

const rules = {
  name: [{ required: true, message: '请输入策略组名称', trigger: 'blur' }]
}

const formTotalPercentage = computed(() => {
  return form.category_allocations.reduce((sum, allocation) => sum + allocation.percentage, 0)
})

function resetForm() {
  form.name = ''
  form.description = ''
  form.category_allocations = [{ category: StrategyCategory.CASH, percentage: 0, deviation_threshold: undefined }]
}

function closeDialog() {
  showCreateDialog.value = false
  editingGroup.value = null
  resetForm()
}

function addAllocation() {
  // 检查已使用的分类
  const usedCategories = new Set(form.category_allocations.map(a => a.category))

  // 查找第一个未使用的分类
  const availableCategories = Object.values(StrategyCategory).filter(category => !usedCategories.has(category))

  if (availableCategories.length === 0) {
    ElMessage.warning('所有策略分类都已使用，无法添加更多')
    return
  }

  // 添加第一个可用的分类
  form.category_allocations.push({
    category: availableCategories[0],
    percentage: 0,
    deviation_threshold: undefined
  })
}

function removeAllocation(index: number) {
  form.category_allocations.splice(index, 1)
}

function validateTotalPercentage() {
  // 只是为了触发UI更新，实际验证在rules中
}

// 获取可用的分类（排除已使用的分类）
function getAvailableCategories(excludeIndex: number): StrategyCategory[] {
  const usedCategories = form.category_allocations
    .map((a, i) => a.category)
    .filter((_, i) => i !== excludeIndex)

  return Object.values(StrategyCategory).filter(category => !usedCategories.includes(category))
}

// 处理分类变化时的验证
function handleCategoryChange(index: number, category: string) {
  // 检查是否有重复分类
  const duplicates = form.category_allocations.filter((a, i) =>
    a.category === category && i !== index
  )

  if (duplicates.length > 0) {
    ElMessage.warning('该策略分类已存在，请选择其他分类')
    // 重置为第一个可用分类
    const available = getAvailableCategories(index)
    if (available.length > 0) {
      form.category_allocations[index].category = available[0]
    }
  }
}

function getCategoryLabel(category: StrategyCategory): string {
  const labels: Record<StrategyCategory, string> = {
    [StrategyCategory.CASH]: '现金',
    [StrategyCategory.CN_STOCK_ETF]: '国内股票ETF',
    [StrategyCategory.OVERSEAS_STOCK_ETF]: '海外股票ETF',
    [StrategyCategory.COMMODITY]: '商品',
    [StrategyCategory.CREDIT_BOND]: '信用债',
    [StrategyCategory.LONG_BOND]: '长债',
    [StrategyCategory.SHORT_BOND]: '短债',
    [StrategyCategory.GOLD]: '黄金',
    [StrategyCategory.OTHER]: '其他'
  }
  return labels[category] || category
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      // 验证总百分比不超过100%
      if (formTotalPercentage.value > 100) {
        ElMessage.error('所有策略分类的百分比总和不能超过100%')
        return
      }

      // 验证分类唯一性
      const categories = form.category_allocations.map(a => a.category)
      const uniqueCategories = new Set(categories)
      if (categories.length !== uniqueCategories.size) {
        const duplicates = categories.filter((cat, index) => categories.indexOf(cat) !== index)
        ElMessage.error(`检测到重复的策略分类：${getCategoryLabel(duplicates[0] as StrategyCategory)}，请确保每个分类只使用一次`)
        return
      }

      if (editingGroup.value) {
        const updateData: StrategyGroupUpdate = {
          name: form.name,
          description: form.description,
          category_allocations: form.category_allocations
        }
        const result = await strategyGroupsStore.updateStrategyGroup(editingGroup.value.id, updateData)
        if (result.success) {
          ElMessage.success('更新成功')
          closeDialog()
        } else {
          ElMessage.error(result.error || '更新失败')
        }
      } else {
        const result = await strategyGroupsStore.createStrategyGroup(form)
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

function handleEditGroup(group: StrategyGroup) {
  editingGroup.value = group
  form.name = group.name
  form.description = group.description || ''
  form.category_allocations = group.category_allocations.map(allocation => ({
    category: allocation.category,
    percentage: allocation.percentage,
    deviation_threshold: allocation.deviation_threshold || undefined
  }))
  showCreateDialog.value = true
}

async function handleDeleteGroup(group: StrategyGroup) {
  try {
    await ElMessageBox.confirm('确定要删除这个策略组吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const result = await strategyGroupsStore.deleteStrategyGroup(group.id)
    if (result.success) {
      ElMessage.success('删除成功')
    } else {
      ElMessage.error(result.error || '删除失败')
    }
  } catch (error) {
    // 用户取消删除
  }
}

function handleViewGroup(group: StrategyGroup) {
  currentGroup.value = group
  showDetailDialog.value = true
}

function formatDateTime(dateString: string | undefined): string {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getTotalPercentage(groupId: number): number {
  return strategyGroupsStore.getTotalPercentage(groupId)
}

onMounted(() => {
  strategyGroupsStore.fetchStrategyGroups()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.strategy-groups-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.strategy-group-card {
  transition: transform 0.2s;
}

.strategy-group-card:hover {
  transform: translateY(-4px);
}

.strategy-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.strategy-group-name {
  font-weight: bold;
  font-size: 16px;
}

.strategy-group-actions {
  display: flex;
  gap: 8px;
}

.strategy-group-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.strategy-group-info {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  color: #909399;
  width: 80px;
  flex-shrink: 0;
}

.info-row .value {
  color: #303133;
  flex: 1;
}

.category-allocations h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #606266;
  border-left: 3px solid #409eff;
  padding-left: 8px;
}

.allocations-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.allocation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.allocation-category {
  color: #303133;
  font-size: 14px;
}

.allocation-percentage {
  color: #409eff;
  font-weight: bold;
  font-size: 14px;
}

.allocation-total {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  font-weight: bold;
}

.total-label {
  color: #606266;
}

.total-value {
  color: #409eff;
}

.total-value.error {
  color: #f56c6c;
}

.error-tag {
  flex-shrink: 0;
}

.allocations-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.allocation-form-item {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.percentage-unit {
  margin-left: 10px;
  color: #909399;
}

.form-total {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: #ecf5ff;
  border-radius: 4px;
  font-weight: bold;
  font-size: 14px;
}

.strategy-group-detail .el-descriptions {
  margin-bottom: 20px;
}

.detail-allocations {
  margin-top: 20px;
}

.detail-total {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-weight: bold;
  font-size: 14px;
  margin-top: 20px;
}
</style>
