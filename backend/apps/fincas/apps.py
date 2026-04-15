from django.apps import AppConfig


class FincasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.fincas"
    verbose_name = "Fincas"

    def ready(self) -> None:  # noqa: D401
        from . import signals  # noqa: F401
