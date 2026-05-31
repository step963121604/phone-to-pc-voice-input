(function () {
  const params = new URLSearchParams(location.search);
  const token = params.get("token");

  /** 正文稳定多久后才自动发送（语音智能改写会持续删改，需更长等待） */
  const AUTO_SEND_MS = 2000;
  /** 检测到频繁删改时，延长等待 */
  const AUTO_SEND_BUSY_MS = 3500;
  const BUSY_INPUT_WINDOW_MS = 2000;
  const BUSY_INPUT_THRESHOLD = 4;
  const SEND_DEBOUNCE_MS = 800;
  const SEND_COOLDOWN_MS = 3000;

  const statusDot = document.getElementById("status-dot");
  const statusText = document.getElementById("status-text");
  const textarea = document.getElementById("text");
  const sendBtn = document.getElementById("send-btn");
  const clearBtn = document.getElementById("clear-btn");
  const autoSendCheckbox = document.getElementById("auto-send");

  let ws = null;
  let reconnectTimer = null;
  let sending = false;
  let composing = false;
  let autoSendTimer = null;
  let lastSendAt = 0;
  let sendCooldownUntil = 0;
  let lastSentText = "";
  let lastInputAt = 0;
  let recentInputCount = 0;
  let recentInputResetTimer = null;

  const autoSendKey = "phone-to-pc-auto-send";
  // 默认关闭：系统语音「智能改写」会反复删加，短防抖易重复发送
  autoSendCheckbox.checked = localStorage.getItem(autoSendKey) === "1";

  function autoSendEnabled() {
    return autoSendCheckbox.checked;
  }

  function setStatus(connected, text) {
    statusDot.classList.toggle("connected", connected);
    statusText.textContent = text;
    sendBtn.disabled = !connected || sending;
  }

  function cancelAutoSend() {
    if (autoSendTimer) {
      clearTimeout(autoSendTimer);
      autoSendTimer = null;
    }
  }

  function noteInputActivity() {
    const now = Date.now();
    lastInputAt = now;
    recentInputCount += 1;
    if (recentInputResetTimer) clearTimeout(recentInputResetTimer);
    recentInputResetTimer = setTimeout(() => {
      recentInputCount = 0;
    }, BUSY_INPUT_WINDOW_MS);
  }

  function autoSendDelay() {
    if (recentInputCount >= BUSY_INPUT_THRESHOLD) return AUTO_SEND_BUSY_MS;
    return AUTO_SEND_MS;
  }

  function wsUrl() {
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    const q = token ? `?token=${encodeURIComponent(token)}` : "";
    return `${proto}//${location.host}/ws${q}`;
  }

  function disconnectWs() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    if (ws) {
      ws.onclose = null;
      ws.close();
      ws = null;
    }
  }

  function scheduleReconnect() {
    if (reconnectTimer || document.hidden) return;
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null;
      connect();
    }, 1500);
  }

  function connect() {
    if (!token) {
      setStatus(false, "缺少 token，请用 PC 托盘里的完整链接打开");
      return;
    }
    if (document.hidden) return;
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    disconnectWs();
    setStatus(false, "连接中…");
    ws = new WebSocket(wsUrl());

    ws.onopen = () => {
      const lite =
        window.matchMedia("(display-mode: standalone)").matches ||
        window.navigator.standalone;
      setStatus(true, lite ? "已连接（轻应用）" : "已连接");
    };

    ws.onclose = () => {
      ws = null;
      if (document.hidden) {
        setStatus(false, "后台已断开（省电）");
        return;
      }
      setStatus(false, "已断开，重连中…");
      scheduleReconnect();
    };

    ws.onerror = () => setStatus(false, "连接错误");

    ws.onmessage = (ev) => {
      let msg;
      try {
        msg = JSON.parse(ev.data);
      } catch {
        return;
      }

      if (msg.t === "ok") {
        cancelAutoSend();
        lastSentText = textarea.value;
        textarea.value = "";
        sending = false;
        sendCooldownUntil = Date.now() + SEND_COOLDOWN_MS;
        setStatus(true, `已发送${msg.ms != null ? ` (${msg.ms}ms)` : ""}`);
        return;
      }

      if (msg.t === "err") {
        sending = false;
        setStatus(true, msg.msg || "发送失败");
      }
    };
  }

  function doSend(source) {
    const now = Date.now();
    if (now - lastSendAt < SEND_DEBOUNCE_MS) return;
    if (now < sendCooldownUntil) return;
    if (sending || composing) return;

    const text = textarea.value;
    if (!text.trim()) return;
    if (text === lastSentText) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      setStatus(false, "未连接");
      return;
    }

    cancelAutoSend();
    lastSendAt = now;
    lastSentText = text;
    sending = true;
    sendBtn.disabled = true;
    setStatus(true, source === "auto" ? "自动发送中…" : "发送中…");
    ws.send(JSON.stringify({ t: "send", text }));
  }

  function scheduleAutoSend() {
    if (!autoSendEnabled() || sending || composing) return;
    if (Date.now() < sendCooldownUntil) return;

    const text = textarea.value;
    if (!text.trim()) {
      cancelAutoSend();
      return;
    }

    const snapshot = text;
    const scheduledAt = Date.now();
    const delay = autoSendDelay();

    cancelAutoSend();
    autoSendTimer = setTimeout(() => {
      autoSendTimer = null;
      if (composing || sending) return;
      if (Date.now() < sendCooldownUntil) return;
      if (textarea.value !== snapshot) return;
      if (Date.now() - lastInputAt < delay - 80) return;
      if (Date.now() - scheduledAt < delay - 80) return;
      doSend("auto");
    }, delay);
  }

  sendBtn.addEventListener("click", () => doSend("manual"));

  clearBtn.addEventListener("click", () => {
    cancelAutoSend();
    lastSentText = "";
    textarea.value = "";
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ t: "clr" }));
    }
    textarea.focus();
  });

  textarea.addEventListener("compositionstart", () => {
    composing = true;
    cancelAutoSend();
  });

  textarea.addEventListener("compositionend", () => {
    composing = false;
    noteInputActivity();
    scheduleAutoSend();
  });

  textarea.addEventListener("input", () => {
    noteInputActivity();
    if (composing) {
      cancelAutoSend();
      return;
    }
    scheduleAutoSend();
  });

  autoSendCheckbox.addEventListener("change", () => {
    localStorage.setItem(autoSendKey, autoSendCheckbox.checked ? "1" : "0");
    if (!autoSendCheckbox.checked) cancelAutoSend();
    else scheduleAutoSend();
  });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      cancelAutoSend();
      disconnectWs();
      setStatus(false, "后台已断开（省电）");
    } else {
      connect();
    }
  });

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch(() => {});
  }

  connect();
})();
