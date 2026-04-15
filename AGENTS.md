# AGENTS.md — CacaoTrace: Granja Digital Inteligente del Cacao de Santander

> Documento maestro para cualquier agente de IA (Claude Code, Cursor, Windsurf, Antigravity, Joker/Qwen Code, Gemini CLI) que trabaje en este repo. **Léelo antes de escribir una sola línea de código.**

---

## 1. Identidad del proyecto

- **Reto:** Exporta Santander Dashboard — Datos y Tecnología para Empresas que Quieren Llegar al Mundo
- **Evento:** Hackathon Regional Bucaramanga — Colombia 5.0 (MinTIC, TEVEANDINA, UD)
- **Sede / fecha:** Auditorio Luis A. Calvo, UIS — **15 de abril de 2026, 9 AM – 5 PM**
- **Nombre del producto:** **CacaoTrace**
- **Sector:** AgroTech — cacao fino de aroma de Santander
- **Tagline:** *"El pasaporte digital del cacao fino de Santander."*
- **Equipo:** 4 personas (2 frontend, 2 backend) — ventana real de codificación **~2 horas**
- **Barrera a resolver:** falta de trazabilidad digital del pequeño cacaocultor → EUDR (jun 2026/2027) + exigencia de chocolateros gourmet
- **Restricciones duras:** sin hardware físico (simulador MQTT); MVP demo-able; pitch de 5 min; deploy obligatorio

### Rúbrica de evaluación (pesos)
Pertinencia territorial 25% · Innovación 20% · Viabilidad técnica 20% · Impacto 20% · Presentación 15%.

---

## 2. Producto — resumen ejecutivo

**CacaoTrace** es una plataforma de dos capas que conecta al pequeño cacaocultor de Santander con el mercado internacional.

- **Capa A — Dashboard privado del agricultor:** mapa de finca con lotes, monitoreo IoT (fermentación, secado, suelo), registro fitosanitario, chatbot IA vía MCP.
- **Capa B — Vitrina pública para compradores:** mapa de fincas verificadas, perfil público con QR de trazabilidad, filtros por variedad/municipio/certificación, datos de mercado exportador.
- **Landing pública:** storytelling del cacao de Santander + CTA para agricultores y compradores.

Ver `Descargas/CONTEXT.md` para el contexto completo del dominio (variedades, actores, municipios, datos de mercado, EUDR).

---

## 3. Stack tecnológico (acordado)

| Componente | Tecnología |
|---|---|
| **Frontend landing + app** | React 19 + Vite + **pnpm** + Tailwind v4 + shadcn/ui + **GSAP + ScrollTrigger + SplitText** |
| **Animaciones hero/landing** | GSAP (SmoothScroller, ScrollTrigger, SplitText, Flip) — inspiración: landeros.framer.website |
| **Backend** | Django 5 + DRF + JWT (`djangorestframework-simplejwt`) + uv |
| **Base de datos** | Supabase Postgres (solo DB, sin Auth/RLS/Realtime) — Neon como fallback |
| **Cache** | Redis local en Docker (opcional) |
| **Broker IoT** | Mosquitto (Docker) — topic `cacao/finca/{id}/lote/{id}/{metric}` |
| **Cliente MQTT (Django)** | `aiomqtt` en management command separado |
| **Realtime al front** | SSE vía Django (no Supabase Realtime) |
| **IA** | **MCP (FastMCP 3.0)** como servicio separado. LLM-agnóstico (Claude / Qwen / Gemini vía MCP) |
| **Mapas** | **Leaflet + OpenStreetMap** (gratis, sin API key) |
| **Gráficas** | Recharts (suficiente para MVP; uPlot si se supera 2k puntos) |
| **QR** | `qrcode` (Python) para generar, `react-qr-code` para mostrar |
| **Contenedores** | Docker + Docker Compose (ya hay base en el repo) |
| **Despliegue** | Coolify (servidor físico) · fallback: Railway + Vercel |
| **CLIs de IA** | Claude Code · Qwen Code (Joker) · Gemini CLI |

