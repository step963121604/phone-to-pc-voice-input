# 项目提示词：手机语音输入 → PC 输入框整段转发

> 将本文件全文复制到新 Cursor 对话 / 新仓库，作为 AI 辅助开发的完整需求与架构说明。

---

## 一、背景与问题

用户在 Windows PC 上尝试多种语音转文字工具（Whisper、VoiceFlow 等），发现瓶颈不在 ASR 引擎，而在 **PC 麦克风收音质量差**。

用户手机上的系统级语音输入法（讯飞、搜狗、Gboard 等）体验远好于 PC 端本地识别。

**目标**：做一个轻量方案，让用户在 **手机浏览器** 里用系统语音输入法完成 **一整段话** 的编辑与校对，确认后 **点击发送**，整段文字出现在 PC 当前焦点输入框中。

**明确不做**：
- 不在 PC 端再跑 ASR（Whisper / 云端转写）
- 不要求手机安装 App（纯网页即可）
- 不依赖第三方剪贴板同步工具（KDE Connect、Phone Link 等需手动粘贴）
- 不做「边说边出字」的实时增量同步（无必要）

---

## 二、核心体验要求（最高优先级）

1. **整段编辑**：用户在手机 textarea 内用系统语音输入法说完、改好，再主动发送
2. **一键发送**：点「发送到电脑」后，整段内容写入 PC **当前焦点控件的光标处**，无需 Ctrl+V；**PC 确认成功后自动清空手机 textarea**，便于写下一段
3. **零 App 安装**：手机仅打开浏览器访问 PC 托管的网页
4. **仅局域网 Wi-Fi**：PC 与手机同一 Wi-Fi，不走云中转
5. **不用剪贴板中转**：PC 端通过 SendInput Unicode 注入，不备份/改写系统剪贴板

---

## 三、系统架构

```
┌─────────────────┐     WebSocket      ┌─────────────────┐     SendInput     ┌─────────────────┐
│  手机浏览器      │  ────────────────►  │  PC Agent       │  ───────────────►  │  任意焦点输入框  │
│  textarea       │   整段 send 消息    │  托盘 + WS 服务  │   Unicode 注入     │  Word/IDE/浏览器 │
│  + 系统语音键盘  │   （用户点击发送）   │  + 静态网页托管  │   （一次性）       │  微信等          │
└─────────────────┘                     └─────────────────┘                    └─────────────────┘
```

### 三层职责

| 层 | 职责 | 说明 |
|----|------|------|
| **采集** | 获取最终文本 | 复用手机系统语音输入法，网页 textarea 接收上屏文字；用户可在发送前随意修改 |
| **传输** | 按需可靠推送 | 局域网 WebSocket 长连接；仅在用户点击发送时传输整段 `text` |
| **注入** | 写入 PC 焦点 | 收到 `send` 后一次性 SendInput Unicode 注入；`\n` 映射为 Enter |

---

## 四、技术选型（已定）

### PC 端 Agent

| 阶段 | 技术栈 | 理由 |
|------|--------|------|
| **MVP** | Python 3.11+ · asyncio · websockets · FastAPI/aiohttp · pynput/ctypes SendInput · pystray | 最快闭环验证注入 |
| **产品化** | C# .NET 8 托盘 · SendInput · 开机自启 | 注入更稳、资源占用低 |

职责：
- 托管手机端静态网页（HTTP）
- WebSocket 服务（默认端口如 `8787`）
- 系统托盘显示局域网 IP + 6 位配对码
- 收到 `send` 后对整段文本注入当前焦点窗口

### 手机端

| 选型 | 说明 |
|------|------|
| **纯 HTML + 原生 JS** | 单页，无 React/Vue 框架，体积极小 |
| **一个大型 textarea** | 用户点击后调起系统键盘，使用系统语音输入；发送前可全文编辑 |
| **WebSocket 长连接** | 页面加载时连接 PC，用于发送与状态反馈 |
| **整段发送** | 点击「发送到电脑」发送全文；可选 **600ms 输入防抖** 后自动发送（默认开启，可关） |
| **发送防抖** | 400ms 内不重复提交，避免连点双发 |

不做：原生 App、PWA 安装、Web Speech API（不如系统输入法）、实时增量 delta 流式推送

### 传输层

