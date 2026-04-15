import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Faq } from '../components/Faq'

describe('Faq', () => {
  it('renders all 6 questions', () => {
    render(<Faq />)
    expect(screen.getByText(/¿Qué es EUDR/i)).toBeInTheDocument()
    expect(screen.getByText(/¿Necesito comprar sensores IoT/i)).toBeInTheDocument()
    expect(screen.getByText(/¿Cuánto cuesta registrar/i)).toBeInTheDocument()
    expect(screen.getByText(/¿Qué modelo de IA/i)).toBeInTheDocument()
    expect(screen.getByText(/¿Cómo exporto/i)).toBeInTheDocument()
    expect(screen.getByText(/certificación orgánica/i)).toBeInTheDocument()
  })

  it('toggles on click without crashing', () => {
    render(<Faq />)
    const btn = screen.getByText(/¿Qué es EUDR/i).closest('button')
    expect(btn).toBeTruthy()
    if (btn) fireEvent.click(btn)
    // answer text is in DOM regardless of open/close, assert it exists
    expect(screen.getByText(/EU Deforestation Regulation/i)).toBeInTheDocument()
  })
})
