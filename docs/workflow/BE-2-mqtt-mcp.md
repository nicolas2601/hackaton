# BE-2 — Simulador MQTT + Worker + FastMCP Server

> **Persona:** Backend-2 · **Rama:** `feat/mqtt-mcp` · **Tiempo:** 2h
> **Deliverable:** Simulador Python publicando MQTT realista + worker Django (aiomqtt) persistiendo en DB + FastMCP server exponiendo 5 tools a LLMs.

## Checklist

- [ ] **T+0–10min** · Setup + verificar Mosquitto en Docker
- [ ] **T+10–40min** · Simulador publicando datos realistas
- [ ] **T+40–70min** · Worker Django `mqtt_ingest` con aiomqtt
- [ ] **T+70–105min** · FastMCP server con 5 tools
- [ ] **T+105–115min** · Endpoint `/chat` que un LLM puede consumir
- [ ] **T+115–120min** · Smoke + merge

## Skills y agentes

```
Skill("code-review")
Agent(subagent_type="Explore", prompt="Lee ~/Documentos/IOTcentral/simulador/device_simulator.py y ~/Documentos/IOTcentral/backend/apps/**/mqtt*.py — qué patrones puedo reciclar adaptando topics y rangos a cacao")
```

---

## Setup (T+0–10min)

```bash
git checkout -b feat/mqtt-mcp
# Mosquitto ya está en docker-compose.yml. Verificar:
docker compose up -d mosquitto
docker compose logs mosquitto | tail -10

# Test publish/subscribe
mosquitto_sub -h localhost -p 1883 -t 'cacao/#' -v &
mosquitto_pub -h localhost -p 1883 -t 'cacao/test' -m 'hola'

# Deps
cd simulator && uv add aiomqtt pydantic python-decouple
cd ../backend && uv add aiomqtt channels 'channels-redis'
cd ../mcp-server && uv add 'fastmcp>=3.0' httpx python-decouple
```

---

## Prompt 1 — Simulador MQTT (30 min)

> En `simulator/main.py`, reemplaza/ajusta para CacaoTrace (ignora el código de manufactura que haya). Basado en `CONTEXT.md §7` y `AGENTS.md §11`.
>
> Estructura:
>
> ```python
> # simulator/main.py
> import asyncio, json, random, math
> from datetime import datetime
> import aiomqtt
>
> BROKER = os.getenv("MQTT_BROKER_URL", "mqtt://mosquitto:1883")
> SPEED = float(os.getenv("SIM_SPEED", "1"))  # 1x, 60x, 120x
>
> FINCAS = [
>     {"id": 1, "lotes": [{"id": 1, "variedad": "trinitario", "en_fermentacion": True},
>                         {"id": 2, "variedad": "criollo", "en_fermentacion": False}]},
>     {"id": 2, "lotes": [{"id": 3, "variedad": "ccn51", "en_fermentacion": True},
>                         {"id": 4, "variedad": "ics95", "en_fermentacion": False}]},
>     # ... 5 fincas total
> ]
>
> class CacaoSim:
>     def __init__(self, finca_id, lote):
>         self.finca_id, self.lote = finca_id, lote
>         self.ferm_day = 0  # día de fermentación (0-7)
>         self.dry_day = 0   # día de secado (0-5)
>
>     def temp_suelo(self):      return round(random.gauss(25, 1.5), 2)
>     def hum_suelo(self):       return round(random.gauss(70, 6), 2)
>     def ph_suelo(self):        return round(random.gauss(6.3, 0.2), 2)
>     def temp_ferm(self):
>         # sube de 28→48 en 4 días, baja a 40
>         curve = [28, 34, 42, 48, 47, 45, 40, 35]
>         base = curve[min(self.ferm_day, 7)]
>         return round(base + random.gauss(0, 1.0), 2)
>     def hum_secado(self):
>         # decae de 60% → 7.5% en 5 días
>         curve = [60, 45, 30, 18, 10, 7.5]
>         base = curve[min(self.dry_day, 5)]
>         return round(base + random.gauss(0, 0.5), 2)
>
> async def publish_loop(client, sim):
>     topic_base = f"cacao/finca/{sim.finca_id}/lote/{sim.lote['id']}"
>     readings = [
>         ("temp_suelo", sim.temp_suelo, "C"),
>         ("hum_suelo", sim.hum_suelo, "%"),
>         ("ph_suelo", sim.ph_suelo, ""),
>     ]
>     if sim.lote["en_fermentacion"]:
>         readings.append(("temp_ferm", sim.temp_ferm, "C"))
>         readings.append(("hum_secado", sim.hum_secado, "%"))
>
>     while True:
>         for tipo, fn, unidad in readings:
>             payload = json.dumps({"valor": fn(), "unidad": unidad, "ts": datetime.utcnow().isoformat()})
>             await client.publish(f"{topic_base}/{tipo}", payload, qos=1)
>         await asyncio.sleep(5 / SPEED)
>
> async def main():
>     async with aiomqtt.Client(BROKER) as client:
>         sims = [CacaoSim(f["id"], l) for f in FINCAS for l in f["lotes"]]
>         await asyncio.gather(*(publish_loop(client, s) for s in sims))
>
> if __name__ == "__main__":
>     asyncio.run(main())
> ```
>
> Añade `time_accelerator.py` (ya existe) para avanzar `ferm_day`/`dry_day` con `SPEED`. Para la demo, `SIM_SPEED=60` comprime 1 día real en 24 min.
>
> Verifica con `mosquitto_sub -h localhost -t 'cacao/#' -v` que publique ~20 msgs/s.

