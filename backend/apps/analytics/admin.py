"""Admin configuration for analytics app."""
from django.contrib import admin
from .models import OEERecord, DailySummary, KPIRecord, QualityRecord, MaintenanceRecord


@admin.register(OEERecord)
class OEERecordAdmin(admin.ModelAdmin):
    list_display = [
        "date", "machine", "production_line", "oee", "availability",
        "performance", "quality",
    ]
    list_filter = ["production_line", "machine"]
    date_hierarchy = "date"
    raw_id_fields = ["machine", "production_line", "tenant"]


@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = [
        "date", "production_line", "total_orders", "completed_orders",
        "total_production_time", "total_downtime", "average_oee",
    ]
    list_filter = ["production_line"]
    date_hierarchy = "date"
    raw_id_fields = ["production_line", "tenant"]


@admin.register(KPIRecord)
class KPIRecordAdmin(admin.ModelAdmin):
    list_display = [
        "kpi_type", "value", "unit", "period_type", "period_start",
    ]
    list_filter = ["kpi_type", "period_type"]
    date_hierarchy = "period_end"
    raw_id_fields = ["production_line", "machine", "tenant"]


@admin.register(QualityRecord)
class QualityRecordAdmin(admin.ModelAdmin):
    list_display = [
        "inspection_time", "production_order", "inspection_type",
        "quantity_inspected", "quantity_defective", "defect_rate",
    ]
    list_filter = ["inspection_type", "production_line"]
    date_hierarchy = "inspection_time"
    raw_id_fields = ["production_order", "production_line", "tenant"]


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        "scheduled_date", "machine", "maintenance_type", "status",
        "duration_minutes", "technician_name",
    ]
    list_filter = ["maintenance_type", "status"]
    date_hierarchy = "scheduled_date"
    raw_id_fields = ["machine", "tenant", "created_by"]