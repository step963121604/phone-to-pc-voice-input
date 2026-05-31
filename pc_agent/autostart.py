"""Windows 开机自启：启动文件夹 + pythonw（无控制台）。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

STARTUP_NAME = "PhoneToPC-VoiceInput.bat"


def startup_folder() -> Path:
    return Path(os.environ["APPDATA"]) / r"Microsoft\Windows\Start Menu\Programs\Startup"


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_pythonw() -> Path:
    root = project_root()
    candidates = [
        root / ".venv" / "Scripts" / "pythonw.exe",
        Path(sys.executable).with_name("pythonw.exe"),
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise FileNotFoundError("未找到 pythonw.exe，请先创建 venv 并安装依赖")


def is_enabled() -> bool:
    return (startup_folder() / STARTUP_NAME).is_file()


def install(port: int = 8787) -> Path:
    pythonw = resolve_pythonw()
    root = project_root()
    bat = startup_folder() / STARTUP_NAME
    bat.write_text(
        f'@echo off\r\n'
        f'cd /d "{root}"\r\n'
        f'"{pythonw}" -m pc_agent.main {port}\r\n',
        encoding="utf-8",
    )
    return bat


def uninstall() -> bool:
    bat = startup_folder() / STARTUP_NAME
    if bat.is_file():
        bat.unlink()
        return True
    return False
