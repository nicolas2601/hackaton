import { Link } from 'react-router-dom'
import { QRCode } from 'react-qr-code'
import { ExternalLink } from 'lucide-react'
import { Card, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { MOCK_FINCA } from '../lib/mocks'

export default function PerfilAdmin() {
  const publicUrl = `${window.location.origin}/finca/${MOCK_FINCA.slug}`
  return (
    <div className="space-y-6 max-w-[1200px]">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Perfil público</h1>
        <p className="text-sm text-white/50 mt-1">Comparta la trazabilidad de su finca con compradores</p>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <Card className="md:col-span-2">
          <CardContent className="space-y-4">
            <h2 className="text-base font-semibold">{MOCK_FINCA.nombre}</h2>
            <p className="text-sm text-white/60">{MOCK_FINCA.descripcion}</p>
            <div className="flex flex-wrap gap-2">
              <Badge tone="success">✓ Verificada EUDR</Badge>
              {MOCK_FINCA.certificaciones.map((c) => (
                <Badge key={c} tone="gold">{c}</Badge>
              ))}
            </div>

            <div className="pt-4 border-t border-white/[0.05]">
              <div className="text-xs text-white/40 uppercase tracking-wider mb-2">URL pública</div>
              <div className="flex items-center gap-2">
                <code className="flex-1 font-mono text-xs px-3 py-2 bg-black/40 rounded-md border border-white/[0.05] text-[var(--color-gold)]">
                  {publicUrl}
                </code>
                <Link to={`/finca/${MOCK_FINCA.slug}`} target="_blank">
                  <Button variant="secondary" size="sm">
                    <ExternalLink className="w-3.5 h-3.5" /> Abrir
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex flex-col items-center">
            <div className="bg-white p-3 rounded-lg">
              <QRCode value={publicUrl} size={160} />
            </div>
            <div className="text-xs text-white/40 mt-3 text-center">
              Escanee desde un móvil para verificar la trazabilidad
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
