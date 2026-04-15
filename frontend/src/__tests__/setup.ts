import '@testing-library/jest-dom/vitest'
import { vi } from 'vitest'

// Ensure localStorage exists even if the environment fails to provide it.
if (typeof globalThis.localStorage === 'undefined' || typeof globalThis.localStorage?.clear !== 'function') {
  const store = new Map<string, string>()
  const ls = {
    getItem: (k: string) => (store.has(k) ? store.get(k)! : null),
    setItem: (k: string, v: string) => { store.set(k, String(v)) },
    removeItem: (k: string) => { store.delete(k) },
    clear: () => { store.clear() },
    key: (i: number) => Array.from(store.keys())[i] ?? null,
    get length() { return store.size },
  }
  Object.defineProperty(globalThis, 'localStorage', { value: ls, writable: true })
}

// Polyfill matchMedia (react-leaflet / shadcn libs)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((q: string) => ({
    matches: false, media: q, onchange: null,
    addListener: vi.fn(), removeListener: vi.fn(),
    addEventListener: vi.fn(), removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Minimal EventSource stub so SensorChart doesn't explode in jsdom
class ESMock {
  onmessage: ((e: MessageEvent) => void) | null = null
  onerror: ((e: Event) => void) | null = null
  onopen: ((e: Event) => void) | null = null
  close() {}
}
// @ts-expect-error injecting
globalThis.EventSource = ESMock

// ResizeObserver for Recharts
class ROMock { observe() {}; unobserve() {}; disconnect() {} }
// @ts-expect-error injecting
globalThis.ResizeObserver = ROMock
