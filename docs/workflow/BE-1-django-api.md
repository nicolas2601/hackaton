# BE-1 — Django API + Auth + Seed · 👨‍💻 Nicolas

> **Persona:** Nicolas · **Rol:** Backend-1 · **Rama:** `feat/api` · **Tiempo:** 2h
> **Deliverable:** Modelos, migraciones, JWT, CRUD REST, seed de 5 fincas + usuarios + sensores, endpoint público de fincas.

## Checklist

- [ ] **T+0–15min** · Setup + settings split + Supabase/SQLite
- [ ] **T+15–45min** · Modelos + migraciones + admin
- [ ] **T+45–75min** · Serializers + ViewSets + routers
- [ ] **T+75–90min** · JWT auth + CORS + permisos
- [ ] **T+90–110min** · Seed management command
- [ ] **T+110–120min** · Test smoke + merge

## Skills y agentes

```
Skill("code-review"), Skill("review")
Agent(subagent_type="backend-dev", prompt="...")
Agent(subagent_type="Explore", prompt="Lee ~/Documentos/IOTcentral/backend/apps/*/models.py — qué campos y patterns puedo reciclar para CacaoTrace según AGENTS.md §11")
```

---

## Setup (T+0–15min)

```bash
git checkout -b feat/api
cd backend
uv add djangorestframework djangorestframework-simplejwt django-cors-headers aiomqtt \
       'psycopg[binary]' python-decouple qrcode pillow django-extensions
uv sync
```

Decidir DB:
- **Opción A (rápida):** SQLite — `db.sqlite3` ya existe. Sirve para demo local.
- **Opción B (demo-ready):** Supabase Postgres — credenciales en `.env`.

Si es B, en `backend/config/settings/base.py`:
```python
import dj_database_url
DATABASES = {"default": dj_database_url.config(default=os.getenv("DATABASE_URL"))}
```

---

## Prompt 1 — Modelos (20 min)

> En `backend/apps/` crea 3 apps nuevas: `fincas`, `iot`, `cosechas`. Agrega a `INSTALLED_APPS` en `config/settings/base.py`.
>
> **`fincas/models.py`** (basado en AGENTS.md §11):
>
> ```python
> from django.db import models
> from django.contrib.auth import get_user_model
> User = get_user_model()
>
> class Finca(models.Model):
>     propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fincas')
>     slug = models.SlugField(unique=True, max_length=80)
>     nombre = models.CharField(max_length=120)
>     municipio = models.CharField(max_length=80)
>     lat = models.DecimalField(max_digits=9, decimal_places=6)
>     lng = models.DecimalField(max_digits=9, decimal_places=6)
>     area_total_ha = models.DecimalField(max_digits=6, decimal_places=2)
>     verificada = models.BooleanField(default=False)
>     foto = models.URLField(blank=True)
>     descripcion = models.TextField(blank=True)
>     created_at = models.DateTimeField(auto_now_add=True)
>
>     class Meta:
>         ordering = ['-created_at']
>
>     def __str__(self):
>         return f"{self.nombre} ({self.municipio})"
>
> VARIEDAD_CHOICES = [
>     ('criollo', 'Criollo'),
>     ('trinitario', 'Trinitario'),
>     ('forastero', 'Forastero'),
>     ('ccn51', 'CCN-51'),
>     ('ics60', 'ICS-60'),
>     ('ics95', 'ICS-95'),
>     ('otro', 'Otro'),
> ]
>
> class Lote(models.Model):
>     finca = models.ForeignKey(Finca, on_delete=models.CASCADE, related_name='lotes')
>     nombre = models.CharField(max_length=80)
>     variedad = models.CharField(max_length=20, choices=VARIEDAD_CHOICES)
>     num_plantas = models.PositiveIntegerField()
>     edad_años = models.PositiveSmallIntegerField()
>     area_ha = models.DecimalField(max_digits=6, decimal_places=2)
>     lat = models.DecimalField(max_digits=9, decimal_places=6)
>     lng = models.DecimalField(max_digits=9, decimal_places=6)
>     estado = models.CharField(max_length=20, default='activo')
>
> class PerfilExportacion(models.Model):
>     finca = models.OneToOneField(Finca, on_delete=models.CASCADE)
>     certificaciones = models.JSONField(default=list)  # ['organico', 'rainforest', 'eudr']
>     mercados_destino = models.JSONField(default=list)  # ['EEUU', 'Belgica']
>     capacidad_anual_kg = models.PositiveIntegerField(default=0)
>     qr_url = models.URLField(blank=True)
> ```
>
> **`iot/models.py`:**
>
> ```python
> from django.db import models
> from apps.fincas.models import Lote
>
> SENSOR_TIPOS = [
>     ('temp_suelo', 'Temperatura suelo'),
>     ('hum_suelo', 'Humedad suelo'),
>     ('temp_ferm', 'Temperatura fermentación'),
>     ('hum_secado', 'Humedad secado'),
>     ('ph_suelo', 'pH suelo'),
> ]
>
> class SensorData(models.Model):
>     lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='sensores')
>     tipo = models.CharField(max_length=20, choices=SENSOR_TIPOS, db_index=True)
>     valor = models.FloatField()
>     unidad = models.CharField(max_length=10)
>     timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
>
>     class Meta:
>         indexes = [models.Index(fields=['lote', 'tipo', '-timestamp'])]
> ```
>
> **`cosechas/models.py`:** Cosecha + ControlFitosanitario (ver AGENTS.md §11).
>
> Corre `uv run python manage.py makemigrations && uv run python manage.py migrate`. Registra todos los modelos en `admin.py`.

