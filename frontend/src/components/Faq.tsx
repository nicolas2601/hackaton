import { useRef, useState } from 'react'
import { gsap } from 'gsap'
import { ChevronDown } from 'lucide-react'

const QUESTIONS = [
  {
    q: '¿Qué es EUDR y por qué me afecta?',
    a: 'El EU Deforestation Regulation (EUDR) es una ley europea que exige trazabilidad completa de productos agrícolas como el cacao. Desde junio de 2026 (PYMES hasta jun 2027), sin geolocalización y diligencia debida no se puede exportar a la UE. CacaoTrace cumple out-of-the-box.',
  },
  {
    q: '¿Necesito comprar sensores IoT para usar CacaoTrace?',
    a: 'No. Podés arrancar solo con el mapa y el registro público. Los sensores MQTT son opcionales: si no los tenés, usamos un simulador con patrones reales de fermentación. Cuando compres, reemplazás los datos simulados sin cambiar nada.',
  },
  {
    q: '¿Cuánto cuesta registrar mi finca?',
    a: 'Durante el piloto con Cámara de Comercio de Bucaramanga y Fedecacao, el registro es gratuito. La idea es que 65.000 familias cacaoteras de Santander puedan exportar sin barreras de entrada digital.',
  },
  {
    q: '¿Qué modelo de IA usa el chatbot?',
    a: 'CacaoTrace es LLM-agnóstico. Hoy corre sobre Claude (Anthropic) vía Model Context Protocol (MCP). Mañana podemos cambiar a Qwen, Gemini o cualquier modelo sin tocar la lógica de negocio. La trazabilidad es tuya, no del proveedor.',
  },
  {
    q: '¿Cómo exporto a Europa con esta plataforma?',
    a: 'Tu finca genera un pasaporte digital con QR público: geolocalización, variedades, fitosanitario, cosechas, lotes fermentados. El comprador europeo lo escanea, pasa el check EUDR, y cierra el negocio. Santander creció +56% en exportaciones 2025.',
  },
  {
    q: '¿Qué pasa con mi certificación orgánica o de comercio justo?',
    a: 'Se suma al perfil. CacaoTrace muestra certificaciones Fedecacao, Rainforest Alliance, Fair Trade o bio, si las tenés. La plataforma no reemplaza la certificación: la potencia con datos verificables.',
  },
]

export function Faq() {
  return (
    <section id="faq" className="py-24 px-6">
      <div className="max-w-3xl mx-auto">
        <p className="text-sm font-semibold uppercase tracking-widest mb-3 text-center" style={{ color: '#F2C94C' }}>
          Preguntas frecuentes
        </p>
        <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-12 text-center">
          Lo que nos preguntan los cacaocultores
        </h2>

        <div className="space-y-3">
          {QUESTIONS.map((item, i) => (
            <FaqItem key={i} question={item.q} answer={item.a} />
          ))}
        </div>
      </div>
    </section>
  )
}

function FaqItem({ question, answer }: { question: string; answer: string }) {
  const [open, setOpen] = useState(false)
  const bodyRef = useRef<HTMLDivElement | null>(null)
  const chevronRef = useRef<SVGSVGElement | null>(null)

  const toggle = () => {
    const body = bodyRef.current
    const chev = chevronRef.current
    if (!body) return
    if (!open) {
      gsap.set(body, { height: 'auto' })
      const h = body.offsetHeight
      gsap.fromTo(body, { height: 0 }, { height: h, duration: 0.4, ease: 'power2.out' })
      if (chev) gsap.to(chev, { rotate: 180, duration: 0.3, ease: 'power2.out' })
    } else {
      gsap.to(body, { height: 0, duration: 0.35, ease: 'power2.inOut' })
      if (chev) gsap.to(chev, { rotate: 0, duration: 0.3, ease: 'power2.out' })
    }
    setOpen(!open)
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] overflow-hidden">
      <button
        onClick={toggle}
        className="w-full px-6 py-5 flex items-center justify-between text-left text-white hover:bg-white/[0.02] transition-colors"
      >
        <span className="font-semibold">{question}</span>
        <ChevronDown ref={chevronRef} className="w-5 h-5 text-white/50 shrink-0" />
      </button>
      <div ref={bodyRef} style={{ height: 0, overflow: 'hidden' }}>
        <div className="px-6 pb-5 text-white/60 leading-relaxed">{answer}</div>
      </div>
    </div>
  )
}
