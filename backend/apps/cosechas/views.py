"""Views for cosechas and controles fitosanitarios."""
from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import ControlFitosanitario, Cosecha
from .serializers import ControlFitosanitarioSerializer, CosechaSerializer


class CosechaViewSet(viewsets.ModelViewSet):
    """CRUD de cosechas, filtrado por propietario."""

    serializer_class = CosechaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["lote", "calidad"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Cosecha.objects.none()
        qs = Cosecha.objects.select_related("lote", "lote__finca")
        if not user.is_superuser:
            qs = qs.filter(lote__finca__propietario=user)
        return qs


class ControlFitosanitarioViewSet(viewsets.ModelViewSet):
    """CRUD de controles fitosanitarios, filtrado por propietario."""

    serializer_class = ControlFitosanitarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["lote", "tipo_control", "plaga_enfermedad"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ControlFitosanitario.objects.none()
        qs = ControlFitosanitario.objects.select_related("lote", "lote__finca")
        if not user.is_superuser:
            qs = qs.filter(lote__finca__propietario=user)
        return qs
