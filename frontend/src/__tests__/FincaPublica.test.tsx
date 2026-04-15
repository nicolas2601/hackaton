import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import FincaPublica from '../pages/FincaPublica'

function setup() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={['/finca/la-esperanza']}>
        <Routes>
          <Route path="/finca/:slug" element={<FincaPublica />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('FincaPublica', () => {
  it('muestra el nombre de la finca y el badge EUDR', () => {
    setup()
    expect(screen.getByText(/Finca La Esperanza/i)).toBeInTheDocument()
    expect(screen.getByText(/Verificada EUDR/i)).toBeInTheDocument()
  })

  it('renderiza secciones esenciales (ubicación, calidad, trazabilidad)', () => {
    setup()
    expect(screen.getAllByText(/Ubicación geográfica/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/Calidad verificada por IoT/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/Pasaporte digital/i).length).toBeGreaterThan(0)
  })
})
