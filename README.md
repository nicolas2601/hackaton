# 🍫 CacaoTrace

> **Pasaporte digital del cacao fino de Santander.** Plataforma de trazabilidad para conectar al pequeño cacaocultor con el mercado internacional — cumple EUDR, IA vía MCP, IoT simulado.

**Hackathon Regional Bucaramanga — Colombia 5.0 · 15 abril 2026 · UIS**

---

## ⚡ Quick start (2 min)

```bash
git clone https://github.com/nicolas2601/hackaton.git cacaotrace && cd cacaotrace
cp .env.example .env     # editar con tus credenciales
docker compose up -d     # levanta db + mosquitto + backend + frontend + mcp + simulador
```

- Frontend: http://localhost:5173
- API Django: http://localhost:8000
- MCP: http://localhost:8765
- Mosquitto: `mqtt://localhost:1883`

## 📚 Lectura obligatoria antes de codear

1. **`AGENTS.md`** — reglas de trabajo + stack + decisiones arquitectónicas
2. **`~/Descargas/CONTEXT.md`** — contexto del dominio (cacao, variedades, EUDR, actores)
3. **`docs/workflow/<tu-rol>.md`** — tu checklist paso a paso con prompts listos
4. **`docs/PROMPTS.md`** — biblioteca de prompts por tarea
5. **`docs/DEPLOY.md`** — Coolify + fallback Railway/Vercel
6. **`docs/design-specs/*.md`** — design systems de referencia (Vercel, Framer, Supabase, Stripe)

## 👥 Equipo (4 devs, 2h coding)

| Rol | Persona | Rama | Deliverable |
|---|---|---|---|
| **FE-1** | Landing + Mapa público | `feat/landing` | Hero GSAP + mapa Leaflet Santander + filtros |
| **FE-2** | Dashboard + Perfil + QR | `feat/dashboard` | Vistas de lote + gráficas IoT + chat + perfil público |
| **BE-1** | Django API + Auth | `feat/api` | Models, seed, JWT, endpoints REST |
| **BE-2** | MQTT + MCP + Simulador | `feat/mqtt-mcp` | Simulador, worker aiomqtt, FastMCP server |

Ver `docs/workflow/` para detalle por persona.

## 🏗️ Estructura del monorepo

```
HACKATON/
├── AGENTS.md               # Reglas + stack + dominio (LEER PRIMERO)
├── README.md               # Este archivo
├── docker-compose.yml      # Stack completo local
├── .env.example            # Variables base
├── backend/                # Django + DRF + uv
│   └── apps/
│       ├── core/           # auth, users
│       ├── fincas/         # Finca, Lote, PerfilExportacion
│       ├── iot/            # SensorData, worker MQTT
│       └── cosechas/       # Cosecha, ControlFitosanitario
├── frontend/               # React 19 + Vite + pnpm + Tailwind v4 + GSAP
│   └── src/
│       ├── pages/
│       │   ├── Landing.jsx         # Hero GSAP + mapa público
│       │   ├── Dashboard.jsx       # Vista agricultor
│       │   └── FincaPublica.jsx    # Perfil público + QR
│       └── components/
├── mcp-server/             # FastMCP 3.0 — tools sobre BD Django
├── simulator/              # Script Python que publica MQTT
├── mosquitto/              # Config del broker
├── nginx/                  # Reverse proxy (prod)
└── docs/
    ├── workflow/           # Checklists por persona
    ├── design-specs/       # DESIGN.md de Vercel, Framer, Supabase
    ├── PROMPTS.md          # Biblioteca de prompts
    └── DEPLOY.md           # Guía Coolify + fallback
```

## ⏱️ Hitos del hackathon

| Hora | Hito |
|---|---|
| **T+0** | Los 4 en paralelo desde minuto cero. NO esperarse. |
| **T+45m** | Primer PR por persona (WIP). Merge squash a `develop`. |
| **T+1h15** | Integración end-to-end: simulador → MQTT → Django → frontend muestra. |
| **T+1h45** | **Code freeze.** Deploy en Coolify. Ensayar pitch. |
| **T+2h** | Pitch 5 min ante jurado. |

## 🎯 Demo flow (5 min)

1. **Landing** → hero animado → scroll a mapa de Santander con fincas.
2. **Click en Finca La Esperanza (San Vicente)** → perfil público → QR.
3. **Login como agricultor** → dashboard → ver lote → gráfica de fermentación en vivo.
4. **Preguntar al chat:** *"¿Cómo va la fermentación del Lote Norte?"* → respuesta vía MCP con datos reales.
5. **Mostrar QR escaneado en móvil** → muestra trazabilidad pública.

## 🔒 Seguridad

- Nunca commitear `.env`, `db.sqlite3`, ni credenciales.
- `.gitignore` ya cubre `.env`, `node_modules`, `__pycache__`, `.venv`.
- Validar input en bordes (DRF serializers + Zod en frontend).

## 🚀 Deploy

Ver `docs/DEPLOY.md`. Primario: Coolify. Fallback: Railway + Vercel (15 min).

---

*Hecho con ❤️ y cacao fino por Nicolas, Paula, Andrés Julián y Nath.*
