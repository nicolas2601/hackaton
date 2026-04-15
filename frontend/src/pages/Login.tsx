import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Loader2, Sparkles } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

const schema = z.object({
  email: z.string().email('Correo inválido'),
  password: z.string().min(4, 'Mínimo 4 caracteres'),
})
type FormV = z.infer<typeof schema>

export default function Login() {
  const navigate = useNavigate()
  const login = useAuth((s) => s.login)
  const [loading, setLoading] = useState(false)
  const { register, handleSubmit, formState: { errors }, setValue } = useForm<FormV>({
    resolver: zodResolver(schema),
    defaultValues: { email: '', password: '' },
  })

  const onSubmit = async (v: FormV) => {
    setLoading(true)
    try {
      await login(v)
      toast.success('Bienvenido a CacaoTrace')
      navigate('/dashboard')
    } catch {
      toast.error('Credenciales inválidas')
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = () => {
    setValue('email', 'efrain@sanvicente.co')
    setValue('password', 'cacao123')
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6 bg-[#0A0A0A] relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full bg-[var(--color-gold)]/10 blur-3xl" />
        <div className="absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full bg-[var(--color-cacao)]/20 blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/[0.03] text-xs text-white/60 mb-4">
            <Sparkles className="w-3 h-3 text-[var(--color-gold)]" />
            Trazabilidad EUDR-ready
          </div>
          <h1 className="text-3xl font-bold tracking-tight">
            Cacao<span className="text-[var(--color-gold)]">Trace</span>
          </h1>
          <p className="text-sm text-white/50 mt-2">
            El pasaporte digital del cacao fino de Santander
          </p>
        </div>

        <div className="rounded-2xl bg-[#111] border border-white/[0.08] p-7 shadow-[0_0_40px_-10px_rgba(242,201,76,0.15)]">
          <h2 className="text-lg font-semibold mb-1">Iniciar sesión</h2>
          <p className="text-xs text-white/40 mb-5">Acceda a su finca</p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-white/70 mb-1.5">Correo</label>
              <Input type="email" placeholder="efrain@sanvicente.co" autoComplete="email" {...register('email')} />
              {errors.email && <p className="text-[11px] text-red-400 mt-1">{errors.email.message}</p>}
            </div>
            <div>
              <label className="block text-xs font-medium text-white/70 mb-1.5">Contraseña</label>
              <Input type="password" placeholder="••••••••" autoComplete="current-password" {...register('password')} />
              {errors.password && <p className="text-[11px] text-red-400 mt-1">{errors.password.message}</p>}
            </div>

            <Button type="submit" className="w-full mt-2" disabled={loading}>
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              {loading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>

          <button
            onClick={fillDemo}
            className="mt-4 w-full text-xs text-white/40 hover:text-[var(--color-gold)] transition-colors"
          >
            Usar credenciales demo → efrain@sanvicente.co / cacao123
          </button>
        </div>

        <div className="mt-6 text-center text-[11px] text-white/30">
          Hackathon Colombia 5.0 · Bucaramanga · 2026
        </div>
      </div>
    </div>
  )
}
