"""Stitching machine simulator."""
from machines.base import Machine
from models.telemetry import MachineConfig


class Stitching(Machine):
    """Stitching machine for upper assembly in footwear."""

    def __init__(self, name: str, tenant: str, line_id: str):
        config = MachineConfig(
            name=name,
            machine_type="stitching",
            temp_min=25.0,
            temp_max=40.0,
            temp_nominal=32.0,
            vibration_min=1.0,
            vibration_max=4.0,
            vibration_nominal=2.0,
            current_min=5.0,
            current_max=12.0,
            current_nominal=8.0,
            production_rate=6.0,
            defect_rate=8.0,
            running_to_stopped=0.025,
            running_to_maintenance=0.018,
            running_to_error=0.007,
            stopped_to_running=0.28,
            maintenance_to_running=0.08,
            error_to_maintenance=0.45,
        )
        super().__init__(config, tenant, line_id)