## Prompt 2 — Worker Django aiomqtt (30 min)

> Crea `backend/apps/iot/management/commands/mqtt_ingest.py`:
>
> ```python
> import asyncio, json
> import aiomqtt
> from django.core.management.base import BaseCommand
> from django.conf import settings
> from asgiref.sync import sync_to_async
> from apps.iot.models import SensorData
> from apps.fincas.models import Lote
>
> class Command(BaseCommand):
>     help = "MQTT ingest worker — cacao/finca/+/lote/+/+"
>
>     def handle(self, *args, **kwargs):
>         asyncio.run(self._run())
>
>     async def _run(self):
>         async with aiomqtt.Client(settings.MQTT_BROKER_HOST, port=settings.MQTT_BROKER_PORT) as client:
>             await client.subscribe("cacao/finca/+/lote/+/+")
>             self.stdout.write(self.style.SUCCESS("✅ MQTT ingest listening"))
>             async for msg in client.messages:
>                 try:
>                     parts = msg.topic.value.split("/")
>                     # cacao/finca/1/lote/2/temp_ferm
>                     lote_id = int(parts[4])
>                     tipo = parts[5]
>                     payload = json.loads(msg.payload.decode())
>                     await sync_to_async(SensorData.objects.create)(
>                         lote_id=lote_id, tipo=tipo,
>                         valor=payload["valor"], unidad=payload.get("unidad", "")
>                     )
>                 except Exception as e:
>                     self.stderr.write(f"drop: {e}")
> ```
>
> Añade en `docker-compose.yml` el servicio `mqtt-worker` que corre `uv run python manage.py mqtt_ingest`.
>
> Verifica: mientras el simulador publica, corre el worker y revisa `SensorData.objects.count()` crezca.

## Prompt 3 — FastMCP Server con 5 tools (35 min)

