"""Seed CacaoTrace with 5 fincas, lotes, sensor history and perfiles."""
from __future__ import annotations

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.cosechas.models import ControlFitosanitario, Cosecha
from apps.fincas.models import Finca, Lote, PerfilExportacion
from apps.fincas.signals import generate_qr_for_finca
from apps.iot.models import SensorData
from apps.core.models import User


FINCAS_SEED = [
    {
        "slug": "la-esperanza",
        "nombre": "Finca La Esperanza",
        "municipio": "San Vicente de Chucurí",
        "lat": Decimal("6.881400"),
        "lng": Decimal("-73.422500"),
        "area": Decimal("4.50"),
        "email": "efrain@sanvicente.co",
        "first": "Efraín",
        "last": "Rodríguez",
        "lotes": [
            {"nombre": "Lote Norte", "variedad": "trinitario", "plantas": 900, "edad": 8, "area": Decimal("2.50")},
            {"nombre": "Lote Criollo", "variedad": "criollo", "plantas": 620, "edad": 6, "area": Decimal("2.00")},
        ],
    },
    {
        "slug": "el-cacaotal",
        "nombre": "Finca El Cacaotal",
        "municipio": "El Carmen de Chucurí",
        "lat": Decimal("6.710000"),
        "lng": Decimal("-73.520000"),
        "area": Decimal("3.00"),
        "email": "maria@carmen.co",
        "first": "María",
        "last": "Peña",
        "lotes": [
            {"nombre": "Lote CCN", "variedad": "ccn51", "plantas": 850, "edad": 5, "area": Decimal("1.50")},
            {"nombre": "Lote ICS-95", "variedad": "ics95", "plantas": 700, "edad": 7, "area": Decimal("1.50")},
        ],
    },
    {
        "slug": "los-yariguies",
        "nombre": "Finca Los Yariguíes",
        "municipio": "Rionegro",
        "lat": Decimal("7.380000"),
        "lng": Decimal("-73.150000"),
        "area": Decimal("5.20"),
        "email": "pedro@rionegro.co",
        "first": "Pedro",
        "last": "Jaimes",
        "lotes": [
            {"nombre": "Lote Alto", "variedad": "trinitario", "plantas": 1100, "edad": 9, "area": Decimal("2.60")},
            {"nombre": "Lote Bajo", "variedad": "trinitario", "plantas": 1050, "edad": 7, "area": Decimal("2.60")},
        ],
    },
    {
        "slug": "aromas-del-rio",
        "nombre": "Finca Aromas del Río",
        "municipio": "Landázuri",
        "lat": Decimal("6.220000"),
        "lng": Decimal("-73.810000"),
        "area": Decimal("2.80"),
        "email": "luz@landazuri.co",
        "first": "Luz",
        "last": "Mendoza",
        "lotes": [
            {"nombre": "Lote Ribera", "variedad": "acriollado", "plantas": 560, "edad": 6, "area": Decimal("1.40")},
            {"nombre": "Lote Madre", "variedad": "acriollado", "plantas": 530, "edad": 8, "area": Decimal("1.40")},
        ],
    },
    {
        "slug": "san-jose",
        "nombre": "Finca San José",
        "municipio": "Cimitarra",
        "lat": Decimal("6.316700"),
        "lng": Decimal("-73.950000"),
        "area": Decimal("6.00"),
        "email": "jorge@cimitarra.co",
        "first": "Jorge",
        "last": "Bautista",
        "lotes": [
            {"nombre": "Lote Llanura", "variedad": "forastero", "plantas": 1300, "edad": 10, "area": Decimal("3.00")},
            {"nombre": "Lote CCN", "variedad": "ccn51", "plantas": 1250, "edad": 6, "area": Decimal("3.00")},
        ],
    },
]


SENSOR_POINTS = 200
TERM_FERM_CURVE = [28, 34, 42, 48, 47, 45, 40]  # day 1..7


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _generate_sensor_history(lote: Lote) -> list[SensorData]:
    now = timezone.now()
    rows: list[SensorData] = []
    for i in range(SENSOR_POINTS):
        ts = now - timedelta(seconds=(SENSOR_POINTS - i) * 36)
        # temp_suelo
        rows.append(
            SensorData(
                lote=lote,
                tipo="temp_suelo",
                valor=round(_clamp(random.gauss(25, 1.5), 22, 28), 2),
                unidad="°C",
            )
        )
        # hum_suelo
        rows.append(
            SensorData(
                lote=lote,
                tipo="hum_suelo",
                valor=round(_clamp(random.gauss(70, 6), 60, 80), 2),
                unidad="%",
            )
        )
        # temp_ferm follows fermentation curve; day index from progress 0..6
        day_idx = min(6, int(i / (SENSOR_POINTS / 7)))
        base_t = TERM_FERM_CURVE[day_idx]
        rows.append(
            SensorData(
                lote=lote,
                tipo="temp_ferm",
                valor=round(_clamp(base_t + random.gauss(0, 1), 28, 52), 2),
                unidad="°C",
            )
        )
        # hum_secado decreases linearly 60 -> 7.5 across series
        frac = i / max(1, SENSOR_POINTS - 1)
        hum_sec = 60 - (60 - 7.5) * frac
        rows.append(
            SensorData(
                lote=lote,
                tipo="hum_secado",
                valor=round(_clamp(hum_sec + random.gauss(0, 1.2), 6, 62), 2),
                unidad="%",
            )
        )
        # ph_suelo
        rows.append(
            SensorData(
                lote=lote,
                tipo="ph_suelo",
                valor=round(_clamp(random.gauss(6.3, 0.2), 5.0, 7.5), 2),
                unidad="pH",
            )
        )
        # Note: SensorData.timestamp uses auto_now_add; historical ts are
        # approximated by insertion order. For hackathon demo this is acceptable.
        _ = ts
    return rows


