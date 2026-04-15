import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { X, Sprout, Leaf, Ruler, TreePine, Activity } from 'lucide-react'
import { Card, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { api } from '../lib/api'
import { MOCK_LOTES, type Lote } from '../lib/mocks'
import { cn, getVariedadColor } from '../lib/utils'
import LoteMap from '../components/LoteMap'
import SensorChart from '../components/SensorChart'

export default function Lotes() {
  const [selected, setSelected] = useState<Lote | null>(null)

  const { data: lotes } = useQuery<Lote[]>({
    queryKey: ['lotes'],
    queryFn: async () => {
      try {
        const { data } = await api.get('/api/lotes/?finca_id=1')
        return Array.isArray(data) ? data : (data.results ?? MOCK_LOTES)
      } catch {
        return MOCK_LOTES
      }
    },
    initialData: MOCK_LOTES,
  })

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Lotes de la finca</h1>
          <p className="text-sm text-white/50 mt-1">Distribución de cultivo y estado en tiempo real</p>
        </div>
        <div className="font-mono text-xs text-white/40">
          {lotes.length} lotes · {lotes.reduce((a, l) => a + l.area_ha, 0).toFixed(1)} ha
        </div>
      </div>

      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {lotes.map((l) => (
          <button
            key={l.id}
            onClick={() => setSelected(l)}
            className="text-left"
          >
            <Card className="hover:border-[var(--color-gold)]/30 transition-all cursor-pointer h-full">
              <CardContent className="space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-xs text-white/40 font-mono">#{String(l.id).padStart(3, '0')}</div>
                    <h3 className="text-base font-semibold mt-0.5">{l.nombre}</h3>
                  </div>
                  <span
                    className={cn(
                      'inline-flex items-center h-6 px-2 text-[10px] font-medium rounded-full border',
                      getVariedadColor(l.variedad),
                    )}
                  >
                    {l.variedad}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2 border-t border-white/[0.05]">
                  <Stat icon={Sprout} label="Plantas" value={l.num_plantas.toLocaleString()} />
                  <Stat icon={Ruler} label="Área" value={`${l.area_ha} ha`} />
                  <Stat icon={TreePine} label="Edad" value={`${l.edad_años} años`} />
                  <Stat
                    icon={Activity}
                    label="Estado"
                    value={l.estado === 'activo' ? 'Activo' : 'En renovación'}
                    tone={l.estado === 'activo' ? 'emerald-300' : 'amber-300'}
                  />
                </div>
              </CardContent>
            </Card>
          </button>
        ))}
      </div>

      {selected && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm flex items-stretch justify-end"
          onClick={() => setSelected(null)}
        >
          <aside
            className="w-full max-w-xl bg-[#0e0e0e] border-l border-white/[0.08] h-full overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 z-10 flex items-center justify-between px-6 h-14 border-b border-white/[0.06] bg-[#0e0e0e]">
              <div>
                <div className="text-xs text-white/40 font-mono">Detalle de lote</div>
                <div className="text-sm font-semibold">{selected.nombre}</div>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="w-8 h-8 rounded-md hover:bg-white/10 flex items-center justify-center text-white/60"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div className="flex items-center gap-2 flex-wrap">
                <Badge tone="gold">{selected.variedad}</Badge>
                <Badge tone={selected.estado === 'activo' ? 'success' : 'warning'}>
                  {selected.estado}
                </Badge>
                <Badge><Leaf className="w-3 h-3" /> {selected.num_plantas} plantas</Badge>
              </div>

              <LoteMap lat={selected.lat} lng={selected.lng} label={selected.nombre} />

              <Card>
                <CardContent>
                  <h3 className="text-sm font-semibold mb-1">Sensores IoT</h3>
                  <p className="text-xs text-white/40 mb-1">Ventana de 30 puntos · ~15 min</p>
                  <SensorChart loteId={selected.id} />
                </CardContent>
              </Card>

              <Card>
                <CardContent className="space-y-2 text-sm">
                  <Row label="ID interno" value={`#${selected.id}`} />
                  <Row label="Área" value={`${selected.area_ha} ha`} />
                  <Row label="Edad" value={`${selected.edad_años} años`} />
                  <Row label="Coordenadas" value={`${selected.lat.toFixed(4)}, ${selected.lng.toFixed(4)}`} mono />
                </CardContent>
              </Card>
            </div>
          </aside>
        </div>
      )}
    </div>
  )
}

function Stat({ icon: Icon, label, value, tone = 'white' }: { icon: React.ElementType; label: string; value: string; tone?: string }) {
  return (
    <div className="flex items-center gap-2">
      <Icon className="w-3.5 h-3.5 text-white/30" />
      <div>
        <div className="text-[10px] uppercase tracking-wider text-white/40">{label}</div>
        <div className={`text-xs font-medium text-${tone}`}>{value}</div>
      </div>
    </div>
  )
}

function Row({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-white/[0.04] last:border-0">
      <span className="text-xs text-white/40">{label}</span>
      <span className={mono ? 'font-mono text-xs' : 'text-sm'}>{value}</span>
    </div>
  )
}
