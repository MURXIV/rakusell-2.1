import { defineStore } from 'pinia'
import { authAPI } from '@/api'
import api from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    isAdmin: (state) => state.user?.role === 'admin',
  },

  actions: {
    async login(username, password) {
      const { data } = await authAPI.login({ username, password })
      this.accessToken = data.access
      this.refreshToken = data.refresh
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      await this.fetchMe()
    },

    async fetchMe() {
      try {
        const { data } = await api.get('/users/me/')
        this.user = data
        localStorage.setItem('user', JSON.stringify(data))
      } catch {}
    },

    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    },
  },
})
