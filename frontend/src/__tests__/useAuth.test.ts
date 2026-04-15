import { describe, it, expect, beforeEach } from 'vitest'
import { useAuth } from '../hooks/useAuth'

describe('useAuth store', () => {
  beforeEach(() => {
    localStorage.clear()
    useAuth.getState().logout()
  })

  it('login con credenciales mock persiste token', async () => {
    await useAuth.getState().login({ email: 'efrain@sanvicente.co', password: 'cacao123' })
    const s = useAuth.getState()
    expect(s.isAuthenticated).toBe(true)
    expect(s.user?.email).toBe('efrain@sanvicente.co')
    expect(localStorage.getItem('jwt')).toBeTruthy()
  })

  it('logout limpia el estado', async () => {
    await useAuth.getState().login({ email: 'efrain@sanvicente.co', password: 'cacao123' })
    useAuth.getState().logout()
    expect(useAuth.getState().isAuthenticated).toBe(false)
    expect(localStorage.getItem('jwt')).toBeNull()
  })

  it('rechaza credenciales inválidas', async () => {
    await expect(
      useAuth.getState().login({ email: 'hacker@evil.com', password: 'wrong' }),
    ).rejects.toThrow()
  })
})
