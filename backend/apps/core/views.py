"""Core app views for authentication, users, and health check."""
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Tenant, UserActivityLog
from .serializers import (
    UserSerializer, UserCreateSerializer, TenantSerializer,
    UserActivityLogSerializer, TokenObtainPairSerializer,
)
from apps.core.permissions import TenantPermission, IsAdmin


class HealthCheckView(APIView):
    """Health check endpoint for load balancers and monitoring."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return JsonResponse({
            "status": "healthy",
            "service": "manufactura-backend",
            "version": "0.1.0",
        })


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management."""
    queryset = User.objects.select_related("tenant").all()
    permission_classes = [IsAuthenticated, TenantPermission]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.select_related("tenant").all()
        return User.objects.select_related("tenant").filter(tenant=user.tenant)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def activity(self, request):
        """Get current user's activity log."""
        logs = UserActivityLog.objects.filter(user=request.user)[:50]
        serializer = UserActivityLogSerializer(logs, many=True)
        return Response(serializer.data)


class TenantViewSet(viewsets.ModelViewSet):
    """ViewSet for tenant management (superuser only)."""
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Tenant.objects.all()
        return Tenant.objects.filter(id=user.tenant_id)

    @action(detail=True, methods=["get"])
    def users(self, request, pk=None):
        """Get users for a specific tenant."""
        tenant = self.get_object()
        users = User.objects.filter(tenant=tenant)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)