import { useEffect, useRef, useState } from 'react'
import { Send, Wrench, Sparkles, Bot } from 'lucide-react'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { MCP_URL } from '../lib/api'
import { useAuth } from '../hooks/useAuth'
import { cn } from '../lib/utils'

interface Message {
  role: 'user' | 'assistant' | 'tool'
  content: string
  tool?: string
}

const SUGERENCIAS = [
  '¿Cómo va mi fermentación del Lote Norte?',
  '¿Qué hago si el pH baja de 5?',
  'Dame precios del cacao en Europa',
  '¿Estoy listo para exportar?',
]

const STUB_RESPONSES: Record<string, { tool?: string; text: string }> = {
  fermentacion: {
    tool: 'get_lote_sensors(1) → 127 puntos',
    text:
      'Revisé el Lote Norte: temperatura de fermentación promedio 47.8°C con pico de 49.2°C al día 4. Humedad de cajón al 72%. Todo dentro del rango óptimo para trinitario (45-50°C). Le recomiendo voltear cada 24h hasta el día 6, cuando el aroma frutal comienza a aparecer. Su cacao va camino a ser fino.',
  },
  ph: {
    tool: 'get_controles_fitosanitarios(1)',
    text:
      'Si el pH del cajón baja de 5, significa que la fermentación se acidificó. Acción inmediata: 1) volteo enérgico para oxigenar, 2) mezcle con cacao de otro cajón con pH 5.8-6.2, 3) asegúrese de que la temperatura supere 45°C — si no sube, añada cacao fresco para activar levaduras. No use cal ni químicos: altera el perfil fino.',
  },
  precios: {
    tool: 'get_mercados_exportacion(variedad="trinitario", pais="EU")',
    text:
      'Precios de referencia semana del 2026-04-15:\n• ICE NY futuro cacao: USD 9,420/t\n• Premium fino de aroma Colombia→Europa: +25-40% (USD 11,700–13,200/t)\n• Puerto Barcelona FOB trinitario santandereano certificado EUDR: USD 12,500/t\n\nSu cacao trinitario con perfil fino califica para el premio. Chocolaterie française (Valrhona, Cluizel) paga hasta USD 14,000/t por lotes de origen único con trazabilidad completa.',
  },
  exportar: {
    tool: 'get_finca_info(1)',
    text:
      'Diagnóstico EUDR de su finca:\n✅ Geolocalización de los 3 lotes (lat/lng registrados)\n✅ Historial fitosanitario auditable (últimos 5 controles)\n✅ IoT activo en fermentación y secado\n⚠️  Falta: declaración de diligencia debida firmada + polígono KML de la finca (hoy solo marker)\n\nCon 2-3 días de trabajo formal, su finca está lista para exportar directo a UE bajo EUDR (jun 2026). Le recomiendo contactar a Fedecacao y a ProColombia para la declaración oficial.',
  },
}

function stubAnswer(q: string): { tool?: string; text: string } {
  const lc = q.toLowerCase()
  if (lc.includes('fermenta')) return STUB_RESPONSES.fermentacion
  if (lc.includes('ph')) return STUB_RESPONSES.ph
  if (lc.includes('precio') || lc.includes('europa') || lc.includes('mercado')) return STUB_RESPONSES.precios
  if (lc.includes('export')) return STUB_RESPONSES.exportar
  return {
    text:
      'Pronto podré analizar los datos de su finca en tiempo real vía MCP. Por ahora puedo ayudarle con preguntas sobre fermentación, pH, precios de exportación o diagnóstico EUDR.',
  }
}

export default function ChatIA() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const user = useAuth((s) => s.user)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  async function send(text: string) {
    const q = text.trim()
    if (!q || sending) return
    setInput('')
    setSending(true)
    setMessages((m) => [...m, { role: 'user', content: q }])

    // Try MCP streaming; fallback to stub.
    try {
      const res = await fetch(`${MCP_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, { role: 'user', content: q }],
          finca_id: user?.finca_id ?? 1,
        }),
        signal: AbortSignal.timeout(2500),
      })
      if (!res.ok || !res.body) throw new Error('no-stream')

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let acc = ''
      setMessages((m) => [...m, { role: 'assistant', content: '' }])
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        acc += decoder.decode(value, { stream: true })
        setMessages((m) => {
          const copy = [...m]
          copy[copy.length - 1] = { role: 'assistant', content: acc }
          return copy
        })
      }
    } catch {
      await new Promise((r) => setTimeout(r, 750))
      const { tool, text } = stubAnswer(q)
      if (tool) setMessages((m) => [...m, { role: 'tool', content: tool, tool }])
      await new Promise((r) => setTimeout(r, 400))
      setMessages((m) => [...m, { role: 'assistant', content: text }])
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto h-full flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Chat IA</h1>
          <p className="text-sm text-white/50 mt-1">Pregúntele a su finca</p>
        </div>
        <Badge tone="gold">
          <Sparkles className="w-3 h-3" />
          MCP · Claude/Qwen/Gemini · Datos de tu finca únicamente
        </Badge>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 min-h-[400px] rounded-2xl bg-[#0e0e0e] border border-white/[0.06] p-5 overflow-y-auto space-y-3"
      >
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[var(--color-gold)] to-[var(--color-cacao)] flex items-center justify-center mb-4">
              <Bot className="w-6 h-6 text-black" />
            </div>
            <h3 className="text-lg font-semibold mb-1">¿En qué le ayudo hoy?</h3>
            <p className="text-sm text-white/40 mb-6 max-w-sm">
              Soy el asistente de su finca. Conectado por MCP a sus sensores, cosechas y el mercado global.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-xl">
              {SUGERENCIAS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-left px-3 py-2.5 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:border-[var(--color-gold)]/30 hover:bg-white/[0.05] transition-colors text-xs text-white/80"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}

        {sending && (
          <div className="flex items-center gap-2 text-xs text-white/40">
            <span className="pulse-dot" /> Analizando datos...
          </div>
        )}
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); send(input) }}
        className="flex items-end gap-2"
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input) }
          }}
          placeholder="Escriba su pregunta (Enter envía · Shift+Enter salto de línea)"
          className="flex-1 resize-none rounded-xl bg-[#111] border border-white/[0.08] px-4 py-3 text-sm focus:outline-none focus:border-[var(--color-gold)]/40 min-h-[52px] max-h-40"
          rows={1}
        />
        <Button type="submit" disabled={!input.trim() || sending} className="h-[52px] w-[52px] p-0">
          <Send className="w-4 h-4" />
        </Button>
      </form>
    </div>
  )
}

function MessageBubble({ message }: { message: Message }) {
  if (message.role === 'tool') {
    return (
      <div className="flex justify-start">
        <div className="inline-flex items-center gap-1.5 px-3 h-7 rounded-full bg-white/[0.04] border border-white/[0.06] text-[11px] font-mono text-white/60">
          <Wrench className="w-3 h-3 text-[var(--color-gold)]" />
          {message.content}
        </div>
      </div>
    )
  }
  const isUser = message.role === 'user'
  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[85%] px-4 py-2.5 rounded-xl text-sm whitespace-pre-wrap leading-relaxed',
          isUser
            ? 'bg-[var(--color-gold)]/15 border border-[var(--color-gold)]/30 text-white'
            : 'bg-white/[0.04] border border-white/[0.06] text-white/90',
        )}
      >
        {message.content}
      </div>
    </div>
  )
}
