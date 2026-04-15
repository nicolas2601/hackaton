# FE-2 — Dashboard agricultor + Perfil público + Chat MCP

> **Persona:** Frontend-2 · **Rama:** `feat/dashboard` · **Tiempo:** 2h
> **Deliverable:** Dashboard privado del agricultor con gráficas IoT + chat IA + perfil público con QR de trazabilidad.

## Checklist

- [ ] **T+0–10min** · Setup + rutas protegidas
- [ ] **T+10–45min** · Layout dashboard + sidebar + lista de lotes
- [ ] **T+45–80min** · Gráficas IoT en tiempo real (SSE) + Recharts
- [ ] **T+80–100min** · Chat MCP (POST a `/mcp/query`)
- [ ] **T+100–115min** · Página pública `/finca/:slug` + QR
- [ ] **T+115–120min** · QA + merge

## Skills y agentes

```
Skill("frontend-design"), Skill("ui-ux-pro-max")
Skill("vercel-react-best-practices")
Skill("code-review")
Agent(subagent_type="coder", prompt="...")  # para scaffolding rápido
```

---

## Setup (T+0–10min)

```bash
git checkout -b feat/dashboard
cd frontend
pnpm add @tanstack/react-query recharts react-qr-code date-fns
pnpm dlx shadcn@latest add card badge tabs dialog sheet separator skeleton table
pnpm dev
```

Variables: `VITE_API_URL=http://localhost:8000`, `VITE_MCP_URL=http://localhost:8765`.

---

## Prompt 1 — Layout dashboard + auth route (15 min)

> En `frontend/src/`:
>
> 1. `src/lib/api.ts` — wrapper axios/fetch con `Authorization: Bearer ${localStorage.getItem('jwt')}`. Endpoints: `/api/auth/login/`, `/api/fincas/me/`, `/api/lotes/?finca_id=`, `/api/sensors/?lote_id=`.
> 2. `src/hooks/useAuth.ts` — zustand store con `{token, user, login(), logout()}`. Persist en localStorage.
> 3. `src/pages/Login.jsx` — card centrada con input email + password + botón dorado. Mock si BE no está listo: usuario `efrain@sanvicente.co` / `cacao123`.
> 4. `src/pages/Dashboard.jsx` layout:
>    - Sidebar izquierda fija (240px): logo "CacaoTrace", nav (Resumen, Lotes, Cosechas, Fitosanitario, Chat IA, Perfil público), botón logout abajo.
>    - Main: header con breadcrumb + badge "Finca La Esperanza · San Vicente de Chucurí".
>    - Route guard: si no hay token → redirect `/login`.
> 5. Estilo: fondo `#0A0A0A`, cards `#111`, borde `rgba(255,255,255,0.08)`. Consulta `docs/design-specs/SUPABASE-DESIGN.md` y `LINEAR` patterns (densidad, monospace para datos).
>
> Verifica que login mock funcione y redirija.

## Prompt 2 — Vista de Lotes + mapa finca + tarjetas (20 min)

> `src/pages/Lotes.jsx`:
>
> - `useQuery` de TanStack trae `/api/lotes/?finca_id=1`. Fallback mock:
>   ```js
>   [
>     { id:1, nombre:'Lote Norte', variedad:'Trinitario', num_plantas:450, area_ha:1.5, edad_años:8, estado:'activo', lat:6.882, lng:-73.423 },
>     { id:2, nombre:'Lote Río', variedad:'Criollo', num_plantas:300, area_ha:1.2, edad_años:12, estado:'activo', lat:6.881, lng:-73.424 },
>     { id:3, nombre:'Lote Sur', variedad:'Trinitario', num_plantas:520, area_ha:1.8, edad_años:5, estado:'en_renovación', lat:6.880, lng:-73.425 }
>   ]
>   ```
> - Grid 3 cols: cada card muestra nombre, variedad badge (color por variedad), plantas, área, edad, estado. Click abre drawer con detalle + mini-mapa leaflet del lote.
> - Mini-mapa: usa MapContainer con zoom 16 centrado en el lote, marker + polígono placeholder.
>
> Design reference: `docs/design-specs/LINEAR-DESIGN.md` (si existe — si no, `SUPABASE-DESIGN.md`).

