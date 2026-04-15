import { useEffect, useRef, useState } from 'react'
import { gsap } from 'gsap'
import { useGSAP } from '@gsap/react'
import { MapPin, Activity, Leaf, QrCode } from 'lucide-react'

const CLAIMS = [
  '🇨🇴 Santander produce el 41% del cacao de Colombia',
  '🌱 95% del cacao santandereano es fino de aroma',
  '📈 +56% en exportaciones de cacao en 2025',
]

export function Hero() {
  const rootRef = useRef<HTMLDivElement | null>(null)
  const titleRef = useRef<HTMLHeadingElement | null>(null)
  const [claimIdx, setClaimIdx] = useState(0)
  const [sensor, setSensor] = useState({ temp: 26.4, hum: 78, ph: 6.2 })

  useEffect(() => {
    const id = setInterval(() => {
      setClaimIdx((i) => (i + 1) % CLAIMS.length)
    }, 3000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    const id = setInterval(() => {
      setSensor({
        temp: +(25 + Math.random() * 3).toFixed(1),
        hum: Math.round(72 + Math.random() * 10),
        ph: +(6 + Math.random() * 0.6).toFixed(2),
      })
    }, 2200)
    return () => clearInterval(id)
  }, [])

  useGSAP(
    () => {
      const title = titleRef.current
      if (!title) return

      // Manual char split to avoid Club-only SplitText
      const text = title.textContent || ''
      title.innerHTML = ''
      const chars: HTMLSpanElement[] = []
      for (const ch of text) {
        const span = document.createElement('span')
        span.textContent = ch
        span.style.display = 'inline-block'
        span.style.willChange = 'transform'
        if (ch === ' ') span.innerHTML = '&nbsp;'
        title.appendChild(span)
        chars.push(span)
      }
      title.classList.remove('split-hidden')

      gsap.from(chars, {
        yPercent: 110,
        opacity: 0,
        duration: 1,
        ease: 'expo.out',
        stagger: 0.02,
        delay: 0.1,
      })

      gsap.from('.hero-sub', {
        y: 30,
        opacity: 0,
        duration: 0.8,
        ease: 'power2.out',
        delay: 0.6,
      })
      gsap.from('.hero-cta', {
        y: 20,
        opacity: 0,
        duration: 0.6,
        ease: 'power2.out',
        stagger: 0.1,
        delay: 0.8,
      })
      gsap.from('.hero-mockup', {
        y: 40,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
        delay: 0.5,
      })
    },
    { scope: rootRef }
  )

  const scrollToMapa = () => {
    document.querySelector('#mapa')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <section
      id="hero"
      ref={rootRef}
      className="relative min-h-screen pt-24 pb-16 px-6 overflow-hidden"
    >
      <div className="absolute inset-0 grid-bg opacity-60 pointer-events-none" />
      <div
        className="absolute top-1/3 -left-40 w-[500px] h-[500px] rounded-full blur-3xl opacity-20 pointer-events-none"
        style={{ background: 'radial-gradient(circle, #F2C94C, transparent 70%)' }}
      />

      <div className="relative max-w-7xl mx-auto grid lg:grid-cols-[1.2fr_1fr] gap-12 items-center">
        <div>
          <div
            key={claimIdx}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-white/10 bg-white/5 backdrop-blur text-sm text-white/80 mb-8 animate-[fadeIn_0.5s_ease-out]"
          >
            {CLAIMS[claimIdx]}
          </div>

          <h1
            ref={titleRef}
            className="split-hidden text-white font-extrabold tracking-tight leading-[0.95] mb-6"
            style={{ fontSize: 'clamp(2.75rem, 8vw, 7.5rem)' }}
          >
            Trazabilidad real del cacao fino de Santander.
          </h1>

          <p className="hero-sub text-lg md:text-xl text-white/60 max-w-xl mb-10 leading-relaxed">
            Del cacaocultor de San Vicente al chocolatero de Bélgica. QR en
            cada lote. Cumple EUDR.
          </p>

          <div className="flex flex-wrap gap-4">
            <button className="hero-cta cta-gold" onClick={scrollToMapa}>
              Ver demo en vivo
              <span aria-hidden>→</span>
            </button>
            <button className="hero-cta cta-ghost">Soy comprador</button>
          </div>

          <div className="mt-12 flex items-center gap-6 text-xs text-white/40">
            <div className="flex items-center gap-2">
              <Leaf className="w-4 h-4" style={{ color: '#2E7D32' }} />
              Cumple EUDR jun 2026
            </div>
            <div className="flex items-center gap-2">
              <QrCode className="w-4 h-4" style={{ color: '#F2C94C' }} />
              QR por lote
            </div>
          </div>
        </div>

        {/* Mockup */}
        <div className="hero-mockup relative">
          <div
            className="relative rounded-3xl border border-white/10 bg-gradient-to-br from-white/5 to-transparent backdrop-blur p-6 shadow-2xl"
            style={{ boxShadow: '0 30px 90px -20px rgba(242,201,52,0.15)' }}
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-xs text-white/50">Finca verificada</p>
                <h3 className="font-bold text-white text-lg">
                  Finca La Esperanza
                </h3>
                <p className="text-xs text-white/50 flex items-center gap-1">
                  <MapPin className="w-3 h-3" /> San Vicente de Chucurí
                </p>
              </div>
              <span
                className="text-xs px-2 py-1 rounded-full font-semibold"
                style={{ background: 'rgba(46,125,50,0.2)', color: '#86efac' }}
              >
                ● Live
              </span>
            </div>

            {/* Mini mapa */}
            <div
              className="h-28 rounded-xl mb-4 relative overflow-hidden"
              style={{
                background:
                  'radial-gradient(circle at 30% 40%, rgba(46,125,50,0.3), #111)',
              }}
            >
              <div
                className="absolute top-1/2 left-1/3 -translate-x-1/2 -translate-y-1/2 text-3xl"
                style={{ filter: 'drop-shadow(0 4px 12px rgba(242,201,52,0.6))' }}
              >
                🍫
              </div>
              <div className="absolute bottom-2 right-2 text-[10px] text-white/40 font-mono">
                6.88°N, -73.42°W
              </div>
            </div>

            {/* Sensor data */}
            <div className="grid grid-cols-3 gap-2">
              <SensorBox label="Temp" value={`${sensor.temp}°`} accent="#F2C94C" />
              <SensorBox label="Hum" value={`${sensor.hum}%`} accent="#C8FF4D" />
              <SensorBox label="pH suelo" value={`${sensor.ph}`} accent="#2E7D32" />
            </div>

            <div className="mt-4 flex items-center justify-between text-xs">
              <span className="text-white/50 flex items-center gap-1">
                <Activity className="w-3 h-3" />
                Fermentación día 3 de 5
              </span>
              <span className="text-white/80 font-semibold">Lote #L-2026-04</span>
            </div>
          </div>

          <div
            className="absolute -bottom-3 -right-3 w-24 h-24 rounded-xl border border-white/20 bg-black grid place-items-center text-3xl"
            style={{ boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}
          >
            <div className="text-center">
              <div>▓▓▓</div>
              <div className="text-[8px] text-white/60">QR lote</div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-6px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </section>
  )
}

function SensorBox({
  label,
  value,
  accent,
}: {
  label: string
  value: string
  accent: string
}) {
  return (
    <div className="rounded-lg border border-white/5 bg-black/40 px-3 py-2">
      <p className="text-[10px] text-white/40 uppercase tracking-wide">{label}</p>
      <p className="font-mono font-bold" style={{ color: accent }}>
        {value}
      </p>
    </div>
  )
}
