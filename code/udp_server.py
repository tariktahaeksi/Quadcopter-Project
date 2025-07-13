# Copyright (c) 2025 Tarık Taha Ekşi
# This file is part of the Quadcopter PID Control project.
# Licensed under the MIT License. See the LICENSE file in the project root for full license information.

import network
import socket
import time

class UDPServer:
    def __init__(self, ssid='PicoCopter', password='12345678', port=5005):
        self.port = port
        self.sock = None
        self._start_access_point(ssid, password)
        self._start_udp_server()

    def _start_access_point(self, ssid, password):
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=ssid, password=password)
        while not ap.active():
            time.sleep(0.1)
        self.ip_address = ap.ifconfig()[0]

    def _start_udp_server(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.01)
        self.sock.bind(("0.0.0.0", self.port))

    def receive(self, bufsize=1024):
        try:
            data, addr = self.sock.recvfrom(bufsize)
            decoded = data.decode()
            return decoded, addr
        except:
            return None, None
