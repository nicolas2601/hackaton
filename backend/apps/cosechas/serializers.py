"""Serializers for cosechas and controles fitosanitarios."""
from rest_framework import serializers

from .models import ControlFitosanitario, Cosecha


class CosechaSerializer(serializers.ModelSerializer):
    """Serializer for Cosecha."""

    lote_nombre = serializers.CharField(source="lote.nombre", read_only=True)

    class Meta:
        model = Cosecha
        fields = [
            "id",
            "lote",
            "lote_nombre",
            "fecha_cosecha",
            "kg_baba",
            "kg_seco",
            "dias_fermentacion",
            "temp_prom_fermentacion",
            "dias_secado",
            "calidad",
        ]
        read_only_fields = ["id", "lote_nombre"]

    def validate(self, attrs: dict) -> dict:
        kg_baba = attrs.get("kg_baba")
        kg_seco = attrs.get("kg_seco")
        if kg_baba is not None and kg_seco is not None and kg_seco > kg_baba:
            raise serializers.ValidationError(
                "kg_seco no puede ser mayor que kg_baba"
            )
        return attrs


class ControlFitosanitarioSerializer(serializers.ModelSerializer):
    """Serializer for ControlFitosanitario."""

    lote_nombre = serializers.CharField(source="lote.nombre", read_only=True)

    class Meta:
        model = ControlFitosanitario
        fields = [
            "id",
            "lote",
            "lote_nombre",
            "fecha",
            "tipo_control",
            "plaga_enfermedad",
            "tratamiento_aplicado",
            "resultado",
            "foto_evidencia",
        ]
        read_only_fields = ["id", "lote_nombre"]
