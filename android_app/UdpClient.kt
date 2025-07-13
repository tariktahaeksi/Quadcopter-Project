// Copyright (c) 2025 Tarık Taha Ekşi
// This file is part of the Quadcopter PID Control project.
// Licensed under the MIT License. See the LICENSE file in the project root for full license information.

package com.example.pipico

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress

class UdpClient(
    private val targetIp: String,
    private val targetPort: Int
) {
    suspend fun send(message: String) {
        withContext(Dispatchers.IO) {
            try {
                val socket = DatagramSocket()
                val address = InetAddress.getByName(targetIp)
                val buffer = message.toByteArray()
                val packet = DatagramPacket(buffer, buffer.size, address, targetPort)
                socket.send(packet)
                socket.close()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
}
