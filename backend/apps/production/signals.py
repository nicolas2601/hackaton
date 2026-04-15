"""
Django signals for production app.
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Machine, TelemetryEvent


@receiver(post_save, sender=TelemetryEvent)
def update_machine_status_from_telemetry(sender, instance, created, **kwargs):
    """
    Update machine status based on telemetry events.
    This allows real-time status updates from sensor data.
    """
    if created and instance.machine:
        machine = instance.machine

        # Update machine status based on operational status
        new_status = None
        if instance.operational_status in ["running", "idle", "maintenance", "fault"]:
            new_status = instance.operational_status

        if new_status and machine.status != new_status:
            machine.status = new_status
            machine.save(update_fields=["status", "updated_at"])


@receiver(pre_delete, sender=TelemetryEvent)
def log_telemetry_deletion(sender, instance, **kwargs):
    """
    Log telemetry event deletion for audit purposes.
    """
    # In production, this would write to an audit log
    pass