## Prompt 3 — Gráfica IoT en tiempo real con SSE (30 min)

> `src/components/SensorChart.jsx` recibe `loteId` y renderiza 4 gráficas Recharts LineChart:
>
> - Temperatura suelo (°C, rango 18-32)
> - Humedad suelo (%, rango 40-95)
> - Temperatura fermentación (°C, rango 28-52)
> - Humedad secado (%, rango 6-65)
>
> Conecta SSE a `${VITE_API_URL}/api/sensors/stream/?lote_id=${loteId}`:
>
> ```js
> const es = new EventSource(url);
> es.onmessage = (e) => {
>   const { tipo, valor, timestamp } = JSON.parse(e.data);
>   setData(prev => ({ ...prev, [tipo]: [...(prev[tipo]||[]).slice(-30), { t: timestamp, v: valor }] }));
> };
> return () => es.close();
> ```
>
> Mantener ventana de 30 puntos. Colors: suelo naranja `#F2C94C`, fermentación rojo `#EF4444`, secado azul `#3B82F6`.
>
> Fallback si SSE falla: polling cada 3s a `/api/sensors/latest/?lote_id=`.
>
> Indicador live: punto verde pulsante + texto "En vivo" con `animate-pulse`.
>
> Verifica consumiendo datos del simulador (BE-2 debe estar corriendo).

## Prompt 4 — Chat MCP (20 min)

> `src/pages/ChatIA.jsx`:
>
> - Layout tipo ChatGPT: mensajes scrolleables + textarea abajo + botón enviar (enter = send, shift+enter = newline).
> - POST a `${VITE_MCP_URL}/chat` con `{ messages, finca_id }`. Respuesta streaming con `fetch().body.getReader()`. Muestra tokens a medida que llegan.
> - Sugerencias iniciales (chips): "¿Cómo va mi fermentación del Lote Norte?", "¿Qué debo hacer si el pH baja de 5?", "Dame precios del cacao en Europa esta semana", "¿Estoy listo para exportar?".
> - Header del chat: badge "MCP · Claude/Qwen/Gemini · Datos de tu finca únicamente".
> - Cuando la IA usa una tool MCP, muéstralo como un mensaje-pill gris: `🔧 get_lote_sensors(1) → 127 puntos`.
>
> Lee `mcp-server/mcp_server/server.py` si existe para entender contrato. Si el endpoint aún no responde, stub con delay de 1s y respuesta *"Pronto podré analizar los datos de tu finca..."*.

## Prompt 5 — Perfil público + QR (15 min)

> `src/pages/FincaPublica.jsx` (ruta pública, sin auth):
>
> - `useParams()` → `slug`. Fetch `/api/fincas/publicas/${slug}/`.
> - Hero fullwidth con foto + nombre + badge "✅ Verificada EUDR" + municipio.
> - Secciones:
>   1. **Ubicación** — mini-mapa Leaflet zoom 13, lat/lng visibles (cumple EUDR).
>   2. **Variedades** — pills con % de cada una.
>   3. **Calidad verificada** — cards con últimos datos IoT promedio (fermentación, secado) + badge "Monitoreo IoT activo".
>   4. **Historial fitosanitario** — tabla últimos 5 controles.
>   5. **Certificaciones** — grid de logos (orgánico, rainforest, EUDR).
>   6. **Trazabilidad** — QR grande (`react-qr-code`) apuntando a la URL actual. Botón "Descargar PDF".
>   7. **Contactar productor** — botón WhatsApp a número del productor.
>
> Estilo claro (light mode) — optimizado para que el comprador europeo lo vea desde su móvil. Consulta `docs/design-specs/STRIPE-DESIGN.md` para tono premium confiable.
>
> Verifica escaneando el QR con tu móvil que abra la URL correcta.

---

## Checklist pre-merge

- [ ] Login mock funciona
- [ ] SSE se conecta (o polling fallback)
- [ ] Chat responde (o stub muestra mensaje)
- [ ] QR escaneable desde móvil
- [ ] `pnpm build` clean
- [ ] Sin console.errors en prod build

```bash
git add frontend/src && git commit -m "feat(dashboard): lotes, iot live, chat mcp, perfil publico"
git push origin feat/dashboard
gh pr create --base develop --title "feat(dashboard): dashboard + perfil publico + chat"
```
