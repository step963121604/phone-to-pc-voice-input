"""持久化配对码，手机主屏幕书签长期有效。"""

from __future__ import annotations

import random
from pathlib import Path

TOKEN_DIR = Path.home() / ".phone-to-pc-voice-input"
TOKEN_FILE = TOKEN_DIR / "token.txt"


def load_or_create_token() -> str:
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    if TOKEN_FILE.is_file():
        raw = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if len(raw) == 6 and raw.isdigit():
            return raw
    token = f"{random.randint(0, 999999):06d}"
    TOKEN_FILE.write_text(token, encoding="utf-8")
    return token
