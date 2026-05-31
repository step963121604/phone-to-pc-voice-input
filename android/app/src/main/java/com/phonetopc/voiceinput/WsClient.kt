package com.phonetopc.voiceinput

import android.os.Handler
import android.os.Looper
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class WsClient(
    private val config: ServerConfig,
    private val callback: Callback,
) {
    interface Callback {
        fun onConnected()
        fun onDisconnected(retrying: Boolean)
        fun onSendOk(ms: Int)
        fun onSendError(message: String)
    }

    private val main = Handler(Looper.getMainLooper())
    private val http = OkHttpClient.Builder()
        .pingInterval(30, TimeUnit.SECONDS)
        .build()

    private var socket: WebSocket? = null
    private var shouldRun = false
    private var reconnectRunnable: Runnable? = null

    fun start() {
        shouldRun = true
        connect()
    }

    fun stop() {
        shouldRun = false
        cancelReconnect()
        socket?.close(1000, "pause")
        socket = null
    }

    fun sendText(text: String) {
        val ws = socket ?: return
        val payload = JSONObject().put("t", "send").put("text", text).toString()
        ws.send(payload)
    }

    fun sendClear() {
        socket?.send(JSONObject().put("t", "clr").toString())
    }

    private fun connect() {
        if (!shouldRun) return
        cancelReconnect()
        socket?.close(1000, "reconnect")

        val url = "ws://${config.host}:${config.port}/ws?token=${config.token}"
        val request = Request.Builder().url(url).build()
        socket = http.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                main.post { callback.onConnected() }
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                main.post { handleMessage(text) }
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                main.post { onSocketGone() }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                main.post { onSocketGone() }
            }
        })
    }

    private fun handleMessage(raw: String) {
        try {
            val msg = JSONObject(raw)
            when (msg.optString("t")) {
                "ok" -> callback.onSendOk(msg.optInt("ms", 0))
                "err" -> callback.onSendError(msg.optString("msg", "发送失败"))
            }
        } catch (_: Exception) {
            /* ignore */
        }
    }

    private fun onSocketGone() {
        socket = null
        if (!shouldRun) {
            callback.onDisconnected(retrying = false)
            return
        }
        callback.onDisconnected(retrying = true)
        scheduleReconnect()
    }

    private fun scheduleReconnect() {
        if (!shouldRun || reconnectRunnable != null) return
        reconnectRunnable = Runnable {
            reconnectRunnable = null
            connect()
        }.also { main.postDelayed(it, 1500) }
    }

    private fun cancelReconnect() {
        reconnectRunnable?.let { main.removeCallbacks(it) }
        reconnectRunnable = null
    }
}
