# FE-1 — Landing + Mapa público

> **Persona:** Frontend-1 · **Rama:** `feat/landing` · **Tiempo:** 2h
> **Deliverable:** Landing con hero GSAP de alto impacto + mapa Leaflet con fincas de Santander + filtros.

## Checklist (orden estricto)

- [ ] **T+0–10min** · Setup
- [ ] **T+10–40min** · Hero + Navbar + SmoothScroll
- [ ] **T+40–70min** · Sección features (bento) + KPIs counter
- [ ] **T+70–95min** · Mapa público Leaflet + filtros
- [ ] **T+95–110min** · FAQ + CTA final + Footer + responsive
- [ ] **T+110–120min** · QA visual en Chrome mobile + merge

## Skills y agentes a invocar

```
Skill("gsap-core"), Skill("gsap-scrolltrigger"), Skill("gsap-timeline")
Skill("frontend-design"), Skill("ui-ux-pro-max")
Skill("vercel-react-best-practices")
Skill("browse")  # para verificar visualmente cada cambio
```

Si algo se atasca → `Agent(subagent_type="Explore", prompt="...")` para buscar patrones en `~/Documentos/gsap-landing-page/`.

---

## Setup (T+0–10min)

```bash
git checkout -b feat/landing
cd frontend
pnpm add react-router-dom leaflet react-leaflet gsap @gsap/react lucide-react clsx tailwind-merge zustand
pnpm add -D tailwindcss@next @tailwindcss/vite
pnpm dlx shadcn@latest init  # yes a todo, color: Neutral
pnpm dlx shadcn@latest add button card badge input dialog
pnpm dev
```

Abre http://localhost:5173 en Chrome con DevTools (mobile view).

---

## Prompt 1 — SmoothScroll + Navbar sticky (15 min)

> Estoy en `~/Documentos/HACKATON/frontend`. Crea:
>
> 1. `src/providers/SmoothScrollProvider.jsx` usando `ScrollSmoother` de GSAP (registra plugin en `main.tsx`). Envuelve children en `<div id="smooth-wrapper"><div id="smooth-content">{children}</div></div>`.
> 2. `src/components/Navbar.jsx` sticky top-0 con `backdrop-blur-md bg-black/60`, logo "CacaoTrace" (Geist-ish, tracking-tight), 4 links ("Landing", "Mapa", "Cómo funciona", "FAQ") + CTA pill **"Registra tu finca"** con bg `#F2C94C` (dorado cacao) y hover scale 1.03. Esconde la navbar al scroll-down y muestra al scroll-up con `gsap.to y:-100, duration:0.3`.
> 3. Integra en `src/App.tsx` y verifica con `Skill("browse")` que scroll sea suave a 60fps y la navbar aparezca/desaparezca limpio.
> 4. Antes de continuar, consulta `docs/design-specs/VERCEL-DESIGN.md` para espaciado y tipografía.

## Prompt 2 — Hero con SplitText stagger (20 min)