> En `mcp-server/mcp_server/server.py`:
>
> ```python
> from fastmcp import FastMCP
> import httpx, os
>
> app = FastMCP("cacaotrace")
> API = os.getenv("API_URL", "http://backend:8000")
> TOKEN = os.getenv("MCP_API_TOKEN", "")  # service token
>
> def _auth_headers():
>     return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
>
> @app.tool()
> async def get_finca_info(finca_id: int) -> dict:
>     """Datos generales de una finca (nombre, municipio, ubicación, variedades, área)."""
>     async with httpx.AsyncClient() as c:
>         r = await c.get(f"{API}/api/fincas/{finca_id}/", headers=_auth_headers())
>         return r.json()
>
> @app.tool()
> async def get_lote_sensors(lote_id: int, tipo: str = "", limit: int = 30) -> dict:
>     """Últimos N datos IoT de un lote. tipo: temp_suelo|hum_suelo|temp_ferm|hum_secado|ph_suelo."""
>     params = {"lote_id": lote_id, "limit": limit}
>     if tipo: params["tipo"] = tipo
>     async with httpx.AsyncClient() as c:
>         r = await c.get(f"{API}/api/sensors/", params=params, headers=_auth_headers())
>         return {"data": r.json(), "count": len(r.json())}
>
> @app.tool()
> async def get_cosechas(finca_id: int, año: int = 0) -> dict:
>     """Historial de cosechas de una finca."""
>     params = {"finca_id": finca_id}
>     if año: params["año"] = año
>     async with httpx.AsyncClient() as c:
>         r = await c.get(f"{API}/api/cosechas/", params=params, headers=_auth_headers())
>         return r.json()
>
> @app.tool()
> async def get_controles_fitosanitarios(lote_id: int) -> dict:
>     """Historial fitosanitario de un lote (plagas, tratamientos)."""
>     async with httpx.AsyncClient() as c:
>         r = await c.get(f"{API}/api/controles/?lote_id={lote_id}", headers=_auth_headers())
>         return r.json()
>
> @app.tool()
> async def get_mercados_exportacion(variedad: str = "", pais_destino: str = "") -> dict:
>     """Datos de mercado de exportación de cacao por variedad y destino. Precios referenciales."""
>     # Hardcode CONTEXT.md §7 data para la demo
>     data = {
>         "precios_cop_kg": {
>             "corriente": [8000, 10000],
>             "fino_aroma": [15000, 25000],
>             "premium_certificado": [25000, 40000],
>         },
>         "precios_export_usd_ton": {
>             "corriente": [2500, 3000],
>             "fino_aroma": [4000, 6000],
>             "premium": [6000, 10000],
>         },
>         "destinos_principales": ["EEUU (37.1%)", "Malasia", "México", "Costa Rica", "Bélgica", "Alemania"],
>         "regulaciones": {
>             "EUDR": "Obligatorio para PYMES desde junio 2026 (posible extensión jun 2027). Requiere: geolocalización, diligencia debida, no deforestación."
>         },
>     }
>     if pais_destino:
>         data["nota"] = f"Filtrado a {pais_destino}"
>     return data
>
> if __name__ == "__main__":
>     app.run(transport="streamable-http", host="0.0.0.0", port=8765)
> ```
>
> Prueba local: `uv run python -m mcp_server.server` y `curl http://localhost:8765/mcp/tools` debería listar las 5 tools.

## Prompt 4 — Endpoint `/chat` con LLM-agnostic router (20 min)

> En `mcp-server/mcp_server/chat.py` agrega FastAPI que envuelve FastMCP y expone `/chat`:
>
> ```python
> from fastapi import FastAPI, Request
> from fastapi.responses import StreamingResponse
> from fastapi.middleware.cors import CORSMiddleware
> import os, httpx, json
>
> http = FastAPI()
> http.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
>
> # Provider selection via env: LLM_PROVIDER=claude|qwen|gemini
> PROVIDER = os.getenv("LLM_PROVIDER", "claude")
>
> SYSTEM = """Eres el asistente de CacaoTrace, especializado en cacao fino de Santander, Colombia.
> Usa las herramientas MCP para acceder a datos reales de la finca del agricultor.
> Responde en español colombiano natural, coloquial y empático. Hablas con Don Efraín, agricultor.
> Protege la información privada — nunca la compartas públicamente.
> Si te preguntan por mercados, usa get_mercados_exportacion."""
>
> @http.post("/chat")
> async def chat(req: Request):
>     body = await req.json()
>     messages = body.get("messages", [])
>     finca_id = body.get("finca_id", 1)
>
>     # Route al provider elegido; implementar al menos uno.
>     if PROVIDER == "claude":
>         return StreamingResponse(_stream_claude(messages, finca_id), media_type="text/event-stream")
>     elif PROVIDER == "qwen":
>         return StreamingResponse(_stream_qwen(messages, finca_id), media_type="text/event-stream")
>     # ... etc
> ```
>
> La integración con el LLM debe pasar las tools MCP en formato que el proveedor entienda (anthropic: `tools=[...]`, openai-compat: `functions=[...]`). Para simplicidad, stub inicial que devuelve un eco + llamada a `get_lote_sensors` si el prompt contiene "sensor|fermentación|lote".
>
> Smoke test: `curl -X POST http://localhost:8765/chat -d '{"messages":[{"role":"user","content":"cómo va el lote norte"}]}'`.

---

## Checklist pre-merge

- [ ] Simulador publica 5+ fincas × 2 lotes × 3-5 tipos cada 5s
- [ ] Worker MQTT persiste en DB (verificar con `manage.py shell`)
- [ ] MCP server expone 5 tools (curl OK)
- [ ] `/chat` responde algo (stub es aceptable para demo)
- [ ] Docker compose `docker compose up -d mosquitto simulator mqtt-worker mcp` → todo sin errores

```bash
git add simulator mcp-server backend/apps/iot && git commit -m "feat(iot+mcp): sim + aiomqtt worker + fastmcp 5 tools"
git push origin feat/mqtt-mcp
gh pr create --base develop --title "feat(iot+mcp): simulator + ingest + MCP 5 tools"
```
