"""Serializers for IoT sensor data."""
from rest_framework import serializers

from .models import SensorData


class SensorDataSerializer(serializers.ModelSerializer):
    """Read/write serializer for SensorData."""

    class Meta:
        model = SensorData
        fields = ["id", "lote", "tipo", "valor", "unidad", "timestamp"]
        read_only_fields = ["id", "timestamp"]
