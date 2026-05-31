# 手机语音输入 → PC 输入框

在手机上用系统语音输入法（讯飞、搜狗等）写好一整段话，点 **发送到电脑**，文字通过局域网写入 PC 当前焦点输入框（SendInput，不用剪贴板）。

## 环境要求

- Windows 10/11
- Python 3.8+（推荐 3.11+）
- 手机与 PC 连接 **同一 Wi-Fi**（关闭访客网络隔离）

## 安装

```powershell
git clone https://github.com/step963121604/phone-to-pc-voice-input.git
cd phone-to-pc-voice-input
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r pc_agent\requirements.txt
```

## 启动 PC Agent

```powershell
python -m pc_agent.main
```

可选指定端口（默认 `8787`）：

```powershell
python -m pc_agent.main 8787
```

### 开机自启

```powershell
python -m pc_agent.main --install-autostart
```

取消：`python -m pc_agent.main --uninstall-autostart`  
也可在托盘菜单勾选 **开机自启**（使用 `pythonw`，登录后无黑窗口）。

### 换行模式（Agent 输入框）

默认 **Shift+Enter** 换行，避免 Enter 被当成「发送」。  
托盘菜单可切换：`Shift+Enter` / `Enter` / `空格`。  
配置保存在 `%USERPROFILE%\.phone-to-pc-voice-input\config.json`。

启动后：

1. 系统托盘会出现图标
2. 控制台会打印 **手机访问链接** 和 **6 位配对码**
3. 托盘菜单可「在浏览器打开」「复制链接」

## 手机使用

### 首次（约 30 秒）

1. PC 托盘 → **手机扫码页**，用手机相机/微信扫二维码打开  
   或复制托盘里的链接到手机浏览器
2. 在页面底部展开 **「添加到主屏幕」**，按提示保存桌面图标  
3. 配对码保存在 PC 的 `%USERPROFILE%\.phone-to-pc-voice-input\token.txt`，**重启 Agent 不变**，书签可长期使用

### 日常使用

1. 在 PC 上先点开要输入的位置
2. 点手机主屏幕 **「发PC」** 图标（**不要每次开 Chrome**，轻应用更省内存）
3. 系统语音听写 → **发送到电脑 ▶**
4. 发送成功后自动清空；切到别的 App 时会自动断开连接省电

> 若家里路由器给 PC 换了 IP，需重新扫码或打开新链接一次。

### 关于手机内存

- **主屏幕图标** = 单独小窗口（PWA），比打开整个 Chrome 轻得多
- 页面已缓存静态资源，二次打开更快
- 若仍嫌重，只能做原生 App（体积更大但可更精简）；当前方案在「能调用系统语音键盘」前提下已较轻

## 协议摘要

- 手机 → PC：`{ "t": "send", "text": "..." }`
- PC → 手机成功：`{ "t": "ok", "ms": 45 }`（随后手机清空 textarea）
- PC → 手机失败：`{ "t": "err", "code": "inject_failed", "msg": "..." }`（保留原文）

## Android 原生 App（更省内存）

不用每次开浏览器，见 [android/README.md](./android/README.md)。

- Android Studio 打开 `android/` 目录编译，或安装 `app-debug.apk`
- 首次在 App 里填写 PC 的 IP、端口、配对码

## 目录结构

```
phone-to-pc-voice-input/
├── android/               # Android 原生客户端
├── pc_agent/
│   ├── main.py          # 托盘 + 启动服务
│   ├── server.py        # HTTP / WebSocket
│   ├── injector.py      # SendInput Unicode
│   └── requirements.txt
├── web/
│   ├── index.html
│   └── app.js
├── PROJECT_PROMPT.md    # 完整规格
└── README.md
```

## 常见问题

| 现象 | 处理 |
|------|------|
| 手机打不开网页 | 检查同一 Wi-Fi；Windows 防火墙放行 Python 专用网络 |
| 显示未连接 | 链接必须带 `?token=`，用托盘复制的完整 URL |
| 字没进目标框 | 发送前在 PC 上先点一下目标输入框 |
| 注入失败 | 先在记事本测试；部分 Electron 应用可能不兼容 |

## 开发说明

完整需求见 [PROJECT_PROMPT.md](./PROJECT_PROMPT.md)。

## 许可

[MIT](./LICENSE)
