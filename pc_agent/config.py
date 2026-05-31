"""用户配置：换行注入方式等。"""

from __future__ import annotations

import json
from pathlib import Path

from .token_store import TOKEN_DIR

CONFIG_FILE = TOKEN_DIR / "config.json"

# shift_enter: Shift+Enter 换行（Cursor/多数 Agent 聊天框 Enter=发送）
# enter: 普通 Enter 换行（记事本等）
# space: 换行变成空格
NEWLINE_MODES = ("shift_enter", "enter", "space")
DEFAULT_NEWLINE_MODE = "shift_enter"


def _default_config() -> dict:
    return {"newline_mode": DEFAULT_NEWLINE_MODE}


def load_config() -> dict:
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.is_file():
        cfg = _default_config()
        save_config(cfg)
        return cfg
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        if data.get("newline_mode") not in NEWLINE_MODES:
            data["newline_mode"] = DEFAULT_NEWLINE_MODE
        return data
    except (json.JSONDecodeError, OSError):
        cfg = _default_config()
        save_config(cfg)
        return cfg


def save_config(data: dict) -> None:
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get_newline_mode() -> str:
    return load_config().get("newline_mode", DEFAULT_NEWLINE_MODE)


def set_newline_mode(mode: str) -> None:
    if mode not in NEWLINE_MODES:
        raise ValueError(f"newline_mode 必须是 {NEWLINE_MODES}")
    cfg = load_config()
    cfg["newline_mode"] = mode
    save_config(cfg)
