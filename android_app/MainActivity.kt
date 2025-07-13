// Copyright (c) 2025 Tarık Taha Ekşi
// This file is part of the Quadcopter PID Control project.
// Licensed under the MIT License. See the LICENSE file in the project root for full license information.

package com.example.pipico

import android.content.res.ColorStateList
import android.os.Bundle
import android.view.View
import android.widget.ImageButton
import androidx.appcompat.app.AppCompatActivity
import com.example.pipico.JoystickView
import kotlinx.coroutines.*
import org.json.JSONObject
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import android.widget.Toast


class MainActivity : AppCompatActivity() {

    private lateinit var udpIndicator: View

    private val droneIp = "192.168.4.1"
    private val dronePort = 5005
    private var isPowerOn = false

    private var verticalValue = 0f
    private var horizontalValue = 0f

    private lateinit var job: Job

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val joystickVertical = findViewById<JoystickView>(R.id.joystickVertical)
        val joystickHorizontal = findViewById<JoystickView>(R.id.joystickHorizontal)

        val btnUp = findViewById<ImageButton>(R.id.btnUp)
        val btnDown = findViewById<ImageButton>(R.id.btnDown)
        val btnPower = findViewById<ImageButton>(R.id.btnPower)
        val btnEmergency = findViewById<ImageButton>(R.id.btnEmergency)

        joystickVertical.listener = { _, y ->
            verticalValue = y * 0.1f  // Even when we maximize it, it should be multiplied by 0.1 and sent.
        }

        joystickHorizontal.listener = { x, _ ->
            horizontalValue = x * 0.1f
        }

        btnUp.setOnClickListener {
            val json = JSONObject()
            json.put("cmd", "up")
            sendUdpAsync(json.toString())
        }

        btnDown.setOnClickListener {
            val json = JSONObject()
            json.put("cmd", "down")
            sendUdpAsync(json.toString())
        }

        btnPower.setOnClickListener {
            isPowerOn = !isPowerOn
            val json = JSONObject()
            json.put("cmd", if (isPowerOn) "start" else "stop")
            sendUdpAsync(json.toString())

            val newColor = if (isPowerOn) 0xFF4CAF50.toInt() else 0xFFB71C1C.toInt()
            btnPower.backgroundTintList = ColorStateList.valueOf(newColor)
        }

        btnEmergency.setOnClickListener {
            val json = JSONObject()
            json.put("cmd", "emergency")
            sendUdpAsync(json.toString())

            runOnUiThread {
                Toast.makeText(this, "Emergency Stop activated!", Toast.LENGTH_LONG).show()
            }
        }

        // continuous joystick data transmission
        job = CoroutineScope(Dispatchers.IO).launch {
            while (isActive) {
                val json = JSONObject()
                json.put("cmd", "move")
                json.put("forward_back", verticalValue)
                json.put("left_right", horizontalValue)
                sendUdp(json.toString())
                delay(100L)
            }
        }

    }

    override fun onDestroy() {
        super.onDestroy()
        job.cancel()
    }

    private fun sendUdpAsync(message: String) {
        CoroutineScope(Dispatchers.IO).launch {
            sendUdp(message)
        }
    }

    private fun sendUdp(message: String) {
        try {
            val socket = DatagramSocket()
            val address = InetAddress.getByName(droneIp)
            val buffer = message.toByteArray()
            val packet = DatagramPacket(buffer, buffer.size, address, dronePort)
            socket.send(packet)
            socket.close()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

}
