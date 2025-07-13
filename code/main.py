# Copyright (c) 2025 Tarık Taha Ekşi
# This file is part of the Quadcopter PID Control project.
# Licensed under the MIT License. See the LICENSE file in the project root for full license information.

from machine import I2C, Pin
import time
import ujson
from mpu6050 import MPU6050
from pid import PID
from esc import ESC
from udp_server import UDPServer
import math

def safe_throttle(value, min_throttle=0.1, max_throttle=1.0):
    return max(min_throttle, min(value, max_throttle))

def constrain(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def get_acc_angles(accel):
    ax = accel['x'] / 16384.0
    ay = accel['y'] / 16384.0
    az = accel['z'] / 16384.0
    roll = math.degrees(math.atan2(ay, az))
    pitch = math.degrees(math.atan2(-ax, (ay**2 + az**2)**0.5))
    return roll, pitch

def calibrate_gyro(mpu, samples=100):
    total_x = total_y = 0
    for _ in range(samples):
        gyro = mpu.get_gyro()
        total_x += gyro['x']
        total_y += gyro['y']
        time.sleep(0.01)
    offset_x = total_x / samples
    offset_y = total_y / samples
    return offset_x, offset_y


i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)
mpu = MPU6050(i2c)
gyro_offset_x, gyro_offset_y = calibrate_gyro(mpu)


pitch_pid = PID(0.015, 0.0008, 0.010, min_output_limit=-0.15, max_output_limit=0.15)
roll_pid  = PID(0.015, 0.0008, 0.010, min_output_limit=-0.15, max_output_limit=0.15)
yaw_pid   = PID(0.5, 0.001, 0.01, min_output_limit=-0.10, max_output_limit=0.10)


motor1 = ESC(8)
motor2 = ESC(6)
motor3 = ESC(4)
motor4 = ESC(12)
motors = [motor1, motor2, motor3, motor4]

server = UDPServer()

last_time = time.ticks_ms()

alpha = 0.90
lpf_smoothing = 0.80
first_sample = True
roll = pitch = roll_angle = pitch_angle = 0.0
g_threshold = 2.0 * 16384

is_running = False
throttle_base = 0.0
pitch_cmd = 0.0
roll_cmd  = 0.0
yaw_cmd   = 0.0

thr_min = 0.10
thr_down = 0.270
thr_hover = 0.330    
thr_up = 0.60
thr_up_max = 0.80

while True:
    now = time.ticks_ms()
    dt = time.ticks_diff(now, last_time) / 1000.0
    last_time = now

    msg, addr = server.receive()
    if msg:
        try:
            data = ujson.loads(msg)
            cmd = data.get("cmd")

            if cmd == "start":
                is_running = True
                throttle_base = thr_min
                time.sleep(0.5)

            elif cmd == "stop":
                is_running = False
                for m in motors:
                    m.stop()
                continue

            elif cmd == "emergency":
                for m in motors:
                    m.stop()
                time.sleep(0.5)
                import machine
                machine.reset()
                break

            elif cmd == "move":
                pitch_cmd = data.get("forward_back", 0.0)
                roll_cmd  = data.get("left_right", 0.0)

            elif cmd == "up":
                if throttle_base < thr_down:
                    throttle_base = thr_down
                elif throttle_base < thr_hover:
                    throttle_base = thr_hover
                elif throttle_base < thr_up:
                    throttle_base = thr_up
                elif throttle_base < thr_up_max:
                    throttle_base = thr_up_max


            elif cmd == "down":
                if throttle_base == thr_up_max:
                    throttle_base = thr_up
                elif throttle_base == thr_up:
                    throttle_base = thr_hover
                elif throttle_base == thr_hover:
                    throttle_base = thr_down
                elif throttle_base == thr_down:
                    throttle_base = thr_min

        except:
            pass

    accel = mpu.get_accel()
    gyro  = mpu.get_gyro()
    
    if abs(accel['x']) > g_threshold or abs(accel['y']) > g_threshold or abs(accel['z']) > g_threshold:
        pass
    else:
        acc_roll, acc_pitch = get_acc_angles(accel)
        gyro_x = (gyro['x'] - gyro_offset_x) / 131.0
        gyro_y = (gyro['y'] - gyro_offset_y) / 131.0

        if first_sample:
            roll = acc_roll
            pitch = acc_pitch
            roll_angle = roll
            pitch_angle = pitch
            roll_offset = roll_angle
            pitch_offset = pitch_angle
            first_sample = False
        else:
            roll = alpha * (roll + gyro_x * dt) + (1 - alpha) * acc_roll
            pitch = alpha * (pitch + gyro_y * dt) + (1 - alpha) * acc_pitch

            roll_angle = lpf_smoothing * roll_angle + (1 - lpf_smoothing) * roll
            pitch_angle = lpf_smoothing * pitch_angle + (1 - lpf_smoothing) * pitch


    if is_running:
        
        pitch_pid.setpoint = pitch_cmd
        roll_pid.setpoint  = roll_cmd
        yaw_pid.setpoint   = yaw_cmd

        # Calculate offset values and find the true deviation
        pitch_error = pitch_angle - pitch_offset
        roll_error  = roll_angle - roll_offset

        # A 5-degree dead zone (also to prevent minimal vibration of the sensor)
        if pitch_error > 0:
            pitch_error = max(0, pitch_error - 5)
        elif pitch_error < 0:
            pitch_error = min(0, pitch_error + 5)

        if roll_error > 0:
            roll_error = max(0, roll_error - 5)
        elif roll_error < 0:
            roll_error = min(0, roll_error + 5)

        # The part we sent to PID
        pitch_output = pitch_pid.compute(pitch_error) * 0.45
        roll_output  = roll_pid.compute(roll_error)  * 0.45
        yaw_output   = 0.0

        adj1 = constrain(pitch_output + roll_output - yaw_output, -0.25, 0.25)
        adj2 = constrain(pitch_output - roll_output + yaw_output, -0.25, 0.25)
        adj3 = constrain(-pitch_output - roll_output - yaw_output, -0.25, 0.25)
        adj4 = constrain(-pitch_output + roll_output + yaw_output, -0.25, 0.25)

        m1 = safe_throttle(throttle_base + adj1)
        m2 = safe_throttle(throttle_base + adj2)
        m3 = safe_throttle(throttle_base + adj3)
        m4 = safe_throttle(throttle_base + adj4)

        motor1.set_throttle(m1)
        motor2.set_throttle(m2)
        motor3.set_throttle(m3)
        motor4.set_throttle(m4)
        
        # Printing data that I use frequently during testing
        print(f"[Angles] Pitch={pitch_error:.2f}°, Roll={roll_error:.2f}°")
        print(f"[PID] Pitch_out={pitch_output:.3f}, Roll_out={roll_output:.3f}, Yaw_out={yaw_output:.3f}")
        print(f"[MPU] Accel: x={accel['x']}, y={accel['y']}, z={accel['z']} | Gyro: x={gyro['x']}, y={gyro['y']}, z={gyro['z']}")
        print(f"[Motors] m1={m1:.3f}, m2={m2:.3f}, m3={m3:.3f}, m4={m4:.3f} | throttle_base={throttle_base:.3f}")       

    else:
        for m in motors:
            m.stop()
    
    time.sleep(0.01)
