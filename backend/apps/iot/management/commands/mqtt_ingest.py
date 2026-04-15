"""MQTT ingest worker — subscribes to cacao/# and persists SensorData."""
import asyncio
import json

import aiomqtt
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.iot.models import SensorData


class Command(BaseCommand):
    help = "MQTT ingest worker — cacao/finca/+/lote/+/+"

    def handle(self, *args, **kwargs):
        asyncio.run(self._run())

    async def _run(self):
        host = getattr(settings, "MQTT_BROKER_HOST", "mosquitto")
        port = getattr(settings, "MQTT_BROKER_PORT", 1883)
        user = getattr(settings, "MQTT_BROKER_USERNAME", "")
        pw = getattr(settings, "MQTT_BROKER_PASSWORD", "")
        retry = 0
        while True:
            try:
                params = {"hostname": host, "port": port}
                if user:
                    params["username"] = user
                    params["password"] = pw
                async with aiomqtt.Client(**params) as client:
                    await client.subscribe("cacao/finca/+/lote/+/+")
                    self.stdout.write(
                        self.style.SUCCESS(f"[ingest] listening @ {host}:{port}")
                    )
                    retry = 0
                    async for msg in client.messages:
                        try:
                            # cacao/finca/<finca>/lote/<lote>/<tipo>
                            parts = msg.topic.value.split("/")
                            lote_id = int(parts[4])
                            tipo = parts[5]
                            payload = json.loads(msg.payload.decode())
                            await sync_to_async(
                                SensorData.objects.create, thread_sensitive=True
                            )(
                                lote_id=lote_id,
                                tipo=tipo,
                                valor=float(payload["valor"]),
                                unidad=payload.get("unidad", ""),
                            )
                        except Exception as e:
                            self.stderr.write(f"drop: {e}")
            except aiomqtt.MqttError as e:
                retry += 1
                wait = min(2**retry, 30)
                self.stderr.write(f"mqtt err: {e}, retry in {wait}s")
                await asyncio.sleep(wait)
