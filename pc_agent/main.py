"""Entry: system tray + HTTP/WebSocket server."""

from __future__ import annotations

import ctypes
import socket
import sys
import threading
import webbrowser

import uvicorn

from . import autostart
from .config import get_newline_mode, set_newline_mode
from .token_store import TOKEN_FILE, load_or_create_token

DEFAULT_PORT = 8787
_SINGLE_INSTANCE_MUTEX = "Global\\PhoneToPCVoiceInput"

_NEWLINE_LABELS = {
    "shift_enter": "换行: Shift+Enter（Agent 推荐）",
    "enter": "换行: Enter（记事本等）",
    "space": "换行: 空格",
}


def get_lan_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def _parse_port(argv: list[str]) -> int:
    for arg in argv[1:]:
        if arg.isdigit():
            return int(arg)
    return DEFAULT_PORT


def _acquire_single_instance() -> bool:
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW(None, True, _SINGLE_INSTANCE_MUTEX)
    return kernel32.GetLastError() != 183


def run_tray(host: str, port: int, token: str) -> None:
    from PIL import Image, ImageDraw
    import pystray

    from .server import create_app

    url = f"http://{host}:{port}/?token={token}"
    qr_page_url = f"http://{host}:{port}/qr"
    ws_url = f"ws://{host}:{port}/ws?token={token}"

    app = create_app(token, host, port)

    def serve():
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

    def open_page(_icon, _item):
        webbrowser.open(url)

    def open_qr(_icon, _item):
        webbrowser.open(qr_page_url)

    def copy_url(_icon, _item):
        try:
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(url)
            root.update()
            root.destroy()
        except Exception:
            pass

    def autostart_checked(_item):
        return autostart.is_enabled()

    def toggle_autostart(icon, _item):
        if autostart.is_enabled():
            autostart.uninstall()
        else:
            try:
                autostart.install(port)
            except FileNotFoundError as e:
                print(f"开机自启失败: {e}", flush=True)

    def cycle_newline(icon, _item):
        order = ("shift_enter", "enter", "space")
        cur = get_newline_mode()
        nxt = order[(order.index(cur) + 1) % len(order)]
        set_newline_mode(nxt)
        icon.title = f"手机语音 → PC ({host}:{port}) [{_NEWLINE_LABELS[nxt]}]"

    def newline_label(_item):
        return _NEWLINE_LABELS.get(get_newline_mode(), "换行模式")

    def on_quit(icon, _item):
        icon.stop()

    img = Image.new("RGB", (64, 64), color=(37, 99, 235))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((8, 8, 56, 56), radius=12, fill=(255, 255, 255))
    draw.text((22, 18), "P", fill=(37, 99, 235))

    title = f"手机语音 → PC ({host}:{port})"
    menu = pystray.Menu(
        pystray.MenuItem(f"配对码: {token}（已固定）", None, enabled=False),
        pystray.MenuItem("手机扫码页", open_qr),
        pystray.MenuItem("在浏览器打开", open_page),
        pystray.MenuItem("复制手机链接", copy_url),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            "开机自启",
            toggle_autostart,
            checked=autostart_checked,
        ),
        pystray.MenuItem(newline_label, cycle_newline),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("退出", on_quit),
    )
    icon = pystray.Icon("phone-to-pc", img, title, menu)

    def log(msg: str) -> None:
        print(msg, flush=True)

    nl = get_newline_mode()
    log("")
    log("=" * 50)
    log("  Phone-to-PC Voice Input 已启动")
    log("=" * 50)
    log(f"  手机链接: {url}")
    log(f"  扫码页:   {qr_page_url}")
    log(f"  配对码:   {token}（保存在 {TOKEN_FILE}）")
    log(f"  换行模式: {_NEWLINE_LABELS.get(nl, nl)}")
    log(f"  开机自启: {'已开启' if autostart.is_enabled() else '未开启'}")
    log(f"  监听:     0.0.0.0:{port}")
    log("=" * 50)
    log("")

    server_thread = threading.Thread(target=serve, daemon=True)
    server_thread.start()

    icon.run()


def main() -> None:
    if sys.platform != "win32":
        print("当前 MVP 仅支持 Windows。", file=sys.stderr)
        sys.exit(1)

    port = _parse_port(sys.argv)

    if "--install-autostart" in sys.argv:
        path = autostart.install(port)
        print(f"已设置开机自启: {path}", flush=True)
        return
    if "--uninstall-autostart" in sys.argv:
        autostart.uninstall()
        print("已取消开机自启", flush=True)
        return

    if not _acquire_single_instance():
        print("Phone-to-PC 已在运行（系统托盘），无需重复启动。", file=sys.stderr)
        sys.exit(0)

    host = get_lan_ip()
    token = load_or_create_token()
    run_tray(host, port, token)


if __name__ == "__main__":
    main()
