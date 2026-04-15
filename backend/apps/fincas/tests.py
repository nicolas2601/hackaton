"""Tests for fincas, signals and QR generation."""
from __future__ import annotations

from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from apps.core.models import User
from apps.fincas.models import Finca, PerfilExportacion


class FincaModelTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@example.com", password="x-pass-1234"
        )

    def test_finca_perfil_autogen(self) -> None:
        """Creating a Finca triggers signals: perfil + qr_url populated."""
        finca = Finca.objects.create(
            propietario=self.user,
            slug="finca-demo",
            nombre="Finca Demo",
            municipio="San Vicente",
            lat=Decimal("6.88"),
            lng=Decimal("-73.42"),
            area_total_ha=Decimal("3.0"),
            verificada=True,
        )
        self.assertTrue(
            PerfilExportacion.objects.filter(finca=finca).exists(),
            "PerfilExportacion no auto-creado",
        )
        perfil = finca.perfil_exportacion
        self.assertTrue(perfil.qr_url.endswith("finca-demo.png"))


class FincaPublicaAPITests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = User.objects.create_user(email="pub@example.com", password="pw-long-1")
        Finca.objects.create(
            propietario=user,
            slug="publica",
            nombre="Pub",
            municipio="Rionegro",
            lat=Decimal("7.38"),
            lng=Decimal("-73.15"),
            area_total_ha=Decimal("2.0"),
            verificada=True,
        )
        Finca.objects.create(
            propietario=user,
            slug="oculta",
            nombre="Oculta",
            municipio="Rionegro",
            lat=Decimal("7.38"),
            lng=Decimal("-73.15"),
            area_total_ha=Decimal("2.0"),
            verificada=False,
        )

    def test_only_verificadas_public(self) -> None:
        resp = self.client.get("/api/fincas/publicas/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        items = data.get("results", data)
        slugs = [it["slug"] for it in items]
        self.assertIn("publica", slugs)
        self.assertNotIn("oculta", slugs)

    def test_public_detail(self) -> None:
        resp = self.client.get("/api/fincas/publicas/publica/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["slug"], "publica")