### Paquetes frontend a instalar al arrancar (copiar-pegar)
```bash
cd frontend && pnpm add react-router-dom @tanstack/react-query zustand leaflet react-leaflet gsap @gsap/react recharts react-qr-code lucide-react clsx tailwind-merge
pnpm add -D tailwindcss@next @tailwindcss/vite autoprefixer
pnpm dlx shadcn@latest init
```

### Paquetes backend a instalar
```bash
cd backend && uv add djangorestframework djangorestframework-simplejwt django-cors-headers aiomqtt psycopg[binary] python-decouple qrcode pillow supabase-py django-extensions
```

---

## 4. Reglas de trabajo OBLIGATORIAS para agentes de IA

### 4.1 Skills y sub-agentes
- Si ves `[OBLIGATORIO]` o `[SUGERIDO]` en el contexto del prompt (hook `skill-router.sh`), úsalo antes de improvisar.
- **Antes de improvisar** en un dominio especializado invoca la skill con `Skill(...)`. Skills críticas para este proyecto:
  - `frontend-design`, `ui-ux-pro-max`, `gsap-core`, `gsap-scrolltrigger`, `gsap-timeline`, `gsap-plugins`
  - `vercel-react-best-practices`
  - `code-review`, `review`, `ship`
  - `qa`, `playwright`, `browse` (para dogfooding visual del demo)
  - `seo-page` (para la landing)
- **Agentes priorizados:** `researcher`, `Explore`, `system-architect`, `backend-dev`, `coder`, `tester`, `reviewer`, `production-validator`, `task-orchestrator`.
- Catálogo local: `~/.agents/agency-agents/` (179 agentes en 15 categorías) y subagent_types disponibles vía Agent tool.

### 4.2 Concurrencia (regla dorada)
- **1 mensaje = todas las operaciones relacionadas.** Siempre que 3+ tool calls puedan ir en paralelo, van en paralelo.
- Multi-dominio (frontend + backend + IoT) → lanzar varios sub-agentes en un solo mensaje.

### 4.3 Uso obligatorio de MCP
- Toda integración IA-↔-datos pasa por el **servidor FastMCP** (servicio separado, NO embebido en Django).
- Herramientas MCP mínimas a exponer (ver `mcp-server/`):
  - `get_finca_info(finca_id)`
  - `get_lote_sensors(lote_id)`
  - `get_cosechas(finca_id, año)`
  - `get_controles_fitosanitarios(lote_id)`
  - `get_mercados_exportacion(variedad?, pais_destino?)`
  - `deep_search_competencia(variedad, pais_destino)` (SI hay tiempo)

### 4.4 Código
- Hacer lo que se pide, nada más.
- NUNCA crear archivos innecesarios. SIEMPRE preferir editar.
- NUNCA crear `.md` o READMEs sin pedido explícito.
- NUNCA guardar tests/markdowns en la raíz del repo.
- SIEMPRE leer un archivo antes de editarlo.
- NUNCA commitear `.env` ni secretos.
- Archivos bajo 500 líneas. Interfaces tipadas en APIs públicas. Validar input en bordes.
- Comentarios de código en inglés; UI en español colombiano coloquial (*"Su finca"*, *"Cosecha"*, *"Está listo para exportar"*).

### 4.5 Design system
- Cuando generes UI, consulta **`docs/design-specs/VERCEL-DESIGN.md`** (landing) y **`docs/design-specs/SUPABASE-DESIGN.md`** (dashboard). Para motion usa **`docs/design-specs/FRAMER-DESIGN.md`** como referencia de animación.
- Paleta CacaoTrace (adaptada): fondo `#0A0A0A`, texto `#F5F5F0`, acento dorado `#F2C94C`, cacao `#7B3F00`, verde hoja `#2E7D32`, lime CTA `#C8FF4D` (sustituible).

---

## 5. Dominio del negocio — contexto resumido (ver CONTEXT.md para detalle)

