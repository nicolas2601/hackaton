import { Sprout, Package, Thermometer, ShieldCheck } from 'lucide-react'
import { Card, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import SensorChart from '../components/SensorChart'
import { MOCK_LOTES, MOCK_COSECHAS, MOCK_FINCA } from '../lib/mocks'

const stats = [
  { label: 'Lotes activos', value: MOCK_LOTES.length, icon: Sprout, hint: '3.5 ha monitoreadas' },
  { label: 'Kg cosechados 2026', value: '440', icon: Package, hint: 'YTD · seco' },
  { label: 'Temp. promedio ferm.', value: '47.8°C', icon: Thermometer, hint: 'últimos 7 días' },
  { label: 'Controles fitosanitarios', value: '5', icon: ShieldCheck, hint: 'último mes' },
]

export default function Resumen() {
  return (
    <div className="space-y-6 max-w-[1400px]">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Buenos días, Don Efraín</h1>
        <p className="text-sm text-white/50 mt-1">
          Resumen de la <span className="text-white">{MOCK_FINCA.nombre}</span> — {MOCK_FINCA.area_ha} ha en {MOCK_FINCA.municipio}
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => (
          <Card key={s.label} className="hover:border-white/20 transition-colors">
            <CardContent>
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-xs text-white/40 uppercase tracking-wider">{s.label}</div>
                  <div className="font-mono text-2xl mt-2 tabular-nums">{s.value}</div>
                  <div className="text-[11px] text-white/30 mt-1">{s.hint}</div>
                </div>
                <div className="w-9 h-9 rounded-lg bg-white/[0.04] border border-white/[0.06] flex items-center justify-center">
                  <s.icon className="w-4 h-4 text-[var(--color-gold)]" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-1">
              <div>
                <h2 className="text-base font-semibold">Sensores IoT en vivo</h2>
                <p className="text-xs text-white/40">Lote Norte · Trinitario · 8 años</p>
              </div>
              <Badge tone="success"><span className="pulse-dot" /> En vivo</Badge>
            </div>
            <SensorChart loteId={1} />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <h2 className="text-base font-semibold mb-3">Últimas cosechas</h2>
            <div className="space-y-3">
              {MOCK_COSECHAS.slice(0, 5).map((c) => (
                <div key={c.id} className="flex items-center justify-between py-2 border-b border-white/[0.05] last:border-0">
                  <div>
                    <div className="text-sm text-white">{c.lote_nombre}</div>
                    <div className="text-[11px] text-white/40 font-mono">{c.fecha}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-mono text-sm text-[var(--color-gold)]">{c.kg_seco} kg</div>
                    <Badge tone={c.calidad === 'Premium' ? 'gold' : 'default'}>{c.calidad}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
