export function Footer() {
  return (
    <footer className="relative pt-24 pb-6 px-6 border-t border-white/5 overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-4 gap-10 mb-16">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">🍫</span>
              <span className="font-bold text-lg text-white">
                Cacao<span style={{ color: '#F2C94C' }}>Trace</span>
              </span>
            </div>
            <p className="text-white/40 text-sm">
              El pasaporte digital del cacao fino de Santander.
            </p>
          </div>

          <FooterCol
            title="Producto"
            links={['Mapa de fincas', 'Dashboard agricultor', 'Chatbot IA', 'Registro QR']}
          />
          <FooterCol
            title="Aliados"
            links={['Fedecacao', 'Cámara de Comercio BGA', 'UNAB', 'ProColombia', 'MinTIC']}
          />
          <FooterCol
            title="Recursos"
            links={['Documentación', 'GitHub', 'EUDR Guía', 'Privacidad']}
          />
        </div>

        <div className="flex flex-wrap gap-6 items-center text-xs text-white/30 pb-12">
          <span>Hackathon Colombia 5.0 · Bucaramanga · 15 abr 2026</span>
          <span className="hidden md:inline">·</span>
          <span>Auditorio Luis A. Calvo · UIS</span>
        </div>

        <div className="wordmark">CACAOTRACE</div>

        <div className="mt-8 pt-6 border-t border-white/5 flex flex-wrap justify-between items-center gap-4 text-xs text-white/40">
          <span>© 2026 CacaoTrace — Un proyecto del equipo CacaoTrace</span>
          <span>Hecho en Santander con 🍫 y código</span>
        </div>
      </div>
    </footer>
  )
}

function FooterCol({ title, links }: { title: string; links: string[] }) {
  return (
    <div>
      <h4 className="text-white font-semibold mb-3 text-sm">{title}</h4>
      <ul className="space-y-2">
        {links.map((l) => (
          <li key={l}>
            <a href="#" className="text-white/40 text-sm hover:text-white transition-colors">
              {l}
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}
