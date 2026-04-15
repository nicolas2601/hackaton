"""URL configuration for core app (auth and users)."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import UserViewSet, TenantViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"tenants", TenantViewSet, basename="tenants")

urlpatterns = [
    # JWT Auth endpoints
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Router URLs
    path("", include(router.urls)),
]