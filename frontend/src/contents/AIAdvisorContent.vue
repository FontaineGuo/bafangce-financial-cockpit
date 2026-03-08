<template>
  <div class="ai-advisor">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>AI建议</span>
          <el-button type="primary" @click="generateAdvice" :loading="loading">
            生成建议
          </el-button>
        </div>
      </template>

      <el-empty v-if="!loading && adviceList.length === 0" description="点击右上角生成AI建议">
        <template #description>
          <div class="feature-not-available">
            <el-icon size="40" color="#909399">
              <Lock />
            </el-icon>
            <div class="feature-text">
              <h3>该功能暂未开放</h3>
              <p>敬请期待</p>
            </div>
          </div>
        </template>
      </el-empty>

      <div v-else class="advice-list">
        <div
          v-for="(advice, index) in adviceList"
          :key="index"
          class="advice-item"
        >
          <div class="advice-header">
            <el-tag :type="getAdviceTypeColor(advice.type)">
              {{ advice.type }}
            </el-tag>
            <span class="advice-time">{{ advice.time }}</span>
          </div>
          <div class="advice-content">
            {{ advice.content }}
          </div>
          <div class="advice-assets" v-if="advice.relatedAssets && advice.relatedAssets.length > 0">
            <span class="assets-label">相关资产：</span>
            <el-tag
              v-for="asset in advice.relatedAssets"
              :key="asset"
              size="small"
              class="asset-tag"
            >
              {{ asset }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Lock } from '@element-plus/icons-vue'

const loading = ref(false)

interface AdviceItem {
  type: string
  time: string
  content: string
  relatedAssets?: string[]
}

const adviceList = ref<AdviceItem[]>([])

function getAdviceTypeColor(type: string): string {
  const colorMap: Record<string, string> = {
    '调仓建议': 'warning',
    '风险提示': 'danger',
    '收益分析': 'success',
    '策略建议': 'primary',
    '资产配置': 'info'
  }
  return colorMap[type] || ''
}

async function generateAdvice() {
  loading.value = true

  // 模拟AI生成建议
  setTimeout(() => {
    const mockAdvices: AdviceItem[] = [
      {
        type: '调仓建议',
        time: new Date().toLocaleString('zh-CN'),
        content: '根据当前市场情况，建议适当增加债券配置比例，降低股票配置比例。建议将债券配置从20%提升至30%，股票配置从50%降低至40%。',
        relatedAssets: ['沪深300', '中证国债']
      },
      {
        type: '风险提示',
        time: new Date().toLocaleString('zh-CN'),
        content: '检测到投资组合中单一资产占比过高，存在集中风险。建议适当分散投资，降低单一资产暴露风险。',
        relatedAssets: ['茅台']
      },
      {
        type: '收益分析',
        time: new Date().toLocaleString('zh-CN'),
        content: '过去30天投资组合收益率达到3.5%，跑赢市场平均水平2.1个百分点。主要收益来源于科技板块的出色表现。',
        relatedAssets: ['科技ETF', '新能源ETF']
      },
      {
        type: '策略建议',
        time: new Date().toLocaleString('zh-CN'),
        content: '建议启用"涨跌幅监控"策略，当单个资产涨跌幅超过10%时自动触发提醒，帮助及时把握投资机会。',
        relatedAssets: []
      }
    ]

    adviceList.value = mockAdvices
    loading.value = false
    ElMessage.success('AI建议生成成功')
  }, 1500)
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.advice-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.advice-item {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  transition: all 0.3s;
}

.advice-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.advice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.advice-time {
  color: #909399;
  font-size: 12px;
}

.advice-content {
  color: #303133;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 12px;
}

.advice-assets {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.assets-label {
  color: #909399;
  font-size: 12px;
}

.asset-tag {
  margin: 0;
}

.feature-not-available {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
}

.feature-not-available .el-icon {
  margin-bottom: 20px;
}

.feature-text {
  text-align: center;
}

.feature-text h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}

.feature-text p {
  font-size: 14px;
  color: #606266;
  margin: 0;
}
</style>
