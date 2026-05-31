package com.phonetopc.voiceinput

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.phonetopc.voiceinput.databinding.ActivitySettingsBinding

class SettingsActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySettingsBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySettingsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        Prefs.load(this)?.let { cfg ->
            binding.hostInput.setText(cfg.host)
            binding.portInput.setText(cfg.port.toString())
            binding.tokenInput.setText(cfg.token)
        } ?: run {
            binding.portInput.setText("8787")
        }

        binding.saveBtn.setOnClickListener { save() }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }

    private fun save() {
        val host = binding.hostInput.text?.toString()?.trim().orEmpty()
        val port = binding.portInput.text?.toString()?.toIntOrNull() ?: 0
        val token = binding.tokenInput.text?.toString()?.trim().orEmpty()
        val cfg = ServerConfig(host, port, token)
        if (!cfg.isValid()) {
            Toast.makeText(this, "请填写正确的 IP、端口和 6 位配对码", Toast.LENGTH_SHORT).show()
            return
        }
        Prefs.save(this, cfg)
        Toast.makeText(this, "已保存", Toast.LENGTH_SHORT).show()
        finish()
    }
}
