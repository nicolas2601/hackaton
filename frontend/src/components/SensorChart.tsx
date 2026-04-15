import { useEffect, useMemo, useRef, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { API_URL } from '../lib/api'
import { seedSensorSeries } from '../lib/mocks'

interface Point { t: string; v: number }
type SensorTipo = 'temp_suelo' | 'hum_suelo' | 'temp_ferm' | 'hum_secado'
type SeriesMap = Record<SensorTipo, Point[]>

const CONFIG: Record<SensorTipo, { label: string; unit: string; color: string; min?: number; max?: number }> = {
  temp_suelo:  { label: 'Temp. suelo',        unit: '°C', color: '#F2C94C', min: 18, max: 32 },
  hum_suelo:   { label: 'Humedad suelo',      unit: '%',  color: '#3B82F6', min: 40, max: 95 },
  temp_ferm:   { label: 'Temp. fermentación', unit: '°C', color: '#EF4444', min: 28, max: 55 },
  hum_secado:  { label: 'Humedad secado',     unit: '%',  color: '#22C55E', min: 6,  max: 65 },
}

const SENSOR_KEYS: SensorTipo[] = ['temp_suelo', 'hum_suelo', 'temp_ferm', 'hum_secado']

interface Props { loteId: number }

export default function SensorChart({ loteId }: Props) {
  const [data, setData] = useState<SeriesMap>(() => seedSensorSeries(30) as SeriesMap)
  const [live, setLive] = useState(false)
  const esRef = useRef<EventSource | null>(null)
  const pollRef = useRef<number | null>(null)

  useEffect(() => {
    // SSE primary
    try {
      const url = `${API_URL}/api/sensors/stream/?lote_id=${loteId}`
      const es = new EventSource(url)
      esRef.current = es
      es.onopen = () => setLive(true)
      es.onmessage = (e) => {
        try {
          const d = JSON.parse(e.data) as { tipo: SensorTipo; valor: number; timestamp: string }
          if (!SENSOR_KEYS.includes(d.tipo)) return
          setData((prev) => ({
            ...prev,
            [d.tipo]: [...(prev[d.tipo] || []).slice(-29), { t: d.timestamp, v: d.valor }],
          }))
        } catch { /* ignore bad event */ }
      }
      es.onerror = () => {
        es.close()
        setLive(false)
        startPolling()
      }
    } catch {
      startPolling()
    }

    function startPolling() {
      if (pollRef.current) return
      pollRef.current = window.setInterval(() => {
        // Demo: nudge existing data a bit so the chart looks alive even offline.
        setData((prev) => {
          const next = { ...prev }
          SENSOR_KEYS.forEach((k) => {
            const last = prev[k]?.at(-1)?.v ?? 30
            const cfg = CONFIG[k]
            const jitter = (Math.random() - 0.5) * 1.2
            const nv = Math.max(cfg.min ?? 0, Math.min(cfg.max ?? 100, +(last + jitter).toFixed(1)))
            next[k] = [...(prev[k] || []).slice(-29), { t: new Date().toISOString(), v: nv }]
          })
          return next
        })
      }, 3000)
      setLive(true)
    }

    return () => {
      esRef.current?.close()
      if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null }
    }
  }, [loteId])

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4" data-live={live}>
      {SENSOR_KEYS.map((k) => (
        <MiniChart key={k} tipo={k} series={data[k]} />
      ))}
    </div>
  )
}

function MiniChart({ tipo, series }: { tipo: SensorTipo; series: Point[] }) {
  const cfg = CONFIG[tipo]
  const current = series?.at(-1)?.v
  const points = useMemo(() => series?.slice(-30).map((p, i) => ({ i, v: p.v, t: p.t })) ?? [], [series])

  return (
    <div className="rounded-lg bg-white/[0.02] border border-white/[0.06] p-3">
      <div className="flex items-center justify-between mb-1">
        <div className="text-[11px] text-white/50">{cfg.label}</div>
        <div className="font-mono text-sm tabular-nums" style={{ color: cfg.color }}>
          {current !== undefined ? `${current}${cfg.unit}` : '—'}
        </div>
      </div>
      <div className="h-24">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points}>
            <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="2 3" vertical={false} />
            <XAxis dataKey="i" hide />
            <YAxis domain={['auto', 'auto']} hide />
            <Tooltip
              contentStyle={{ background: '#0e0e0e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 11 }}
              labelFormatter={() => ''}
              formatter={(v: number) => [`${v}${cfg.unit}`, cfg.label]}
            />
            <Line
              type="monotone" dataKey="v" stroke={cfg.color}
              strokeWidth={2} dot={false} isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
