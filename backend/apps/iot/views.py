"""Views for IoT sensor data."""
from __future__ import annotations

from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.fincas.models import Finca

from .models import SensorData
from .serializers import SensorDataSerializer


class SensorDataViewSet(viewsets.ReadOnlyModelViewSet):
    """Lectura de telemetria IoT (solo del propietario del lote)."""

    serializer_class = SensorDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["lote", "tipo"]
    ordering_fields = ["timestamp"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return SensorData.objects.none()
        qs = SensorData.objects.select_related("lote", "lote__finca")
        if not user.is_superuser:
            qs = qs.filter(lote__finca__propietario=user)
        lote_id = self.request.query_params.get("lote_id")
        if lote_id:
            qs = qs.filter(lote_id=lote_id)
        return qs.order_by("-timestamp")

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        limit_raw = self.request.query_params.get("limit", "30")
        try:
            limit = max(1, min(1000, int(limit_raw)))
        except (TypeError, ValueError):
            limit = 30
        return queryset[:limit]

    @action(detail=False, methods=["get"], url_path="latest")
    def latest(self, request):
        """Ultimo valor por tipo para un lote dado."""
        lote_id = request.query_params.get("lote_id")
        if not lote_id:
            return Response({"detail": "lote_id es requerido"}, status=400)
        user = request.user
        qs = SensorData.objects.filter(lote_id=lote_id)
        if not user.is_superuser:
            qs = qs.filter(lote__finca__propietario=user)
        qs = qs.order_by("tipo", "-timestamp").distinct("tipo")
        return Response(SensorDataSerializer(qs, many=True).data)

    @action(
        detail=False,
        methods=["get"],
        url_path="publicos",
        permission_classes=[AllowAny],
        authentication_classes=[],
    )
    def publicos(self, request):
        """Promedios agregados por finca (vitrina publica)."""
        finca_id = request.query_params.get("finca_id")
        slug = request.query_params.get("slug")
        try:
            if finca_id:
                finca = Finca.objects.get(id=finca_id, verificada=True)
            elif slug:
                finca = Finca.objects.get(slug=slug, verificada=True)
            else:
                return Response(
                    {"detail": "finca_id o slug es requerido"}, status=400
                )
        except Finca.DoesNotExist:
            return Response({"detail": "Finca no encontrada"}, status=404)

        agg = (
            SensorData.objects.filter(lote__finca=finca)
            .values("tipo")
            .annotate(promedio=Avg("valor"))
            .order_by("tipo")
        )
        return Response(
            {
                "finca": finca.slug,
                "promedios": [
                    {"tipo": a["tipo"], "promedio": round(a["promedio"] or 0.0, 2)}
                    for a in agg
                ],
            }
        )
