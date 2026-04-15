export interface Finca {
  id: number
  slug: string
  nombre: string
  municipio: string
  lat: number
  lng: number
  variedades: string[]
  area_ha: number
  verificada?: boolean
  propietario?: string
}

export const FINCAS_MOCK: Finca[] = [
  {
    id: 1,
    slug: 'la-esperanza',
    nombre: 'Finca La Esperanza',
    municipio: 'San Vicente de Chucurí',
    lat: 6.8814,
    lng: -73.4225,
    variedades: ['Trinitario', 'Criollo'],
    area_ha: 4.5,
    verificada: true,
    propietario: 'Don Efraín Suárez',
  },
  {
    id: 2,
    slug: 'el-cacaotal',
    nombre: 'Finca El Cacaotal',
    municipio: 'El Carmen de Chucurí',
    lat: 6.71,
    lng: -73.52,
    variedades: ['CCN-51', 'ICS-95'],
    area_ha: 3.0,
    verificada: true,
    propietario: 'María Clemencia Vega',
  },
  {
    id: 3,
    slug: 'los-yariguies',
    nombre: 'Finca Los Yariguíes',
    municipio: 'Rionegro',
    lat: 7.38,
    lng: -73.15,
    variedades: ['Trinitario'],
    area_ha: 5.2,
    verificada: true,
    propietario: 'José Antonio Rangel',
  },
  {
    id: 4,
    slug: 'aromas-del-rio',
    nombre: 'Finca Aromas del Río',
    municipio: 'Landázuri',
    lat: 6.22,
    lng: -73.81,
    variedades: ['Criollo acriollado'],
    area_ha: 2.8,
    verificada: true,
    propietario: 'Luz Marina Ardila',
  },
  {
    id: 5,
    slug: 'san-jose',
    nombre: 'Finca San José',
    municipio: 'Cimitarra',
    lat: 6.3167,
    lng: -73.95,
    variedades: ['Forastero', 'CCN-51'],
    area_ha: 6.0,
    verificada: true,
    propietario: 'Pedro Gómez',
  },
]

export const VARIEDADES_UNICAS = [
  'Trinitario',
  'Criollo',
  'Criollo acriollado',
  'CCN-51',
  'ICS-95',
  'Forastero',
]
