import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { FincasMap } from '../components/FincasMap'
import { FINCAS_MOCK } from '../data/fincas'

function renderWithProviders(ui: React.ReactElement) {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('FincasMap', () => {
  // TODO: react-leaflet Markers no se renderizan en jsdom (requiere DOM real).
  // Habilitar cuando migremos tests a @vitest/browser o playwright-component-test.
  it.skip('renders 5 markers with mock data', async () => {
    renderWithProviders(<FincasMap />)
    const markers = await screen.findAllByTestId('marker')
    expect(markers.length).toBe(FINCAS_MOCK.length)
    expect(markers.length).toBe(5)
  })

  it('shows verified count header', () => {
    renderWithProviders(<FincasMap />)
    expect(screen.getByText(/fincas verificadas/i)).toBeInTheDocument()
  })

  it('lists filter checkboxes for variedades', () => {
    renderWithProviders(<FincasMap />)
    expect(screen.getByLabelText('Trinitario')).toBeInTheDocument()
    expect(screen.getByLabelText('Criollo')).toBeInTheDocument()
  })
})
