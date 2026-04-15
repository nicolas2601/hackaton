"""
MQTT Worker Management Command.

Consumes telemetry data from MQTT broker using aiomqtt (async, no callbacks).
Topics follow the schema: factory/{tenant}/{line}/{machine}/{metric}
"""
import asyncio
import json
import logging
import signal
import sys
from datetime import datetime
from typing import Any

import aiomqtt
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.telemetry.models import TelemetryEvent, Sensor
from apps.production.models import Machine

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run MQTT worker to consume telemetry data from broker"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._shutdown = False
        self._client: aiomqtt.Client | None = None
        self._reconnect_delay = 1
        self._max_reconnect_delay = 60

    def add_arguments(self, parser):
        parser.add_argument(
            "--broker-url",
            type=str,
            default= None,
            help="MQTT broker URL (default: from settings)",
        )
        parser.add_argument(
            "--topics",
            type=str,
            nargs="+",
            default=["factory/+/+/+/+"],
            help="MQTT topics to subscribe to (default: factory/+/+/+/+)",
        )
        parser.add_argument(
            "--qos",
            type=int,
            choices=[0, 1, 2],
            default=1,
            help="MQoS level for subscription (default: 1)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of events to batch before writing to DB (default: 100)",
        )
        parser.add_argument(
            "--batch-timeout",
            type=int,
            default=5,
            help="Max seconds to wait before flushing batch (default: 5)",
        )

    def handle(self, *args, **options):
        """Main entry point for the management command."""
        self.stdout.write(self.style.SUCCESS("Starting MQTT worker..."))

        # Set up signal handlers for graceful shutdown
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._handle_shutdown)

        try:
            loop.run_until_complete(self._run_worker(options))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Received keyboard interrupt"))
        finally:
            loop.run_until_complete(self._cleanup())
            loop.close()

        self.stdout.write(self.style.SUCCESS("MQTT worker stopped"))

    async def _run_worker(self, options: dict) -> None:
        """Run the async MQTT worker."""
        broker_url = options["broker_url"] or self._get_broker_url()
        topics = options["topics"]
        qos = options["qos"]
        batch_size = options["batch_size"]
        batch_timeout = options["batch_timeout"]

        self.stdout.write(f"Connecting to MQTT broker: {broker_url}")
        self.stdout.write(f"Subscribing to topics: {topics}")

        batch: list[TelemetryEvent] = []
        batch_lock = asyncio.Lock()

        async def flush_batch() -> None:
            """Flush the batch to the database."""
            nonlocal batch
            async with batch_lock:
                if not batch:
                    return
                events_to_save = batch.copy()
                batch = []

            try:
                with transaction.atomic():
                    TelemetryEvent.objects.bulk_create(events_to_save, batch_size)
                self.stdout.write(f"Flushed {len(events_to_save)} telemetry events")
            except Exception as e:
                logger.error(f"Failed to flush batch: {e}")
                # Re-add events to batch on failure
                async with batch_lock:
                    batch = events_to_save + batch

        # Create flush task
        flush_task = asyncio.create_task(self._flush_periodically(flush_batch, batch_timeout))

        while not self._shutdown:
            try:
                async with aiomqtt.Client(identifier=f"manufactura-worker-{id(self)}") as client:
                    self._client = client
                    self._reconnect_delay = 1  # Reset reconnect delay on successful connection
                    self.stdout.write(self.style.SUCCESS("Connected to MQTT broker"))

                    # Subscribe to topics
                    for topic in topics:
                        await client.subscribe(topic, qos=qos)
                        self.stdout.write(f"Subscribed to: {topic}")

                    # Process messages
                    async for message in client.messages:
                        if self._shutdown:
                            break

                        try:
                            event = await self._parse_message(message)
                            if event:
                                async with batch_lock:
                                    batch.append(event)

                                    if len(batch) >= batch_size:
                                        asyncio.create_task(flush_batch())

                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            continue

            except aiomqtt.MqttError as e:
                if self._shutdown:
                    break
                logger.error(f"MQTT error: {e}")
                self.stdout.write(
                    self.style.WARNING(f"MQTT connection lost, reconnecting in {self._reconnect_delay}s...")
                )
                await asyncio.sleep(self._reconnect_delay)
                self._reconnect_delay = min(self._reconnect_delay * 2, self._max_reconnect_delay)

        # Flush remaining events
        flush_task.cancel()
        await flush_task
        await flush_batch()

    async def _flush_periodically(self, flush_func, timeout: int) -> None:
        """Periodically flush the batch."""
        while not self._shutdown:
            await asyncio.sleep(timeout)
            await flush_func()

    async def _parse_message(self, message: aiomqtt.Message) -> TelemetryEvent | None:
        """Parse MQTT message into TelemetryEvent."""
        try:
            topic_parts = message.topic.value.split("/")

            if len(topic_parts) < 5:
                logger.warning(f"Invalid topic format: {message.topic}")
                return None

            # Parse topic: factory/{tenant}/{line}/{machine}/{metric}
            _, tenant_slug, line_slug, machine_slug, metric_type = topic_parts[:5]

            # Parse payload
            payload = json.loads(message.payload.decode())

            # Get or create machine
            try:
                machine = await self._get_or_create_machine(
                    tenant_slug,
                    line_slug,
                    machine_slug,
                    payload,
                )
            except Machine.DoesNotExist:
                logger.warning(f"Machine not found: {tenant_slug}/{line_slug}/{machine_slug}")
                return None

            # Create telemetry event
            event = TelemetryEvent(
                machine=machine,
                metric_type=metric_type,
                value=float(payload.get("value", 0)),
                unit=payload.get("unit", ""),
                quality=payload.get("quality", 1.0),
                metadata=payload.get("metadata", {}),
            )

            return event

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in message: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None

    async def _get_or_create_machine(
        self,
        tenant_slug: str,
        line_slug: str,
        machine_slug: str,
        payload: dict,
    ) -> Machine:
        """Get or create machine from database."""
        from apps.core.models import Tenant
        from apps.production.models import ProductionLine

        # Get tenant
        tenant = await self._sync_get_or_create_tenant(tenant_slug)

        # Get production line
        line, _ = await self._sync_get_or_create_line(tenant, line_slug, payload)

        # Get machine
        machine, created = await self._sync_get_or_create_machine(line, machine_slug, payload)

        if created:
            self.stdout.write(f"Created machine: {machine.name} ({tenant.slug})")

        return machine

    def _sync_get_or_create_tenant(self, slug: str):
        """Synchronous helper to get or create tenant."""
        from apps.core.models import Tenant

        tenant, _ = Tenant.objects.get_or_create(
            slug=slug,
            defaults={"name": slug.replace("-", " ").title()},
        )
        return tenant

    def _sync_get_or_create_line(self, tenant, slug: str, payload: dict):
        """Synchronous helper to get or create production line."""
        from apps.production.models import ProductionLine

        line, created = ProductionLine.objects.get_or_create(
            tenant=tenant,
            slug=slug,
            defaults={
                "name": payload.get("line_name", slug.replace("-", " ").title()),
                "location": payload.get("line_location", ""),
            },
        )
        return line, created

    def _sync_get_or_create_machine(self, line, slug: str, payload: dict):
        """Synchronous helper to get or create machine."""
        machine, created = Machine.objects.get_or_create(
            production_line=line,
            slug=slug,
            defaults={
                "name": payload.get("machine_name", slug.replace("-", " ").title()),
                "machine_type": payload.get("machine_type", "unknown"),
                "serial_number": payload.get("serial_number", ""),
            },
        )
        return machine, created

    def _get_broker_url(self) -> str:
        """Get MQTT broker URL from settings or environment."""
        import os

        return os.environ.get(
            "MQTT_BROKER_URL",
            "mqtt://manufactura:changeme@localhost:1883",
        )

    def _handle_shutdown(self) -> None:
        """Handle shutdown signal."""
        self.stdout.write(self.style.WARNING("Received shutdown signal..."))
        self._shutdown = True
        if self._client:
            asyncio.create_task(self._client.disconnect())

    async def _cleanup(self) -> None:
        """Cleanup resources."""
        if self._client:
            try:
                await self._client.disconnect()
            except Exception:
                pass