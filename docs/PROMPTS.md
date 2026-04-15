# 📝 Biblioteca de prompts — CacaoTrace

> Copy-paste listos por tarea. Cada prompt:
> - Menciona paquetes a instalar
> - Referencia archivos exactos
> - Termina pidiendo **verificación visual / smoke test**
> - Invoca skills/agentes cuando aplica

Antes de usar cualquier prompt **lee `AGENTS.md`**. Skills útiles siempre: `frontend-design`, `gsap-*`, `code-review`, `review`, `browse`.

---

## 🎨 Frontend — patrones reutilizables

### A.1 Componente con GSAP + useGSAP
```
En frontend/src/components/<Nombre>.jsx crea un componente que [descripción]. Usa gsap + @gsap/react (useGSAP para cleanup automático). Registra plugins necesarios en main.tsx una sola vez. Antes de empezar consulta Skill("gsap-core") y Skill("gsap-scrolltrigger"). Después de escribir el código, verifica en http://localhost:5173 que la animación corra a 60fps sin jank. Si falla, ajusta ease a "power2.out" y duration 0.6-1.0. No uses keyframes CSS — todo vía gsap.
```

### A.2 Tarjeta con tilt 3D magnético
```
En frontend/src/components/TiltCard.jsx crea un wrapper que aplique tilt 3D magnético a cualquier child. Usa gsap.quickTo sobre rotateX/rotateY (±8°) siguiendo al mouse relativo al rect del elemento. perspective: 1000px en padre. Reset suave al mouseleave. Memoiza con useMemo. Verifica hover en 5 cards distintas sin lag.
```

### A.3 Sección con ScrollTrigger pin + scrub
```
Crea frontend/src/components/PinnedSection.jsx que recibe children y los pinea al scrollear. Usa gsap.registerPlugin(ScrollTrigger). ScrollTrigger config: { trigger: ref, pin: true, scrub: 1, start: "top top", end: "+=2000" }. Anima x:-75% en el track interno. Verifica que al terminar el scroll el pin se libera limpio sin saltos.
```

### A.4 Formulario con validación y toast
```
En frontend/src/forms/<Nombre>.tsx crea un form con shadcn Input/Button/Card + react-hook-form + zod para validación. On submit POST a <endpoint> con axios, muestra toast success/error con sonner. Loading state con Skeleton. Invoca Skill("frontend-design") antes. Verifica con datos inválidos y válidos.
```

---

## 🔧 Backend Django

### B.1 Nuevo modelo + migración + admin
```
En backend/apps/<app>/models.py añade modelo <Nombre> con campos [lista]. Agrega __str__ y Meta.ordering. Registra en admin.py con list_display y search_fields. Corre `uv run python manage.py makemigrations && migrate`. Antes de empezar lee AGENTS.md §11 para convención de nombres. Verifica en /admin que los campos editables se vean bien.
```

### B.2 Endpoint REST + permisos
```
En backend/apps/<app>/ crea serializer + viewset para <Modelo> con CRUD. Filtros por [campos] via django-filter. Permiso: IsAuthenticated para escritura, AllowAny para GET publicos (usa @action(detail=False, methods=['get'], permission_classes=[AllowAny]) para /publicas/). Registra en router DRF. Testea con curl: GET, POST con JWT, filtro por param. Verifica con Skill("code-review") antes de commit.
```

### B.3 Worker asyncio (aiomqtt)
```
Crea backend/apps/iot/management/commands/<nombre>.py que conecte a aiomqtt.Client, suscriba a <topic>, parsee mensajes JSON y persista en DB usando sync_to_async(Model.objects.create). Maneja reconnect automático en except aiomqtt.MqttError con backoff exponencial. Logs con self.stdout.SUCCESS/ERROR. Verifica con mosquitto_pub que los mensajes se persistan y count crezca.
```

