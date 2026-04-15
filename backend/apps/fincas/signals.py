"""Signals for fincas: auto-generate QR code and ensure PerfilExportacion."""
from __future__ import annotations

import os

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Finca, PerfilExportacion


def generate_qr_for_finca(finca: Finca) -> str:
    """Generate a QR PNG pointing to the public profile URL. Returns url path."""
    import qrcode

    frontend = os.getenv("FRONTEND_URL", "http://localhost:5173")
    url = f"{frontend}/finca/{finca.slug}"
    img = qrcode.make(url)
    media_dir = os.path.join(settings.MEDIA_ROOT, "qr")
    os.makedirs(media_dir, exist_ok=True)
    path = os.path.join(media_dir, f"{finca.slug}.png")
    img.save(path)
    qr_rel = f"{settings.MEDIA_URL}qr/{finca.slug}.png"
    perfil, _ = PerfilExportacion.objects.get_or_create(finca=finca)
    if perfil.qr_url != qr_rel:
        perfil.qr_url = qr_rel
        perfil.save(update_fields=["qr_url"])
    return qr_rel


@receiver(post_save, sender=Finca)
def finca_post_save(sender, instance: Finca, created: bool, **kwargs) -> None:
    """Generate QR and PerfilExportacion on Finca save."""
    try:
        generate_qr_for_finca(instance)
    except Exception:  # noqa: BLE001 - don't break save flow on qr errors
        # Ensure perfil exists even if QR generation fails.
        PerfilExportacion.objects.get_or_create(finca=instance)
