<template>
  <div class="portfolio-container">
    <h1>持仓管理</h1>
    
    <div class="portfolio-header">
      <button @click="forceSyncData" class="sync-btn">强制同步数据</button>
      <button @click="showAddModal = true" class="create-btn">添加持仓</button>
      <button @click="viewAssetAllocation" class="allocation-btn">资产配置</button>
      <div class="search-container">
        <input type="text" v-model="searchKeyword" placeholder="搜索持仓..." class="search-input">
        <button @click="handleSearch" class="search-btn">搜索</button>
        <button v-if="searchKeyword" @click="clearSearch" class="clear-btn">清除</button>
      </div>
    </div>
    
    <!-- 持仓列表 -->
    <div class="holdings-container">
      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else-if="holdings.length === 0" class="empty-state">
        <p>暂无持仓记录</p>
      </div>
      
      <div v-else class="holdings-table-container">
        <table class="holdings-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>类型</th>
              <th>代码</th>
              <th>名称</th>
              <th>类别</th>
              <th>份额</th>
              <th>成本价</th>
              <th>当前价</th>
              <th>成本总额</th>
              <th>当前总额</th>
              <th>盈亏额</th>
              <th>盈亏率</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="holding in holdings" :key="holding.id" :class="{'profit': (holding.current_price - holding.purchase_price) > 0, 'loss': (holding.current_price - holding.purchase_price) < 0}">
              <td>{{ holding.id }}</td>
              <td>{{ getProductTypeText(holding.product_type) }}</td>
              <td>{{ holding.product_code }}</td>
              <td>{{ holding.product_name }}</td>
              <td>{{ getCategoryText(holding.category) }}</td>
              <td>{{ holding.quantity.toFixed(2) }}</td>
              <td>{{ holding.purchase_price.toFixed(2) }}</td>
              <td>{{ holding.current_price.toFixed(2) }}</td>
              <td>{{ (holding.quantity * holding.purchase_price).toFixed(2) }}</td>
              <td>{{ (holding.quantity * holding.current_price).toFixed(2) }}</td>
              <td>{{ ((holding.quantity * holding.current_price) - (holding.quantity * holding.purchase_price)).toFixed(2) }}</td>
              <td>{{ (((holding.current_price - holding.purchase_price) / holding.purchase_price) * 100).toFixed(2) }}%</td>
              <td>
                <button @click="editHolding(holding)" class="edit-btn">编辑</button>
                <button @click="deleteHolding(holding.id)" class="delete-btn">删除</button>
              </td>
            </tr>
          </tbody>
          <tfoot v-if="totalStats">
            <tr>
              <td colspan="8">总计</td>
              <td>{{ totalStats.total_cost.toFixed(2) }}</td>
              <td>{{ totalStats.total_current.toFixed(2) }}</td>
              <td :class="{'profit': totalStats.total_profit > 0, 'loss': totalStats.total_profit < 0}">{{ totalStats.total_profit.toFixed(2) }}</td>
              <td :class="{'profit': totalStats.total_profit_rate > 0, 'loss': totalStats.total_profit_rate < 0}">{{ totalStats.total_profit_rate.toFixed(2) }}%</td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
    
    <!-- 添加持仓模态框 -->
    <div v-if="showAddModal" class="modal-overlay" @click="showAddModal = false">
      <div class="modal-content" @click.stop>
        <h2>添加持仓</h2>
        <form @submit.prevent="addHolding">
          <div class="form-group">
            <label for="productCode">产品代码</label>
            <input type="text" id="productCode" v-model="newHolding.product_code" required placeholder="输入6位股票/基金代码">
          </div>
          <div class="form-group" v-if="newHolding.product_name">
            <label>产品名称</label>
            <input type="text" :value="newHolding.product_name" readonly>
          </div>
          <div class="form-group" v-if="newHolding.product_type">
            <label>产品类型</label>
            <input type="text" :value="getProductTypeText(newHolding.product_type)" readonly>
          </div>
          <div class="form-group">
            <label for="quantity">持仓份额</label>
            <input type="number" id="quantity" v-model.number="newHolding.quantity" step="0.01" min="0.01" required>
          </div>
          <div class="form-group">
            <label for="purchasePrice">持仓成本</label>
            <input type="number" id="purchasePrice" v-model.number="newHolding.purchase_price" step="0.01" min="0" required>
          </div>
          <div class="form-group">
            <label for="category">资产类别</label>
            <select id="category" v-model="newHolding.category" required>
              <option value="china_stock_etf">中国股票或指数ETF</option>
              <option value="foreign_stock_etf">海外股票或指数ETF</option>
              <option value="commodity">大宗商品</option>
              <option value="gold">黄金</option>
              <option value="long_bond">长债</option>
              <option value="short_bond">短债</option>
              <option value="credit_bond">信用债</option>
              <option value="cash">现金</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" @click="resetAddForm" class="cancel-btn">取消</button>
            <button type="submit" class="confirm-btn" :disabled="!isAddFormValid">确认添加</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 更新持仓模态框 -->
    <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
      <div class="modal-content" @click.stop>
        <h2>更新持仓</h2>
        <form @submit.prevent="updateHolding">
          <div class="form-group">
            <label>ID</label>
            <input type="text" v-model="editingHolding.id" readonly>
          </div>
          <div class="form-group">
            <label>产品代码</label>
            <input type="text" v-model="editingHolding.product_code" readonly>
          </div>
          <div class="form-group">
            <label>产品名称</label>
            <input type="text" v-model="editingHolding.product_name" readonly>
          </div>
          <div class="form-group">
            <label>产品类型</label>
            <input type="text" :value="getProductTypeText(editingHolding.product_type)" readonly>
          </div>
          <div class="form-group">
            <label for="editQuantity">持仓份额</label>
            <input type="number" id="editQuantity" v-model.number="editingHolding.quantity" step="0.01" min="0.01" required>
          </div>
          <div class="form-group">
            <label for="editPurchasePrice">持仓成本</label>
            <input type="number" id="editPurchasePrice" v-model.number="editingHolding.purchase_price" step="0.01" min="0" required>
          </div>
          <div class="form-group">
            <label for="editCategory">资产类别</label>
            <select id="editCategory" v-model="editingHolding.category" required>
              <option value="china_stock_etf">中国股票或指数ETF</option>
              <option value="foreign_stock_etf">海外股票或指数ETF</option>
              <option value="commodity">大宗商品</option>
              <option value="gold">黄金</option>
              <option value="long_bond">长债</option>
              <option value="short_bond">短债</option>
              <option value="credit_bond">信用债</option>
              <option value="cash">现金</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showEditModal = false" class="cancel-btn">取消</button>
            <button type="submit" class="confirm-btn">确认更新</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 资产配置模态框 -->
    <div v-if="showAllocationModal" class="modal-overlay" @click="showAllocationModal = false">
      <div class="modal-content" @click.stop>
        <h2>资产配置报告</h2>
        <div v-if="allocationLoading" class="loading">加载中...</div>
        <div v-else-if="!assetAllocation" class="empty-state">
          <p>无法获取资产配置数据</p>
        </div>
        <div v-else>
          <div class="allocation-summary">
            <p>总市值: {{ assetAllocation.total_value.toFixed(2) }}元</p>
          </div>
          <div class="allocation-list">
            <div v-for="(data, category) in assetAllocation.categories" :key="category" class="allocation-item">
              <div class="allocation-info">
                <span class="category-name">{{ getCategoryText(category) }}</span>
                <span class="category-value">{{ data.market_value.toFixed(2) }}元</span>
              </div>
              <div class="allocation-bar">
                <div class="allocation-progress" :style="{ width: `${data.percentage.toFixed(2)}%` }"></div>
              </div>
              <div class="allocation-percentage">{{ data.percentage.toFixed(2) }}%</div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button type="button" @click="showAllocationModal = false" class="cancel-btn">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../services/api.js';