### B.4 SSE endpoint
```
En backend/apps/iot/views_sse.py crea endpoint async que haga polling cada 1.5s a DB por registros con id > last_id y los emita como eventos SSE text/event-stream. Usa StreamingHttpResponse + async generator. Cierra conexión limpia si cliente desconecta. Smoke test: `curl -N http://localhost:8000/api/sensors/stream/?lote_id=1` debería stream-ear eventos cada 5s.
```

---

## 🤖 MCP (FastMCP)

### C.1 Nueva tool MCP
```
En mcp-server/mcp_server/server.py añade @app.tool() async def <nombre>(param:tipo) -> dict que [descripción]. Llama al endpoint Django correspondiente con httpx.AsyncClient (reutilizando _auth_headers()). Documenta el docstring — el LLM lo lee para decidir cuándo usar la tool. Smoke: `curl http://localhost:8765/mcp/tools | jq '.tools[].name'` debe listar la nueva tool.
```

### C.2 Router LLM-agnostic
```
En mcp-server/mcp_server/providers/<claude|qwen|gemini>.py implementa un cliente que tome messages + tools y stream-ee tokens al cliente. Debe convertir las tools MCP al formato del provider: Anthropic tools schema | OpenAI functions | Gemini function_declarations. Cuando el LLM llame una tool, fetch el resultado del MCP y alimentalo de vuelta al modelo. Para hackathon basta 1 provider funcional. Verifica con un prompt de prueba que dispare get_lote_sensors.
```

---

## 🗺️ Leaflet / Mapas

### D.1 Mapa con filtros
```
En frontend/src/components/FincasMap.jsx usa react-leaflet MapContainer zoom=9 center=[7.13,-73.12]. Tiles OSM. Recibe prop `fincas` y renderiza Marker por cada una con divIcon emoji 🍫. Popup con nombre + variedades + link a /finca/:slug. Recibe `filters` prop con {variedades:[], municipios:[]} y filtra antes de renderizar. Import 'leaflet/dist/leaflet.css' en main.tsx. Fix para iconos rotos de Leaflet en React: `delete L.Icon.Default.prototype._getIconUrl`. Verifica marcadores visibles y filtros reactivos.
```

---

## 🐳 Docker / DevOps

### E.1 Añadir servicio a docker-compose
```
En docker-compose.yml añade servicio <nombre> con: build context, env_file:.env, depends_on:[mosquitto, backend], networks:[default], restart:unless-stopped, healthcheck curl-based. Corre `docker compose config` para validar YAML. Corre `docker compose up -d <nombre>` y `docker compose logs <nombre>` — debe quedar "listening" en <30s.
```

### E.2 Deploy Coolify / Railway
```
Invoca Skill("ship") si existe. Si no:
1. git push a main
2. En Coolify UI: crea proyecto apuntando a github.com/nicolas2601/hackaton, branch main
3. Crea 4 services: backend (Dockerfile.backend), frontend (Dockerfile.frontend), mcp (Dockerfile.mcp), simulator (Dockerfile.sim). Mosquitto como one-click service.
4. Asigna dominios: cacaotrace, api.cacaotrace, mcp.cacaotrace
5. Env vars desde docs/DEPLOY.md
6. Deploy y verifica health checks
```

---

## 🧪 QA / Testing

### F.1 Smoke test end-to-end
```
Invoca Skill("browse") o Skill("playwright") y ejecuta este flow:
1. Navega a http://localhost:5173 — verifica hero carga y scroll smooth
2. Scroll a mapa — verifica 5 markers visibles
3. Click "Finca La Esperanza" popup → click "Ver perfil" → /finca/la-esperanza renderiza QR
4. /login con efrain@sanvicente.co / cacao123 → redirect a /dashboard
5. Dashboard → Lotes → click Lote Norte → gráfica IoT actualiza cada 5s (live)
6. Chat IA → pregunta "cómo va mi fermentación" → respuesta no vacía en <10s
Reporta con screenshot cada paso. Si algo falla, abre issue.
```

### F.2 Lighthouse landing
```
Invoca Skill("seo-page") apuntando a http://localhost:5173. Objetivo: Performance > 80, Accesibilidad > 90, SEO > 90. Si performance < 80, revisa: imágenes sin lazy loading, fonts no preload, bundles grandes (pnpm build --analyze). Itera máximo 2 veces.
```

---

## 🎬 Pitch / Demo

### G.1 Guión de 5 minutos
```
Lee CONTEXT.md §6. Genera guión palabra-por-palabra de 5min dividido en:
0:00–0:45 — Problema (Don Efraín, EUDR, cifras Santander)
0:45–1:30 — Solución (CacaoTrace 2 capas + MCP + QR)
1:30–3:30 — Demo en vivo (landing → mapa → perfil → dashboard IoT → chat IA → QR)
3:30–4:30 — Impacto (65k familias, 2x-3x precio, escalabilidad)
4:30–5:00 — Viabilidad (Coolify, MCP agnostic, sensores $15k COP)
Incluye transiciones naturales y un cierre memorable. Redáctalo en español colombiano natural, no corporate.
```

---

## 🧹 Meta

### H.1 Antes de cualquier PR
```
1. `Skill("review")` sobre el diff de tu rama
2. `pnpm build` (frontend) o `uv run python manage.py check` (backend) sin errores
3. `git diff develop...HEAD` — ¿hay secrets? ¿hay archivos no pedidos?
4. PR body con: qué cambia, cómo se prueba, screenshot si es UI, cómo se reversa
```

### H.2 Debugging rápido
```
Invoca Agent(subagent_type="Explore", prompt="Busca en el repo patrones similares a [problema]. Leer archivos relevantes y proponer fix en bajo 200 palabras"). Si el bug es de build, pega el error en el prompt. NO intentes fixes especulativos — diagnóstica primero.
```
