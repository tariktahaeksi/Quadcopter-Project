# Quadcopter-Project
IMU-supported, Android app-controlled PID-based quadcopter project.
# 🛸 Quadcopter PID Control with Raspberry Pi Pico W

This project involves the development of a custom-built quadcopter system controlled by a Raspberry Pi Pico W, utilizing a complementary filter and PID algorithms to achieve stable flight. The drone is controlled via a custom-developed Android application using UDP communication over Wi-Fi.

## 🚀 Project Highlights

- Real-time stabilization using a complementary filter (MPU6050)
- PID-based roll and pitch control
- UDP-based communication with a custom Android app
- ESC and BLDC motor control via PWM signals
- Full system built on MicroPython (Pico W) and Kotlin (Android)

## 📂 Project Structure

```
drone-pid-control/
├── code/               # MicroPython source code for Raspberry Pi Pico W
│   ├── main.py
│   ├── mpu6050.py
│   └── udp_server.py
│
├── android_app/        # Android Studio Kotlin code
│   ├── MainActivity.kt
│   └── JoystickView.kt
│
├── media/              # Images or demo GIFs
│   ├── demo.gif
│   ├── system_diagram.png
│   ├── android_interface.png
│   └── motor_connection_diagram.png
│
├── README.md
└── LICENSE
```

![System Diagram](media/system_diagram.png)

## 📱 Android App Interface

The Android application features dual joystick control and a real-time connectivity indicator. Commands are sent over UDP, and the drone responds with acknowledgment signals.

![Android Interface](media/android_interface.png)

## 🧠 Control Algorithm

The stabilization is achieved using a complementary filter (80% gyro, 20% accelerometer) and a PID loop tuned through trial and error. The quadcopter is tested in a home environment with motors anchored for tuning.

## 🎥 Demo

![Drone Demo](media/demo.gif)

> Or add a link to a video:  
> [▶️ Watch the demo video](https://your-video-link.com)

## 🧰 Hardware Wiring

The image below shows how the ESCs, motors, power source, and Pico W are connected:

![Motor Wiring](media/motor_connection_diagram.png)

## 🛠 Technologies Used

- Raspberry Pi Pico W (MicroPython)
- MPU6050 IMU sensor
- Android Studio (Kotlin)
- UDP Sockets
- ESCs + Brushless DC Motors

## 📜 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
