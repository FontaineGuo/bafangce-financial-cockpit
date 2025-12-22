<template>
  <div class="settings-container">
    <h1>策略配置</h1>
    
    <div class="settings-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id" 
        :class="['tab-btn', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.name }}
      </button>
    </div>
    
    <div class="settings-content">
      <!-- 基础配置 -->
      <div v-if="activeTab === 'basic'" class="settings-section">
        <h2>基础配置</h2>
        <div class="settings-grid">
          <div class="setting-item">
            <label for="refreshInterval">数据刷新间隔（分钟）</label>
            <input 
              type="number" 
              id="refreshInterval" 
              v-model.number="settings.refreshInterval" 
              min="1" 
              max="60"
            >
          </div>
          <div class="setting-item">
            <label for="defaultPortfolio">默认持仓</label>
            <select id="defaultPortfolio" v-model="settings.defaultPortfolio">
              <option value="">选择持仓</option>
              <option 
                v-for="portfolio in portfolios" 
                :key="portfolio.id" 
                :value="portfolio.id"
              >
                {{ portfolio.name }}
              </option>
            </select>
          </div>
        </div>
      </div>
      
      <!-- 策略参数 -->
      <div v-if="activeTab === 'strategy'" class="settings-section">
        <h2>策略参数</h2>
        <div class="settings-grid">
          <div class="setting-item">
            <label for="riskLevel">风险等级</label>
            <select id="riskLevel" v-model="settings.riskLevel">
              <option value="low">低风险</option>
              <option value="medium">中风险</option>
              <option value="high">高风险</option>
            </select>
          </div>
          <div class="setting-item">
            <label for="maxStocks">最大股票数量</label>
            <input 
              type="number" 
              id="maxStocks" 
              v-model.number="settings.maxStocks" 
              min="5" 
              max="30"
            >
          </div>
          <div class="setting-item">
            <label for="minDiversification">最小行业分散度</label>
            <input 
              type="number" 
              id="minDiversification" 
              v-model.number="settings.minDiversification" 
              min="2" 
              max="10"
            >
          </div>
          <div class="setting-item">
            <label for="maxAllocation">单只股票最大配置比例（%）</label>
            <input 
              type="number" 
              id="maxAllocation" 
              v-model.number="settings.maxAllocation" 
              min="5" 
              max="50"
            >
          </div>
        </div>
      </div>
      
      <!-- AI配置 -->
      <div v-if="activeTab === 'ai'" class="settings-section">
        <h2>AI建议配置</h2>
        <div class="settings-grid">
          <div class="setting-item">
            <label for="aiEnabled">启用AI建议</label>
            <input type="checkbox" id="aiEnabled" v-model="settings.aiEnabled">
          </div>
          <div class="setting-item" v-if="settings.aiEnabled">
            <label for="aiModel">AI模型</label>
            <select id="aiModel" v-model="settings.aiModel">
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              <option value="gpt-4">GPT-4</option>
            </select>
          </div>
          <div class="setting-item" v-if="settings.aiEnabled">
            <label for="aiFrequency">AI建议频率</label>
            <select id="aiFrequency" v-model="settings.aiFrequency">
              <option value="daily">每日</option>
              <option value="weekly">每周</option>
              <option value="monthly">每月</option>
            </select>
          </div>
        </div>
      </div>
      
      <!-- 通知设置 -->
      <div v-if="activeTab === 'notifications'" class="settings-section">
        <h2>通知设置</h2>
        <div class="settings-grid">
          <div class="setting-item">
            <label for="priceAlerts">价格提醒</label>
            <input type="checkbox" id="priceAlerts" v-model="settings.priceAlerts">
          </div>
          <div class="setting-item" v-if="settings.priceAlerts">
            <label for="priceThreshold">价格变动阈值（%）</label>
            <input 
              type="number" 
              id="priceThreshold" 
              v-model.number="settings.priceThreshold" 
              min="0.5" 
              max="10"
              step="0.5"
            >
          </div>
          <div class="setting-item">
            <label for="newsAlerts">新闻提醒</label>
            <input type="checkbox" id="newsAlerts" v-model="settings.newsAlerts">
          </div>
        </div>
      </div>
    </div>
    
    <div class="settings-actions">
      <button @click="resetSettings" class="reset-btn">重置</button>
      <button @click="saveSettings" class="save-btn">保存配置</button>
    </div>
  </div>
</template>

<script>
import api from '../services/api.js';

export default {
  name: 'Settings',
  data() {
    return {
      tabs: [
        { id: 'basic', name: '基础配置' },
        { id: 'strategy', name: '策略参数' },
        { id: 'ai', name: 'AI配置' },
        { id: 'notifications', name: '通知设置' }
      ],
      activeTab: 'basic',
      portfolios: [],
      settings: {
        refreshInterval: 30,
        defaultPortfolio: '',
        riskLevel: 'medium',
        maxStocks: 15,
        minDiversification: 5,
        maxAllocation: 20,
        aiEnabled: true,
        aiModel: 'gpt-3.5-turbo',
        aiFrequency: 'weekly',
        priceAlerts: true,
        priceThreshold: 5,
        newsAlerts: false
      },
      originalSettings: {}
    };
  },
  mounted() {
    this.loadSettings();
    this.loadPortfolios();
  },
  methods: {
    async loadSettings() {
      try {
        // 从localStorage加载设置
        const savedSettings = localStorage.getItem('settings');
        if (savedSettings) {
          this.settings = JSON.parse(savedSettings);
        }
        // 保存原始设置用于重置
        this.originalSettings = { ...this.settings };
      } catch (error) {
        console.error('加载设置失败:', error);
      }
    },
    async loadPortfolios() {
      try {
        const response = await api.portfolio.getList();
        this.portfolios = response.data;
      } catch (error) {
        console.error('加载持仓列表失败:', error);
      }
    },
    async saveSettings() {
      try {
        // 保存到localStorage
        localStorage.setItem('settings', JSON.stringify(this.settings));
        // 这里可以添加保存到后端的逻辑
        // await api.settings.save(this.settings);
        alert('配置保存成功');
      } catch (error) {
        console.error('保存配置失败:', error);
        alert('保存配置失败，请稍后重试');
      }
    },
    resetSettings() {
      this.settings = { ...this.originalSettings };
      alert('配置已重置');
    }
  }
};
</script>

<style scoped>
.settings-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.settings-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background-color: transparent;
  color: #666;
  cursor: pointer;
  font-size: 16px;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  color: #2196F3;
}

.tab-btn.active {
  color: #2196F3;
  border-bottom-color: #2196F3;
}

.settings-content {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.settings-section {
  margin-bottom: 40px;
}

.settings-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-item label {
  color: #555;
  font-weight: bold;
}

.setting-item input,
.setting-item select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.setting-item input[type="checkbox"] {
  width: auto;
  margin-top: 5px;
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.reset-btn, .save-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
}

.reset-btn {
  background-color: #9e9e9e;
  color: white;
}

.save-btn {
  background-color: #2196F3;
  color: white;
}
</style>