import axios from 'axios'; // 直接导入axios

// 状态管理
const holdings = ref([]);
const loading = ref(false);
const showAddModal = ref(false);
const showEditModal = ref(false);
const showAllocationModal = ref(false);
const allocationLoading = ref(false);
const assetAllocation = ref(null);
// 搜索相关状态
const searchKeyword = ref('');
const isSearching = ref(false);
const isSearchActive = ref(false);
// 新持仓数据
const newHolding = ref({
  product_code: '',
  product_name: '',
  product_type: '',
  quantity: 0,
  purchase_price: 0,
  category: 'china_stock_etf'
});

// 编辑持仓数据
const editingHolding = ref({});

// 总计数据
const totalStats = computed(() => {
  if (holdings.value.length === 0) return null;
  
  let totalCost = 0;
  let totalCurrent = 0;
  
  holdings.value.forEach(holding => {
    totalCost += holding.quantity * holding.purchase_price;
    totalCurrent += holding.quantity * holding.current_price;
  });
  
  const totalProfit = totalCurrent - totalCost;
  const totalProfitRate = totalCost > 0 ? (totalProfit / totalCost * 100) : 0;
  
  return {
    total_cost: totalCost,
    total_current: totalCurrent,
    total_profit: totalProfit,
    total_profit_rate: totalProfitRate
  };
});