| 选型 | 说明 |
|------|------|
| **WebSocket `ws://`** | 长连接，发送时 LAN RTT 2–15ms；禁止为听写做 HTTP 轮询 |
| **QR / 手动 IP** | 首次访问 `http://{PC_IP}:8787?token=xxxxxx` |
| **可选后期** | mDNS 服务发现（`_voicepipe._tcp`）、Tailscale（外网扩展，非 MVP） |

### 注入策略（Windows）

| 场景 | 方法 |
|------|------|
| 整段发送（默认） | `SendInput` + `KEYEVENTF_UNICODE`，从光标处一次性打入全文 |
| 换行（默认） | `\n` → **Shift+Enter**（Cursor/Agent 里 Enter 常等于发送） |
| 换行（可选） | 托盘切换为 Enter 或空格，见 `config.json` |
| 中文 | 必须 Unicode 注入，禁止 ASCII 键盘映射 |
| 极长文本（可选后期） | 按字符分批 SendInput，仍不走剪贴板 |

---

## 五、通信协议（极简 JSON）

### 连接

```
ws://192.168.x.x:8787/ws?token=482913
```

### 手机 → PC

```json
{ "t": "send", "text": "今天天气不错，适合出门。" }
{ "t": "clr" }
```

| 字段 | 含义 |
|------|------|
| `t: "send"` | 用户确认发送的整段文本 |
| `text` | textarea 全文（可为空字符串，PC 可忽略或清空注入） |
| `t: "clr"` | 仅清空手机端会话状态（可选，由手机 UI「清空」触发，不要求 PC 删已注入内容） |

### PC → 手机

```json
{ "t": "ok", "ms": 45 }
{ "t": "err", "code": "inject_failed", "msg": "注入失败" }
```

| 字段 | 含义 |
|------|------|
| `t: "ok"` | 注入成功，`ms` 为 PC 侧处理耗时（可选） |
| `t: "err"` | 注入失败，手机 UI 提示用户 |

---

## 六、手机端核心逻辑（伪代码）

```javascript
let ws;

function connect(token) {
  ws = new WebSocket(`ws://${location.hostname}:8787/ws?token=${token}`);
  ws.onopen = () => setStatus('已连接');
  ws.onclose = () => setTimeout(() => connect(token), 1000);
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.t === 'ok') {
      textarea.value = '';
      setStatus(`已发送 (${msg.ms}ms)`);
    }
    if (msg.t === 'err') setStatus(msg.msg || '发送失败');
  };
}

sendBtn.addEventListener('click', () => {
  const text = textarea.value;
  if (!text.trim()) return;
  if (ws.readyState !== WebSocket.OPEN) {
    setStatus('未连接');
    return;
  }
  ws.send(JSON.stringify({ t: 'send', text }));
});

