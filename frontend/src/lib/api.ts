import axios, { AxiosError } from 'axios'

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const MCP_URL = import.meta.env.VITE_MCP_URL || 'http://localhost:8765'

export const api = axios.create({
  baseURL: API_URL,
  timeout: 8000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (resp) => resp,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('jwt')
      localStorage.removeItem('refresh')
      if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/finca/')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

// ------- Endpoints helpers (con fallback mock si BE no responde) ----

export async function safeGet<T>(path: string, fallback: T): Promise<T> {
  try {
    const { data } = await api.get<T>(path)
    return data
  } catch {
    return fallback
  }
}
