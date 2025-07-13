# Copyright (c) 2025 Tarık Taha Ekşi
# This file is part of the Quadcopter PID Control project.
# Licensed under the MIT License. See the LICENSE file in the project root for full license information.

from machine import PWM, Pin

class ESC:
    def __init__(self, pin_num, min_us=1000, max_us=2000, freq=50):
        self.pin = Pin(pin_num)
        self.pwm = PWM(self.pin)
        self.pwm.freq(freq)
        self.min_duty = self._us_to_duty(min_us)
        self.max_duty = self._us_to_duty(max_us)
        self.set_throttle(0) 

    def _us_to_duty(self, us):
        # 65535 duty_u16 = 20ms (50Hz) → 1ms = ~3276, 2ms = ~6553
        return int(us * 65535 // 20000)

    def set_us(self, us):
        duty = self._us_to_duty(us)
        self.pwm.duty_u16(duty)

    def set_throttle(self, value):
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
        duty_range = self.max_duty - self.min_duty
        duty = self.min_duty + int(value * duty_range)
        self.pwm.duty_u16(duty)

    def stop(self):
        self.set_throttle(0)
