package com.phonetopc.voiceinput

import android.content.Context

data class ServerConfig(val host: String, val port: Int, val token: String) {
    fun isValid(): Boolean =
        host.isNotBlank() && port in 1..65535 && token.length == 6 && token.all { it.isDigit() }
}

object Prefs {
    private const val NAME = "phone_to_pc"

    fun load(context: Context): ServerConfig? {
        val p = context.getSharedPreferences(NAME, Context.MODE_PRIVATE)
        val host = p.getString("host", null) ?: return null
        val port = p.getInt("port", 0)
        val token = p.getString("token", null) ?: return null
        val cfg = ServerConfig(host.trim(), port, token.trim())
        return cfg.takeIf { it.isValid() }
    }

    fun save(context: Context, config: ServerConfig) {
        context.getSharedPreferences(NAME, Context.MODE_PRIVATE).edit()
            .putString("host", config.host)
            .putInt("port", config.port)
            .putString("token", config.token)
            .apply()
    }
}
