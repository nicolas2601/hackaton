"""
Django models for analytics app.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class OEERecord(models.Model):
    """OEE (Overall Equipment Effectiveness) calculated record."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    machine = models.ForeignKey(
        "production.Machine",
        on_delete=models.CASCADE,
        related_name="oee_records",
    )
    production_line = models.ForeignKey(
        "production.ProductionLine",
        on_delete=models.CASCADE,
        related_name="oee_records",
    )
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="oee_records",
    )

    date = models.DateField(db_index=True)

    # OEE Components (all as decimals, e.g., 0.85 for 85%)
    availability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Availability factor (0-1)",
    )
    performance = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Performance factor (0-1)",
    )
    quality = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Quality factor (0-1)",
    )
    oee = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="OEE = Availability × Performance × Quality (0-1)",
    )

    # Additional metrics
    planned_production_time = models.IntegerField(
        help_text="Planned production time in seconds"
    )
    actual_production_time = models.IntegerField(
        help_text="Actual production time in seconds"
    )
    downtime = models.IntegerField(
        default=0,
        help_text="Total downtime in seconds"
    )
    ideal_cycle_time = models.FloatField(
        default=0.0,
        help_text="Ideal cycle time in seconds per unit"
    )
    actual_cycle_time = models.FloatField(
        default=0.0,
        help_text="Actual cycle time in seconds per unit"
    )

    total_count = models.IntegerField(default=0)
    good_count = models.IntegerField(default=0)
    defect_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "OEE Record"
        verbose_name_plural = "OEE Records"
        unique_together = ["machine", "date"]
        indexes = [
            models.Index(fields=["tenant", "-date"]),
            models.Index(fields=["production_line", "-date"]),
            models.Index(fields=["machine", "-date"]),
        ]

    def __str__(self) -> str:
        return f"{self.machine.name} - {self.date} - OEE: {self.oee:.1%}"

    @property
    def oee_grade(self) -> str:
        """Return OEE grade based on world-class standards."""
        if self.oee >= 0.85:
            return "World Class"
        elif self.oee >= 0.70:
            return "Good"
        elif self.oee >= 0.60:
            return "Fair"
        else:
            return "Needs Improvement"

    @property
    def oee_percentage(self) -> float:
        """Return OEE as percentage for admin display."""
        return round(self.oee * 100, 1)


