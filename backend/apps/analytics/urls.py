"""URL configuration for analytics app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OEERecordViewSet, DailySummaryViewSet, KPIRecordViewSet,
    QualityRecordViewSet, MaintenanceRecordViewSet,
)

router = DefaultRouter()
router.register(r"oee", OEERecordViewSet, basename="oee")
router.register(r"daily-summary", DailySummaryViewSet, basename="daily-summary")
router.register(r"kpi", KPIRecordViewSet, basename="kpi")
router.register(r"quality", QualityRecordViewSet, basename="quality")
router.register(r"maintenance", MaintenanceRecordViewSet, basename="maintenance")

urlpatterns = [path("", include(router.urls))]