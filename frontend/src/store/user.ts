import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string) {
    try {
      const response = await authApi.login({ username, password })
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)

      // 获取用户信息
      await fetchUser()
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  async function register(userData: { username: string; email: string; password: string }) {
    try {
      await authApi.register(userData)
      return true
    } catch (error) {
      console.error('Register failed:', error)
      return false
    }
  }

  async function fetchUser() {
    try {
      const response = await authApi.me()
      user.value = response.data
    } catch (error) {
      console.error('Fetch user failed:', error)
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    fetchUser,
    logout
  }
})
