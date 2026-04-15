"""Cutting machine simulator."""
from machines.base import Machine
from models.telemetry import MachineConfig


class Cutting(Machine):
    """Cutting machine for upper materials in footwear."""

    def __init__(self, name: str, tenant: str, line_id: str):
        config = MachineConfig(
            name=name,
            machine_type="cutting",
            temp_min=20.0,
            temp_max=80.0,
            temp_nominal=45.0,
            vibration_min=2.0,
            vibration_max=8.0,
            vibration_nominal=4.5,
            current_min=8.0,
            current_max=18.0,
            current_nominal=12.0,
            production_rate=8.0,
            defect_rate=5.0,
            running_to_stopped=0.022,
            running_to_maintenance=0.012,
            running_to_error=0.008,
            stopped_to_running=0.25,
            maintenance_to_running=0.09,
            error_to_maintenance=0.4,
        )
        super().__init__(config, tenant, line_id)