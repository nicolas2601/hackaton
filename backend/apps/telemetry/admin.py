"""Admin configuration for telemetry app."""
from django.contrib import admin
from .models import TelemetryEvent, Sensor, TelemetryAlert


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = [
        "name", "machine", "sensor_type", "unit", "is_active",
    ]
    list_filter = ["sensor_type", "is_active", "machine"]
    search_fields = ["name"]
    raw_id_fields = ["machine"]


@admin.register(TelemetryEvent)
class TelemetryEventAdmin(admin.ModelAdmin):
    list_display = [
        "timestamp", "machine", "operational_status",
        "temperature", "vibration", "current",
    ]
    list_filter = ["operational_status", "machine"]
    search_fields = ["machine__name"]
    raw_id_fields = ["machine"]
    date_hierarchy = "timestamp"


@admin.register(TelemetryAlert)
class TelemetryAlertAdmin(admin.ModelAdmin):
    list_display = [
        "sensor", "severity", "status", "metric_value", "created_at",
    ]
    list_filter = ["severity", "status"]
    search_fields = ["sensor__name", "message"]
    raw_id_fields = ["sensor", "telemetry_event", "acknowledged_by"]
    date_hierarchy = "created_at"