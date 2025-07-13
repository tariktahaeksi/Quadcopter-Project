# Copyright (c) 2025 Tarık Taha Ekşi
# This file is part of the Quadcopter PID Control project.
# Licensed under the MIT License. See the LICENSE file in the project root for full license information.

import time
class PID:
    def __init__(self, kp, ki, kd, setpoint=0, min_output_limit=None, max_output_limit=None):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.min_output_limit = min_output_limit
        self.max_output_limit = max_output_limit

        self._last_error = 0
        self._integral = 0
        self._last_time = time.ticks_ms()

    def compute(self, measurement):
        now = time.ticks_ms()
        dt = time.ticks_diff(now, self._last_time) / 1000  # convert to seconds

        error = self.setpoint - measurement
        self._integral += error * dt
        derivative = (error - self._last_error) / dt if dt > 0 else 0

        output = self.kp * error + self.ki * self._integral + self.kd * derivative

        if self.min_output_limit is not None:
            output = max(self.min_output_limit, output)
        if self.max_output_limit is not None:
            output = min(self.max_output_limit, output)

        self._last_error = error
        self._last_time = now

        return output

    def reset(self):
        self._last_error = 0
        self._integral = 0
        self._last_time = time.ticks_ms()
