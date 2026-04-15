import { forwardRef, type InputHTMLAttributes } from 'react'
import { cn } from '../../lib/utils'

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        'h-10 w-full rounded-lg bg-white/[0.03] border border-white/10 px-3.5 text-sm text-white placeholder:text-white/30',
        'focus:outline-none focus:border-[var(--color-gold)]/60 focus:ring-2 focus:ring-[var(--color-gold)]/20',
        'transition-colors',
        className,
      )}
      {...props}
    />
  ),
)
Input.displayName = 'Input'
