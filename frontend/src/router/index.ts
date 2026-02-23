import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/assets',
    name: 'Assets',
    component: () => import('@/views/Assets.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/portfolios',
    name: 'Portfolios',
    component: () => import('@/views/Portfolios.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/strategies',
    name: 'Strategies',
    component: () => import('@/views/Strategies.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-advisor',
    name: 'AIAdvisor',
    component: () => import('@/views/AIAdvisor.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && userStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
