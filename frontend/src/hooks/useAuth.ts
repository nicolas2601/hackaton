import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { api } from '../lib/api'
import { MOCK_USER, type User } from '../lib/mocks'

interface LoginPayload { email: string; password: string }

interface AuthState {
  token: string | null
  refresh: string | null
  user: User | null
  isAuthenticated: boolean
  login: (payload: LoginPayload) => Promise<void>
  logout: () => void
  hydrateToken: () => void
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      refresh: null,
      user: null,
      isAuthenticated: false,

      login: async ({ email, password }) => {
        // Try backend first; fall back to mock credential for demo resiliency.
        try {
          const { data } = await api.post('/api/auth/login/', { email, password })
          const accessToken: string = data.access ?? data.token ?? ''
          const refreshToken: string = data.refresh ?? ''
          if (!accessToken) throw new Error('no-token')

          localStorage.setItem('jwt', accessToken)
          if (refreshToken) localStorage.setItem('refresh', refreshToken)

          const user: User = data.user ?? MOCK_USER
          set({ token: accessToken, refresh: refreshToken, user, isAuthenticated: true })
          return
        } catch (err) {
          // Mock credentials (demo-safe)
          if (email === 'efrain@sanvicente.co' && password === 'cacao123') {
            const mockToken = `mock.${btoa(email)}.${Date.now()}`
            localStorage.setItem('jwt', mockToken)
            set({ token: mockToken, refresh: null, user: MOCK_USER, isAuthenticated: true })
            return
          }
          throw err instanceof Error ? err : new Error('login-failed')
        }
      },

      logout: () => {
        localStorage.removeItem('jwt')
        localStorage.removeItem('refresh')
        set({ token: null, refresh: null, user: null, isAuthenticated: false })
      },

      hydrateToken: () => {
        const token = localStorage.getItem('jwt')
        if (token && !get().token) {
          set({ token, isAuthenticated: true, user: get().user ?? MOCK_USER })
        }
      },
    }),
    {
      name: 'cacaotrace-auth',
      partialize: (s) => ({ token: s.token, refresh: s.refresh, user: s.user, isAuthenticated: s.isAuthenticated }),
    },
  ),
)
