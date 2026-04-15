"""CacaoTrace MQTT simulator — 5 fincas x lotes x sensores.

Publishes realistic cacao telemetry per lote to Mosquitto:
    cacao/finca/{finca_id}/lote/{lote_id}/{tipo}
Payload: {"valor": <float>, "unidad": "<str>", "ts": "<iso>"}
"""
import asyncio
import json
import os
import random
from datetime import datetime

import aiomqtt

BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "mosquitto")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
BROKER_USER = os.getenv("MQTT_BROKER_USERNAME", "")
BROKER_PASS = os.getenv("MQTT_BROKER_PASSWORD", "")
SPEED = float(os.getenv("SIM_SPEED", "1"))
INTERVAL = 5 / SPEED

# Fincas -> [(lote_id, variedad, en_fermentacion)]
# IDs must match BE-1 seed.
FINCAS = [
    (1, [(1, "trinitario", True), (2, "criollo", False)]),
    (2, [(3, "ccn51", True), (4, "ics95", False)]),
    (3, [(5, "trinitario", False)]),
    (4, [(6, "acriollado", True)]),
    (5, [(7, "forastero", False), (8, "ccn51", True)]),
]


class Sim:
    """State machine per lote. Advances fermentation/drying day as ticks flow."""

    def __init__(self, finca_id: int, lote_id: int, variedad: str, en_ferm: bool):
        self.finca_id = finca_id
        self.lote_id = lote_id
        self.variedad = variedad
        self.en_ferm = en_ferm
        self.ferm_day = 0
        self.dry_day = 0
        self.tick = 0

    def advance(self):
        self.tick += 1
        # Advance a simulated day every N ticks (scaled by SIM_SPEED).
        if self.tick % max(1, int(300 / SPEED)) == 0:
            if self.ferm_day < 7:
                self.ferm_day += 1
            elif self.dry_day < 5:
                self.dry_day += 1

    def readings(self):
        """Yield (tipo, valor, unidad) tuples for this tick."""
        yield ("temp_suelo", round(random.gauss(25, 1.5), 2), "C")
        yield ("hum_suelo", round(random.gauss(70, 6), 2), "%")
        yield ("ph_suelo", round(random.gauss(6.3, 0.2), 2), "")
        if self.en_ferm:
            # Fermentation curve: ramps 28->48C over 7 days.
            curve_ferm = [28, 34, 42, 48, 47, 45, 40, 35]
            yield (
                "temp_ferm",
                round(curve_ferm[min(self.ferm_day, 7)] + random.gauss(0, 1.0), 2),
                "C",
            )
            # Drying curve: decays 60%->7.5% over 5 days.
            curve_dry = [60, 45, 30, 18, 10, 7.5]
            yield (
                "hum_secado",
                round(curve_dry[min(self.dry_day, 5)] + random.gauss(0, 0.5), 2),
                "%",
            )


async def publish_loop(client: aiomqtt.Client, sim: Sim):
    base = f"cacao/finca/{sim.finca_id}/lote/{sim.lote_id}"
    while True:
        sim.advance()
        for tipo, valor, unidad in sim.readings():
            payload = json.dumps(
                {"valor": valor, "unidad": unidad, "ts": datetime.utcnow().isoformat()}
            )
            await client.publish(f"{base}/{tipo}", payload, qos=1)
        await asyncio.sleep(INTERVAL)


async def main():
    params = {"hostname": BROKER_HOST, "port": BROKER_PORT}
    if BROKER_USER:
        params["username"] = BROKER_USER
        params["password"] = BROKER_PASS
    async with aiomqtt.Client(**params) as client:
        sims = [
            Sim(fid, lid, var, ferm)
            for fid, lotes in FINCAS
            for (lid, var, ferm) in lotes
        ]
        print(
            f"[sim] {len(sims)} sims started @ {BROKER_HOST}:{BROKER_PORT} speed={SPEED}x"
        )
        await asyncio.gather(*(publish_loop(client, s) for s in sims))


if __name__ == "__main__":
    asyncio.run(main())
