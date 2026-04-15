"""
Views for telemetry app.
"""
import json
from django.http import StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import TelemetryEvent, Sensor, TelemetryAlert
from .serializers import (
    TelemetryEventSerializer,
    SensorSerializer,
    TelemetryAlertSerializer,
)
from apps.core.permissions import TenantPermission


class SensorViewSet(viewsets.ModelViewSet):
    """ViewSet for Sensor model."""

    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [TenantPermission]

    def get_queryset(self):
        user = self.request.user
        queryset = Sensor.objects.select_related("machine").all()
        if user.is_superuser:
            return queryset
        return queryset.filter(machine__production_line__tenant=user.tenant)


class TelemetryEventViewSet(viewsets.ModelViewSet):
    """ViewSet for TelemetryEvent model."""

    queryset = TelemetryEvent.objects.all()
    serializer_class = TelemetryEventSerializer
    permission_classes = [TenantPermission]

    def get_queryset(self):
        user = self.request.user
        queryset = TelemetryEvent.objects.select_related(
            "machine", "machine__production_line"
        ).order_by("-timestamp")

        if user.is_superuser:
            return queryset

        queryset = queryset.filter(machine__production_line__tenant=user.tenant)

        # Filter by machine
        machine_id = self.request.query_params.get("machine_id")
        if machine_id:
            queryset = queryset.filter(machine_id=machine_id)

        # Filter by metric type
        metric_type = self.request.query_params.get("metric_type")
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)

        # Filter by time range
        from django.utils import timezone

        time_range = self.request.query_params.get("time_range")
        if time_range:
            if time_range == "1h":
                since = timezone.now() - timezone.timedelta(hours=1)
            elif time_range == "24h":
                since = timezone.now() - timezone.timedelta(hours=24)
            elif time_range == "7d":
                since = timezone.now() - timezone.timedelta(days=7)
            else:
                since = timezone.now() - timezone.timedelta(hours=1)
            queryset = queryset.filter(timestamp__gte=since)

        return queryset

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """Get latest event for each machine."""
        from django.db.models import Max

        latest_events = (
            TelemetryEvent.objects.values("machine_id")
            .annotate(latest_timestamp=Max("timestamp"))
            .order_by("machine_id")
        )

        machine_ids = [e["machine_id"] for e in latest_events]
        events = TelemetryEvent.objects.filter(
            id__in=[
                TelemetryEvent.objects.filter(machine_id=mid, timestamp=lt)
                .values_list("id", flat=True)[0]
                for mid, lt in [(e["machine_id"], e["latest_timestamp"]) for e in latest_events]
            ]
        )

        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="stream")
    def stream_events(self, request):
        """Server-Sent Events endpoint for real-time telemetry."""

        def event_stream():
            import time

            channel_layer = get_channel_layer()

            while True:
                try:
                    # Get latest events from Redis channel
                    messages = async_to_sync(channel_layer.receive)(
                        ["telemetry_updates"]
                    )

                    if messages:
                        for message in messages:
                            event_data = message.get("event", {})
                            yield f"data: {json.dumps(event_data)}\n\n"

                    time.sleep(0.1)  # 10Hz update rate
                except Exception:
                    time.sleep(1)

        response = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get telemetry statistics."""
        from django.db.models import Count
        from django.utils import timezone

        user = request.user
        queryset = self.get_queryset()

        # Total events
        total_events = queryset.count()

        # Events per metric type
        by_metric = (
            queryset.filter(
                timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
            )
            .values("metric_type")
            .annotate(count=Count("id"))
        )

        # Events per machine
        by_machine = (
            queryset.filter(
                timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
            )
            .values("machine__name")
            .annotate(count=Count("id"))
        )

        return Response(
            {
                "total_events": total_events,
                "by_metric_type": list(by_metric),
                "by_machine": list(by_machine),
            }
        )


class TelemetryAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for TelemetryAlert model."""

    queryset = TelemetryAlert.objects.all()
    serializer_class = TelemetryAlertSerializer
    permission_classes = [TenantPermission]

    def get_queryset(self):
        user = self.request.user
        queryset = TelemetryAlert.objects.select_related(
            "sensor", "sensor__machine"
        ).order_by("-created_at")

        if user.is_superuser:
            return queryset

        queryset = queryset.filter(sensor__machine__production_line__tenant=user.tenant)

        # Filter by severity
        severity = self.request.query_params.get("severity")
        if severity:
            queryset = queryset.filter(severity=severity)

        # Filter by acknowledged status
        acknowledged = self.request.query_params.get("acknowledged")
        if acknowledged is not None:
            queryset = queryset.filter(acknowledged=acknowledged.lower() == "true")

        return queryset

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert."""
        alert = self.get_object()
        alert.acknowledged = True
        alert.acknowledged_by = request.user
        alert.save(update_fields=["acknowledged", "acknowledged_by", "updated_at"])

        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unacknowledged(self, request):
        """Get all unacknowledged alerts."""
        alerts = self.get_queryset().filter(acknowledged=False)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)


@require_http_methods(["GET"])
def telemetry_health(request):
    """Health check endpoint for telemetry service."""
    return Response({"status": "healthy", "service": "telemetry"})