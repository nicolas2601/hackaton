import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Hero } from '../components/Hero'

describe('Hero', () => {
  it('renders the main title text', () => {
    render(
      <MemoryRouter>
        <Hero />
      </MemoryRouter>
    )
    // Title chars are split into spans but textContent still holds the text
    const h1 = document.querySelector('h1')
    expect(h1).toBeTruthy()
    expect(h1?.textContent?.toLowerCase()).toContain('santander')
  })

  it('renders both CTAs', () => {
    render(
      <MemoryRouter>
        <Hero />
      </MemoryRouter>
    )
    expect(screen.getByText(/Ver demo en vivo/i)).toBeInTheDocument()
    expect(screen.getByText(/Soy comprador/i)).toBeInTheDocument()
  })
})
