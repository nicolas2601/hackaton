import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import SensorChart from '../components/SensorChart'

describe('SensorChart', () => {
  it('renderiza las 4 series IoT (temp suelo, hum suelo, temp ferm, hum secado)', () => {
    const { getByText } = render(<SensorChart loteId={1} />)
    expect(getByText('Temp. suelo')).toBeInTheDocument()
    expect(getByText('Humedad suelo')).toBeInTheDocument()
    expect(getByText('Temp. fermentación')).toBeInTheDocument()
    expect(getByText('Humedad secado')).toBeInTheDocument()
  })
})
