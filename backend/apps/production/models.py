"""
Django models for production app.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator


class ProductionLine(models.Model):
    """
    Production line model representing a manufacturing line.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="production_lines",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)

    # Capacity
    shifts_per_day = models.IntegerField(default=1)
    hours_per_shift = models.FloatField(default=8.0)

    # Status
    is_active = models.BooleanField(default=True)

    # Settings
    target_oee = models.FloatField(
        default=0.85,
        validators=[MinValueValidator(0.0)],
        help_text="Target OEE as decimal (0.85 = 85%)",
    )
    settings = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Production Line"
        verbose_name_plural = "Production Lines"
        unique_together = ["tenant", "slug"]
        indexes = [
            models.Index(fields=["tenant", "slug"]),
        ]

    def __str__(self) -> str:
        return f"{self.tenant.name} / {self.name}"

    @property
    def full_name(self) -> str:
        return f"{self.tenant.name}/{self.name}"


class MachineType(models.Model):
    """
    Machine type catalog for standardizing machine configurations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    # Default thresholds
    default_temp_min = models.FloatField(default=0.0)
    default_temp_max = models.FloatField(default=250.0)
    default_vibration_max = models.FloatField(default=10.0)
    default_current_max = models.FloatField(default=30.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Machine Type"
        verbose_name_plural = "Machine Types"

    def __str__(self) -> str:
        return self.name


class Machine(models.Model):
    """
    Machine model representing a production machine.
    """
    STATUS_CHOICES = [
        ("online", "Online"),
        ("offline", "Offline"),
        ("warning", "Warning"),
        ("maintenance", "Maintenance"),
        ("idle", "Idle"),
    ]

    MACHINE_TYPE_CHOICES = [
        ("injection", "Injection Molding"),
        ("cutting", "Cutting"),
        ("stitching", "Stitching"),
        ("assembly", "Assembly"),
        ("finishing", "Finishing"),
        ("packaging", "Packaging"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    machine_type = models.CharField(max_length=50, choices=MACHINE_TYPE_CHOICES)
    serial_number = models.CharField(max_length=100, unique=True)
    production_line = models.ForeignKey(
        ProductionLine,
        on_delete=models.CASCADE,
        related_name="machines",
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="offline")
    is_active = models.BooleanField(default=True)

    # Location within the line
    location = models.CharField(max_length=200, blank=True)

    # Sensor thresholds
    temp_min = models.FloatField(default=0.0)
    temp_max = models.FloatField(default=250.0)
    vibration_max = models.FloatField(default=10.0)
    current_max = models.FloatField(default=30.0)

    # Specifications
    specifications = models.JSONField(default=dict, blank=True)

    # Timestamps
    installed_at = models.DateTimeField(null=True, blank=True)
    last_maintenance_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Machine"
        verbose_name_plural = "Machines"
        unique_together = ["production_line", "slug"]
        indexes = [
            models.Index(fields=["production_line", "slug"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.production_line.name} / {self.name}"

    @property
    def full_name(self) -> str:
        return f"{self.production_line.tenant.name}/{self.production_line.name}/{self.name}"

    @property
    def availability(self) -> float:
        """Calculate availability based on status."""
        if self.status == "online":
            return 1.0
        elif self.status in ("warning", "idle"):
            return 0.8
        elif self.status == "maintenance":
            return 0.0
        return 0.0


class Product(models.Model):
    """
    Product/SKU model for manufactured items.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="products",
    )
    sku = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Category
    category = models.CharField(max_length=100, blank=True)

    # Bill of materials reference
    bom_reference = models.CharField(max_length=200, blank=True)

    # Cycle time (seconds per unit)
    standard_cycle_time = models.FloatField(
        default=60.0,
        help_text="Standard cycle time in seconds",
    )

    # Quality
    quality_target = models.FloatField(
        default=0.95,
        validators=[MinValueValidator(0.0)],
        help_text="Target quality as decimal (0.95 = 95%)",
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sku"]
        verbose_name = "Product"
        verbose_name_plural = "Products"
        unique_together = ["tenant", "sku"]

    def __str__(self) -> str:
        return f"{self.sku} - {self.name}"


class ProductionOrder(models.Model):
    """
    Production order model for tracking manufacturing orders.
    """
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("paused", "Paused"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        (1, "Low"),
        (2, "Normal"),
        (3, "High"),
        (4, "Urgent"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)

    production_line = models.ForeignKey(
        ProductionLine,
        on_delete=models.CASCADE,
        related_name="production_orders",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="production_orders",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)

    # Quantities
    quantity_planned = models.IntegerField(default=0)
    quantity_completed = models.IntegerField(default=0)
    quantity_defective = models.IntegerField(default=0)

    # Schedule
    planned_start = models.DateTimeField(null=True, blank=True)
    planned_end = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)

    # Assignment
    assigned_to = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_orders",
    )

    # Notes
    notes = models.TextField(blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "planned_start"]
        verbose_name = "Production Order"
        verbose_name_plural = "Production Orders"
        indexes = [
            models.Index(fields=["status", "planned_start"]),
            models.Index(fields=["production_line", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.order_number} - {self.product.sku}"

    @property
    def completion_rate(self) -> float:
        """Calculate completion percentage."""
        if self.quantity_planned == 0:
            return 0.0
        return round((self.quantity_completed / self.quantity_planned) * 100, 1)

    @property
    def quality_rate(self) -> float:
        """Calculate quality percentage."""
        total_output = self.quantity_completed + self.quantity_defective
        if total_output == 0:
            return 0.0
        return round((self.quantity_completed / total_output) * 100, 1)


class ProductionOrderItem(models.Model):
    """
    Item within a production order (for batch tracking).
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )

    batch_number = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    produced_quantity = models.IntegerField(default=0)
    defective_quantity = models.IntegerField(default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Production Order Item"
        verbose_name_plural = "Production Order Items"
        unique_together = ["order", "batch_number"]

    def __str__(self) -> str:
        return f"{self.order.order_number} / Batch {self.batch_number}"


class Shift(models.Model):
    """
    Shift model for tracking work shifts.
    """
    SHIFT_TYPE_CHOICES = [
        ("day", "Day Shift"),
        ("afternoon", "Afternoon Shift"),
        ("night", "Night Shift"),
        ("custom", "Custom"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    production_line = models.ForeignKey(
        ProductionLine,
        on_delete=models.CASCADE,
        related_name="shifts",
    )

    name = models.CharField(max_length=100)
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES)

    # Time definitions (local time)
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Days of week (0=Monday, 6=Sunday)
    days_of_week = models.JSONField(
        default=list,
        help_text="List of days [0,1,2,3,4] for Mon-Fri",
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["start_time"]
        verbose_name = "Shift"
        verbose_name_plural = "Shifts"

    def __str__(self) -> str:
        return f"{self.production_line.name} / {self.name}"

    @property
    def duration_hours(self) -> float:
        """Calculate shift duration in hours."""
        from datetime import datetime, time
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        if end < start:  # Overnight shift
            end = datetime.combine(datetime.today(), self.end_time)
            duration = (end - start).total_seconds() / 3600
            return duration + 24 if duration < 0 else duration
        return (end - start).total_seconds() / 3600