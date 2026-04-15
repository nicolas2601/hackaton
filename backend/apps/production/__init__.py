"""Production app configuration."""
from django.apps import AppConfig


class ProductionConfig(AppConfig):
    """Configuration for production app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.production"
    verbose_name = "Production - Lines, Machines, Orders"