> En `frontend/src/components/Hero.jsx` para CacaoTrace:
>
> - Fondo `#0A0A0A` con grid noise overlay sutil.
> - Pill superior animada: *"🇨🇴 Santander produce el 41% del cacao de Colombia"* rotando entre 3 claims cada 3s con `gsap.timeline().repeat(-1)`.
> - Título masivo: *"Trazabilidad real del cacao fino de Santander."* — font-size clamp(3.5rem, 9vw, 9rem), font-weight 800, tracking-tight.
> - Usa `SplitText` de `gsap/SplitText` para animar **chars con stagger 0.02, yPercent 100→0, duration 1, ease "expo.out"** dentro de `useGSAP` de `@gsap/react`.
> - Sub: *"Del cacaocultor de San Vicente al chocolatero de Bélgica. QR en cada lote. Cumple EUDR."*
> - CTAs dual: **"Ver demo en vivo"** (dorado `#F2C94C`, onClick scroll a #mapa) + **"Soy comprador"** (ghost con borde blanco 10%).
> - Mockup a la derecha: card con "Finca La Esperanza" + mini-mapa + datos IoT en vivo (placeholder con valores rotando).
>
> Verifica en navegador que:
> - Stagger se vea limpio sin FOUC (usar `visibility:hidden` hasta que SplitText haga su trabajo).
> - Responsive: en mobile el mockup se apila debajo.
>
> Lee primero `docs/design-specs/FRAMER-DESIGN.md` para el tono motion.

## Prompt 3 — Features bento + KPIs counter (25 min)

> Crea dos componentes:
>
> 1. `src/components/BentoFeatures.jsx` — grid 3 columnas × 2 filas (responsive: 1 col mobile). 6 cards:
>    - "Mapa de fincas verificadas" (col-span 2, icon Leaflet)
>    - "Monitoreo IoT en vivo" (sensores fermentación, gráfica placeholder)
>    - "QR de trazabilidad" (mockup QR grande)
>    - "Chatbot IA con MCP" (badge "LLM-agnostic")
>    - "Cumple EUDR out-of-the-box" (badge UE 🇪🇺)
>    - "Precio justo al productor" (span 2, chart up)
>    Cada `BentoCard` con tilt 3D magnético: `gsap.quickTo` sobre `rotateX/rotateY` (±8°) siguiendo al mouse. `perspective: 1000px` en el contenedor padre. Border `1px rgba(255,255,255,0.08)`, radius 24px.
>
> 2. `src/components/KpiCounters.jsx` — 4 contadores scroll-triggered: `65.000 familias`, `41% producción nacional`, `95% fino de aroma`, `+56% exportaciones 2025`. Usa `gsap.to({val:0}, {val:target, duration:2, snap:{val:1}, onUpdate, scrollTrigger:{start:"top 80%", once:true}})`.
>
> Verifica con `Skill("browse")` que hover y counter se vean fluidos. Cita `docs/design-specs/SUPABASE-DESIGN.md` §Layout.

## Prompt 4 — Mapa público Leaflet (25 min)

> En `src/pages/Landing.jsx` agrega sección `#mapa`:
>
> - `import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'` + `import 'leaflet/dist/leaflet.css'` en `main.tsx`.
> - Centro Santander: `[7.13, -73.12]`, zoom 9.
> - Tiles OSM: `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`.
> - Fetch de fincas: `fetch(import.meta.env.VITE_API_URL + '/api/fincas/publicas/')` con fallback a mock hardcoded:
>   ```js
>   [
>     { id:1, slug:'la-esperanza', nombre:'Finca La Esperanza', municipio:'San Vicente de Chucurí', lat:6.8814, lng:-73.4225, variedades:['Trinitario','Criollo'], area_ha:4.5 },
>     { id:2, slug:'el-cacaotal', nombre:'Finca El Cacaotal', municipio:'El Carmen de Chucurí', lat:6.71, lng:-73.52, variedades:['CCN-51','ICS-95'], area_ha:3.0 },
>     { id:3, slug:'los-yariguies', nombre:'Finca Los Yariguíes', municipio:'Rionegro', lat:7.38, lng:-73.15, variedades:['Trinitario'], area_ha:5.2 },
>     { id:4, slug:'aromas-del-rio', nombre:'Finca Aromas del Río', municipio:'Landázuri', lat:6.22, lng:-73.81, variedades:['Criollo'], area_ha:2.8 },
>     { id:5, slug:'san-jose', nombre:'Finca San José', municipio:'Cimitarra', lat:6.3167, lng:-73.95, variedades:['Forastero','CCN-51'], area_ha:6.0 }
>   ]
>   ```
> - Cada marker con icon custom (emoji 🍫 en `L.divIcon`). Popup muestra nombre + municipio + variedades + botón "Ver perfil público" que navega a `/finca/:slug`.
> - Panel izquierdo de filtros: checkboxes por variedad (Criollo, Trinitario, Forastero, CCN-51) y por municipio. Filtra el array.
> - Arriba del mapa: contador *"X fincas verificadas"* reactivo.
>
> Verifica que el mapa cargue sin errores de hidratación (Leaflet + SSR requiere `dynamic` o usar solo en cliente). Prueba filtros.

## Prompt 5 — FAQ + CTA final + Footer (15 min)

> 1. `src/components/Faq.jsx` — 6 preguntas animadas con `gsap.to height:auto, duration:0.4, ease:"power2.out"` + chevron rotación. Preguntas: "¿Qué es EUDR?", "¿Necesito comprar sensores IoT?", "¿Cuánto cuesta registrar mi finca?", "¿Qué LLM usa el chatbot?", "¿Puedo exportar a Europa?", "¿Cómo me certifico?".
>
> 2. `src/components/CtaFinal.jsx` — headline **"Siembra confianza en cada grano"** revelado con `SplitText` lines, stagger 0.15. Input email con glow dorado on focus + botón *"Registrar mi finca"*.
>
> 3. `src/components/Footer.jsx` — wordmark gigante **"CACAOTRACE"** (font-size 20vw, outline-text-webkit o color `rgba(242,201,52,0.1)`), links a GitHub, créditos, logos de actores (MinTIC, UIS, Fedecacao — placeholders).
>
> Verifica Lighthouse > 85 en performance. Invoca `Skill("seo-page")` sobre `http://localhost:5173` antes del freeze.

---

## Checklist pre-merge

- [ ] `pnpm build` sin errores
- [ ] Sin imports rotos (`pnpm lint`)
- [ ] Responsive en 375px, 768px, 1440px
- [ ] Navbar no tapa el hero en mobile
- [ ] Leaflet carga tiles correctamente
- [ ] Todos los CTAs tienen href o onClick definido
- [ ] `Skill("browse")` con screenshot final pasado

## Commit pattern

```bash
git add frontend/src && git commit -m "feat(landing): hero gsap + bento + mapa leaflet + faq"
git push origin feat/landing
gh pr create --base develop --title "feat(landing): CacaoTrace landing MVP" --body "Cierra hero, mapa, bento, faq, cta. Lista para integrar."
```
