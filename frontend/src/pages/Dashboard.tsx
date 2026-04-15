import { Outlet, useLocation } from 'react-router-dom'
import { ChevronRight, MapPin } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import { Badge } from '../components/ui/Badge'
import { MOCK_FINCA } from '../lib/mocks'

const CRUMB_MAP: Record<string, string> = {
  '/dashboard': 'Resumen',
  '/dashboard/lotes': 'Lotes',
  '/dashboard/cosechas': 'Cosechas',
  '/dashboard/fitosanitario': 'Fitosanitario',
  '/dashboard/chat': 'Chat IA',
  '/dashboard/perfil': 'Perfil público',
}

export default function Dashboard() {
  const { pathname } = useLocation()
  const crumb = CRUMB_MAP[pathname] ?? 'Dashboard'

  return (
    <div className="flex min-h-screen bg-[#0A0A0A] text-white">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0">
        <header className="h-14 border-b border-white/[0.06] px-6 flex items-center justify-between bg-[#0A0A0A]/80 backdrop-blur sticky top-0 z-10">
          <div className="flex items-center gap-2 text-sm">
            <span className="text-white/40">Dashboard</span>
            <ChevronRight className="w-3.5 h-3.5 text-white/30" />
            <span className="text-white font-medium">{crumb}</span>
          </div>
          <Badge tone="gold" className="h-7 px-3 text-[11px]">
            <MapPin className="w-3 h-3" />
            {MOCK_FINCA.nombre} · {MOCK_FINCA.municipio}
          </Badge>
        </header>
        <div className="flex-1 p-6 overflow-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
