// API调用封装

// 基础API URL
const API_BASE_URL = 'http://localhost:8000';

// 请求方法封装
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // 设置默认请求头
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };

  // 获取token
  const token = localStorage.getItem('token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : null
    });

    // 处理响应
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API请求错误:', error);
    throw error;
  }
}

// 导出API方法
export default {
  // 认证相关
  auth: {
    login: (credentials) => request('/api/auth/login', {
      method: 'POST',
      body: credentials
    }),
    register: (userData) => request('/api/auth/register', {
      method: 'POST',
      body: userData
    })
  },

  // 持仓相关
  portfolio: {
    // 获取持仓列表
    getList: () => request('/api/portfolio/list'),
    // 获取持仓详情
    getDetail: (id) => request(`/api/portfolio/${id}`),
    // 创建持仓
    create: (data) => request('/api/portfolio', {
      method: 'POST',
      body: data
    }),
    // 更新持仓
    update: (id, data) => request(`/api/portfolio/${id}`, {
      method: 'PUT',
      body: data
    }),
    // 删除持仓
    delete: (id) => request(`/api/portfolio/${id}`, {
      method: 'DELETE'
    }),
    // 同步持仓数据
    sync: (id) => request(`/api/portfolio/${id}/sync`, {
      method: 'POST'
    })
  },

  // AI建议相关
  aiAdvisor: {
    getSuggestion: (portfolioId) => request(`/api/ai-advisor/${portfolioId}`)
  }
};
