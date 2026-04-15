"""Production app serializers."""
from rest_framework import serializers
from .models import (
    ProductionLine, Machine, MachineType, Product,
    ProductionOrder, ProductionOrderItem, Shift,
)


class MachineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineType
        fields = "__all__"


class MachineSerializer(serializers.ModelSerializer):
    production_line_name = serializers.CharField(
        source="production_line.name", read_only=True
    )
    availability = serializers.FloatField(read_only=True)

    class Meta:
        model = Machine
        fields = [
            "id", "name", "slug", "machine_type", "serial_number",
            "production_line", "production_line_name", "status", "is_active",
            "location", "temp_min", "temp_max", "vibration_max", "current_max",
            "specifications", "installed_at", "last_maintenance_at",
            "created_at", "updated_at", "availability",
        ]


class ProductionLineSerializer(serializers.ModelSerializer):
    machines_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductionLine
        fields = [
            "id", "name", "slug", "description", "location",
            "shifts_per_day", "hours_per_shift", "is_active",
            "target_oee", "settings", "created_at", "updated_at",
            "machines_count",
        ]

    def get_machines_count(self, obj):
        return obj.machines.count()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductionOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionOrderItem
        fields = "__all__"


class ProductionOrderSerializer(serializers.ModelSerializer):
    production_line_name = serializers.CharField(
        source="production_line.name", read_only=True
    )
    product_name = serializers.CharField(source="product.name", read_only=True)
    assigned_to_name = serializers.CharField(
        source="assigned_to.full_name", read_only=True
    )
    completion_rate = serializers.FloatField(read_only=True)
    quality_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = ProductionOrder
        fields = [
            "id", "order_number", "production_line", "production_line_name",
            "product", "product_name", "status", "priority",
            "quantity_planned", "quantity_completed", "quantity_defective",
            "planned_start", "planned_end", "actual_start", "actual_end",
            "assigned_to", "assigned_to_name", "notes", "metadata",
            "created_at", "updated_at", "completion_rate", "quality_rate",
        ]


class ShiftSerializer(serializers.ModelSerializer):
    duration_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = Shift
        fields = [
            "id", "production_line", "name", "shift_type",
            "start_time", "end_time", "days_of_week", "is_active",
            "duration_hours",
        ]