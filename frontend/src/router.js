import { createRouter, createWebHistory } from 'vue-router';

// 导入页面组件
import Portfolio from './views/Portfolio.vue';
import Settings from './views/Settings.vue';

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Portfolio',
    component: Portfolio
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
