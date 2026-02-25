<template>
  <div class="strategies">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>策略管理</span>
          <el-button type="primary" @click="showCreateDialog = true">创建策略</el-button>
        </div>
      </template>

      <!-- 策略列表 -->
      <el-empty v-if="!loading && strategies.length === 0" description="暂无策略，点击右上角创建" />

      <div v-else class="strategy-list">
        <el-card
          v-for="strategy in strategies"
          :key="strategy.id"
          class="strategy-card"
          shadow="hover"
        >
          <template #header>
            <div class="strategy-header">
              <span class="strategy-name">{{ strategy.name }}</span>
              <div class="strategy-status">
                <el-switch
                  v-model="strategy.enabled"
                  @change="handleToggleStrategy(strategy)"
                  :loading="toggleLoading[strategy.id]"
                />
              </div>
            </div>
          </template>

          <div class="strategy-content">
            <!-- 基本信息 -->
            <div class="strategy-info">
              <div class="info-row">
                <span class="label">类型：</span>
                <span class="value">{{ strategy.type || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">分类：</span>
                <span class="value">{{ strategy.category || '-' }}</span>
              </div>
              <div class="info-row" v-if="strategy.description">
                <span class="label">描述：</span>
                <span class="value">{{ strategy.description }}</span>
              </div>
              <div class="info-row">
                <span class="label">最后执行：</span>
                <span class="value">{{ formatDateTime(strategy.last_execution) }}</span>
              </div>
              <div class="info-row">
                <span class="label">创建时间：</span>
                <span class="value">{{ formatDateTime(strategy.created_at) }}</span>
              </div>
            </div>

            <!-- 策略条件 -->
            <div class="strategy-conditions" v-if="strategy.conditions && strategy.conditions.length > 0">
              <h5>触发条件</h5>
              <div class="conditions-list">
                <div
                  v-for="(condition, index) in strategy.conditions"
                  :key="condition.id"
                  class="condition-item"
                >
                  <span class="condition-index">{{ index + 1 }}</span>
                  <span class="condition-text">
                    {{ condition.field }} {{ condition.operator }} {{ condition.value }}
                  </span>
                  <span class="condition-logic" v-if="index < strategy.conditions.length - 1">
                    {{ condition.logical_operator }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="strategy-actions">
              <el-button size="small" @click="handleViewStrategy(strategy)">查看</el-button>
              <el-button size="small" @click="handleEditStrategy(strategy)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDeleteStrategy(strategy)">删除</el-button>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 创建/编辑策略对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingStrategy ? '编辑策略' : '创建策略'"
      width="700px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="策略名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择策略类型">
            <el-option label="价格监控" value="price" />
            <el-option label="涨跌幅监控" value="change_percent" />
            <el-option label="市值监控" value="market_value" />
            <el-option label="时间触发" value="time" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="策略分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择策略分类">
            <el-option label="现金" value="CASH" />
            <el-option label="国内股票ETF" value="CN_STOCK_ETF" />
            <el-option label="海外股票ETF" value="OVERSEAS_STOCK_ETF" />
            <el-option label="商品" value="COMMODITY" />
            <el-option label="信用债" value="CREDIT_BOND" />
            <el-option label="长债" value="LONG_BOND" />
            <el-option label="短债" value="SHORT_BOND" />
            <el-option label="黄金" value="GOLD" />
            <el-option label="其他" value="OTHER" />
          </el-select>
        </el-form-item>
        <el-form-item label="策略描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入策略描述"
          />
        </el-form-item>
        <el-form-item label="启用策略" prop="enabled">
          <el-switch v-model="form.enabled" />
        </el-form-item>

        <!-- 策略条件 -->
        <el-divider>触发条件</el-divider>
        <div class="conditions-section">
          <div
            v-for="(condition, index) in form.conditions"
            :key="index"
            class="condition-form-item"
          >
            <el-form-item label="字段">
              <el-select v-model="condition.field" placeholder="选择字段">
                <el-option label="当前价格" value="current_price" />
                <el-option label="涨跌幅" value="change_percent" />
                <el-option label="市值" value="market_value" />
                <el-option label="盈亏" value="profit" />
                <el-option label="盈亏百分比" value="profit_percent" />
              </el-select>
            </el-form-item>
            <el-form-item label="操作符">
              <el-select v-model="condition.operator" placeholder="选择操作符">
                <el-option label="大于" value=">" />
                <el-option label="小于" value="<" />
                <el-option label="等于" value="==" />
                <el-option label="大于等于" value=">=" />
                <el-option label="小于等于" value="<=" />
              </el-select>
            </el-form-item>
            <el-form-item label="值">
              <el-input v-model="condition.value" placeholder="输入值" />
            </el-form-item>
            <el-form-item label="逻辑">
              <el-select v-model="condition.logical_operator" placeholder="选择逻辑关系">
                <el-option label="AND" value="AND" />
                <el-option label="OR" value="OR" />
              </el-select>
            </el-form-item>
            <el-button
              size="small"
              type="danger"
              @click="removeCondition(index)"
              v-if="form.conditions.length > 1"
            >
              删除条件
            </el-button>
            <el-divider v-if="index < form.conditions.length - 1" />
          </div>

          <el-button size="small" @click="addCondition">
            添加条件
          </el-button>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看策略详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`策略详情 - ${currentStrategy?.name}`"
      width="600px"
    >
      <div v-if="currentStrategy" class="strategy-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="策略名称">{{ currentStrategy.name }}</el-descriptions-item>
          <el-descriptions-item label="策略类型">{{ currentStrategy.type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="策略分类">{{ currentStrategy.category || '-' }}</el-descriptions-item>
          <el-descriptions-item label="策略状态">
            <el-tag :type="currentStrategy.enabled ? 'success' : 'info'">
              {{ currentStrategy.enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentStrategy.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDateTime(currentStrategy.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="最后执行">{{ formatDateTime(currentStrategy.last_execution) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="描述" v-if="currentStrategy.description">
            {{ currentStrategy.description }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>触发条件</el-divider>
        <div v-if="currentStrategy.conditions && currentStrategy.conditions.length > 0" class="detail-conditions">
          <div
            v-for="(condition, index) in currentStrategy.conditions"
            :key="condition.id"
            class="detail-condition-item"
          >
            <span class="condition-number">{{ index + 1 }}.</span>
            <span class="condition-text">
              {{ condition.field }} {{ condition.operator }} {{ condition.value }}
            </span>
            <span class="condition-logic" v-if="index < currentStrategy.conditions.length - 1">
              {{ condition.logical_operator }}
            </span>
          </div>
        </div>
        <el-empty v-else description="暂无触发条件" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useStrategiesStore } from '@/store/strategies'
import type { Strategy, StrategyCreate, StrategyUpdate, StrategyConditionCreate } from '@/types'

const strategiesStore = useStrategiesStore()

const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const editingStrategy = ref<Strategy | null>(null)
const currentStrategy = ref<Strategy | null>(null)
const formRef = ref()
const loading = computed(() => strategiesStore.loading)
const toggleLoading = ref<Record<number, boolean>>({})

const strategies = computed(() => strategiesStore.strategies)

const form = reactive({
  name: '',
  type: '',
  category: '',
  description: '',
  enabled: false,
  conditions: [] as StrategyConditionCreate[]
})

const rules = {
  name: [{ required: true, message: '请输入策略名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择策略类型', trigger: 'change' }]
}

function resetForm() {
  form.name = ''
  form.type = ''
  form.category = ''
  form.description = ''
  form.enabled = false
  form.conditions = [{ field: '', operator: '', value: '', logical_operator: 'AND', order: 0 }]
}

function closeDialog() {
  showCreateDialog.value = false
  editingStrategy.value = null
  resetForm()
}

function addCondition() {
  form.conditions.push({
    field: '',
    operator: '',
    value: '',
    logical_operator: 'AND',
    order: form.conditions.length
  })
}

function removeCondition(index: number) {
  form.conditions.splice(index, 1)
  // 更新顺序
  form.conditions.forEach((cond, i) => {
    cond.order = i
  })
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      // 验证条件
      if (form.conditions.length === 0 || form.conditions.some(c => !c.field || !c.operator || !c.value)) {
        ElMessage.warning('请完善所有触发条件')
        return
      }

      if (editingStrategy.value) {
        const updateData: StrategyUpdate = {
          name: form.name,
          type: form.type,
          category: form.category,
          description: form.description,
          enabled: form.enabled
        }
        const result = await strategiesStore.updateStrategy(editingStrategy.value.id, updateData)
        if (result.success) {
          ElMessage.success('更新成功')
          closeDialog()
        } else {
          ElMessage.error(result.error || '更新失败')
        }
      } else {
        const result = await strategiesStore.createStrategy(form)
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

function handleEditStrategy(strategy: Strategy) {
  editingStrategy.value = strategy
  form.name = strategy.name
  form.type = strategy.type || ''
  form.category = strategy.category || ''
  form.description = strategy.description || ''
  form.enabled = strategy.enabled
  form.conditions = strategy.conditions.map(c => ({
    field: c.field,
    operator: c.operator,
    value: c.value,
    logical_operator: c.logical_operator || 'AND',
    order: c.order
  }))
  showCreateDialog.value = true
}

async function handleToggleStrategy(strategy: Strategy) {
  toggleLoading.value[strategy.id] = true
  const result = await strategiesStore.toggleStrategy(strategy.id, !strategy.enabled)
  toggleLoading.value[strategy.id] = false

  if (!result.success) {
    // 恢复开关状态
    strategy.enabled = !strategy.enabled
    ElMessage.error(result.error || '切换策略状态失败')
  }
}

async function handleDeleteStrategy(strategy: Strategy) {
  try {
    await ElMessageBox.confirm('确定要删除这个策略吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const result = await strategiesStore.deleteStrategy(strategy.id)
    if (result.success) {
      ElMessage.success('删除成功')
    } else {
      ElMessage.error(result.error || '删除失败')
    }
  } catch (error) {
    // 用户取消删除
  }
}

function handleViewStrategy(strategy: Strategy) {
  currentStrategy.value = strategy
  showDetailDialog.value = true
}

function formatDateTime(dateString: string | null | undefined): string {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  strategiesStore.fetchStrategies()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.strategy-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.strategy-card {
  transition: transform 0.2s;
}

.strategy-card:hover {
  transform: translateY(-4px);
}

.strategy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.strategy-name {
  font-weight: bold;
  font-size: 16px;
}

.strategy-status {
  display: flex;
  align-items: center;
}

.strategy-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.strategy-info {
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

.strategy-conditions h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #606266;
  border-left: 3px solid #409eff;
  padding-left: 8px;
}

.conditions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.condition-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.condition-index {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.condition-text {
  color: #303133;
  font-size: 14px;
}

.condition-logic {
  padding: 4px 8px;
  background: #e6f7ff;
  color: #409eff;
  border-radius: 3px;
  font-size: 12px;
  font-weight: bold;
}

.strategy-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}

.conditions-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.condition-form-item {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.strategy-detail .el-descriptions {
  margin-bottom: 20px;
}

.detail-conditions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-condition-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.condition-number {
  font-weight: bold;
  color: #409eff;
  min-width: 30px;
}

.detail-condition-item .condition-text {
  color: #303133;
  font-size: 14px;
}

.detail-condition-item .condition-logic {
  padding: 4px 8px;
  background: #e6f7ff;
  color: #409eff;
  border-radius: 3px;
  font-size: 12px;
  font-weight: bold;
}
</style>
