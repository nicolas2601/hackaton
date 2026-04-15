"""Modelos de Fincas, Lotes y Perfil de Exportación para CacaoTrace."""
from django.conf import settings
from django.db import models


VARIEDAD_CHOICES = [
    ("criollo", "Criollo"),
    ("trinitario", "Trinitario"),
    ("forastero", "Forastero"),
    ("ccn51", "CCN-51"),
    ("ics60", "ICS-60"),
    ("ics95", "ICS-95"),
    ("acriollado", "Criollo acriollado"),
    ("otro", "Otro"),
]

ESTADO_LOTE_CHOICES = [
    ("activo", "Activo"),
    ("renovacion", "En renovación"),
    ("improductivo", "Improductivo"),
]


class Finca(models.Model):
    """Finca cacaotera de Santander."""

    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fincas",
    )
    slug = models.SlugField(max_length=80, unique=True)
    nombre = models.CharField(max_length=120)
    municipio = models.CharField(max_length=80)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    area_total_ha = models.DecimalField(max_digits=6, decimal_places=2)
    verificada = models.BooleanField(default=False)
    foto = models.URLField(blank=True)
    descripcion = models.TextField(blank=True)
    telefono_wa = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Finca"
        verbose_name_plural = "Fincas"

    def __str__(self) -> str:
        return f"{self.nombre} ({self.municipio})"

    def get_absolute_url(self) -> str:
        return f"/finca/{self.slug}"


class Lote(models.Model):
    """Lote productivo dentro de una finca."""

    finca = models.ForeignKey(
        Finca,
        on_delete=models.CASCADE,
        related_name="lotes",
    )
    nombre = models.CharField(max_length=80)
    variedad = models.CharField(max_length=20, choices=VARIEDAD_CHOICES)
    num_plantas = models.PositiveIntegerField()
    edad_años = models.PositiveSmallIntegerField()
    area_ha = models.DecimalField(max_digits=6, decimal_places=2)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_LOTE_CHOICES,
        default="activo",
    )

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"

    def __str__(self) -> str:
        return f"{self.nombre} · {self.finca.nombre}"


class PerfilExportacion(models.Model):
    """Perfil de exportación asociado a una finca."""

    finca = models.OneToOneField(
        Finca,
        on_delete=models.CASCADE,
        related_name="perfil_exportacion",
    )
    certificaciones = models.JSONField(default=list, blank=True)
    mercados_destino = models.JSONField(default=list, blank=True)
    capacidad_anual_kg = models.PositiveIntegerField(default=0)
    qr_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Perfil de exportación"
        verbose_name_plural = "Perfiles de exportación"

    def __str__(self) -> str:
        return f"Perfil export · {self.finca.nombre}"
