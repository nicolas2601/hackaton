"""Modelos de Cosechas y Controles Fitosanitarios."""
from django.db import models


CALIDAD_CHOICES = [
    ("premium", "Premium"),
    ("estandar", "Estándar"),
    ("pasilla", "Pasilla"),
]

TIPO_CONTROL_CHOICES = [
    ("preventivo", "Preventivo"),
    ("correctivo", "Correctivo"),
]

PLAGA_ENFERMEDAD_CHOICES = [
    ("monilia", "Monilia"),
    ("fitoftora", "Fitóftora"),
    ("escoba_bruja", "Escoba de bruja"),
    ("otra", "Otra"),
]


class Cosecha(models.Model):
    """Registro de cosecha por lote."""

    lote = models.ForeignKey(
        "fincas.Lote",
        on_delete=models.CASCADE,
        related_name="cosechas",
    )
    fecha_cosecha = models.DateField()
    kg_baba = models.DecimalField(max_digits=8, decimal_places=2)
    kg_seco = models.DecimalField(max_digits=8, decimal_places=2)
    dias_fermentacion = models.PositiveSmallIntegerField()
    temp_prom_fermentacion = models.DecimalField(max_digits=4, decimal_places=1)
    dias_secado = models.PositiveSmallIntegerField()
    calidad = models.CharField(
        max_length=20,
        choices=CALIDAD_CHOICES,
        default="estandar",
    )

    class Meta:
        ordering = ["-fecha_cosecha"]
        verbose_name = "Cosecha"
        verbose_name_plural = "Cosechas"

    def __str__(self) -> str:
        return f"Cosecha {self.fecha_cosecha} · {self.lote.nombre}"


class ControlFitosanitario(models.Model):
    """Control fitosanitario aplicado a un lote."""

    lote = models.ForeignKey(
        "fincas.Lote",
        on_delete=models.CASCADE,
        related_name="controles",
    )
    fecha = models.DateField()
    tipo_control = models.CharField(max_length=20, choices=TIPO_CONTROL_CHOICES)
    plaga_enfermedad = models.CharField(max_length=20, choices=PLAGA_ENFERMEDAD_CHOICES)
    tratamiento_aplicado = models.TextField()
    resultado = models.CharField(max_length=200, blank=True)
    foto_evidencia = models.URLField(blank=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Control fitosanitario"
        verbose_name_plural = "Controles fitosanitarios"

    def __str__(self) -> str:
        return f"{self.tipo_control}/{self.plaga_enfermedad} · {self.fecha}"
