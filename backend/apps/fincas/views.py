"""Views for fincas, lotes and perfiles de exportacion."""
from __future__ import annotations

import os
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Finca, Lote, PerfilExportacion
from .serializers import (
    FincaPublicaSerializer,
    FincaSerializer,
    LoteSerializer,
    PerfilExportacionSerializer,
)


class FincaViewSet(viewsets.ModelViewSet):
    """CRUD de fincas propias del usuario autenticado."""

    serializer_class = FincaSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["municipio", "verificada"]
    search_fields = ["nombre", "municipio"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Finca.objects.none()
        if user.is_superuser:
            return Finca.objects.all().prefetch_related("lotes", "perfil_exportacion")
        return Finca.objects.filter(propietario=user).prefetch_related(
            "lotes", "perfil_exportacion"
        )

    def perform_create(self, serializer):
        serializer.save(propietario=self.request.user)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """Devuelve la(s) finca(s) del usuario actual."""
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class FincaPublicaViewSet(viewsets.ReadOnlyModelViewSet):
    """Vitrina publica: fincas verificadas."""

    serializer_class = FincaPublicaSerializer
    permission_classes = [AllowAny]
    authentication_classes: list = []
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["municipio"]
    search_fields = ["nombre", "municipio", "lotes__variedad"]

    def get_queryset(self):
        qs = Finca.objects.filter(verificada=True).prefetch_related(
            "lotes", "perfil_exportacion"
        )
        variedad = self.request.query_params.get("variedad")
        if variedad:
            qs = qs.filter(lotes__variedad=variedad).distinct()
        return qs


class LoteViewSet(viewsets.ModelViewSet):
    """CRUD de lotes, filtrado por propietario."""

    serializer_class = LoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["finca", "variedad", "estado"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Lote.objects.none()
        qs = Lote.objects.select_related("finca")
        if not user.is_superuser:
            qs = qs.filter(finca__propietario=user)
        finca_id = self.request.query_params.get("finca_id")
        if finca_id:
            qs = qs.filter(finca_id=finca_id)
        return qs


class PerfilExportacionViewSet(viewsets.ModelViewSet):
    """CRUD de perfiles de exportacion (solo del dueno)."""

    serializer_class = PerfilExportacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return PerfilExportacion.objects.none()
        if user.is_superuser:
            return PerfilExportacion.objects.all()
        return PerfilExportacion.objects.filter(finca__propietario=user)


@api_view(["GET"])
@permission_classes([AllowAny])
def finca_qr_png(request, slug: str):
    """Devuelve el PNG del QR de trazabilidad para una finca publica."""
    try:
        finca = Finca.objects.get(slug=slug, verificada=True)
    except Finca.DoesNotExist as exc:
        raise Http404("Finca no encontrada") from exc
    path = Path(settings.MEDIA_ROOT) / "qr" / f"{finca.slug}.png"
    if not path.exists():
        # Regenerate on the fly if missing.
        from .signals import generate_qr_for_finca

        generate_qr_for_finca(finca)
    if not path.exists():
        raise Http404("QR no disponible")
    return FileResponse(open(path, "rb"), content_type="image/png")
