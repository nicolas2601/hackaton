"""Serializers for fincas, lotes, and perfil de exportacion."""
from __future__ import annotations

from typing import Any

from django.utils.text import slugify
from rest_framework import serializers

from apps.iot.models import SensorData

from .models import Finca, Lote, PerfilExportacion


class PerfilExportacionSerializer(serializers.ModelSerializer):
    """Serializer for PerfilExportacion."""

    class Meta:
        model = PerfilExportacion
        fields = [
            "id",
            "finca",
            "certificaciones",
            "mercados_destino",
            "capacidad_anual_kg",
            "qr_url",
        ]
        read_only_fields = ["id", "qr_url"]


class LoteSerializer(serializers.ModelSerializer):
    """Serializer for Lote."""

    finca_nombre = serializers.CharField(source="finca.nombre", read_only=True)

    class Meta:
        model = Lote
        fields = [
            "id",
            "finca",
            "finca_nombre",
            "nombre",
            "variedad",
            "num_plantas",
            "edad_años",
            "area_ha",
            "lat",
            "lng",
            "estado",
        ]
        read_only_fields = ["id", "finca_nombre"]

    def validate_num_plantas(self, value: int) -> int:
        if value < 0:
            raise serializers.ValidationError("num_plantas debe ser no negativo")
        return value

    def validate_area_ha(self, value: Any) -> Any:
        if float(value) <= 0:
            raise serializers.ValidationError("area_ha debe ser positiva")
        return value


class FincaSerializer(serializers.ModelSerializer):
    """Full serializer (owner-facing). Includes telefono_wa and contact data."""

    lotes = LoteSerializer(many=True, read_only=True)
    perfil_exportacion = PerfilExportacionSerializer(read_only=True)
    propietario_email = serializers.CharField(
        source="propietario.email", read_only=True
    )

    class Meta:
        model = Finca
        fields = [
            "id",
            "slug",
            "nombre",
            "municipio",
            "lat",
            "lng",
            "area_total_ha",
            "verificada",
            "foto",
            "descripcion",
            "telefono_wa",
            "propietario",
            "propietario_email",
            "lotes",
            "perfil_exportacion",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "propietario",
            "propietario_email",
            "created_at",
            "lotes",
            "perfil_exportacion",
        ]

    def create(self, validated_data: dict[str, Any]) -> Finca:
        # Auto-generate slug, ensure uniqueness
        nombre = validated_data.get("nombre", "finca")
        base = slugify(nombre)[:60] or "finca"
        slug = base
        i = 2
        while Finca.objects.filter(slug=slug).exists():
            slug = f"{base}-{i}"
            i += 1
        validated_data["slug"] = slug
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["propietario"] = request.user
        return super().create(validated_data)


class FincaPublicaSerializer(serializers.ModelSerializer):
    """Public-facing serializer. Omits telefono_wa; adds ultimos_sensores."""

    lotes = LoteSerializer(many=True, read_only=True)
    perfil_exportacion = PerfilExportacionSerializer(read_only=True)
    ultimos_sensores = serializers.SerializerMethodField()
    propietario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Finca
        fields = [
            "id",
            "slug",
            "nombre",
            "municipio",
            "lat",
            "lng",
            "area_total_ha",
            "verificada",
            "foto",
            "descripcion",
            "propietario_nombre",
            "lotes",
            "perfil_exportacion",
            "ultimos_sensores",
            "created_at",
        ]

    def get_propietario_nombre(self, obj: Finca) -> str:
        p = obj.propietario
        return (p.full_name or p.email.split("@")[0]) if p else ""

    def get_ultimos_sensores(self, obj: Finca) -> list[dict[str, Any]]:
        # Latest value per sensor tipo across all lotes of the finca.
        lote_ids = list(obj.lotes.values_list("id", flat=True))
        if not lote_ids:
            return []
        qs = (
            SensorData.objects.filter(lote_id__in=lote_ids)
            .order_by("tipo", "-timestamp")
            .distinct("tipo")
        )
        return [
            {
                "tipo": s.tipo,
                "valor": s.valor,
                "unidad": s.unidad,
                "timestamp": s.timestamp.isoformat(),
                "lote_id": s.lote_id,
            }
            for s in qs
        ]
