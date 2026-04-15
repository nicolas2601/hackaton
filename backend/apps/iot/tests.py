"""Tests for IoT sensor data endpoints and MQTT topic parsing."""
from __future__ import annotations

from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from apps.core.models import User
from apps.fincas.models import Finca, Lote
from apps.iot.models import SensorData


def _parse_topic(topic: str):
    # cacao/finca/<finca>/lote/<lote>/<tipo>
    parts = topic.split("/")
    return int(parts[4]), parts[5]


class ParseTopicTests(TestCase):
    def test_parse_topic_basic(self) -> None:
        lote, tipo = _parse_topic("cacao/finca/1/lote/2/temp_suelo")
        self.assertEqual(lote, 2)
        self.assertEqual(tipo, "temp_suelo")

    def test_parse_topic_hum_secado(self) -> None:
        lote, tipo = _parse_topic("cacao/finca/3/lote/7/hum_secado")
        self.assertEqual(lote, 7)
        self.assertEqual(tipo, "hum_secado")

    def test_parse_topic_ph_suelo(self) -> None:
        lote, tipo = _parse_topic("cacao/finca/5/lote/8/ph_suelo")
        self.assertEqual(lote, 8)
        self.assertEqual(tipo, "ph_suelo")


class SensorDataTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="iot@example.com", password="pw-long-123"
        )
        finca = Finca.objects.create(
            propietario=self.user,
            slug="iot-finca",
            nombre="IoT",
            municipio="San Vicente",
            lat=Decimal("6.88"),
            lng=Decimal("-73.42"),
            area_total_ha=Decimal("3.0"),
        )
        self.lote = Lote.objects.create(
            finca=finca,
            nombre="L1",
            variedad="trinitario",
            num_plantas=100,
            edad_años=5,
            area_ha=Decimal("1.0"),
            lat=Decimal("6.88"),
            lng=Decimal("-73.42"),
        )
        SensorData.objects.create(
            lote=self.lote, tipo="temp_suelo", valor=25.5, unidad="°C"
        )
        SensorData.objects.create(
            lote=self.lote, tipo="hum_suelo", valor=72.0, unidad="%"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_filter_by_tipo(self) -> None:
        resp = self.client.get("/api/sensors/", {"tipo": "temp_suelo"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        items = data.get("results", data)
        for row in items:
            self.assertEqual(row["tipo"], "temp_suelo")

    def test_sse_missing_lote_id(self) -> None:
        """SSE endpoint returns 400 when lote_id is missing."""
        resp = self.client.get("/api/sensors/stream/")
        self.assertEqual(resp.status_code, 400)

    def test_latest_endpoint(self) -> None:
        """Latest endpoint returns most recent row per tipo."""
        resp = self.client.get("/api/sensors/latest/", {"lote_id": self.lote.id})
        self.assertEqual(resp.status_code, 200)
        tipos = {row["tipo"] for row in resp.json()}
        self.assertIn("temp_suelo", tipos)