### 5.1 Persona objetivo
**Don Efraín Suárez**, 54 años, cacaocultor en San Vicente de Chucurí. 3 ha, variedades trinitario + criollo acriollado. 12 años fermentando a ojo. Celular con internet. Lo que le importa: vender su cacao como fino (no como corriente) y demostrar que su finca no viene de deforestación para exportar a Europa.

### 5.2 Barrera concreta
EUDR (UE) exige trazabilidad completa (geolocalización + diligencia debida + no deforestación) para PYMES desde **junio 2026** (posible extensión jun 2027). Sin trazabilidad → no se exporta → campesino pierde 2x-3x por kilo.

### 5.3 Municipios cacaoteros clave
San Vicente de Chucurí, El Carmen de Chucurí, Rionegro, Landázuri, Cimitarra, El Playón, Lebrija, Sabana de Torres.

### 5.4 Variedades
Criollo (fino, ~5%) · Trinitario (fino, común en Santander, ~10-15%) · Forastero (industrial, ~80%) · CCN-51 (productivo, no fino) · ICS-60 / ICS-95 (clones trinitarios locales).

### 5.5 Actores a mencionar en el pitch
Cámara de Comercio de Bucaramanga · Fedecacao · ICA · UNAB (Proyecto Hållbar Kakao) · ProColombia · Analdex · AGROSAVIA · MinAgricultura.

---

## 6. Decisiones arquitectónicas (no re-debatir)

| Decisión | Razón |
|---|---|
| **Supabase solo como DB + Storage** | El equipo controla auth/realtime desde Django. Evita lock-in. |
| **Django maneja auth/sesiones/multi-tenancy** | Stack que el equipo domina. |
| **FastMCP separado del proceso web Django** | Sesiones MCP long-lived. Escalado independiente. |
| **Mosquitto en Docker local** | Costo cero, control total. |
| **Sin TimescaleDB en MVP** | Datos de 1 demo caben en tablas planas. |
| **MCP es la única vía de integración con LLMs** | Agnosticismo. |
| **Landing + app en un solo repo monorepo** | Menos fricción en 2h. Misma build. |
| **QR apunta a `/finca/:slug`** público | Trazabilidad verificable sin login. |

---

## 7. Diferenciadores (cualquier feature los debe reforzar)

1. **Pasaporte digital por finca** — geolocalización, variedades, IoT, fitosanitario, todo en un perfil público con QR.
2. **LLM-agnóstico vía MCP** — hoy Claude, mañana Qwen/Gemini sin reescribir.
3. **Offline-first / on-prem friendly** — todo corre en servidor propio (Coolify).
4. **Lenguaje del cacaocultor santandereano** — UI en español coloquial, no jerga tech.
5. **Cumplimiento EUDR out-of-the-box** — geolocalización + historial auditable.
6. **Simulador de sensores** — el agricultor que aún no tiene sensores puede simular y ver impacto.

---

## 8. Plan operativo del hackathon (2 horas de coding real)

### 8.1 Roles (4 personas)
- **FE-1 — Landing + Mapa público** (React + GSAP + Leaflet)
- **FE-2 — Dashboard agricultor + Chat MCP + Perfil público/QR** (React + Recharts + shadcn)
- **BE-1 — Django models/APIs + Auth JWT + Seed** (Django + DRF + Supabase)
- **BE-2 — MQTT worker + Simulador + FastMCP server** (aiomqtt + FastMCP)

Ver `docs/workflow/` — un `.md` por persona con tareas, prompts copy-paste y checklist.

### 8.2 Hitos
- **T+0:** los 4 empiezan a la vez sobre `develop`. Rama por persona: `feat/landing`, `feat/dashboard`, `feat/api`, `feat/mqtt-mcp`.
- **T+45min:** primer PR de cada uno (WIP). Merge a `develop` con squash.
- **T+1h15:** integración end-to-end (sim → Django → frontend lee datos).
- **T+1h45:** code freeze. Deploy en Coolify. Ensayar pitch.
- **T+2h:** demo.

