"""MQTT publisher with aiomqtt."""
import asyncio
import json
import logging
import time
from aiomqtt import Client, MqttError
from models.telemetry import MachineTelemetry

logger = logging.getLogger(__name__)


class MQTTPublisher:
    """Async MQTT publisher for machine telemetry."""

    def __init__(self, broker_host: str, broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client: Client | None = None
        self._connected = False

    async def connect(self):
        """Connect to MQTT broker."""
        try:
            self.client = Client(self.broker_host, self.broker_port)
            await self.client.__aenter__()
            self._connected = True
            logger.info(f"Connected to MQTT broker {self.broker_host}:{self.broker_port}")
        except MqttError as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    async def disconnect(self):
        """Gracefully disconnect."""
        if self.client:
            await self.client.__aexit__(None, None, None)
            self._connected = False
            logger.info("Disconnected from MQTT broker")

    async def publish_telemetry(self, telemetry: MachineTelemetry):
        """Publish telemetry to correct topic with QoS 1."""
        topic = f"factory/{telemetry.tenant}/{telemetry.line}/{telemetry.machine}/telemetry"
        payload = telemetry.model_dump_json()

        if not self._connected:
            return

        try:
            await self.client.publish(topic, payload, qos=1)
            logger.debug(f"Published to {topic}")
        except MqttError as e:
            logger.error(f"Failed to publish telemetry: {e}")

    async def publish_heartbeat(self, tenant: str, line: str, machine: str):
        """Publish heartbeat with QoS 0."""
        topic = f"factory/{tenant}/{line}/{machine}/heartbeat"
        payload = json.dumps({
            "timestamp": int(time.time()),
            "status": "alive"
        })

        if not self._connected:
            return

        try:
            await self.client.publish(topic, payload, qos=0)
        except MqttError as e:
            logger.error(f"Failed to publish heartbeat: {e}")