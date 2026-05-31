# 发PC — Android 原生客户端

极简 Android App：调用系统语音键盘听写，一键发到 PC 输入框。协议与网页版相同，**不打开浏览器**，内存占用更小。

## 功能

- 多行输入框 + 系统语音听写
- WebSocket 连接 PC Agent（`send` / `ok` / `err`）
- 发送成功后自动清空
- 切到后台自动断开（`onPause`），回前台再连
- 设置页保存 PC IP、端口、6 位配对码

## 环境

- Android Studio Hedgehog (2023.1+) 或更新
- JDK 17
- Android SDK 34

## 编译安装

1. 用 Android Studio 打开本目录：`phone-to-pc-voice-input/android`
2. 等待 Gradle 同步完成
3. 手机开启 **开发者选项 → USB 调试**，用数据线连接电脑
4. 菜单 **Run → Run 'app'**，或命令行：

```powershell
cd android
.\gradlew.bat assembleDebug
```

生成的 APK：

- `android\app\build\outputs\apk\debug\app-debug.apk`
- 或项目根目录：`发PC-debug.apk`（编译后复制）

拷到手机安装即可（允许「未知来源」）。

命令行编译需 **JDK 17**（设置 `JAVA_HOME`）：

```powershell
cd android
$env:JAVA_HOME = "你的JDK17路径"
.\gradlew.bat assembleDebug
```

## 首次配置

1. PC 上运行 `python -u -m pc_agent.main`
2. 记下托盘里的 **IP**、**端口**（默认 8787）、**配对码**
3. 手机 App → 右上角设置 → 填入并保存
4. 回到主界面，等显示 **已连接**

## 日常使用

1. PC 先点开目标输入框
2. 打开 **发PC** App → 听写 → **发送到电脑**
3. 用完直接划掉，不占 Chrome 内存

## 与网页版对比

| | 网页/PWA | 本 App |
|--|---------|--------|
| 内存 | 浏览器/WebView 较重 | 单 Activity，更轻 |
| 语音键盘 | ✅ | ✅ |
| 安装 | 无需 | 需装 APK |
