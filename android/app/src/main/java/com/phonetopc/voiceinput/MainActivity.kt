package com.phonetopc.voiceinput

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.phonetopc.voiceinput.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity(), WsClient.Callback {

    private lateinit var binding: ActivityMainBinding
    private var config: ServerConfig? = null
    private var ws: WsClient? = null
    private var sending = false
    private var connected = false
    private var statusLocked = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.sendBtn.setOnClickListener { sendManual() }
        binding.clearBtn.setOnClickListener {
            binding.inputText.text?.clear()
            ws?.sendClear()
            binding.inputText.requestFocus()
        }
        binding.settingsBtn.setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }

        ensureConfig()
    }

    override fun onResume() {
        super.onResume()
        config = Prefs.load(this)
        if (config == null) {
            ensureConfig()
            return
        }
        if (ws == null) {
            binding.statusText.text = getString(R.string.status_connecting)
            ws = WsClient(config!!, this).also { it.start() }
        }
    }

    override fun onPause() {
        ws?.stop()
        ws = null
        connected = false
        statusLocked = false
        updateUi()
        super.onPause()
    }

    private fun ensureConfig() {
        config = Prefs.load(this)
        if (config == null) {
            Toast.makeText(this, R.string.setup_required, Toast.LENGTH_LONG).show()
            startActivity(Intent(this, SettingsActivity::class.java))
        }
    }

    private fun sendManual() {
        val text = binding.inputText.text?.toString() ?: ""
        if (text.isBlank()) return
        if (!connected) {
            Toast.makeText(this, R.string.status_disconnected, Toast.LENGTH_SHORT).show()
            return
        }
        sending = true
        statusLocked = false
        updateUi()
        ws?.sendText(text)
    }

    override fun onConnected() {
        connected = true
        sending = false
        statusLocked = false
        binding.statusText.text = getString(R.string.status_connected)
        updateUi()
    }

    override fun onDisconnected(retrying: Boolean) {
        connected = false
        sending = false
        statusLocked = false
        binding.statusText.text =
            if (retrying) "已断开，重连中…" else getString(R.string.status_disconnected)
        updateUi()
    }

    override fun onSendOk(ms: Int) {
        sending = false
        statusLocked = true
        binding.inputText.text?.clear()
        binding.statusText.text = if (ms > 0) "已发送 (${ms}ms)" else "已发送"
        updateUi()
    }

    override fun onSendError(message: String) {
        sending = false
        statusLocked = true
        binding.statusText.text = message
        updateUi()
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun updateUi() {
        binding.statusDot.background = ContextCompat.getDrawable(
            this,
            if (connected) R.drawable.status_dot_connected else R.drawable.status_dot_disconnected,
        )
        if (connected && !sending && !statusLocked) {
            binding.statusText.text = getString(R.string.status_connected)
        }
        binding.sendBtn.isEnabled = connected && !sending
        binding.sendBtn.text =
            if (sending) getString(R.string.status_sending) else getString(R.string.send)
    }
}
