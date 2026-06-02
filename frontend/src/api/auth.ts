import apiClient from './client'
import type { LoginRequest, RegisterRequest, AuthResponse } from '@/types'

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', data)
    return response.data
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register', data)
    return response.data
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout')
  },

  refresh: async (refreshToken: string): Promise<{ access_token: string }> => {
    const response = await apiClient.post<{ access_token: string }>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me')
    return response.data
  },
}
