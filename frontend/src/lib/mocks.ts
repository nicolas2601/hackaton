// Mock data para que la demo funcione aunque el BE no responda.

export interface User {
  id: number
  email: string
  nombre: string
  finca_id: number
  finca_slug: string
}

export interface Lote {
  id: number
  nombre: string
  variedad: string
  num_plantas: number
  area_ha: number
  edad_años: number
  estado: string
  lat: number
  lng: number
}

export interface Finca {
  id: number
  slug: string
  nombre: string
  propietario_nombre: string
  municipio: string
  departamento: string
  lat: number
  lng: number
  area_ha: number
  verificada: boolean
  foto: string
  telefono: string
  descripcion: string
  certificaciones: string[]
  variedades: { nombre: string; pct: number }[]
}

export interface Cosecha {
  id: number
  lote_id: number
  lote_nombre: string
  fecha: string
  kg_baba: number
  kg_seco: number
  dias_ferment: number
  temp_prom_ferm: number
  dias_secado: number
  calidad: string
}

export interface Control {
  id: number
  lote_id: number
  lote_nombre: string
  fecha: string
  tipo_control: string
  plaga: string
  tratamiento: string
  resultado: string
}

export const MOCK_USER: User = {
  id: 1,
  email: 'efrain@sanvicente.co',
  nombre: 'Don Efraín Suárez',
  finca_id: 1,
  finca_slug: 'la-esperanza',
}

export const MOCK_FINCA: Finca = {
  id: 1,
  slug: 'la-esperanza',
  nombre: 'Finca La Esperanza',
  propietario_nombre: 'Don Efraín Suárez',
  municipio: 'San Vicente de Chucurí',
  departamento: 'Santander',
  lat: 6.8815,
  lng: -73.4237,
  area_ha: 3.5,
  verificada: true,
  foto: 'https://images.unsplash.com/photo-1606914469633-279e8a33f4f5?w=1600&q=80',
  telefono: '573001234567',
  descripcion:
    'Tres generaciones cultivando cacao fino de aroma en la ladera andina. Trinitario y criollo acriollado, fermentación en cajones de cedro.',
  certificaciones: ['EUDR-ready', 'Orgánico', 'Rainforest Alliance'],
  variedades: [
    { nombre: 'Trinitario', pct: 65 },
    { nombre: 'Criollo', pct: 30 },
    { nombre: 'ICS-60', pct: 5 },
  ],
}

export const MOCK_LOTES: Lote[] = [
  { id: 1, nombre: 'Lote Norte', variedad: 'Trinitario', num_plantas: 450, area_ha: 1.5, edad_años: 8, estado: 'activo', lat: 6.882, lng: -73.423 },
  { id: 2, nombre: 'Lote Río', variedad: 'Criollo', num_plantas: 300, area_ha: 1.2, edad_años: 12, estado: 'activo', lat: 6.881, lng: -73.424 },
  { id: 3, nombre: 'Lote Sur', variedad: 'Trinitario', num_plantas: 520, area_ha: 1.8, edad_años: 5, estado: 'en_renovación', lat: 6.880, lng: -73.425 },
]

export const MOCK_COSECHAS: Cosecha[] = [
  { id: 1, lote_id: 1, lote_nombre: 'Lote Norte', fecha: '2026-03-28', kg_baba: 420, kg_seco: 168, dias_ferment: 6, temp_prom_ferm: 47.8, dias_secado: 7, calidad: 'Premium' },
  { id: 2, lote_id: 2, lote_nombre: 'Lote Río', fecha: '2026-03-20', kg_baba: 310, kg_seco: 120, dias_ferment: 7, temp_prom_ferm: 49.1, dias_secado: 8, calidad: 'Premium' },
  { id: 3, lote_id: 1, lote_nombre: 'Lote Norte', fecha: '2026-02-14', kg_baba: 390, kg_seco: 152, dias_ferment: 6, temp_prom_ferm: 46.5, dias_secado: 7, calidad: 'Estándar' },
]

export const MOCK_CONTROLES: Control[] = [
  { id: 1, lote_id: 1, lote_nombre: 'Lote Norte', fecha: '2026-04-02', tipo_control: 'Monilia', plaga: 'Moniliophthora roreri', tratamiento: 'Poda + retiro de mazorcas', resultado: 'Controlado' },
  { id: 2, lote_id: 3, lote_nombre: 'Lote Sur', fecha: '2026-03-25', tipo_control: 'Escoba de bruja', plaga: 'M. perniciosa', tratamiento: 'Poda sanitaria', resultado: 'En seguimiento' },
  { id: 3, lote_id: 2, lote_nombre: 'Lote Río', fecha: '2026-03-18', tipo_control: 'Abono', plaga: '—', tratamiento: 'Compost + cenizas', resultado: 'Aplicado' },
  { id: 4, lote_id: 1, lote_nombre: 'Lote Norte', fecha: '2026-03-10', tipo_control: 'Fumigación orgánica', plaga: 'Thrips', tratamiento: 'Neem + jabón potásico', resultado: 'Efectivo' },
  { id: 5, lote_id: 2, lote_nombre: 'Lote Río', fecha: '2026-02-28', tipo_control: 'Monitoreo', plaga: '—', tratamiento: '—', resultado: 'Sano' },
]

// Generador de serie IoT realista para fallback
export function seedSensorSeries(n = 30) {
  const now = Date.now()
  const gen = (base: number, jitter: number) =>
    Array.from({ length: n }, (_, i) => ({
      t: new Date(now - (n - i) * 30_000).toISOString(),
      v: +(base + (Math.random() - 0.5) * jitter).toFixed(1),
    }))
  return {
    temp_suelo: gen(24, 2.5),
    hum_suelo: gen(68, 8),
    temp_ferm: gen(46, 4),
    hum_secado: gen(22, 6),
  }
}
