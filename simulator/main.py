"""Main entry point for the IoT simulator."""
import asyncio
import logging
import signal
import os
import sys
from dotenv import load_dotenv

from mqtt_client import MQTTPublisher
from time_accelerator import TimeAccelerator, SpeedMode
from machines.injection import InjectionMolding
from machines.cutting import Cutting
from machines.stitching import Stitching
from machines.base import Machine

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class Simulator:
    """Main simulator orchestrator."""

    def __init__(self):
        broker = os.getenv("MQTT_BROKER", "localhost")
        port = int(os.getenv("MQTT_PORT", "1883"))
        self.tenant = os.getenv("TENANT", "trebol")

        self.publisher = MQTTPublisher(broker, port)
        self.time_accel = TimeAccelerator()
        self.machines: list[Machine] = []
        self._running = False
        self._update_task: asyncio.Task | None = None

        self._setup_machines()

    def _setup_machines(self):
        """Initialize 6 machines across 3 production lines."""
        for line_num in range(1, 4):
            line_id = f"line{line_num}"
            self.machines.append(
                InjectionMolding(f"injection-{line_num}", self.tenant, line_id)
            )
            self.machines.append(
                Cutting(f"cutting-{line_num}", self.tenant, line_id)
            )

        self.machines[3] = Stitching("stitching-2", self.tenant, "line2")
        logger.info(f"Setup {len(self.machines)} machines across 3 lines")

    async def start(self):
        """Start the simulator."""
        logger.info("Starting Manufactura Santander 4.0 IoT Simulator...")
        await self.publisher.connect()
        self._running = True
        self._update_task = asyncio.create_task(self._update_loop())
        logger.info(f"Simulator running at {self.time_accel.mode.value}")

    async def stop(self):
        """Gracefully stop the simulator."""
        logger.info("Stopping simulator...")
        self._running = False

        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass

        await self.publisher.disconnect()
        logger.info("Simulator stopped")

    async def _update_loop(self):
        """Main update loop with time acceleration."""
        real_interval = 1.0
        sim_per_real = {
            SpeedMode.REAL_TIME: 1.0,
            SpeedMode.FAST: 60.0,
            SpeedMode.VERY_FAST: 120.0,
        }
        heartbeat_counter = 0

        while self._running:
            try:
                sim_delta = sim_per_real[self.time_accel.mode]

                for machine in self.machines:
                    machine.update(real_interval, sim_delta)
                    telemetry = machine.generate_telemetry()
                    await self.publisher.publish_telemetry(telemetry)

                heartbeat_counter += real_interval
                if heartbeat_counter >= 5.0:
                    heartbeat_counter = 0
                    for machine in self.machines:
                        await self.publisher.publish_heartbeat(
                            self.tenant, machine.line_id, machine.machine_id
                        )

                await asyncio.sleep(real_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(1.0)

    def set_speed(self, mode: SpeedMode):
        """Change simulation speed."""
        self.time_accel.set_mode(mode)
        logger.info(f"Speed set to {mode.value} ({self.time_accel.label})")


async def main():
    simulator = Simulator()

    loop = asyncio.get_running_loop()

    def signal_handler():
        asyncio.create_task(simulator.stop())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    try:
        await simulator.start()

        print("\n" + "=" * 60)
        print("  Manufactura Santander 4.0 - IoT Simulator")
        print("=" * 60)
        print("  Speed modes: 1=1x | 2=60x | 3=120x | q=quit")
        print("  Default: 60x (8h shift = 8 minutes)")
        print("-" * 60)

        while simulator._running:
            try:
                import select
                if select.select([sys.stdin], [], [], 0.0)[0]:
                    char = sys.stdin.read(1)
                    if char == "1":
                        simulator.set_speed(SpeedMode.REAL_TIME)
                    elif char == "2":
                        simulator.set_speed(SpeedMode.FAST)
                    elif char == "3":
                        simulator.set_speed(SpeedMode.VERY_FAST)
                    elif char == "q":
                        await simulator.stop()
                        break
            except Exception:
                pass

            await asyncio.sleep(0.1)

    except Exception as e:
        logger.error(f"Simulator error: {e}")
        await simulator.stop()


if __name__ == "__main__":
    asyncio.run(main())