import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'
import { Map as MapIcon, Activity, QrCode, Bot, ShieldCheck, TrendingUp } from 'lucide-react'

interface Feature {
  title: string
  description: string
  icon: React.ReactNode
  span?: string
  badge?: string
  accent: string
}

const FEATURES: Feature[] = [
  {
    title: 'Mapa de fincas verificadas',
    description: 'Geolocalización exacta de cada finca cacaotera de Santander. Sin deforestación, sin sorpresas.',
    icon: <MapIcon className="w-6 h-6" />,
    span: 'md:col-span-2',
    accent: '#2E7D32',
  },
  {
    title: 'Monitoreo IoT en vivo',
    description: 'Sensores de fermentación, secado y suelo publicando por MQTT.',
    icon: <Activity className="w-6 h-6" />,
    accent: '#C8FF4D',
  },
  {
    title: 'QR de trazabilidad',
    description: 'Cada lote lleva su pasaporte digital público.',
    icon: <QrCode className="w-6 h-6" />,
    accent: '#F2C94C',
  },
  {
    title: 'Chatbot IA con MCP',
    description: 'Claude, Qwen, Gemini — LLM-agnóstico vía Model Context Protocol.',
    icon: <Bot className="w-6 h-6" />,
    badge: 'LLM-agnostic',
    accent: '#aa3bff',
  },
  {
    title: 'Cumple EUDR out-of-the-box',
    description: 'Trazabilidad completa + diligencia debida para exportar a la UE desde jun 2026.',
    icon: <ShieldCheck className="w-6 h-6" />,
    badge: '🇪🇺 UE Ready',
    accent: '#60a5fa',
  },
  {
    title: 'Precio justo al productor',
    description: 'Cacao fino rastreable se paga 2x–3x más. Conectamos directo al chocolatero gourmet.',
    icon: <TrendingUp className="w-6 h-6" />,
    span: 'md:col-span-2',
    accent: '#F2C94C',
  },
]

export function BentoFeatures() {
  return (
    <section id="features" className="relative py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-16 max-w-2xl">
          <p className="text-sm font-semibold uppercase tracking-widest mb-3" style={{ color: '#F2C94C' }}>
            Cómo funciona
          </p>
          <h2 className="text-4xl md:text-6xl font-bold tracking-tight text-white mb-4">
            Una plataforma. Dos mundos conectados.
          </h2>
          <p className="text-white/50 text-lg">
            El cacaocultor registra. El comprador verifica. La UE aprueba.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5" style={{ perspective: 1000 }}>
          {FEATURES.map((f, i) => (
            <BentoCard key={i} {...f} />
          ))}
        </div>
      </div>
    </section>
  )
}

function BentoCard({ title, description, icon, span, badge, accent }: Feature) {
  const ref = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const xTo = gsap.quickTo(el, 'rotationY', { duration: 0.5, ease: 'power3.out' })
    const yTo = gsap.quickTo(el, 'rotationX', { duration: 0.5, ease: 'power3.out' })

    const handleMove = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect()
      const x = (e.clientX - rect.left) / rect.width - 0.5
      const y = (e.clientY - rect.top) / rect.height - 0.5
      xTo(x * 16)
      yTo(-y * 16)
    }
    const handleLeave = () => {
      xTo(0)
      yTo(0)
    }
    el.addEventListener('mousemove', handleMove)
    el.addEventListener('mouseleave', handleLeave)
    return () => {
      el.removeEventListener('mousemove', handleMove)
      el.removeEventListener('mouseleave', handleLeave)
    }
  }, [])

  return (
    <div
      ref={ref}
      className={`bento-card relative rounded-3xl border border-white/8 bg-gradient-to-br from-white/[0.04] to-transparent p-8 min-h-[260px] overflow-hidden group hover:border-white/20 transition-colors ${span || ''}`}
      style={{ background: 'linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01))' }}
    >
      <div
        className="absolute -top-20 -right-20 w-64 h-64 rounded-full blur-3xl opacity-20 group-hover:opacity-40 transition-opacity"
        style={{ background: accent }}
      />
      <div className="bento-card-inner relative flex flex-col h-full">
        <div
          className="inline-flex w-12 h-12 rounded-xl items-center justify-center mb-4 border border-white/10"
          style={{ color: accent, background: `${accent}14` }}
        >
          {icon}
        </div>
        <h3 className="text-xl md:text-2xl font-bold text-white mb-2 tracking-tight">
          {title}
        </h3>
        <p className="text-white/50 text-sm leading-relaxed flex-1">
          {description}
        </p>
        {badge && (
          <span
            className="self-start mt-4 text-xs font-semibold px-2.5 py-1 rounded-full border"
            style={{ color: accent, borderColor: `${accent}66`, background: `${accent}14` }}
          >
            {badge}
          </span>
        )}
      </div>
    </div>
  )
}
