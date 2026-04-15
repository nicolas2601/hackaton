"""Server-Sent Events endpoint for live IoT telemetry."""
from __future__ import annotations

import asyncio
import json

from asgiref.sync import sync_to_async
from django.http import StreamingHttpResponse
from django.views.decorators.http import require_GET

from apps.iot.models import SensorData


@require_GET
def sensor_stream(request):
    """Stream SSE events with new sensor readings for a given lote."""
    lote_id = request.GET.get("lote_id")
    if not lote_id:
        return StreamingHttpResponse("missing lote_id", status=400)

    async def stream():
        last_id = 0
        yield ": connected\n\n"
        while True:
            rows = await sync_to_async(list)(
                SensorData.objects.filter(lote_id=lote_id, id__gt=last_id).order_by(
                    "id"
                )[:50]
            )
            for r in rows:
                last_id = r.id
                payload = {
                    "id": r.id,
                    "tipo": r.tipo,
                    "valor": r.valor,
                    "unidad": r.unidad,
                    "timestamp": r.timestamp.isoformat(),
                }
                yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(1.5)

    resp = StreamingHttpResponse(stream(), content_type="text/event-stream")
    resp["Cache-Control"] = "no-cache"
    resp["X-Accel-Buffering"] = "no"
    return resp
