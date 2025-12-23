import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000', // 后端API地址
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
});

// 持仓管理相关API
export default {
  // 用户认证相关API
  auth: {
    login: (credentials) => api.post('/auth/login', credentials),
    register: (userData) => api.post('/auth/register', userData),
    logout: () => api.post('/auth/logout')
  },
  
  // 仪表盘相关API
  dashboard: {
    getOverview: () => api.get('/dashboard/overview'),
    getPortfolioStats: () => api.get('/dashboard/portfolio-stats'),
    getLatestTransactions: () => api.get('/dashboard/latest-transactions'),
    getMarketTrends: () => api.get('/dashboard/market-trends')
  },
  
  // 持仓管理相关API
  holdings: {
    // 获取所有持仓
    getAll: () => api.get('/api/portfolio/'),
    
    // 添加持仓
    add: (holdingData) => api.post('/api/portfolio/', holdingData),
    
    // 更新持仓
    update: (id, holdingData) => api.put(`/api/portfolio/${id}`, holdingData),
    
    // 删除持仓
    delete: (id) => api.delete(`/api/portfolio/${id}`),
    
    // 强制同步数据
    forceSync: () => api.post('/api/portfolio/sync'),
    
    // 获取资产配置
    getAssetAllocation: () => api.get('/api/portfolio/allocation')
  },
  
  // 收益分析相关API
  performance: {
    getDailyPerformance: () => api.get('/performance/daily'),
    getMonthlyPerformance: () => api.get('/performance/monthly'),
    getYearlyPerformance: () => api.get('/performance/yearly'),
    getComparison: () => api.get('/performance/comparison')
  },
  
  // 市场数据相关API
  market: {
    getIndexData: () => api.get('/market/indexes'),
    getSectorPerformance: () => api.get('/market/sectors'),
    getStockRankings: () => api.get('/market/rankings')
  },
  
  // 系统设置相关API
  settings: {
    getSettings: () => api.get('/settings'),
    updateSettings: (settingsData) => api.put('/settings', settingsData)
  }
};