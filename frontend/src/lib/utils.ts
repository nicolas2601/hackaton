import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(d: string | Date, opts: Intl.DateTimeFormatOptions = {}) {
  const date = typeof d === 'string' ? new Date(d) : d
  return new Intl.DateTimeFormat('es-CO', {
    year: 'numeric', month: 'short', day: 'numeric', ...opts,
  }).format(date)
}

export function formatNumber(n: number, digits = 1) {
  return new Intl.NumberFormat('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: digits }).format(n)
}

export const VARIEDAD_COLORS: Record<string, string> = {
  Trinitario: 'bg-amber-500/15 text-amber-300 border-amber-400/30',
  Criollo: 'bg-emerald-500/15 text-emerald-300 border-emerald-400/30',
  Forastero: 'bg-rose-500/15 text-rose-300 border-rose-400/30',
  'CCN-51': 'bg-sky-500/15 text-sky-300 border-sky-400/30',
  'ICS-60': 'bg-violet-500/15 text-violet-300 border-violet-400/30',
  'ICS-95': 'bg-fuchsia-500/15 text-fuchsia-300 border-fuchsia-400/30',
}

export function getVariedadColor(v: string) {
  return VARIEDAD_COLORS[v] ?? 'bg-white/5 text-white/80 border-white/10'
}
