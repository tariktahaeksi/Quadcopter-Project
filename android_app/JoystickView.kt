// Copyright (c) 2025 Tarık Taha Ekşi
// This file is part of the Quadcopter PID Control project.
// Licensed under the MIT License. See the LICENSE file in the project root for full license information.

package com.example.pipico

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.View
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.min
import kotlin.math.sin
import kotlin.math.sqrt

class JoystickView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private var centerX = 0f
    private var centerY = 0f
    private var baseRadius = 0f
    private var hatRadius = 0f
    private var touchX = 0f
    private var touchY = 0f
    private var isTouching = false

    private val basePaint = Paint().apply {
        color = Color.GRAY
        style = Paint.Style.FILL
    }

    private val hatPaint = Paint().apply {
        color = Color.BLACK
        style = Paint.Style.FILL
    }

    var listener: ((xPercent: Float, yPercent: Float) -> Unit)? = null

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        centerX = (w / 2).toFloat()
        centerY = (h / 2).toFloat()
        baseRadius = min(w, h) / 3f
        hatRadius = min(w, h) / 5f
    }

    override fun onDraw(canvas: Canvas) {
        canvas.drawCircle(centerX, centerY, baseRadius, basePaint)

        val drawX = if (isTouching) touchX else centerX
        val drawY = if (isTouching) touchY else centerY
        canvas.drawCircle(drawX, drawY, hatRadius, hatPaint)
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN, MotionEvent.ACTION_MOVE -> {
                val dx = event.x - centerX
                val dy = event.y - centerY
                val distance = sqrt(dx * dx + dy * dy)
                val angle = atan2(dy, dx)

                if (distance < baseRadius) {
                    touchX = event.x
                    touchY = event.y
                } else {
                    touchX = centerX + baseRadius * cos(angle)
                    touchY = centerY + baseRadius * sin(angle)
                }

                val xPercent = (touchX - centerX) / baseRadius
                val yPercent = (touchY - centerY) / baseRadius
                listener?.invoke(xPercent, yPercent)

                isTouching = true
                invalidate()
            }

            MotionEvent.ACTION_UP -> {
                touchX = centerX
                touchY = centerY
                isTouching = false
                listener?.invoke(0f, 0f)
                invalidate()
            }
        }
        return true
    }
}
