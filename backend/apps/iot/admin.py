from django.contrib import admin

from .models import SensorData


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ("tipo", "valor", "unidad", "lote", "timestamp")
    list_filter = ("tipo", "lote__finca__municipio")
    search_fields = ("lote__nombre", "lote__finca__nombre")
    date_hierarchy = "timestamp"
