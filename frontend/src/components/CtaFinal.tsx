import { useEffect, useRef, useState } from 'react'
import { gsap } from 'gsap'

export function CtaFinal() {
  const titleRef = useRef<HTMLHeadingElement | null>(null)
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)

  useEffect(() => {
    const title = titleRef.current
    if (!title) return

    // Split into words/lines manually (fallback without SplitText plugin)
    const text = title.textContent || ''
    const words = text.split(' ')
    title.innerHTML = words
      .map((w) => `<span class="cta-word" style="display:inline-block;overflow:hidden"><span class="cta-word-inner" style="display:inline-block;will-change:transform">${w}&nbsp;</span></span>`)
      .join('')

    gsap.from(title.querySelectorAll('.cta-word-inner'), {
      yPercent: 120,
      duration: 1,
      ease: 'expo.out',
      stagger: 0.12,
      scrollTrigger: {
        trigger: title,
        start: 'top 85%',
        once: true,
      },
    })
  }, [])

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    setSent(true)
    setTimeout(() => setSent(false), 3500)
    setEmail('')
  }

  return (
    <section id="cta" className="py-32 px-6 relative overflow-hidden">
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full blur-3xl opacity-20 pointer-events-none"
        style={{ background: 'radial-gradient(circle, #F2C94C, transparent 70%)' }}
      />

      <div className="relative max-w-4xl mx-auto text-center">
        <p className="text-sm font-semibold uppercase tracking-widest mb-4" style={{ color: '#F2C94C' }}>
          Empieza hoy
        </p>
        <h2
          ref={titleRef}
          className="font-extrabold tracking-tight text-white leading-[0.95] mb-6"
          style={{ fontSize: 'clamp(2.5rem, 7vw, 6rem)' }}
        >
          Siembra confianza en cada grano.
        </h2>
        <p className="text-white/60 text-lg mb-10 max-w-xl mx-auto">
          Registrá tu finca hoy. El jurado de Bruselas te verá mañana.
        </p>

        <form onSubmit={submit} className="flex flex-col sm:flex-row gap-3 justify-center max-w-lg mx-auto">
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tu@finca.com"
            className="flex-1 px-5 py-3.5 rounded-full bg-white/5 border border-white/10 text-white placeholder:text-white/30 outline-none transition-all focus:border-[#F2C94C] focus:shadow-[0_0_0_4px_rgba(242,201,52,0.2)]"
          />
          <button type="submit" className="cta-gold whitespace-nowrap">
            {sent ? '¡Gracias!' : 'Registrar mi finca'}
          </button>
        </form>

        <p className="text-xs text-white/40 mt-4">
          Gratuito durante el piloto · Datos encriptados · Cumple habeas data Ley 1581
        </p>
      </div>
    </section>
  )
}
