import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock GSAP (jsdom can't handle its DOM queries)
vi.mock('gsap', () => {
  const noop = () => ({ kill: () => {} })
  return {
    gsap: {
      registerPlugin: () => {},
      to: noop,
      from: noop,
      fromTo: noop,
      set: () => {},
      timeline: () => ({ to: noop, from: noop, repeat: () => ({}) }),
      quickTo: () => () => {},
    },
  }
})
vi.mock('gsap/ScrollTrigger', () => ({ ScrollTrigger: { create: () => {} } }))
vi.mock('@gsap/react', () => ({ useGSAP: (cb: () => void) => cb && cb() }))

// Mock react-leaflet (jsdom lacks full DOM Leaflet needs)
vi.mock('react-leaflet', () => ({
  MapContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="map">{children}</div>,
  TileLayer: () => null,
  Marker: ({ children }: { children: React.ReactNode }) => <div data-testid="marker">{children}</div>,
  Popup: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}))

vi.mock('leaflet', () => ({
  default: {
    divIcon: () => ({}),
    Icon: { Default: { prototype: {}, mergeOptions: () => {} } },
  },
}))
