import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import QRCodeMod from 'react-qr-code'
const QRCode = (QRCodeMod as unknown as { default?: typeof QRCodeMod }).default || QRCodeMod
import { MapPin, ArrowLeft, ShieldCheck } from 'lucide-react'
import { FINCAS_MOCK, type Finca } from '../data/fincas'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function fetchFinca(slug: string): Promise<Finca | null> {
  try {
    const res = await fetch(`${API_URL}/api/fincas/publicas/${slug}/`, { signal: AbortSignal.timeout(2500) })
    if (!res.ok) throw new Error('not-found')
    return await res.json()
  } catch {
    return FINCAS_MOCK.find((f) => f.slug === slug) || null
  }
}

export function FincaPublica() {
  const { slug = '' } = useParams()
  const { data: finca, isLoading } = useQuery({
    queryKey: ['finca', slug],
    queryFn: () => fetchFinca(slug),
    initialData: () => FINCAS_MOCK.find((f) => f.slug === slug) || null,
  })

  if (isLoading) {
    return <div className="min-h-screen grid place-items-center text-white/60">Cargando finca...</div>
  }

  if (!finca) {
    return (
      <div className="min-h-screen grid place-items-center text-center px-6">
        <div>
          <h1 className="text-4xl font-bold text-white mb-4">Finca no encontrada</h1>
          <Link to="/" className="cta-gold">
            <ArrowLeft className="w-4 h-4" /> Volver al mapa
          </Link>
        </div>
      </div>
    )
  }

  const currentUrl = typeof window !== 'undefined' ? window.location.href : ''

  return (
    <div className="min-h-screen py-12 px-6">
      <div className="max-w-4xl mx-auto">
        <Link to="/" className="inline-flex items-center gap-2 text-white/60 hover:text-white mb-8">
          <ArrowLeft className="w-4 h-4" /> Volver al mapa
        </Link>

        <div className="rounded-3xl border border-white/10 bg-white/[0.02] p-8 md:p-12">
          <div className="flex items-start justify-between flex-wrap gap-4 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <ShieldCheck className="w-5 h-5" style={{ color: '#2E7D32' }} />
                <span className="text-xs uppercase tracking-wider" style={{ color: '#2E7D32' }}>
                  Finca verificada
                </span>
              </div>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-2">
                {finca.nombre}
              </h1>
              <div className="flex items-center gap-2 text-white/60">
                <MapPin className="w-4 h-4" />
                {finca.municipio}, Santander
              </div>
            </div>

            <div className="bg-white p-3 rounded-xl">
              <QRCode value={currentUrl} size={120} bgColor="#ffffff" fgColor="#0A0A0A" />
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <Stat label="Área" value={`${finca.area_ha} ha`} />
            <Stat label="Variedades" value={finca.variedades.join(', ')} />
            <Stat label="Coordenadas" value={`${finca.lat.toFixed(4)}°, ${finca.lng.toFixed(4)}°`} />
          </div>

          {finca.propietario && (
            <div className="border-t border-white/10 pt-6">
              <p className="text-sm text-white/40 mb-1">Propietario</p>
              <p className="text-lg text-white">{finca.propietario}</p>
            </div>
          )}

          <div className="mt-8 p-5 rounded-2xl border border-white/5 bg-black/40">
            <p className="text-xs text-white/40 mb-2">Pasaporte EUDR</p>
            <p className="text-white/80 text-sm leading-relaxed">
              Esta finca cumple con los requisitos de la EU Deforestation Regulation.
              Geolocalización confirmada, sin deforestación post-2020, diligencia debida completa.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/5 bg-black/40 p-4">
      <p className="text-xs text-white/40 uppercase tracking-wider mb-1">{label}</p>
      <p className="text-white font-semibold">{value}</p>
    </div>
  )
}
