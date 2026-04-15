import { useEffect, useRef, useState } from 'react'
import { gsap } from 'gsap'
import { Link } from 'react-router-dom'

const LINKS = [
  { label: 'Landing', href: '#hero' },
  { label: 'Mapa', href: '#mapa' },
  { label: 'Cómo funciona', href: '#features' },
  { label: 'FAQ', href: '#faq' },
]

export function Navbar() {
  const navRef = useRef<HTMLElement | null>(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    let lastY = window.scrollY
    let tween: gsap.core.Tween | null = null
    const nav = navRef.current
    if (!nav) return

    const onScroll = () => {
      const y = window.scrollY
      const goingDown = y > lastY && y > 120
      if (tween) tween.kill()
      tween = gsap.to(nav, {
        y: goingDown ? -100 : 0,
        duration: 0.3,
        ease: 'power2.out',
      })
      lastY = y
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const scrollTo = (id: string) => {
    const el = document.querySelector(id)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    setOpen(false)
  }

  return (
    <nav
      ref={navRef}
      className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-black/60 border-b border-white/5"
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <span className="text-2xl">🍫</span>
          <span className="font-bold text-lg tracking-tight text-white">
            Cacao<span style={{ color: '#F2C94C' }}>Trace</span>
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-8">
          {LINKS.map((l) => (
            <button
              key={l.href}
              onClick={() => scrollTo(l.href)}
              className="text-sm text-white/70 hover:text-white transition-colors"
            >
              {l.label}
            </button>
          ))}
        </div>

        <button className="cta-gold text-sm" onClick={() => scrollTo('#cta')}>
          Registra tu finca
        </button>

        <button
          className="md:hidden text-white"
          onClick={() => setOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          {open ? '✕' : '☰'}
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-white/5 bg-black/90 px-6 py-4 flex flex-col gap-3">
          {LINKS.map((l) => (
            <button
              key={l.href}
              onClick={() => scrollTo(l.href)}
              className="text-left text-white/80 py-2"
            >
              {l.label}
            </button>
          ))}
        </div>
      )}
    </nav>
  )
}
