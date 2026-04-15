import { Card, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { MOCK_COSECHAS } from '../lib/mocks'

export default function Cosechas() {
  const total = MOCK_COSECHAS.reduce((a, c) => a + c.kg_seco, 0)
  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Cosechas</h1>
          <p className="text-sm text-white/50 mt-1">Registro de cada cosecha de la finca</p>
        </div>
        <div className="text-right">
          <div className="text-xs text-white/40 uppercase">Total histórico</div>
          <div className="font-mono text-xl text-[var(--color-gold)]">{total} kg</div>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-white/[0.02] border-b border-white/[0.05]">
              <tr>
                {['Fecha', 'Lote', 'Baba (kg)', 'Seco (kg)', 'Ferm. días', 'Temp. °C', 'Calidad'].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-[10px] uppercase tracking-wider text-white/40 font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MOCK_COSECHAS.map((c) => (
                <tr key={c.id} className="border-b border-white/[0.04] hover:bg-white/[0.02]">
                  <td className="px-4 py-3 font-mono text-xs text-white/80">{c.fecha}</td>
                  <td className="px-4 py-3">{c.lote_nombre}</td>
                  <td className="px-4 py-3 font-mono text-xs">{c.kg_baba}</td>
                  <td className="px-4 py-3 font-mono text-xs text-[var(--color-gold)]">{c.kg_seco}</td>
                  <td className="px-4 py-3 font-mono text-xs">{c.dias_ferment}</td>
                  <td className="px-4 py-3 font-mono text-xs">{c.temp_prom_ferm}</td>
                  <td className="px-4 py-3"><Badge tone={c.calidad === 'Premium' ? 'gold' : 'default'}>{c.calidad}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}
