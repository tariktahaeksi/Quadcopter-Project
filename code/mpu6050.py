# Copyright (c) 2025 Tarık Taha Ekşi
# This file is part of the Quadcopter PID Control project.
# Licensed under the MIT License. See the LICENSE file in the project root for full license information.

from machine import I2C
import time

class MPU6050:
    def __init__(self, i2c, addr=0x68, offsets=None):
        self.i2c = i2c
        self.addr = addr
        self.offsets = offsets or {'accel': {'x':0, 'y':0, 'z':0}, 'gyro': {'x':0, 'y':0, 'z':0}}
        self._init_sensor()

    def _init_sensor(self):
        # Wake up MPU6050
        self.i2c.writeto_mem(self.addr, 0x6B, bytes([0]))

    def read_raw_data(self, reg):
        high = self.i2c.readfrom_mem(self.addr, reg, 1)[0]
        low = self.i2c.readfrom_mem(self.addr, reg+1, 1)[0]
        value = (high << 8) | low
        if value > 32767:
            value -= 65536
        return value

    def get_accel(self):
        ax = self.read_raw_data(0x3B) - self.offsets['accel']['x']
        ay = self.read_raw_data(0x3D) - self.offsets['accel']['y']
        az = self.read_raw_data(0x3F) - self.offsets['accel']['z']
        return {'x': ax, 'y': ay, 'z': az}

    def get_gyro(self):
        gx = self.read_raw_data(0x43) - self.offsets['gyro']['x']
        gy = self.read_raw_data(0x45) - self.offsets['gyro']['y']
        gz = self.read_raw_data(0x47) - self.offsets['gyro']['z']
        return {'x': gx, 'y': gy, 'z': gz}
