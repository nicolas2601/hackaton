"""
Django models for telemetry app.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Sensor(models.Model):
    """Sensor model representing IoT sensors attached to machines."""

    SENSOR_TYPE_CHOICES = [
        ("temperature", "Temperature"),
        ("vibration", "Vibration"),
        ("current", "Current"),
        ("pressure", "Pressure"),
        ("humidity", "Humidity"),
        ("rpm", "RPM"),
        ("counter", "Counter"),
        ("custom", "Custom"),
    ]

    UNIT_CHOICES = [
        ("°C", "Celsius"),
        ("°F", "Fahrenheit"),
        ("mm/s", "Vibration mm/s"),
        ("A", "Amperes"),
        ("V", "Volts"),
        ("Pa", "Pascals"),
        ("%", "Percentage"),
        ("rpm", "RPM"),
        ("counts", "Counts"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    machine = models.ForeignKey(
        "production.Machine",
        on_delete=models.CASCADE,
        related_name="sensors",
    )
    sensor_type = models.CharField(max_length=50, choices=SENSOR_TYPE_CHOICES)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)

    # Configuration
    is_active = models.BooleanField(default=True)
    sampling_rate = models.IntegerField(
        default=1,
        help_text="Sampling rate in seconds",
    )

    # Thresholds
    threshold_min = models.FloatField(null=True, blank=True)
    threshold_max = models.FloatField(null=True, blank=True)
    threshold_critical_min = models.FloatField(null=True, blank=True)
    threshold_critical_max = models.FloatField(null=True, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["machine", "name"]
        verbose_name = "Sensor"
        verbose_name_plural = "Sensors"

    def __str__(self) -> str:
        return f"{self.machine.name} / {self.name}"

    def is_in_normal_range(self, value: float) -> bool:
        """Check if value is within normal thresholds."""
        if self.threshold_min is not None and value < self.threshold_min:
            return False
        if self.threshold_max is not None and value > self.threshold_max:
            return False
        return True


class TelemetryEvent(models.Model):
    """Telemetry event from machine sensors."""

    OPERATIONAL_STATUS_CHOICES = [
        ("running", "Running"),
        ("idle", "Idle"),
        ("stopped", "Stopped"),
        ("maintenance", "Maintenance"),
        ("fault", "Fault"),
    ]

    id = models.BigAutoField(primary_key=True)
    machine = models.ForeignKey(
        "production.Machine",
        on_delete=models.CASCADE,
        related_name="telemetry_events",
    )
    timestamp = models.DateTimeField(db_index=True)
    operational_status = models.CharField(
        max_length=20,
        choices=OPERATIONAL_STATUS_CHOICES,
        default="running",
    )

    # Production metrics
    production_count = models.IntegerField(default=0)
    defects = models.IntegerField(default=0)

    # Sensor readings
    temperature = models.FloatField(
        validators=[MinValueValidator(-50.0), MaxValueValidator(500.0)],
        help_text="Temperature in Celsius",
    )
    vibration = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Vibration in mm/s",
    )
    current = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Current in Amperes",
    )

    # Computed uptime in seconds
    uptime = models.IntegerField(default=0)

    # MQTT metadata
    mqtt_topic = models.CharField(max_length=500, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Telemetry Event"
        verbose_name_plural = "Telemetry Events"
        indexes = [
            models.Index(fields=["machine", "-timestamp"]),
            models.Index(fields=["-timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.machine.name} @ {self.timestamp.isoformat()}"

    @property
    def defect_rate(self) -> float:
        """Calculate defect rate as percentage."""
        total = self.production_count + self.defects
        if total == 0:
            return 0.0
        return round((self.defects / total) * 100, 2)


class AlertRule(models.Model):
    """Rule for generating alerts based on telemetry thresholds."""

    SEVERITY_CHOICES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("critical", "Critical"),
    ]

    METRIC_CHOICES = [
        ("temperature", "Temperature"),
        ("vibration", "Vibration"),
        ("current", "Current"),
        ("defect_rate", "Defect Rate"),
    ]

    OPERATOR_CHOICES = [
        ("gt", "Greater Than"),
        ("lt", "Less Than"),
        ("eq", "Equal To"),
        ("gte", "Greater Than or Equal"),
        ("lte", "Less Than or Equal"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name="alert_rules",
        null=True,
        blank=True,
        help_text="Leave empty to apply to all sensors of similar type",
    )
    metric = models.CharField(max_length=50, choices=METRIC_CHOICES)
    operator = models.CharField(max_length=10, choices=OPERATOR_CHOICES)
    threshold = models.FloatField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="warning")

    # Cooldown to prevent alert spam (in seconds)
    cooldown_seconds = models.IntegerField(default=300)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.metric} {self.operator} {self.threshold})"


class TelemetryAlert(models.Model):
    """Generated alert instance."""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("acknowledged", "Acknowledged"),
        ("resolved", "Resolved"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(
        AlertRule,
        on_delete=models.SET_NULL,
        null=True,
        related_name="alerts",
    )
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    telemetry_event = models.ForeignKey(
        TelemetryEvent,
        on_delete=models.SET_NULL,
        null=True,
        related_name="alerts",
    )

    severity = models.CharField(max_length=20)
    message = models.TextField()
    metric_value = models.FloatField()
    threshold_value = models.FloatField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    acknowledged_by = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acknowledged_telemetry_alerts",
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Telemetry Alert"
        verbose_name_plural = "Telemetry Alerts"
        indexes = [
            models.Index(fields=["sensor", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.sensor.name}: {self.message[:50]}..."