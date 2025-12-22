<script setup>
import { ref } from 'vue';
import { RouterLink, RouterView } from 'vue-router';
</script>

<template>
  <div id="app">
    <header class="app-header">
      <div class="app-logo">
        <h1>八方策金融座舱</h1>
      </div>
      <nav class="app-nav">
        <RouterLink to="/" class="nav-link" active-class="active">持仓管理</RouterLink>
        <RouterLink to="/settings" class="nav-link" active-class="active">策略配置</RouterLink>
      </nav>
      <div class="app-user">
        <button class="user-btn">用户菜单</button>
      </div>
    </header>
    
    <main class="app-main">
      <RouterView />
    </main>
    
    <footer class="app-footer">
      <p>© 2024 八方策金融座舱. 保留所有权利.</p>
    </footer>
  </div>
</template>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  color: #333;
  background-color: #f5f5f5;
}

/* 应用容器 */
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 头部样式 */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background-color: #2196F3;
  color: white;
  height: 60px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-logo h1 {
  font-size: 20px;
  font-weight: bold;
}

.app-nav {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 10px 15px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: bold;
}

.app-user .user-btn {
  background-color: transparent;
  color: white;
  border: 1px solid white;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.app-user .user-btn:hover {
  background-color: white;
  color: #2196F3;
}

/* 主体内容 */
.app-main {
  flex: 1;
  padding: 20px;
}

/* 底部样式 */
.app-footer {
  background-color: #333;
  color: white;
  text-align: center;
  padding: 10px;
  font-size: 14px;
}
</style>