class DailySummary(models.Model):
    """Daily production summary for a production line."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="daily_summaries",
    )
    production_line = models.ForeignKey(
        "production.ProductionLine",
        on_delete=models.CASCADE,
        related_name="daily_summaries",
    )
    date = models.DateField(db_index=True)

    # Order counts
    total_orders = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    cancelled_orders = models.IntegerField(default=0)

    # Production totals
    total_planned_quantity = models.IntegerField(default=0)
    total_produced_quantity = models.IntegerField(default=0)
    total_defective_quantity = models.IntegerField(default=0)

    # Time metrics
    total_production_time = models.IntegerField(
        default=0,
        help_text="Total production time in seconds",
    )
    total_downtime = models.IntegerField(
        default=0,
        help_text="Total downtime in seconds",
    )

    # Average OEE
    average_oee = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.0,
    )

    # Quality metrics
    quality_rate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=0.0,
    )

    # Alerts
    total_alerts = models.IntegerField(default=0)
    critical_alerts = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Daily Summary"
        verbose_name_plural = "Daily Summaries"
        unique_together = ["production_line", "date"]
        indexes = [
            models.Index(fields=["tenant", "-date"]),
            models.Index(fields=["production_line", "-date"]),
        ]

    def __str__(self) -> str:
        return f"{self.production_line.name} - {self.date}"

    @property
    def completion_rate(self) -> float:
        """Calculate completion rate as percentage."""
        if self.total_planned_quantity == 0:
            return 0.0
        return round((self.total_produced_quantity / self.total_planned_quantity) * 100, 1)


class KPIRecord(models.Model):
    """Key Performance Indicator record."""

    KPI_TYPES = [
        ("oee", "OEE"),
        ("mtbf", "MTBF (Mean Time Between Failures)"),
        ("mttr", "MTTR (Mean Time To Repair)"),
        ("availability", "Availability"),
        ("performance", "Performance"),
        ("quality", "Quality"),
        ("throughput", "Throughput"),
        ("defect_rate", "Defect Rate"),
        ("scrap_rate", "Scrap Rate"),
        ("fpy", "First Pass Yield"),
        ("takt_time", "Takt Time"),
    ]

    PERIOD_TYPES = [
        ("shift", "Shift"),
        ("day", "Day"),
        ("week", "Week"),
        ("month", "Month"),
        ("year", "Year"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="kpi_records",
    )

    kpi_type = models.CharField(max_length=50, choices=KPI_TYPES, db_index=True)
    value = models.FloatField()
    unit = models.CharField(max_length=50, blank=True)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES)

    # Optional filters
    production_line = models.ForeignKey(
        "production.ProductionLine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kpi_records",
    )
    machine = models.ForeignKey(
        "production.Machine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kpi_records",
    )

    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-period_end", "-created_at"]
        verbose_name = "KPI Record"
        verbose_name_plural = "KPI Records"
        indexes = [
            models.Index(fields=["tenant", "kpi_type", "-period_end"]),
            models.Index(fields=["-period_end"]),
        ]

    def __str__(self) -> str:
        return f"{self.kpi_type}: {self.value} {self.unit} ({self.period_type})"


class QualityRecord(models.Model):
    """Quality inspection record."""

    INSPECTION_TYPES = [
        ("visual", "Visual Inspection"),
        ("dimensional", "Dimensional Check"),
        ("functional", "Functional Test"),
        ("material", "Material Test"),
        ("final", "Final Inspection"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="quality_records",
    )

    production_order = models.ForeignKey(
        "production.ProductionOrder",
        on_delete=models.CASCADE,
        related_name="quality_records",
    )
    production_line = models.ForeignKey(
        "production.ProductionLine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quality_records",
    )

    inspection_type = models.CharField(max_length=50, choices=INSPECTION_TYPES)
    inspection_time = models.DateTimeField(auto_now_add=True)

    quantity_inspected = models.IntegerField(default=0)
    quantity_defective = models.IntegerField(default=0)
    quantity_reworked = models.IntegerField(default=0)
    quantity_accepted = models.IntegerField(default=0)

    defect_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Defect rate as percentage",
    )

    # Defect breakdown stored as JSON
    defect_types = models.JSONField(
        default=dict,
        blank=True,
        help_text="{'type_name': count, ...}",
    )

    inspector_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-inspection_time"]
        verbose_name = "Quality Record"
        verbose_name_plural = "Quality Records"
        indexes = [
            models.Index(fields=["production_order", "-inspection_time"]),
            models.Index(fields=["tenant", "-inspection_time"]),
        ]

    def __str__(self) -> str:
        return f"{self.production_order.order_number} - {self.inspection_type} @ {self.inspection_time}"

    def calculate_defect_rate(self) -> float:
        """Calculate defect rate."""
        if self.quantity_inspected == 0:
            return 0.0
        return round((self.quantity_defective / self.quantity_inspected) * 100, 2)

    def save(self, *args, **kwargs):
        self.defect_rate = self.calculate_defect_rate()
        super().save(*args, **kwargs)


class MaintenanceRecord(models.Model):
    """Maintenance activity record."""

    MAINTENANCE_TYPES = [
        ("preventive", "Preventive"),
        ("corrective", "Corrective"),
        ("predictive", "Predictive"),
        ("emergency", "Emergency"),
    ]

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="maintenance_records",
    )

    machine = models.ForeignKey(
        "production.Machine",
        on_delete=models.CASCADE,
        related_name="maintenance_records",
    )

    maintenance_type = models.CharField(max_length=50, choices=MAINTENANCE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")

    scheduled_date = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    duration_minutes = models.IntegerField(default=0, help_text="Total maintenance duration")

    description = models.TextField()
    work_performed = models.TextField(blank=True)
    parts_replaced = models.JSONField(default=list, blank=True)

    technician_name = models.CharField(max_length=200, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_by = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_maintenance_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_date"]
        verbose_name = "Maintenance Record"
        verbose_name_plural = "Maintenance Records"

    def __str__(self) -> str:
        return f"{self.machine.name} - {self.maintenance_type} - {self.scheduled_date.date()}"