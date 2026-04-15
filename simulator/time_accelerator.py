"""Time acceleration controller for demo compression."""
from dataclasses import dataclass
from enum import Enum


class SpeedMode(str, Enum):
    REAL_TIME = "1x"
    FAST = "60x"
    VERY_FAST = "120x"


@dataclass
class TimeAccelerator:
    """Controls simulation time compression.

    Allows compressing 8-hour shifts into minutes for live demos.
    """
    mode: SpeedMode = SpeedMode.FAST

    @property
    def label(self) -> str:
        labels = {
            SpeedMode.REAL_TIME: "Real-time (1 second = 1 second)",
            SpeedMode.FAST: "Fast mode (1 second = 1 minute, 8h = 8 min)",
            SpeedMode.VERY_FAST: "Very fast (1 second = 2 minutes, 8h = 4 min)",
        }
        return labels[self.mode]

    def get_real_interval(self, sim_seconds: float) -> float:
        """Given simulated seconds, return real wait time."""
        factor = {
            SpeedMode.REAL_TIME: 1.0,
            SpeedMode.FAST: 1.0 / 60.0,
            SpeedMode.VERY_FAST: 1.0 / 120.0,
        }[self.mode]
        return sim_seconds * factor

    def set_mode(self, mode: SpeedMode):
        self.mode = mode

    def toggle(self):
        """Cycle through speed modes."""
        modes = list(SpeedMode)
        idx = modes.index(self.mode)
        self.mode = modes[(idx + 1) % len(modes)]