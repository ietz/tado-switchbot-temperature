import datetime as dt
import math
from typing import Optional


class EwmaSmoother:
    def __init__(self, halftime: dt.timedelta):
        self.halftime = halftime
        self.value: Optional[float] = None
        self.last_observation_time: Optional[dt.datetime] = None

    def observe(self, value: float, time: Optional[dt.datetime] = None):
        if time is None:
            time = dt.datetime.now()

        if self.value is None or self.halftime.total_seconds() == 0:
            self.value = value
            self.last_observation_time = time
        else:
            elapsed_halftimes = (time - self.last_observation_time) / self.halftime
            previous_value_factor = math.pow(0.5, elapsed_halftimes)
            self.value = previous_value_factor * self.value + (1 - previous_value_factor) * value

    def zero(self):
        self.value = 0
