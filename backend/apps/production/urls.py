"""
URL configuration for production app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductionLineViewSet, ProductionOrderViewSet, MachineViewSet

router = DefaultRouter()
router.register(r"lines", ProductionLineViewSet, basename="production-lines")
router.register(r"orders", ProductionOrderViewSet, basename="production-orders")
router.register(r"machines", MachineViewSet, basename="machines")

urlpatterns = [
    path("", include(router.urls)),
]