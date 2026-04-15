"""Views for analytics app (KPIs and OEE metrics)."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Sum, F, Q
from django.utils import timezone
from datetime import timedelta
from .models import OEERecord, DailySummary, KPIRecord, QualityRecord, MaintenanceRecord
from .serializers import (
    OEERecordSerializer, DailySummarySerializer, KPIRecordSerializer,
    QualityRecordSerializer, MaintenanceRecordSerializer,
)
from apps.core.permissions import TenantPermission


class OEERecordViewSet(viewsets.ModelViewSet):
    """ViewSet for OEE records."""
    queryset = OEERecord.objects.all()
    serializer_class = OEERecordSerializer
    permission_classes = [TenantPermission]

    def get_queryset(self):
        user = self.request.user
        queryset = OEERecord.objects.select_related(
            "machine", "production_line"
        ).order_by("-date")

        if not user.is_superuser:
            queryset = queryset.filter(tenant=user.tenant)

        machine_id = self.request.query_params.get("machine_id")
        if machine_id:
            queryset = queryset.filter(machine_id=machine_id)

        date_from = self.request.query_params.get("date_from")
        if date_from:
            queryset = queryset.filter(date__gte=date_from)

        date_to = self.request.query_params.get("date_to")
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get OEE summary statistics."""
        queryset = self.get_queryset()
        since = timezone.now() - timedelta(days=30)
        data = queryset.filter(date__gte=since.date()).aggregate(
            avg_oee=Avg("oee"),
            avg_availability=Avg("availability"),
            avg_performance=Avg("performance"),
            avg_quality=Avg("quality"),
        )
        return Response({
            "period": "30d",
            "oee": round(data["avg_oee"] or 0, 2),
            "availability": round(data["avg_availability"] or 0, 2),
            "performance": round(data["avg_performance"] or 0, 2),
            "quality": round(data["avg_quality"] or 0, 2),
        })


class DailySummaryViewSet(viewsets.ModelViewSet):
    """ViewSet for daily production summaries."""
    queryset = DailySummary.objects.all()
    serializer_class = DailySummarySerializer
    permission_classes = [TenantPermission]

    def get_queryset(self):
        user = self.request.user
        queryset = DailySummary.objects.select_related(
            "production_line"
        ).order_by("-date")
        if not user.is_superuser:
            queryset = queryset.filter(tenant=user.tenant)
        return queryset


class KPIRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for KPI records."""
    queryset = KPIRecord.objects.all()
    serializer_class = KPIRecordSerializer
    permission_classes = [TenantPermission]

    def get_queryset(self):
        user = self.request.user
        queryset = KPIRecord.objects.select_related(
            "production_line", "machine"
        ).order_by("-period_end")
        if not user.is_superuser:
            queryset = queryset.filter(tenant=user.tenant)
        return queryset


class QualityRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for quality inspection records."""
    queryset = QualityRecord.objects.all()
    serializer_class = QualityRecordSerializer
    permission_classes = [TenantPermission]

    def get_queryset(self):
        user = self.request.user
        queryset = QualityRecord.objects.select_related(
            "production_order", "production_line"
        ).order_by("-inspection_time")
        if not user.is_superuser:
            queryset = queryset.filter(tenant=user.tenant)
        return queryset


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for maintenance records."""
    queryset = MaintenanceRecord.objects.all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [TenantPermission]

    def get_queryset(self):
        user = self.request.user
        queryset = MaintenanceRecord.objects.select_related(
            "machine", "created_by"
        ).order_by("-scheduled_date")
        if not user.is_superuser:
            queryset = queryset.filter(tenant=user.tenant)
        return queryset

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark maintenance as completed."""
        record = self.get_object()
        record.status = "completed"
        record.completed_at = timezone.now()
        record.save(update_fields=["status", "completed_at", "updated_at"])
        serializer = self.get_serializer(record)
        return Response(serializer.data)