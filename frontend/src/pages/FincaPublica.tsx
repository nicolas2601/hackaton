import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import QRCodeMod from 'react-qr-code'
const QRCode = (QRCodeMod as unknown as { default?: typeof QRCodeMod }).default || QRCodeMod
import {
  ShieldCheck, MapPin, Leaf, Award, Download, MessageCircle, TreePine,
  Thermometer, Droplets,
} from 'lucide-react'
import { api } from '../lib/api'
import { MOCK_FINCA, MOCK_CONTROLES, type Finca } from '../lib/mocks'
import LoteMap from '../components/LoteMap'

export default function FincaPublica() {
  const { slug } = useParams<{ slug: string }>()

  const { data: finca } = useQuery<Finca>({
    queryKey: ['finca-publica', slug],
    queryFn: async () => {
      try {
        const { data } = await api.get(`/api/fincas/publicas/${slug}/`)
        return data
      } catch {
        return { ...MOCK_FINCA, slug: slug ?? MOCK_FINCA.slug }
      }
    },
    initialData: { ...MOCK_FINCA, slug: slug ?? MOCK_FINCA.slug },
  })

  const publicUrl = typeof window !== 'undefined' ? window.location.href : ''

  return (
    <div className="min-h-screen bg-[#FAFAF7] text-[#111] font-sans">
      {/* Hero */}
      <header className="relative h-[55vh] min-h-[420px] overflow-hidden">
        <img src={finca.foto} alt={finca.nombre} className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent" />
        <div className="relative z-10 max-w-6xl mx-auto h-full flex flex-col justify-end px-6 pb-10 text-white">
          <div className="inline-flex items-center gap-2 bg-emerald-500/90 text-white px-3 py-1 rounded-full text-xs font-medium self-start mb-3">
            <ShieldCheck className="w-3.5 h-3.5" />
            Verificada EUDR · Trazabilidad completa
          </div>
          <h1 className="text-5xl md:text-6xl font-semibold tracking-tight">{finca.nombre}</h1>
          <div className="flex items-center gap-2 mt-3 text-sm opacity-90">
            <MapPin className="w-4 h-4" />
            {finca.municipio}, {finca.departamento} · {finca.propietario_nombre}
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-14 space-y-16">
        {/* Descripción */}
        <section className="grid md:grid-cols-3 gap-8 items-start">
          <div className="md:col-span-2 space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight">Sobre la finca</h2>
            <p className="text-lg leading-relaxed text-[#444]">{finca.descripcion}</p>
            <div className="grid grid-cols-3 gap-4 pt-4">
              <Stat label="Área" value={`${finca.area_ha} ha`} />
              <Stat label="Variedades" value={String(finca.variedades.length)} />
              <Stat label="Certificaciones" value={String(finca.certificaciones.length)} />
            </div>
          </div>
          <aside className="bg-white rounded-2xl shadow-sm border border-[#eee] p-6">
            <h3 className="text-sm font-semibold text-[#666] uppercase tracking-wide mb-3">Variedades</h3>
            <ul className="space-y-3">
              {finca.variedades.map((v) => (
                <li key={v.nombre} className="flex items-center gap-3">
                  <Leaf className="w-4 h-4 text-emerald-700" />
                  <span className="flex-1 text-sm font-medium">{v.nombre}</span>
                  <span className="font-mono text-xs text-[#777]">{v.pct}%</span>
                </li>
              ))}
            </ul>
          </aside>
        </section>

        {/* Ubicación */}
        <section>
          <h2 className="text-2xl font-semibold tracking-tight mb-4">Ubicación geográfica</h2>
          <p className="text-[#555] mb-4 max-w-2xl">
            Coordenadas verificables que cumplen con la Regulación EUDR de la Unión Europea para trazabilidad de origen sin deforestación.
          </p>
          <div className="flex items-center gap-6 mb-5 text-sm">
            <span className="font-mono text-[#666]">Lat: {finca.lat.toFixed(5)}</span>
            <span className="font-mono text-[#666]">Lng: {finca.lng.toFixed(5)}</span>
          </div>
          <div className="rounded-xl border border-[#eee] overflow-hidden">
            <LoteMap lat={finca.lat} lng={finca.lng} label={finca.nombre} zoom={13} height={360} light />
          </div>
        </section>

        {/* Calidad verificada */}
        <section>
          <h2 className="text-2xl font-semibold tracking-tight mb-2">Calidad verificada por IoT</h2>
          <p className="text-[#555] mb-6 max-w-2xl">
            Sensores en los lotes monitorean continuamente fermentación y secado. Últimos promedios:
          </p>
          <div className="grid md:grid-cols-3 gap-4">
            <QualityCard Icon={Thermometer} label="Temp. fermentación" value="47.8 °C" hint="Rango óptimo fino 45–50°C" />
            <QualityCard Icon={Droplets} label="Humedad secado" value="22.4 %" hint="Rango exportación 6.5–7.5%" />
            <QualityCard Icon={TreePine} label="Monitoreo activo" value="24/7" hint="Registro auditable de 90 días" />
          </div>
        </section>

        {/* Historial fitosanitario */}
        <section>
          <h2 className="text-2xl font-semibold tracking-tight mb-4">Historial fitosanitario</h2>
          <div className="rounded-xl border border-[#eee] overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-[#fafaf7] border-b border-[#eee]">
                <tr className="text-[#666] text-xs uppercase tracking-wide">
                  <th className="text-left px-4 py-3">Fecha</th>
                  <th className="text-left px-4 py-3">Lote</th>
                  <th className="text-left px-4 py-3">Tipo</th>
                  <th className="text-left px-4 py-3">Resultado</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_CONTROLES.slice(0, 5).map((c) => (
                  <tr key={c.id} className="border-b border-[#f0f0f0] last:border-0">
                    <td className="px-4 py-3 font-mono text-xs">{c.fecha}</td>
                    <td className="px-4 py-3">{c.lote_nombre}</td>
                    <td className="px-4 py-3 text-[#555]">{c.tipo_control}</td>
                    <td className="px-4 py-3 font-medium text-emerald-700">{c.resultado}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Certificaciones */}
        <section>
          <h2 className="text-2xl font-semibold tracking-tight mb-4">Certificaciones</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {finca.certificaciones.map((c) => (
              <div key={c} className="bg-white rounded-xl border border-[#eee] p-5 flex flex-col items-center gap-2 hover:shadow-sm transition-shadow">
                <Award className="w-8 h-8 text-[var(--color-gold,#B8860B)]" />
                <div className="text-sm font-medium text-center">{c}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Trazabilidad + QR */}
        <section className="bg-white rounded-2xl border border-[#eee] p-8 md:p-10">
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div>
              <h2 className="text-2xl font-semibold tracking-tight mb-3">Pasaporte digital</h2>
              <p className="text-[#555] leading-relaxed mb-5">
                Este QR apunta a la página pública de trazabilidad de la finca. Puede imprimirlo en cada saco de cacao exportado para que el comprador verifique origen, variedad, geolocalización, controles fitosanitarios y calidad verificada por IoT.
              </p>
              <div className="flex gap-3">
                <button className="inline-flex items-center gap-2 h-11 px-5 rounded-lg bg-[#111] text-white text-sm font-medium hover:bg-black">
                  <Download className="w-4 h-4" />
                  Descargar PDF
                </button>
                <a
                  href={`https://wa.me/${finca.telefono}`}
                  target="_blank" rel="noreferrer"
                  className="inline-flex items-center gap-2 h-11 px-5 rounded-lg border border-[#111] text-[#111] text-sm font-medium hover:bg-[#111] hover:text-white transition-colors"
                >
                  <MessageCircle className="w-4 h-4" />
                  Contactar productor
                </a>
              </div>
            </div>
            <div className="flex flex-col items-center gap-3">
              <div className="p-4 bg-white rounded-2xl border border-[#eee] shadow-sm">
                <QRCode value={publicUrl} size={220} />
              </div>
              <div className="text-xs text-[#666] font-mono text-center max-w-xs truncate">{publicUrl}</div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-[#eee] py-8 text-center text-xs text-[#999]">
        CacaoTrace · Hackathon Colombia 5.0 · Bucaramanga 2026
      </footer>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-[#eee] rounded-xl p-4">
      <div className="text-[11px] uppercase tracking-wide text-[#888]">{label}</div>
      <div className="text-2xl font-semibold mt-1 font-mono">{value}</div>
    </div>
  )
}

function QualityCard({ Icon, label, value, hint }: { Icon: React.ElementType; label: string; value: string; hint: string }) {
  return (
    <div className="bg-white rounded-2xl border border-[#eee] p-6">
      <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center mb-4">
        <Icon className="w-5 h-5 text-emerald-700" />
      </div>
      <div className="text-[11px] uppercase tracking-wide text-[#888]">{label}</div>
      <div className="text-2xl font-semibold mt-1 font-mono">{value}</div>
      <div className="text-xs text-[#777] mt-1">{hint}</div>
    </div>
  )
}
