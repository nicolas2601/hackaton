"""Modelos IoT para CacaoTrace — telemetría de sensores."""
from django.db import models


SENSOR_TIPOS = [
    ("temp_suelo", "Temperatura suelo"),
    ("hum_suelo", "Humedad suelo"),
    ("temp_ferm", "Temperatura fermentación"),
    ("hum_secado", "Humedad secado"),
    ("ph_suelo", "pH suelo"),
]


class SensorData(models.Model):
    """Lectura puntual de un sensor IoT asociado a un lote."""

    lote = models.ForeignKey(
        "fincas.Lote",
        on_delete=models.CASCADE,
        related_name="sensores",
    )
    tipo = models.CharField(max_length=20, choices=SENSOR_TIPOS, db_index=True)
    valor = models.FloatField()
    unidad = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Lectura de sensor"
        verbose_name_plural = "Lecturas de sensores"
        indexes = [
            models.Index(fields=["lote", "tipo", "-timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.tipo}={self.valor}{self.unidad} @ {self.timestamp:%Y-%m-%d %H:%M}"
