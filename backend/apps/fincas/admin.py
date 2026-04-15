from django.contrib import admin

from .models import Finca, Lote, PerfilExportacion


@admin.register(Finca)
class FincaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "municipio", "propietario", "verificada", "created_at")
    list_filter = ("municipio", "verificada")
    search_fields = ("nombre", "municipio", "slug")
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "variedad", "finca", "estado", "area_ha", "num_plantas")
    list_filter = ("variedad", "estado")
    search_fields = ("nombre", "finca__nombre")


@admin.register(PerfilExportacion)
class PerfilExportacionAdmin(admin.ModelAdmin):
    list_display = ("finca", "capacidad_anual_kg", "qr_url")
    search_fields = ("finca__nombre",)