// 检查添加表单是否有效
const isAddFormValid = computed(() => {
  return newHolding.value.product_code && 
         newHolding.value.product_name && 
         newHolding.value.product_type && 
         newHolding.value.quantity > 0 && 
         newHolding.value.purchase_price >= 0;
});

// 获取产品类型文本
const getProductTypeText = (type) => {
  const typeMap = {
    'stock': '股票',
    'etf': 'ETF',
    'fund': '基金'
  };
  return typeMap[type] || type;
};

// 获取资产类别文本
const getCategoryText = (category) => {
  const categoryMap = {
    'china_stock_etf': '中国股票/ETF',
    'foreign_stock_etf': '海外股票/ETF',
    'commodity': '大宗商品',
    'gold': '黄金',
    'long_bond': '长债',
    'short_bond': '短债',
    'credit_bond': '信用债',
    'cash': '现金'
  };
  return categoryMap[category] || category;
};

// 加载持仓数据
const loadHoldings = async () => {
  loading.value = true;
  try {
    const response = await axios.get('http://localhost:8000/api/portfolio/');
    if (response.status === 200 && Array.isArray(response.data)) {
      holdings.value = response.data;
    }
  } catch (error) {
    console.error('获取持仓失败:', error);
    alert('获取持仓失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 搜索持仓
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    alert('请输入搜索关键词');
    return;
  }
  
  isSearching.value = true;
  try {
    const response = await api.holdings.search(searchKeyword.value.trim());
    holdings.value = response;
    isSearchActive.value = true;
  } catch (error) {
    console.error('搜索持仓失败:', error);
    alert('搜索持仓失败，请稍后重试');
  } finally {
    isSearching.value = false;
  }
};

// 清除搜索
const clearSearch = () => {
  searchKeyword.value = '';
  isSearchActive.value = false;
  loadHoldings();
};

// 添加持仓
const addHolding = async () => {
  try {
    await api.holdings.add(newHolding.value);
    showAddModal.value = false;
    resetAddForm();
    loadHoldings();
    alert('持仓添加成功');
  } catch (error) {
    console.error('添加持仓失败:', error);
    alert('添加持仓失败，请稍后重试');
  }
};

// 更新持仓
const updateHolding = async () => {
  try {
    await api.holdings.update(editingHolding.value.id, {
      quantity: editingHolding.value.quantity,
      purchase_price: editingHolding.value.purchase_price,
      category: editingHolding.value.category
    });
    showEditModal.value = false;
    loadHoldings();
    alert('持仓更新成功');
  } catch (error) {
    console.error('更新持仓失败:', error);
    alert('更新持仓失败，请稍后重试');
  }
};

// 删除持仓
const deleteHolding = async (id) => {
  if (confirm('确定要删除这个持仓吗？')) {
    try {
      await api.holdings.delete(id);
      loadHoldings();
      alert('持仓删除成功');
    } catch (error) {
      console.error('删除持仓失败:', error);
      alert('删除持仓失败，请稍后重试');
    }
  }
};

// 编辑持仓
const editHolding = (holding) => {
  editingHolding.value = { ...holding };
  showEditModal.value = true;
};

// 强制同步数据
const forceSyncData = async () => {
  if (confirm('确认要强制同步所有持仓数据吗？')) {
    try {
      await api.holdings.forceSync();
      loadHoldings();
      alert('数据同步成功');
    } catch (error) {
      console.error('同步数据失败:', error);
      alert('同步数据失败，请稍后重试');
    }
  }
};

// 查看资产配置
const viewAssetAllocation = async () => {
  allocationLoading.value = true;
  try {
    const response = await api.holdings.getAssetAllocation();
    assetAllocation.value = response;
    showAllocationModal.value = true;
  } catch (error) {
    console.error('获取资产配置失败:', error);
    alert('获取资产配置失败，请稍后重试');
  } finally {
    allocationLoading.value = false;
  }
};

// 重置添加表单
const resetAddForm = () => {
  newHolding.value = {
    product_code: '',
    product_name: '',
    product_type: '',
    quantity: 0,
    purchase_price: 0,
    category: 'china_stock_etf'
  };
};

// 监听产品代码变化，自动获取产品信息
const watchProductCode = () => {
  if (newHolding.value.product_code.length === 6) {
    // 这里可以添加自动获取产品信息的逻辑
    // 使用API查询产品信息
  }
};

// 生命周期钩子
onMounted(() => {
  loadHoldings();
});
</script>

<style scoped>
.portfolio-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.portfolio-header {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.search-container {
  display: flex;
  gap: 5px;
  margin-left: auto;
}

.search-input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 250px;
}

.search-btn, .clear-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.search-btn {
  background-color: #2196F3;
  color: white;
}

.clear-btn {
  background-color: #f44336;
  color: white;
}

.sync-btn, .create-btn, .allocation-btn {
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

.allocation-btn {
  background-color: #FF9800;
  color: white;
}

.holdings-container {
  margin-top: 20px;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.holdings-table-container {
  overflow-x: auto;
}

.holdings-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.holdings-table th, .holdings-table td {
  padding: 12px;
  text-align: right;
  border-bottom: 1px solid #ddd;
}

.holdings-table th {
  background-color: #f5f5f5;
  font-weight: bold;
  text-align: center;
}

.holdings-table tr:hover {
  background-color: #f9f9f9;
}

.holdings-table tr.profit td:last-child {
  color: #4CAF50;
}

.holdings-table tr.loss td:last-child {
  color: #f44336;
}

.edit-btn, .delete-btn {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin: 0 2px;
}

.edit-btn {
  background-color: #2196F3;
  color: white;
}

.delete-btn {
  background-color: #f44336;
  color: white;
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
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
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

.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
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

.confirm-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 资产配置样式 */
.allocation-summary {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.allocation-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.allocation-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.allocation-info {
  display: flex;
  flex-direction: column;
  width: 150px;
}

.category-name {
  font-weight: bold;
}

.allocation-bar {
  flex: 1;
  height: 20px;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.allocation-progress {
  height: 100%;
  background-color: #2196F3;
  border-radius: 10px;
}

.allocation-percentage {
  width: 80px;
  text-align: right;
  font-weight: bold;
}
</style>