### 8.3 Orden de sacrificio
Si hay retraso, sacrificar en este orden:
1. Deep search MCP (P5)
2. Plantillas de simulación IoT (P5)
3. Chat MCP (P4)
4. **NUNCA sacrificar:** landing + mapa público + 1 dashboard con 1 gráfica IoT + simulador publicando + al menos 1 tool MCP consumida por un LLM en vivo. **Esa es la demo.**

---

## 9. Despliegue

- **Primario:** Coolify (servidor físico). Ver `docs/DEPLOY.md`.
- **Fallback (15 min):** Vercel (frontend) + Railway (Django + Mosquitto + MCP). Variables en UI de cada plataforma.
- **Dominios:** `cacaotrace.<dominio>` (app), `api.cacaotrace.<dominio>`, `mcp.cacaotrace.<dominio>`.
- Variables de entorno se gestionan en Coolify/Railway, jamás en repo.

---

## 10. Reutilización del proyecto IoT Central

Nicolas ya tiene un proyecto funcional **IoT Central (Django + Next + Mosquitto + Coolify)** en `~/Documentos/IOTcentral/`. Reutilizar:
- `backend/apps/` — estructura de modelos de dispositivos/sensores → adaptar a `finca`, `lote`, `sensor_data`.
- `backend/config/` — settings de Django split (base/dev/prod) y Daphne/ASGI.
- `mosquitto/` — config de broker y auth.
- `docker-compose.yaml` — labels de Traefik para Coolify (copiar patrón).
- `simulador/device_simulator.py` — base del simulador MQTT (ajustar topics y rangos a cacao).

Prompt para reciclar: *"Lee `~/Documentos/IOTcentral/backend/apps/<app>/models.py` y adapta el esquema a CacaoTrace según `AGENTS.md` §11. No copies literal — refactoriza nombres y campos al dominio cacao."*

---

## 11. Modelos de datos (mínimos para el MVP)

```
Finca(id, slug, nombre, propietario_nombre, municipio, lat, lng, area_ha, verificada, foto, created_at)
Lote(id, finca_id, nombre, variedad, num_plantas, edad_años, area_ha, lat, lng, estado)
SensorData(id, lote_id, tipo, valor, unidad, timestamp)   # tipo: temp_suelo|hum_suelo|temp_ferm|hum_secado
ControlFitosanitario(id, lote_id, fecha, tipo_control, plaga, tratamiento, resultado, foto)
Cosecha(id, lote_id, fecha, kg_baba, kg_seco, dias_ferment, temp_prom_ferm, dias_secado, calidad)
PerfilExportacion(id, finca_id, certificaciones, mercados, capacidad_anual_kg, qr_url)
```

Seed obligatorio con 5 fincas (ver CONTEXT.md §7).

---

## 12. Anti-patrones

- ❌ Supabase Auth / RLS / Realtime / Edge Functions.
- ❌ SDK de Anthropic/OpenAI directo en Django views (todo por MCP).
- ❌ MCP embebido en Django.
- ❌ `paho-mqtt` síncrono en código async.
- ❌ Binarios en Postgres (usar Supabase Storage).
- ❌ Hardcodear dominios/URLs en código.
- ❌ Recharts para >2k puntos (usar uPlot).
- ❌ Crear `.md` no solicitados.
- ❌ Improvisar en GSAP/Tailwind/shadcn sin invocar la skill.
- ❌ Trabajar secuencialmente cuando 3 tareas pueden ir en paralelo.
- ❌ Slides genéricas en el pitch — **la demo viva manda**.

---

## 13. Recordatorio final

> El jurado no premia features, premia **historias que resuelven dolores reales con tecnología viable y territorialmente pertinente**. Toda decisión debe responder a: *¿esto le sirve a Don Efraín de San Vicente mañana lunes?* Si no, no se construye.

> **Prioridad absoluta:** demo viva que funciona > arquitectura elegante > código limpio. En ese orden.

---

*CacaoTrace — Hackathon Colombia 5.0 — Bucaramanga, 15 de abril de 2026*
