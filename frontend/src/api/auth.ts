import apiClient from './index'
import type { UserCreate, User, Token } from '@/types'

export interface LoginData {
  username: string
  password: string
}

export const authApi = {
  // 用户注册
  register: (data: UserCreate) => {
    return apiClient.post<User>('/auth/register', data)
  },

  // 用户登录
  login: (data: LoginData) => {
    // 使用URLSearchParams而不是FormData，因为FastAPI的OAuth2PasswordRequestForm需要application/x-www-form-urlencoded格式
    const params = new URLSearchParams()
    params.append('username', data.username)
    params.append('password', data.password)
    return apiClient.post<Token>('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
  },

  // 获取当前用户信息
  me: () => {
    return apiClient.get<User>('/auth/me')
  }
}
