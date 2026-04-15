"""URL configuration for telemetry app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SensorViewSet, TelemetryEventViewSet, TelemetryAlertViewSet

router = DefaultRouter()
router.register(r"sensors", SensorViewSet, basename="sensors")
router.register(r"events", TelemetryEventViewSet, basename="telemetry-events")
router.register(r"alerts", TelemetryAlertViewSet, basename="telemetry-alerts")

urlpatterns = [
    path("", include(router.urls)),
]