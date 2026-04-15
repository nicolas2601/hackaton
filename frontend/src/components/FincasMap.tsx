import { useMemo, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { FINCAS_MOCK, VARIEDADES_UNICAS, type Finca } from '../data/fincas'
import { MapPin, Filter } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const CENTER: [number, number] = [7.13, -73.12]

const cacaoIcon = L.divIcon({
  className: 'cacao-marker',
  html: '<div style="font-size:30px;line-height:1">🍫</div>',
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  popupAnchor: [0, -12],
})

async function fetchFincas(): Promise<Finca[]> {
  try {
    const res = await fetch(`${API_URL}/api/fincas/publicas/`, { signal: AbortSignal.timeout(2500) })
    if (!res.ok) throw new Error('bad')
    const data = await res.json()
    if (!Array.isArray(data) || data.length === 0) throw new Error('empty')
    return data
  } catch {
    return FINCAS_MOCK
  }
}

export function FincasMap() {
  const { data: fincas = FINCAS_MOCK } = useQuery({
    queryKey: ['fincas-publicas'],
    queryFn: fetchFincas,
    initialData: FINCAS_MOCK,
  })

  const municipiosUnicos = useMemo(
    () => Array.from(new Set(fincas.map((f) => f.municipio))).sort(),
    [fincas]
  )

  const [variedadesSel, setVariedadesSel] = useState<string[]>([])
  const [municipiosSel, setMunicipiosSel] = useState<string[]>([])

  const filtradas = useMemo(() => {
    return fincas.filter((f) => {
      const varOk =
        variedadesSel.length === 0 ||
        f.variedades.some((v) => variedadesSel.some((s) => v.includes(s)))
      const munOk = municipiosSel.length === 0 || municipiosSel.includes(f.municipio)
      return varOk && munOk
    })
  }, [fincas, variedadesSel, municipiosSel])

  const toggle = (list: string[], setList: (l: string[]) => void, v: string) => {
    setList(list.includes(v) ? list.filter((x) => x !== v) : [...list, v])
  }

  return (
    <section id="mapa" className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-12 flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest mb-3" style={{ color: '#F2C94C' }}>
              Mapa público
            </p>
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-white">
              Fincas cacaoteras verificadas de Santander
            </h2>
          </div>
          <div className="text-right">
            <div className="font-bold text-3xl text-white">
              {filtradas.length}
              <span className="text-base text-white/40 font-normal ml-2">fincas verificadas</span>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-[280px_1fr] gap-6">
          {/* Filters */}
          <aside className="rounded-2xl border border-white/10 bg-white/[0.02] p-5 h-fit lg:sticky lg:top-24">
            <div className="flex items-center gap-2 mb-4 text-white">
              <Filter className="w-4 h-4" />
              <h3 className="font-semibold">Filtros</h3>
            </div>

            <div className="mb-6">
              <h4 className="text-xs uppercase tracking-wider text-white/50 mb-3">Variedad</h4>
              <div className="space-y-2">
                {VARIEDADES_UNICAS.map((v) => (
                  <label key={v} className="flex items-center gap-2 cursor-pointer text-sm text-white/80 hover:text-white">
                    <input
                      type="checkbox"
                      checked={variedadesSel.includes(v)}
                      onChange={() => toggle(variedadesSel, setVariedadesSel, v)}
                      className="accent-[#F2C94C] w-4 h-4"
                    />
                    {v}
                  </label>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-xs uppercase tracking-wider text-white/50 mb-3">Municipio</h4>
              <div className="space-y-2">
                {municipiosUnicos.map((m) => (
                  <label key={m} className="flex items-center gap-2 cursor-pointer text-sm text-white/80 hover:text-white">
                    <input
                      type="checkbox"
                      checked={municipiosSel.includes(m)}
                      onChange={() => toggle(municipiosSel, setMunicipiosSel, m)}
                      className="accent-[#F2C94C] w-4 h-4"
                    />
                    {m}
                  </label>
                ))}
              </div>
            </div>

            {(variedadesSel.length > 0 || municipiosSel.length > 0) && (
              <button
                onClick={() => {
                  setVariedadesSel([])
                  setMunicipiosSel([])
                }}
                className="mt-5 text-xs text-white/60 hover:text-white underline"
              >
                Limpiar filtros
              </button>
            )}
          </aside>

          {/* Map */}
          <div className="relative rounded-2xl overflow-hidden border border-white/10" style={{ minHeight: 520 }}>
            <MapContainer
              center={CENTER}
              zoom={9}
              scrollWheelZoom={false}
              style={{ height: 520, width: '100%' }}
            >
              <TileLayer
                attribution='&copy; OpenStreetMap'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {filtradas.map((f) => (
                <Marker key={f.id} position={[f.lat, f.lng]} icon={cacaoIcon}>
                  <Popup>
                    <div style={{ minWidth: 200 }}>
                      <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>
                        {f.nombre}
                      </div>
                      <div style={{ fontSize: 12, opacity: 0.7, display: 'flex', alignItems: 'center', gap: 4, marginBottom: 6 }}>
                        <MapPin size={12} /> {f.municipio}
                      </div>
                      <div style={{ fontSize: 11, opacity: 0.7, marginBottom: 8 }}>
                        Variedades: {f.variedades.join(', ')}
                      </div>
                      <div style={{ fontSize: 11, opacity: 0.6, marginBottom: 10 }}>
                        Área: {f.area_ha} ha
                      </div>
                      <Link
                        to={`/finca/${f.slug}`}
                        style={{
                          display: 'inline-block',
                          padding: '6px 12px',
                          background: '#F2C94C',
                          color: '#0A0A0A',
                          fontWeight: 600,
                          fontSize: 12,
                          borderRadius: 999,
                          textDecoration: 'none',
                        }}
                      >
                        Ver perfil público →
                      </Link>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </div>
      </div>
    </section>
  )
}
