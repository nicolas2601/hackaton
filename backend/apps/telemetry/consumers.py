"""
WebSocket consumer for real-time telemetry updates.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TelemetryConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for machine telemetry streaming."""

    async def connect(self):
        """Handle WebSocket connection."""
        self.machine_id = self.scope["url_route"]["kwargs"]["machine_id"]
        self.room_group_name = f"telemetry_{self.machine_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
            elif message_type == "subscribe":
                # Client subscribing to specific metrics
                metrics = data.get("metrics", ["temperature", "vibration", "current"])
                await self.send(text_data=json.dumps({
                    "type": "subscribed",
                    "metrics": metrics
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"type": "error", "message": "Invalid JSON"}))

    async def telemetry_update(self, event):
        """Send telemetry update to WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "telemetry",
            "data": event["data"]
        }))

    async def alert(self, event):
        """Send alert to WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "alert",
            "data": event["data"]
        }))