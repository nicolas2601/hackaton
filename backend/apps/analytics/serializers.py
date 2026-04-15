"""Analytics app serializers."""
from rest_framework import serializers
from .models import OEERecord, DailySummary, KPIRecord, QualityRecord, MaintenanceRecord


class OEERecordSerializer(serializers.ModelSerializer):
    machine_name = serializers.CharField(source="machine.name", read_only=True)
    production_line_name = serializers.CharField(
        source="production_line.name", read_only=True
    )

    class Meta:
        model = OEERecord
        fields = [
            "id", "machine", "machine_name", "production_line_name",
            "date", "availability", "performance", "quality", "oee",
            "planned_production_time", "actual_production_time",
            "downtime", "ideal_cycle_time", "actual_cycle_time",
            "total_count", "good_count", "defect_count", "created_at",
        ]


class DailySummarySerializer(serializers.ModelSerializer):
    production_line_name = serializers.CharField(
        source="production_line.name", read_only=True
    )
    completion_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = DailySummary
        fields = [
            "id", "production_line", "production_line_name", "date",
            "total_orders", "completed_orders", "cancelled_orders",
            "total_planned_quantity", "total_produced_quantity",
            "total_defective_quantity", "total_production_time",
            "total_downtime", "average_oee", "quality_rate",
            "total_alerts", "critical_alerts", "completion_rate",
            "created_at", "updated_at",
        ]


class KPIRecordSerializer(serializers.ModelSerializer):
    production_line_name = serializers.CharField(
        source="production_line.name", read_only=True, allow_null=True
    )
    machine_name = serializers.CharField(
        source="machine.name", read_only=True, allow_null=True
    )

    class Meta:
        model = KPIRecord
        fields = [
            "id", "tenant", "kpi_type", "value", "unit",
            "period_start", "period_end", "period_type",
            "production_line", "production_line_name",
            "machine", "machine_name", "description", "metadata",
            "created_at",
        ]


class QualityRecordSerializer(serializers.ModelSerializer):
    production_order_number = serializers.CharField(
        source="production_order.order_number", read_only=True
    )
    production_line_name = serializers.CharField(
        source="production_line.name", read_only=True, allow_null=True
    )

    class Meta:
        model = QualityRecord
        fields = [
            "id", "production_order", "production_order_number",
            "production_line", "production_line_name",
            "inspection_type", "inspection_time",
            "quantity_inspected", "quantity_defective", "quantity_reworked",
            "quantity_accepted", "defect_rate", "defect_types",
            "inspector_name", "notes", "created_at", "updated_at",
        ]


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    machine_name = serializers.CharField(source="machine.name", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True, allow_null=True
    )

    class Meta:
        model = MaintenanceRecord
        fields = [
            "id", "tenant", "machine", "machine_name", "maintenance_type",
            "status", "scheduled_date", "started_at", "completed_at",
            "duration_minutes", "description", "work_performed",
            "parts_replaced", "technician_name", "cost",
            "created_by", "created_by_name", "created_at", "updated_at",
        ]