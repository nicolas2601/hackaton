import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Sprout, Package, Stethoscope, Bot, Share2, LogOut,
} from 'lucide-react'
import { cn } from '../lib/utils'
import { useAuth } from '../hooks/useAuth'

const nav = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Resumen', end: true },
  { to: '/dashboard/lotes', icon: Sprout, label: 'Lotes' },
  { to: '/dashboard/cosechas', icon: Package, label: 'Cosechas' },
  { to: '/dashboard/fitosanitario', icon: Stethoscope, label: 'Fitosanitario' },
  { to: '/dashboard/chat', icon: Bot, label: 'Chat IA' },
  { to: '/dashboard/perfil', icon: Share2, label: 'Perfil público' },
]

export default function Sidebar() {
  const { logout, user } = useAuth()
  const navigate = useNavigate()

  return (
    <aside className="w-60 shrink-0 border-r border-white/[0.06] bg-[#0c0c0c] flex flex-col h-screen sticky top-0">
      <div className="px-5 h-14 flex items-center gap-2 border-b border-white/[0.06]">
        <div className="w-7 h-7 rounded-md bg-gradient-to-br from-[var(--color-gold)] to-[var(--color-cacao)] flex items-center justify-center text-black font-black text-xs">
          C
        </div>
        <div>
          <div className="text-sm font-semibold tracking-tight">CacaoTrace</div>
          <div className="text-[10px] text-white/40 uppercase tracking-wider">Santander</div>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-0.5">
        {nav.map(({ to, icon: Icon, label, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2.5 px-3 py-2 text-sm rounded-md transition-colors',
                isActive
                  ? 'bg-white/[0.06] text-white'
                  : 'text-white/60 hover:text-white hover:bg-white/[0.03]',
              )
            }
          >
            <Icon className="w-4 h-4" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t border-white/[0.06]">
        {user && (
          <div className="px-2 pb-3">
            <div className="text-xs text-white/80 font-medium truncate">{user.nombre}</div>
            <div className="text-[10px] text-white/40 truncate">{user.email}</div>
          </div>
        )}
        <button
          onClick={() => { logout(); navigate('/login') }}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-white/60 hover:text-white hover:bg-white/[0.03] rounded-md transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Cerrar sesión
        </button>
      </div>
    </aside>
  )
}
