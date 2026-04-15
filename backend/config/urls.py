"""URL configuration for CacaoTrace."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.auth_views import MeView, RegisterView
from apps.cosechas.views import ControlFitosanitarioViewSet, CosechaViewSet
from apps.fincas.views import (
    FincaPublicaViewSet,
    FincaViewSet,
    LoteViewSet,
    PerfilExportacionViewSet,
    finca_qr_png,
)
from apps.iot.views import SensorDataViewSet
from apps.iot.views_sse import sensor_stream

router = DefaultRouter()
router.register(r"fincas/publicas", FincaPublicaViewSet, basename="finca-publica")
router.register(r"fincas", FincaViewSet, basename="finca")
router.register(r"lotes", LoteViewSet, basename="lote")
router.register(
    r"perfiles-exportacion", PerfilExportacionViewSet, basename="perfil-exportacion"
)
router.register(r"sensors", SensorDataViewSet, basename="sensor")
router.register(r"cosechas", CosechaViewSet, basename="cosecha")
router.register(
    r"controles-fito", ControlFitosanitarioViewSet, basename="control-fito"
)


urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/me/", MeView.as_view(), name="me"),
    # SSE stream (declared before router to avoid /sensors/stream clash)
    path("api/sensors/stream/", sensor_stream, name="sensor-stream"),
    # Public QR PNG
    path(
        "api/fincas/publicas/<slug:slug>/qr.png",
        finca_qr_png,
        name="finca-qr-png",
    ),
    # REST router
    path("api/", include(router.urls)),
    # Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
