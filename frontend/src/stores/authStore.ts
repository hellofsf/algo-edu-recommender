import { create } from 'zustand'
import type { User } from '@/types'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  setUser: (user: User | null, token?: string | null) => void
  logout: () => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: (() => {
    try {
      const stored = localStorage.getItem('user')
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  })(),
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,

  setUser: (user, token) => {
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
      if (token) {
        localStorage.setItem('access_token', token)
      }
      set({ user, token: token ?? null, isAuthenticated: true })
    }
  },

  logout: () => {
    localStorage.removeItem('user')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, token: null, isAuthenticated: false })
  },

  setLoading: (loading) => set({ isLoading: loading }),
}))
