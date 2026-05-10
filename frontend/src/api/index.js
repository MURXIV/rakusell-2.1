import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refresh = localStorage.getItem('refresh_token')
        const { data } = await axios.post('http://localhost:8000/api/v1/auth/token/refresh/', { refresh })
        localStorage.setItem('access_token', data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api

// Resource helpers
export const authAPI = {
  login: (credentials) => api.post('/auth/token/', credentials),
  refresh: (refresh) => api.post('/auth/token/refresh/', { refresh }),
}

export const chatsAPI = {
  list: (params) => api.get('/chats/', { params }),
  get: (id) => api.get(`/chats/${id}/`),
  messages: (id, params) => api.get(`/chats/${id}/messages/`, { params }),
}

export const clientsAPI = {
  list: (params) => api.get('/clients/', { params }),
  get: (id) => api.get(`/clients/${id}/`),
  update: (id, data) => api.patch(`/clients/${id}/`, data),
}

export const messagesAPI = {
  send: (data) => api.post('/messages/send/', data),
}

export const promptsAPI = {
  list: () => api.get('/prompts/'),
  get: (id) => api.get(`/prompts/${id}/`),
  create: (data) => api.post('/prompts/', data),
  update: (id, data) => api.put(`/prompts/${id}/`, data),
  delete: (id) => api.delete(`/prompts/${id}/`),
  active: (scenario) => api.get('/prompts/active/', { params: { scenario } }),
}

export const knowledgeAPI = {
  list: () => api.get('/knowledge/'),
  get: (id) => api.get(`/knowledge/${id}/`),
  create: (data) => api.post('/knowledge/', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  delete: (id) => api.delete(`/knowledge/${id}/`),
}

export const logsAPI = {
  list: (params) => api.get('/logs/', { params }),
}

export const monitoringAPI = {
  health: () => api.get('/monitoring/health/'),
  queues: () => api.get('/monitoring/health/queues/'),
  stats: () => api.get('/monitoring/health/stats/'),
}
