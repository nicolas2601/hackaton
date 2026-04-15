import { Card, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { MOCK_CONTROLES } from '../lib/mocks'

export default function Fitosanitario() {
  return (
    <div className="space-y-6 max-w-[1400px]">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Historial fitosanitario</h1>
        <p className="text-sm text-white/50 mt-1">
          Todos los controles, tratamientos y monitoreos de sus lotes — auditable para EUDR
        </p>
      </div>

      <Card>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-white/[0.02] border-b border-white/[0.05]">
              <tr>
                {['Fecha', 'Lote', 'Tipo', 'Plaga / agente', 'Tratamiento', 'Resultado'].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-[10px] uppercase tracking-wider text-white/40 font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MOCK_CONTROLES.map((c) => (
                <tr key={c.id} className="border-b border-white/[0.04] hover:bg-white/[0.02]">
                  <td className="px-4 py-3 font-mono text-xs text-white/80">{c.fecha}</td>
                  <td className="px-4 py-3">{c.lote_nombre}</td>
                  <td className="px-4 py-3 text-xs">{c.tipo_control}</td>
                  <td className="px-4 py-3 text-xs text-white/60">{c.plaga}</td>
                  <td className="px-4 py-3 text-xs text-white/70">{c.tratamiento}</td>
                  <td className="px-4 py-3">
                    <Badge tone={c.resultado === 'Efectivo' || c.resultado === 'Sano' || c.resultado === 'Controlado' ? 'success' : 'warning'}>
                      {c.resultado}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}
