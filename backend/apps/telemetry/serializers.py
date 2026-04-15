"""Telemetry app serializers."""
from rest_framework import serializers
from .models import Sensor, TelemetryEvent, AlertRule, TelemetryAlert


class SensorSerializer(serializers.ModelSerializer):
    machine_name = serializers.CharField(source="machine.name", read_only=True)

    class Meta:
        model = Sensor
        fields = [
            "id", "name", "machine", "machine_name", "sensor_type", "unit",
            "is_active", "sampling_rate", "threshold_min", "threshold_max",
            "threshold_critical_min", "threshold_critical_max", "metadata",
            "created_at", "updated_at",
        ]


class TelemetryEventSerializer(serializers.ModelSerializer):
    machine_name = serializers.CharField(source="machine.name", read_only=True)
    defect_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = TelemetryEvent
        fields = [
            "id", "machine", "machine_name", "timestamp",
            "operational_status", "production_count", "defects",
            "temperature", "vibration", "current", "uptime",
            "mqtt_topic", "raw_payload", "defect_rate",
        ]


class AlertRuleSerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(
        source="sensor.name", read_only=True, allow_null=True
    )

    class Meta:
        model = AlertRule
        fields = [
            "id", "name", "description", "sensor", "sensor_name",
            "metric", "operator", "threshold", "severity",
            "cooldown_seconds", "is_active", "created_at", "updated_at",
        ]


class TelemetryAlertSerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(source="sensor.name", read_only=True)
    rule_name = serializers.CharField(
        source="rule.name", read_only=True, allow_null=True
    )
    acknowledged_by_name = serializers.CharField(
        source="acknowledged_by.full_name", read_only=True, allow_null=True
    )

    class Meta:
        model = TelemetryAlert
        fields = [
            "id", "rule", "rule_name", "sensor", "sensor_name",
            "telemetry_event", "severity", "message",
            "metric_value", "threshold_value", "status",
            "acknowledged_by", "acknowledged_by_name",
            "acknowledged_at", "resolved_at", "created_at", "updated_at",
        ]