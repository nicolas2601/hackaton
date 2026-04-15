import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'

interface Kpi {
  value: number
  suffix: string
  prefix?: string
  label: string
  accent: string
  format?: (n: number) => string
}

const KPIS: Kpi[] = [
  {
    value: 65000,
    suffix: '',
    label: 'Familias santandereanas viven del cacao',
    accent: '#F2C94C',
    format: (n) => Math.round(n).toLocaleString('es-CO'),
  },
  {
    value: 41,
    suffix: '%',
    label: 'De la producción nacional de cacao',
    accent: '#C8FF4D',
  },
  {
    value: 95,
    suffix: '%',
    label: 'Es fino de aroma — el oro del cacao',
    accent: '#2E7D32',
  },
  {
    value: 56,
    suffix: '%',
    prefix: '+',
    label: 'Crecimiento en exportaciones 2025',
    accent: '#aa3bff',
  },
]

export function KpiCounters() {
  return (
    <section id="kpis" className="py-24 px-6 border-y border-white/5 bg-white/[0.02]">
      <div className="max-w-7xl mx-auto">
        <p className="text-sm font-semibold uppercase tracking-widest mb-10 text-center" style={{ color: '#F2C94C' }}>
          Santander en cifras
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {KPIS.map((k, i) => (
            <Counter key={i} {...k} />
          ))}
        </div>
      </div>
    </section>
  )
}

function Counter({ value, suffix, prefix, label, accent, format }: Kpi) {
  const numRef = useRef<HTMLSpanElement | null>(null)

  useEffect(() => {
    const el = numRef.current
    if (!el) return
    const obj = { v: 0 }
    const tween = gsap.to(obj, {
      v: value,
      duration: 2.2,
      ease: 'power2.out',
      snap: { v: 1 },
      scrollTrigger: {
        trigger: el,
        start: 'top 85%',
        once: true,
      },
      onUpdate: () => {
        el.textContent = format ? format(obj.v) : Math.round(obj.v).toString()
      },
    })
    return () => {
      tween.kill()
    }
  }, [value, format])

  return (
    <div className="text-center">
      <div className="font-bold tracking-tight" style={{ color: accent, fontSize: 'clamp(2.5rem, 5vw, 4.5rem)' }}>
        {prefix}
        <span ref={numRef}>0</span>
        {suffix}
      </div>
      <p className="text-white/50 text-sm mt-2 max-w-[220px] mx-auto leading-snug">
        {label}
      </p>
    </div>
  )
}
