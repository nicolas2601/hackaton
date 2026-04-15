"""Injection molding machine simulator."""
from machines.base import Machine
from models.telemetry import MachineConfig


class InjectionMolding(Machine):
    """Injection molding machine for sole manufacturing."""

    def __init__(self, name: str, tenant: str, line_id: str):
        config = MachineConfig(
            name=name,
            machine_type="injection",
            temp_min=180.0,
            temp_max=220.0,
            temp_nominal=200.0,
            vibration_min=0.5,
            vibration_max=3.0,
            vibration_nominal=1.5,
            current_min=15.0,
            current_max=25.0,
            current_nominal=20.0,
            production_rate=12.0,
            defect_rate=3.0,
            running_to_stopped=0.02,
            running_to_maintenance=0.01,
            running_to_error=0.005,
            stopped_to_running=0.3,
            maintenance_to_running=0.1,
            error_to_maintenance=0.5,
        )
        super().__init__(config, tenant, line_id)