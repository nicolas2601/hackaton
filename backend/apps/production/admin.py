"""Admin configuration for production app."""
from django.contrib import admin
from .models import ProductionLine, Machine, ProductionOrder, ProductionOrderItem


@admin.register(ProductionLine)
class ProductionLineAdmin(admin.ModelAdmin):
    list_display = ["name", "tenant", "location", "is_active", "created_at"]
    list_filter = ["is_active", "tenant"]
    search_fields = ["name", "location"]
    raw_id_fields = ["tenant"]


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = [
        "name", "production_line", "machine_type", "status", "is_active",
    ]
    list_filter = ["machine_type", "status", "is_active", "production_line"]
    search_fields = ["name", "serial_number"]
    raw_id_fields = ["production_line"]


class ProductionOrderItemInline(admin.TabularInline):
    model = ProductionOrderItem
    extra = 1


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number", "production_line", "status", "priority",
        "planned_start", "quantity_planned",
    ]
    list_filter = ["status", "priority", "production_line"]
    search_fields = ["order_number", "notes"]
    inlines = [ProductionOrderItemInline]
    raw_id_fields = ["production_line", "product", "assigned_to"]


@admin.register(ProductionOrderItem)
class ProductionOrderItemAdmin(admin.ModelAdmin):
    list_display = [
        "order", "batch_number", "quantity", "produced_quantity", "status",
    ]
    list_filter = ["status"]
    search_fields = ["batch_number"]
    raw_id_fields = ["order"]