import type { HTMLAttributes } from 'react'
import { cn } from '../../lib/utils'

interface Props extends HTMLAttributes<HTMLSpanElement> {
  tone?: 'default' | 'success' | 'warning' | 'gold' | 'cacao'
}

const tones = {
  default: 'bg-white/5 text-white/80 border-white/10',
  success: 'bg-emerald-500/10 text-emerald-300 border-emerald-400/25',
  warning: 'bg-amber-500/10 text-amber-300 border-amber-400/25',
  gold: 'bg-[var(--color-gold)]/15 text-[var(--color-gold)] border-[var(--color-gold)]/30',
  cacao: 'bg-[#7B3F00]/20 text-amber-200 border-amber-700/40',
}

export function Badge({ className, tone = 'default', ...props }: Props) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-2 h-6 text-[11px] font-medium rounded-full border',
        tones[tone],
        className,
      )}
      {...props}
    />
  )
}
