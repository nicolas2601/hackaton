"""
Views for production app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import ProductionLine, Machine, ProductionOrder, ProductionOrderItem
from .serializers import (
    ProductionLineSerializer,
    MachineSerializer,
    ProductionOrderSerializer,
    ProductionOrderItemSerializer,
)
from apps.core.permissions import TenantPermission


class ProductionLineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProductionLine model.
    Provides CRUD operations for production lines.
    """

    queryset = ProductionLine.objects.all()
    serializer_class = ProductionLineSerializer
    permission_classes = [TenantPermission]

    def get_queryset(self):
        """Filter by tenant if not superuser."""
        user = self.request.user
        if user.is_superuser:
            return ProductionLine.objects.all()
        return ProductionLine.objects.filter(tenant=user.tenant)

    def perform_create(self, serializer):
        """Set tenant on create."""
        user = self.request.user
        serializer.save(tenant=user.tenant)


class MachineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Machine model.
    Provides CRUD operations for machines.
    """

    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    permission_classes = [TenantPermission]

    def get_queryset(self):
        """Filter by tenant."""
        user = self.request.user
        if user.is_superuser:
            return Machine.objects.select_related("production_line").all()
        return Machine.objects.select_related("production_line").filter(
            production_line__tenant=user.tenant
        )

    @action(detail=True, methods=["post"])
    def toggle_status(self, request, pk=None):
        """Toggle machine active status."""
        machine = self.get_object()
        machine.is_active = not machine.is_active
        machine.save(update_fields=["is_active"])
        serializer = self.get_serializer(machine)
        return Response(serializer.data)


class ProductionOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProductionOrder model.
    Provides CRUD operations for production orders.
    """

    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    permission_classes = [TenantPermission]

    def get_queryset(self):
        """Filter by tenant."""
        user = self.request.user
        queryset = ProductionOrder.objects.select_related(
            "production_line", "assigned_to"
        ).prefetch_related("items")

        if user.is_superuser:
            return queryset

        queryset = queryset.filter(production_line__tenant=user.tenant)

        # Filter by status if provided
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by priority if provided
        priority = self.request.query_params.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset

    def perform_create(self, serializer):
        """Set tenant from user on create."""
        user = self.request.user
        serializer.save()

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get all active production orders."""
        orders = self.get_queryset().filter(
            status__in=["pending", "in_progress"]
        ).order_by("priority", "planned_start")
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_line(self, request):
        """Get production orders grouped by production line."""
        line_id = request.query_params.get("line_id")
        if not line_id:
            return Response(
                {"error": "line_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        orders = self.get_queryset().filter(production_line_id=line_id)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


class ProductionOrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProductionOrderItem model.
    Provides CRUD operations for order items.
    """

    queryset = ProductionOrderItem.objects.all()
    serializer_class = ProductionOrderItemSerializer
    permission_classes = [TenantPermission]

    def get_queryset(self):
        """Filter by tenant."""
        user = self.request.user
        queryset = ProductionOrderItem.objects.select_related(
            "order", "order__production_line"
        )

        if user.is_superuser:
            return queryset

        return queryset.filter(order__production_line__tenant=user.tenant)