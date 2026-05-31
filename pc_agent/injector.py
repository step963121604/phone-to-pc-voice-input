"""Windows SendInput Unicode text injection (no clipboard)."""

from __future__ import annotations

import ctypes
import sys
import time
from ctypes import wintypes

if sys.platform != "win32":
    raise OSError("injector 仅支持 Windows")

from .config import get_newline_mode

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

INPUT_KEYBOARD = 1
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_KEYUP = 0x0002
VK_RETURN = 0x0D
VK_SHIFT = 0x10

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

_MAX_INPUTS_PER_CALL = 120


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION),
    ]


def _make_unicode_input(char: str, key_up: bool) -> INPUT:
    inp = INPUT(type=INPUT_KEYBOARD)
    inp.union.ki = KEYBDINPUT(
        wVk=0,
        wScan=ord(char),
        dwFlags=KEYEVENTF_UNICODE | (KEYEVENTF_KEYUP if key_up else 0),
        time=0,
        dwExtraInfo=ULONG_PTR(0),
    )
    return inp


def _make_vk_input(vk: int, key_up: bool) -> INPUT:
    inp = INPUT(type=INPUT_KEYBOARD)
    inp.union.ki = KEYBDINPUT(
        wVk=vk,
        wScan=0,
        dwFlags=KEYEVENTF_KEYUP if key_up else 0,
        time=0,
        dwExtraInfo=ULONG_PTR(0),
    )
    return inp


def _append_newline(batch: list[INPUT], mode: str) -> None:
    if mode == "space":
        batch.append(_make_unicode_input(" ", False))
        batch.append(_make_unicode_input(" ", True))
        return
    if mode == "shift_enter":
        batch.append(_make_vk_input(VK_SHIFT, False))
        batch.append(_make_vk_input(VK_RETURN, False))
        batch.append(_make_vk_input(VK_RETURN, True))
        batch.append(_make_vk_input(VK_SHIFT, True))
        return
    # enter
    batch.append(_make_vk_input(VK_RETURN, False))
    batch.append(_make_vk_input(VK_RETURN, True))


def _flush_inputs(batch: list[INPUT]) -> None:
    if not batch:
        return
    n = len(batch)
    arr = (INPUT * n)(*batch)
    sent = user32.SendInput(n, ctypes.byref(arr), ctypes.sizeof(INPUT))
    if sent != n:
        err = kernel32.GetLastError()
        raise OSError(f"SendInput 仅成功 {sent}/{n} 个事件 (GetLastError={err})")


def _iter_input_events(text: str):
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "\r":
            if i + 1 < len(text) and text[i + 1] == "\n":
                i += 1
            yield ("newline",)
            i += 1
            continue
        if ch == "\n":
            yield ("newline",)
            i += 1
            continue
        yield ("char", ch)
        i += 1


def inject_text(text: str, newline_mode: str | None = None) -> None:
    """向当前焦点控件注入整段文本。"""
    if not text:
        return

    mode = newline_mode or get_newline_mode()
    batch: list[INPUT] = []
    for kind, *rest in _iter_input_events(text):
        if kind == "newline":
            _append_newline(batch, mode)
        else:
            ch = rest[0]
            batch.append(_make_unicode_input(ch, False))
            batch.append(_make_unicode_input(ch, True))

        if len(batch) >= _MAX_INPUTS_PER_CALL:
            _flush_inputs(batch)
            batch = []

    _flush_inputs(batch)


def inject_text_timed(text: str) -> int:
    start = time.perf_counter()
    inject_text(text)
    return int((time.perf_counter() - start) * 1000)
