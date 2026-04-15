# 🚀 Deploy — CacaoTrace

> Tiempo estimado: **10 min Coolify** / **15 min fallback Vercel+Railway**. Hacer SOLO después de T+1h45 (code freeze).

## Ruta 1 — Coolify (primaria)

### Prerequisitos
- Servidor Coolify funcionando (ya lo tienes, ver IoT Central deploy)
- DNS apuntando: `cacaotrace.<tu-dominio>`, `api.cacaotrace.<tu-dominio>`, `mcp.cacaotrace.<tu-dominio>`

### Pasos

1. **Push a main**
   ```bash
   git checkout main && git merge develop && git push origin main
   ```

2. **En Coolify UI** → New Resource → Docker Compose → apunta a `github.com/nicolas2601/hackaton` branch `main`. Coolify detecta `docker-compose.yml`.

3. **Configurar servicios** (asigna dominio a cada uno):
   | Servicio | Imagen/Dockerfile | Dominio | Puerto |
   |---|---|---|---|
   | frontend | `Dockerfile.frontend` | `cacaotrace.dominio` | 80 |
   | backend | `Dockerfile.backend` | `api.cacaotrace.dominio` | 8000 |
   | mcp | `Dockerfile.mcp` | `mcp.cacaotrace.dominio` | 8765 |
   | mosquitto | one-click service | — | 1883 |
   | mqtt-worker | `backend` image cmd `manage.py mqtt_ingest` | (sin dominio) | — |
   | simulator | `Dockerfile.sim` | (sin dominio) | — |

4. **Env vars** (en UI de Coolify → cada servicio):
   ```
   DATABASE_URL=postgres://user:pass@host:5432/db
   DJANGO_SECRET_KEY=<genera 50+ chars>
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=api.cacaotrace.dominio
   CORS_ALLOWED_ORIGINS=https://cacaotrace.dominio
   MQTT_BROKER_URL=mqtt://mosquitto:1883
   VITE_API_URL=https://api.cacaotrace.dominio
   VITE_MCP_URL=https://mcp.cacaotrace.dominio
   MCP_API_TOKEN=<service token>
   LLM_PROVIDER=claude
   ANTHROPIC_API_KEY=<si usas claude>
   SIM_SPEED=60
   ```

5. **TLS** — Coolify + Traefik + Let's Encrypt automático. Dar 1 min para issuer.

6. **Primer deploy** → click Deploy. Coolify construye las 5 imágenes en paralelo.

7. **Post-deploy (SSH al servicio backend)**:
   ```bash
   python manage.py migrate
   python manage.py seed_cacao
   python manage.py createsuperuser  # opcional
   ```

8. **Smoke test**:
   - `curl https://api.cacaotrace.dominio/api/fincas/publicas/` → 5 fincas
   - `curl https://mcp.cacaotrace.dominio/mcp/tools` → 5 tools
   - Navegar a `https://cacaotrace.dominio` → landing carga
   - Escanear QR desde móvil → `/finca/la-esperanza` abre

---

## Ruta 2 — Fallback rápido (15 min, sin Coolify)

Si Coolify falla o no hay tiempo:

### Frontend → **Vercel**
```bash
cd frontend
pnpm dlx vercel --prod
# responder: framework Vite, build `pnpm build`, output `dist`
# env vars: VITE_API_URL, VITE_MCP_URL
```

### Backend + MCP + Mosquitto → **Railway** (monorepo, 3 servicios)

1. `railway login && railway init`
2. En dashboard Railway:
   - Servicio 1 (`backend`): apuntar a `Dockerfile.backend`, env vars arriba, agregar **Railway Postgres** plugin y usar `DATABASE_URL` automático.
   - Servicio 2 (`mcp`): `Dockerfile.mcp`, expose port 8765.
   - Servicio 3 (`mosquitto`): template official `eclipse-mosquitto:2`, port 1883 interno.
   - Servicio 4 (`mqtt-worker`): mismo Dockerfile backend, CMD override `python manage.py mqtt_ingest`.
   - Servicio 5 (`simulator`): `Dockerfile.sim`, env `MQTT_BROKER_URL=mqtt://mosquitto.railway.internal:1883`.
3. `railway up` en cada servicio.
4. Agregar dominio custom o usar `*.up.railway.app`.

### Supabase Postgres (alternativa a Railway Postgres)
1. Crear proyecto en supabase.com (free tier)
2. `Settings → Database → Connection string` → copiar `DATABASE_URL`
3. Pegar en Railway env vars del backend.

---

## Checklist post-deploy

- [ ] HTTPS funciona en los 3 dominios
- [ ] `api/fincas/publicas/` devuelve 5
- [ ] Landing renderiza sin CORS errors
- [ ] Login con `efrain@sanvicente.co / cacao123` funciona
- [ ] Gráfica IoT muestra datos que cambian cada 5s
- [ ] Chat IA responde (aunque sea stub)
- [ ] QR escaneado desde móvil abre perfil público
- [ ] Screenshot/grabación de demo hecha como backup

## Rollback

Coolify: click Revert al deploy anterior.
Railway: cada servicio tiene historial de deploys, revert en 1 click.
Vercel: `vercel rollback`.

---

## Troubleshooting express

| Síntoma | Causa probable | Fix |
|---|---|---|
| Frontend no carga, CORS error | `CORS_ALLOWED_ORIGINS` no incluye dominio Vercel | Editar env y redeploy backend |
| SSE no conecta en prod | Traefik buffering | Añadir header `X-Accel-Buffering: no` en respuesta |
| Mosquitto no recibe conexión del worker | Red incorrecta | En Railway usar `mosquitto.railway.internal`; en Coolify usar el nombre del servicio |
| Seed falla | Migraciones no aplicadas | `manage.py migrate --run-syncdb` |
| MCP tools vacías | Token inválido | Regenerar `MCP_API_TOKEN` y propagar a frontend |
