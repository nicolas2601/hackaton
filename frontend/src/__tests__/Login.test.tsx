import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Login from '../pages/Login'
import { useAuth } from '../hooks/useAuth'

function setup() {
  return render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>,
  )
}

describe('Login page', () => {
  it('renderiza email, password y botón Entrar', () => {
    setup()
    expect(screen.getByPlaceholderText(/efrain@sanvicente/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText('••••••••')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument()
  })

  it('submit con credenciales mock autentica al usuario', async () => {
    useAuth.getState().logout()
    setup()
    fireEvent.change(screen.getByPlaceholderText(/efrain@sanvicente/i), {
      target: { value: 'efrain@sanvicente.co' },
    })
    fireEvent.change(screen.getByPlaceholderText('••••••••'), {
      target: { value: 'cacao123' },
    })
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }))

    await waitFor(() => {
      expect(useAuth.getState().isAuthenticated).toBe(true)
    })
  })
})
