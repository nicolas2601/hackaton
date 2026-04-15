"""URL configuration for Manufactura Santander 4.0."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.core.views import HealthCheckView

# API documentation schema
schema_view = SpectacularAPIView.as_view()
swagger_view = SpectacularSwaggerView.as_view(url_name="schema")

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Health check (no auth required)
    path("health/", HealthCheckView.as_view(), name="health-check"),
    # JWT Authentication
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # API endpoints
    path("api/auth/", include("apps.core.urls")),
    path("api/production/", include("apps.production.urls")),
    path("api/telemetry/", include("apps.telemetry.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    # API documentation
    path("api/schema/", schema_view, name="schema"),
    path("api/docs/", swagger_view, name="swagger-ui"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)