class Command(BaseCommand):
    help = "Seed CacaoTrace demo data (5 fincas, 2 lotes c/u, 200 puntos IoT)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Vacia las tablas de demo antes de poblar.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        flush = options.get("flush", False)
        if flush:
            self.stdout.write("Limpiando datos previos…")
            SensorData.objects.all().delete()
            Cosecha.objects.all().delete()
            ControlFitosanitario.objects.all().delete()
            Lote.objects.all().delete()
            PerfilExportacion.objects.all().delete()
            Finca.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        # Admin
        if not User.objects.filter(email="admin@cacaotrace.co").exists():
            User.objects.create_superuser(
                email="admin@cacaotrace.co",
                password="admin123",
                first_name="Admin",
                last_name="CacaoTrace",
            )

        for data in FINCAS_SEED:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "first_name": data["first"],
                    "last_name": data["last"],
                    "role": "owner",
                },
            )
            if created:
                user.set_password("cacao123")
                user.save()

            finca, _ = Finca.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "propietario": user,
                    "nombre": data["nombre"],
                    "municipio": data["municipio"],
                    "lat": data["lat"],
                    "lng": data["lng"],
                    "area_total_ha": data["area"],
                    "verificada": True,
                    "descripcion": (
                        f"Finca cacaotera ubicada en {data['municipio']}, "
                        "Santander, registrada en la plataforma CacaoTrace."
                    ),
                },
            )

            # Lotes
            lote_objs: list[Lote] = []
            for ldata in data["lotes"]:
                lote, _ = Lote.objects.update_or_create(
                    finca=finca,
                    nombre=ldata["nombre"],
                    defaults={
                        "variedad": ldata["variedad"],
                        "num_plantas": ldata["plantas"],
                        "edad_años": ldata["edad"],
                        "area_ha": ldata["area"],
                        "lat": data["lat"],
                        "lng": data["lng"],
                        "estado": "activo",
                    },
                )
                lote_objs.append(lote)

            # Sensor history (bulk create then patch timestamps)
            for lote in lote_objs:
                rows = _generate_sensor_history(lote)
                # Bulk create without forced timestamp (auto_now_add sets now)
                SensorData.objects.bulk_create(rows, batch_size=500)

            # Cosechas demo
            for lote in lote_objs:
                Cosecha.objects.create(
                    lote=lote,
                    fecha_cosecha=timezone.now().date() - timedelta(days=45),
                    kg_baba=Decimal("320.00"),
                    kg_seco=Decimal("108.00"),
                    dias_fermentacion=6,
                    temp_prom_fermentacion=Decimal("44.5"),
                    dias_secado=4,
                    calidad="premium",
                )
                ControlFitosanitario.objects.create(
                    lote=lote,
                    fecha=timezone.now().date() - timedelta(days=15),
                    tipo_control="preventivo",
                    plaga_enfermedad="monilia",
                    tratamiento_aplicado=(
                        "Poda sanitaria y remoción de mazorcas enfermas."
                    ),
                    resultado="Sin incidencias",
                )

            # PerfilExportacion
            PerfilExportacion.objects.update_or_create(
                finca=finca,
                defaults={
                    "certificaciones": ["organico", "eudr"],
                    "mercados_destino": ["Belgica", "EEUU"],
                    "capacidad_anual_kg": 2500,
                },
            )
            try:
                generate_qr_for_finca(finca)
            except Exception as e:  # noqa: BLE001
                self.stdout.write(self.style.WARNING(f"QR fallo {finca.slug}: {e}"))

        self.stdout.write(self.style.SUCCESS("✅ Seed CacaoTrace completado"))
        self.stdout.write("Admin:       admin@cacaotrace.co / admin123")
        self.stdout.write("Productores: efrain|maria|pedro|luz|jorge @ cacao123")
        self.stdout.write("Frontend:    http://localhost:5173/finca/la-esperanza")