## Prompt 2 — Serializers + ViewSets REST (25 min)

> Crea en cada app `serializers.py` + `views.py`:
>
> **Endpoints obligatorios:**
>
> | Método | Path | Permisos | Descripción |
> |---|---|---|---|
> | POST | `/api/auth/login/` | public | JWT login (simplejwt) |
> | POST | `/api/auth/refresh/` | public | refresh token |
> | GET | `/api/fincas/me/` | auth | finca del usuario logueado |
> | GET | `/api/fincas/publicas/` | public | lista fincas verificadas (para mapa landing) |
> | GET | `/api/fincas/publicas/<slug>/` | public | perfil público |
> | GET | `/api/lotes/?finca_id=` | auth | lotes del agricultor |
> | GET | `/api/lotes/<id>/` | auth dueño | detalle lote |
> | GET | `/api/sensors/?lote_id=&tipo=&limit=30` | auth dueño | series IoT |
> | GET | `/api/sensors/latest/?lote_id=` | auth dueño | último valor por tipo |
> | GET | `/api/sensors/stream/?lote_id=` | auth dueño | **SSE** eventos nuevos |
>
> Para el SSE, crea `iot/views_sse.py`:
>
> ```python
> from django.http import StreamingHttpResponse
> import asyncio, json, time
> from apps.iot.models import SensorData
>
> async def sensor_stream(request):
>     lote_id = request.GET.get('lote_id')
>     last_id = 0
>     async def event_stream():
>         nonlocal last_id
>         while True:
>             qs = SensorData.objects.filter(lote_id=lote_id, id__gt=last_id).order_by('id')[:50]
>             async for s in qs:
>                 last_id = s.id
>                 yield f"data: {json.dumps({'tipo': s.tipo, 'valor': s.valor, 'timestamp': s.timestamp.isoformat()})}\n\n"
>             await asyncio.sleep(1.5)
>     return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
> ```
>
> Endpoint `/api/sensors/publicos/?finca_id=` para la vitrina pública (solo promedios, no raw).
>
> Registra router DRF en `config/urls.py`. Configura CORS_ALLOWED_ORIGINS con `http://localhost:5173`.
>
> Invoca `Skill("code-review")` sobre el diff antes de commit.

## Prompt 3 — Seed management command (20 min)

> `backend/apps/core/management/commands/seed_cacao.py`:
>
> Crea 5 usuarios productores + 5 fincas (datos exactos de `CONTEXT.md §7`):
>
> | Finca | Municipio | Lat | Lng | Variedades | Ha |
> |---|---|---|---|---|---|
> | Finca La Esperanza | San Vicente de Chucurí | 6.8814 | -73.4225 | Trinitario + Criollo | 4.5 |
> | Finca El Cacaotal | El Carmen de Chucurí | 6.7100 | -73.5200 | CCN-51 + ICS-95 | 3.0 |
> | Finca Los Yariguíes | Rionegro | 7.3800 | -73.1500 | Trinitario | 5.2 |
> | Finca Aromas del Río | Landázuri | 6.2200 | -73.8100 | Criollo acriollado | 2.8 |
> | Finca San José | Cimitarra | 6.3167 | -73.9500 | Forastero + CCN-51 | 6.0 |
>
> Para cada finca crea 2-3 lotes con variedades coherentes + 200 puntos históricos de sensores (últimas 2 horas, 1 cada 30s) con valores realistas según `CONTEXT.md §7`:
> - temp_suelo: 22-28°C
> - hum_suelo: 60-80%
> - temp_ferm: 35-50°C (curva que sube)
> - hum_secado: decreciente 60→8%
>
> Al final imprime URLs + credenciales:
> ```
> ✅ Seed completado
> Admin: admin@cacaotrace.co / admin
> Agricultor demo: efrain@sanvicente.co / cacao123
> http://localhost:5173/finca/la-esperanza
> ```
>
> Ejecuta `uv run python manage.py seed_cacao --flush`.

## Prompt 4 — QR generación + PerfilExportacion (10 min)

> En `apps/fincas/signals.py` al crear/actualizar `Finca`:
> - Genera QR apuntando a `{FRONTEND_URL}/finca/{slug}` usando `qrcode.make()`.
> - Sube a `Supabase Storage` en bucket `qr-codes/` (si configurado) o guarda en `media/qr/{slug}.png`.
> - Actualiza `PerfilExportacion.qr_url`.
>
> Endpoint `/api/fincas/<slug>/qr.png` devuelve el PNG directo con `FileResponse`.

---

## Checklist pre-merge

- [ ] `uv run python manage.py check` sin warnings
- [ ] Migraciones commiteadas
- [ ] Seed corre limpio
- [ ] `curl http://localhost:8000/api/fincas/publicas/ | jq length` → 5
- [ ] Login con JWT devuelve access+refresh
- [ ] `Skill("code-review")` pasado

```bash
git add backend && git commit -m "feat(api): models + jwt + sse + seed cacaotrace"
git push origin feat/api
gh pr create --base develop --title "feat(api): Django REST + JWT + SSE + seed"
```