clearBtn.addEventListener('click', () => {
  textarea.value = '';
  ws?.send(JSON.stringify({ t: 'clr' }));
});
```

**原则**：
- 听写、改错在 textarea 完成；可点发送，或 **停说约 600ms 后防抖自动发送**（勾选框可关）
- 发送防抖 400ms + 发送中 `disabled`，避免连点双发
- **收到 PC `ok` 后自动清空 textarea**；失败（`err`）则保留原文便于修改重发

---

## 七、延迟预算（验收标准）

| 环节 | 目标 |
|------|------|
| Wi-Fi RTT | 2–10 ms |
| WebSocket 解析 | < 5 ms |
| PC 整段注入（常见段落 ≤500 字） | 20–150 ms |
| **点击发送到 PC 可见** | **< 300 ms**（局域网常态） |

若 > 1s，排查：guest WiFi 隔离、Agent 阻塞主线程、目标窗口无焦点、注入 API 失败未上报。

**说明**：不做流式「边说边出字」，故不设 50ms 防抖与 100ms 增量端到端指标。

---

## 八、手机网页 UI（最小可用）

```
┌─────────────────────────┐
│  ● 已连接               │
├─────────────────────────┤
│                         │
│   [ 大 textarea ]        │  ← 系统语音键盘，整段编辑
│                         │
├─────────────────────────┤
│  清空  │  发送到电脑 ▶    │  ← 主操作
└─────────────────────────┘
```

---

## 九、目录结构建议

```
phone-to-pc-voice-input/
├── pc_agent/
│   ├── main.py              # 入口：托盘 + HTTP + WebSocket
│   ├── injector.py          # SendInput Unicode 整段注入
│   ├── server.py            # FastAPI/aiohttp 路由
│   └── requirements.txt
├── web/
│   ├── index.html           # 手机端单页
│   └── app.js               # WebSocket + 发送按钮
└── README.md                # 使用说明：同 WiFi、扫 QR、编辑后发送
```

---

## 十、风险与对策

| 风险 | 对策 |
|------|------|
| 路由器 AP / guest 隔离 | 手机与 PC 同 SSID，关闭 AP 隔离 |
| PC 焦点丢失，字进错窗口 | 发送前提示「请先在 PC 点目标输入框」；后期 PC `status` 回传窗口标题 |
| 微信 / Electron 控件注入异常 | 优先 SendInput Unicode；失败返回 `err`，提示换 Notepad 等验证 |
| 浏览器后台 WebSocket 断开 | 发送前检查连接；断线自动重连；可选提示切回前台 |
| 中文乱码 / 缺字 | SendInput 必须 KEYEVENTF_UNICODE |
| 重复点击发送 | 发送中禁用按钮；或对同一连接做简单去重 |

---

## 十一、明确排除（第一版不做）

- ❌ 手机原生 App（Android/iOS）
- ❌ PC 端 ASR（Whisper、faster-whisper）
- ❌ 云中转 / 账号体系
- ❌ Electron 全栈
- ❌ 蓝牙 HID 模拟键盘
- ❌ 音频流传输
- ❌ 实时增量 delta / 50ms 防抖自动推送
- ❌ 剪贴板中转（含 Ctrl+V fallback）

---

## 十二、开发任务清单（按顺序）

1. [ ] PC Agent：FastAPI 托管 `web/index.html`，WebSocket `/ws` 带 token 校验
2. [ ] PC Agent：SendInput Unicode 整段注入，实测 Notepad / 浏览器 / VS Code
3. [ ] 手机网页：textarea +「发送到电脑」按钮 + 连接状态
4. [ ] 托盘：显示 IP、端口、配对码、连接状态
5. [ ] 发送反馈：PC 回传 `ok`/`err` 与 `ms`，手机 UI 展示结果
6. [ ] 边界：换行、空文本、焦点丢失提示、发送防重复；`ok` 后清空 textarea、`err` 保留原文
7. [ ] README：同 WiFi 连接步骤与使用流程（编辑 → 发送）
8. [ ] （可选）QR 码生成、开机自启、mDNS

---

## 十三、给 AI 的执行指令（可直接粘贴）

```
请按照 PROJECT_PROMPT.md 的规格，实现一个「手机浏览器语音输入 → PC 输入框整段转发」MVP。

硬性要求：
1. 手机端纯 HTML/JS 网页，不装 App；用户在 textarea 用系统语音输入法整段编辑，点击「发送到电脑」才通过 WebSocket 发送全文；收到 PC `ok` 后自动清空 textarea
2. PC 端 Python 托盘 Agent：托管网页 + WebSocket + SendInput Unicode 一次性注入当前焦点
3. 仅局域网 Wi-Fi，WebSocket 长连接；点击发送到 PC 可见目标 < 300ms
4. 不做 PC 端 ASR，不走云端，不用剪贴板中转，不做实时增量推送

请先实现可运行 MVP（Notepad 和浏览器输入框整段注入成功），再处理换行、错误反馈与边界情况。
代码放 phone-to-pc-voice-input/ 目录，提供 requirements.txt 和 README 使用说明。
```

---

## 十四、参考讨论摘要

- Whisper（openai/whisper）：~10 万 ⭐，ASR 引擎，非桌面听写 App
- VoiceFlow（infiniV/VoiceFlow）：~370 ⭐，基于 Whisper 的 Windows 听写 App
- 用户痛点是 PC 麦克风，不是 ASR 工具选型
- KDE Connect / Phone Link 剪贴板方案需手动粘贴，且非焦点注入
- 相近开源（AirMic、BrainJack Service）：多为手机端 ASR + 按键注入；本项目差异为 **系统输入法出字 + 网页整段发送**
- 最优路径：手机系统输入法出字 → 用户确认发送 → 局域网 WS 整段 → PC SendInput 注入
