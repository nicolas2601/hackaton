"""Base machine class with Markov chain state transitions."""
import random
import time
from models.telemetry import MachineConfig, MachineTelemetry, MachineState


class Machine:
    """Base machine with state machine and telemetry generation."""

    def __init__(self, config: MachineConfig, tenant: str, line_id: str):
        self.config = config
        self.tenant = tenant
        self.line_id = line_id
        self.state = MachineState.RUNNING
        self.production_count = 0
        self.defects = 0
        self.uptime = 0
        self._last_transition_check = 0.0
        self._production_fraction = 0.0
        self._defect_fraction = 0.0

    @property
    def machine_id(self) -> str:
        return self.config.name

    def transition_state(self, delta_seconds: float):
        """Apply Markov chain state transitions based on elapsed time."""
        self._last_transition_check += delta_seconds
        if self._last_transition_check < 10.0:
            return

        self._last_transition_check = 0.0
        rand = random.random()

        if self.state == MachineState.RUNNING:
            if rand < self.config.running_to_error:
                self.state = MachineState.ERROR
            elif rand < self.config.running_to_error + self.config.running_to_maintenance:
                self.state = MachineState.MAINTENANCE
            elif rand < (self.config.running_to_error + self.config.running_to_maintenance +
                        self.config.running_to_stopped):
                self.state = MachineState.STOPPED
        elif self.state == MachineState.STOPPED:
            if rand < self.config.stopped_to_running:
                self.state = MachineState.RUNNING
        elif self.state == MachineState.MAINTENANCE:
            if rand < self.config.maintenance_to_running:
                self.state = MachineState.RUNNING
        elif self.state == MachineState.ERROR:
            if rand < self.config.error_to_maintenance:
                self.state = MachineState.MAINTENANCE

    def generate_telemetry(self) -> MachineTelemetry:
        """Generate realistic telemetry based on current state."""
        now = int(time.time())

        if self.state == MachineState.RUNNING:
            temp = self._normal_sample(
                self.config.temp_nominal,
                (self.config.temp_max - self.config.temp_min) / 4
            )
            vibration = max(0, self._normal_sample(
                self.config.vibration_nominal,
                self.config.vibration_max / 6
            ))
            current = self._normal_sample(
                self.config.current_nominal,
                (self.config.current_max - self.config.current_min) / 4
            )
            self.uptime += 1
        elif self.state == MachineState.STOPPED:
            temp = self._normal_sample(25.0, 2.0)
            vibration = 0.0
            current = 0.0
        elif self.state == MachineState.MAINTENANCE:
            temp = self._normal_sample(35.0, 5.0)
            vibration = self._normal_sample(1.0, 0.5)
            current = self._normal_sample(self.config.current_nominal * 0.3, 0.5)
        else:  # ERROR
            temp = self._normal_sample(self.config.temp_max - 5, 3.0)
            vibration = self._normal_sample(self.config.vibration_max * 0.8, 2.0)
            current = self._normal_sample(self.config.current_max * 0.9, 1.0)

        return MachineTelemetry(
            tenant=self.tenant,
            line=self.line_id,
            machine=self.machine_id,
            timestamp=now,
            state=self.state,
            production_count=int(self.production_count),
            defects=int(self.defects),
            temperature=round(temp, 1),
            vibration=round(vibration, 2),
            current=round(current, 2),
            uptime=self.uptime,
        )

    def update(self, delta_seconds: float, sim_time_accelerated: float):
        """Update machine state based on simulated time."""
        self.transition_state(delta_seconds)

        if self.state == MachineState.RUNNING:
            new_pairs = self.config.production_rate * (sim_time_accelerated / 60.0)
            self._production_fraction += new_pairs
            if self._production_fraction >= 1.0:
                whole = int(self._production_fraction)
                self.production_count += whole
                self._production_fraction -= whole

                expected_defects = (whole / 1000.0) * self.config.defect_rate
                self._defect_fraction += expected_defects
                if self._defect_fraction >= 1.0:
                    self.defects += int(self._defect_fraction)
                    self._defect_fraction -= int(self._defect_fraction)

    @staticmethod
    def _normal_sample(mean: float, std: float) -> float:
        """Generate a sample from normal distribution."""
        return random.gauss(mean, std)