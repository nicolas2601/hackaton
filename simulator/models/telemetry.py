"""Telemetry data models."""
from pydantic import BaseModel
from enum import Enum


class MachineState(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class MachineTelemetry(BaseModel):
    """Telemetry payload for a machine."""
    tenant: str
    line: str
    machine: str
    timestamp: int  # Unix timestamp
    state: MachineState
    production_count: int = 0
    defects: int = 0
    temperature: float = 0.0  # °C
    vibration: float = 0.0  # mm/s
    current: float = 0.0  # A
    uptime: int = 0  # seconds


class MachineConfig(BaseModel):
    """Configuration for a simulated machine."""
    name: str
    machine_type: str
    temp_min: float
    temp_max: float
    temp_nominal: float
    vibration_min: float
    vibration_max: float
    vibration_nominal: float
    current_min: float
    current_max: float
    current_nominal: float
    production_rate: float
    defect_rate: float
    running_to_stopped: float = 0.02
    running_to_maintenance: float = 0.01
    running_to_error: float = 0.005
    stopped_to_running: float = 0.3
    maintenance_to_running: float = 0.1
    error_to_maintenance: float = 0.5