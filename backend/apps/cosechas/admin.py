from django.contrib import admin

from .models import ControlFitosanitario, Cosecha


@admin.register(Cosecha)
class CosechaAdmin(admin.ModelAdmin):
    list_display = ("fecha_cosecha", "lote", "kg_seco", "calidad", "dias_fermentacion")
    list_filter = ("calidad",)
    search_fields = ("lote__nombre", "lote__finca__nombre")
    date_hierarchy = "fecha_cosecha"


@admin.register(ControlFitosanitario)
class ControlFitosanitarioAdmin(admin.ModelAdmin):
    list_display = ("fecha", "lote", "tipo_control", "plaga_enfermedad")
    list_filter = ("tipo_control", "plaga_enfermedad")
    search_fields = ("lote__nombre", "tratamiento_aplicado")
    date_hierarchy = "fecha"
