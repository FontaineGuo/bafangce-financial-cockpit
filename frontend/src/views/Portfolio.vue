<template>
  <div class="portfolio-container">
    <h1>持仓管理</h1>
    
    <div class="portfolio-header">
      <button @click="syncData" class="sync-btn">同步数据</button>
      <button @click="showCreateModal = true" class="create-btn">创建持仓</button>
    </div>
    
    <div class="portfolio-grid">
      <div v-for="portfolio in portfolios" :key="portfolio.id" class="portfolio-card">
        <div class="portfolio-header">
          <h3>{{ portfolio.name }}</h3>
          <div class="portfolio-actions">
            <button @click="viewDetails(portfolio.id)" class="detail-btn">查看详情</button>
            <button @click="deletePortfolio(portfolio.id)" class="delete-btn">删除</button>
          </div>
        </div>
        <div class="portfolio-info">
          <p>总市值: {{ portfolio.total_value.toFixed(2) }}元</p>
          <p>收益率: {{ portfolio.return_rate.toFixed(2) }}%</p>
          <p>更新时间: {{ formatDate(portfolio.updated_at) }}</p>
        </div>
      </div>
    </div>
    
    <!-- 创建持仓模态框 -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal-content" @click.stop>
        <h2>创建持仓</h2>
        <form @submit.prevent="createPortfolio">
          <div class="form-group">
            <label for="portfolioName">持仓名称</label>
            <input type="text" id="portfolioName" v-model="newPortfolio.name" required>
          </div>
          <div class="form-group">
            <label for="portfolioDescription">描述</label>
            <textarea id="portfolioDescription" v-model="newPortfolio.description"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="cancel-btn">取消</button>
            <button type="submit" class="confirm-btn">创建</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api.js';

export default {
  name: 'Portfolio',
  data() {
    return {
      portfolios: [],
      showCreateModal: false,
      newPortfolio: {
        name: '',
        description: ''
      }
    };
  },
  mounted() {
    this.fetchPortfolios();
  },
  methods: {
    async fetchPortfolios() {
      try {
        const response = await api.portfolio.getList();
        this.portfolios = response.data;
      } catch (error) {
        console.error('获取持仓列表失败:', error);
        alert('获取持仓列表失败，请稍后重试');
      }
    },
    async syncData() {
      try {
        // 模拟同步数据
        alert('数据同步中...');
        // 这里可以根据需要同步所有或特定持仓
        // 例如：await api.portfolio.sync(portfolioId);
        await new Promise(resolve => setTimeout(resolve, 1500));
        alert('数据同步完成');
        this.fetchPortfolios(); // 刷新数据
      } catch (error) {
        console.error('同步数据失败:', error);
        alert('同步数据失败，请稍后重试');
      }
    },
    async createPortfolio() {
      try {
        await api.portfolio.create(this.newPortfolio);
        this.showCreateModal = false;
        this.newPortfolio = { name: '', description: '' };
        this.fetchPortfolios(); // 刷新数据
        alert('持仓创建成功');
      } catch (error) {
        console.error('创建持仓失败:', error);
        alert('创建持仓失败，请稍后重试');
      }
    },
    async deletePortfolio(id) {
      if (confirm('确定要删除这个持仓吗？')) {
        try {
          await api.portfolio.delete(id);
          this.fetchPortfolios(); // 刷新数据
          alert('持仓删除成功');
        } catch (error) {
          console.error('删除持仓失败:', error);
          alert('删除持仓失败，请稍后重试');
        }
      }
    },
    viewDetails(id) {
      // 跳转到持仓详情页面
      // this.$router.push(`/portfolio/${id}`);
      alert(`查看持仓 ${id} 的详情`);
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    }
  }
};
</script>

<style scoped>
.portfolio-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.portfolio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.sync-btn, .create-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.sync-btn {
  background-color: #4CAF50;
  color: white;
}

.create-btn {
  background-color: #2196F3;
  color: white;
}

.portfolio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.portfolio-card {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.portfolio-card .portfolio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.portfolio-card h3 {
  margin: 0;
  color: #333;
}

.portfolio-actions {
  display: flex;
  gap: 10px;
}

.detail-btn, .delete-btn {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.detail-btn {
  background-color: #2196F3;
  color: white;
}

.delete-btn {
  background-color: #f44336;
  color: white;
}

.portfolio-info p {
  margin: 5px 0;
  color: #666;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  padding: 30px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-content h2 {
  margin-top: 0;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: bold;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.cancel-btn, .confirm-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.cancel-btn {
  background-color: #9e9e9e;
  color: white;
}

.confirm-btn {
  background-color: #2196F3;
  color: white;
}
</style>
