"""Foreground-only ordinary Windows input, with bounded holds and release cleanup.

This is an explicit supervised diagnostic boundary, not a strategy interpreter.
F8 or Escape latches a stop; switching focus or resizing also stops the run.
"""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import json
import math
import os
import re
import time
from dataclasses import asdict
from pathlib import Path

from . import phase1


class StopRun(RuntimeError):
    """Stop the current input path; only a separate fresh session may recover."""
    def __init__(self,message,*,kind='failure'):
        super().__init__(message)
        self.kind=kind


def is_active_computer_use_window_title(title):
    normalized=' '.join(title.casefold().split())
    return any(marker in normalized for marker in (
        'chatgpt is using your computer',
        'chatgpt is using your screen',
    ))


def active_computer_use_controller_pids():
    """Return active Computer Use controller PIDs, including newer overlay sessions."""
    if os.name!='nt':
        return ()

    class ProcessEntry32W(ctypes.Structure):
        _fields_=[('dwSize',wintypes.DWORD),('cntUsage',wintypes.DWORD),
                  ('th32ProcessID',wintypes.DWORD),('th32DefaultHeapID',ctypes.c_size_t),
                  ('th32ModuleID',wintypes.DWORD),('cntThreads',wintypes.DWORD),
                  ('th32ParentProcessID',wintypes.DWORD),('pcPriClassBase',wintypes.LONG),
                  ('dwFlags',wintypes.DWORD),('szExeFile',wintypes.WCHAR*260)]

    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes=[wintypes.DWORD,wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype=wintypes.HANDLE
    kernel.Process32FirstW.argtypes=[wintypes.HANDLE,ctypes.POINTER(ProcessEntry32W)]
    kernel.Process32FirstW.restype=wintypes.BOOL
    kernel.Process32NextW.argtypes=[wintypes.HANDLE,ctypes.POINTER(ProcessEntry32W)]
    kernel.Process32NextW.restype=wintypes.BOOL
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    kernel.CloseHandle.restype=wintypes.BOOL

    snapshot=kernel.CreateToolhelp32Snapshot(0x00000002,0)  # TH32CS_SNAPPROCESS
    if snapshot==ctypes.c_void_p(-1).value:
        raise StopRun('Cannot verify that the computer-use controller is closed.',kind='setup')
    pids=[]
    try:
        entry=ProcessEntry32W()
        entry.dwSize=ctypes.sizeof(entry)
        if not kernel.Process32FirstW(snapshot,ctypes.byref(entry)):
            raise StopRun('Cannot enumerate processes before guarded input.',kind='setup')
        while True:
            if entry.szExeFile.casefold()=='codex-computer-use.exe':
                pids.append(int(entry.th32ProcessID))
            ctypes.set_last_error(0)
            if not kernel.Process32NextW(snapshot,ctypes.byref(entry)):
                error=ctypes.get_last_error()
                if error not in (0,18):  # ERROR_NO_MORE_FILES is the normal end.
                    raise StopRun('Process scan failed before guarded input.',kind='setup')
                break
    finally:
        kernel.CloseHandle(snapshot)

    # The Swift helper can retain a hidden overlay window while idle.
    user=ctypes.WinDLL('user32',use_last_error=True)
    user.EnumWindows.argtypes=[ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM),wintypes.LPARAM]
    user.EnumWindows.restype=wintypes.BOOL
    user.IsWindowVisible.argtypes=[wintypes.HWND]
    user.IsWindowVisible.restype=wintypes.BOOL
    user.GetWindowTextLengthW.argtypes=[wintypes.HWND]
    user.GetWindowTextLengthW.restype=ctypes.c_int
    user.GetWindowTextW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
    user.GetWindowTextW.restype=ctypes.c_int
    user.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
    user.GetWindowThreadProcessId.restype=wintypes.DWORD
    overlay_pids=set()

    @ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
    def inspect_window(hwnd,_):
        if not user.IsWindowVisible(hwnd):
            return True
        length=user.GetWindowTextLengthW(hwnd)
        if length<=0:
            return True
        title=ctypes.create_unicode_buffer(length+1)
        if user.GetWindowTextW(hwnd,title,len(title))>0 and is_active_computer_use_window_title(title.value):
            pid=wintypes.DWORD()
            if user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid)):
                overlay_pids.add(int(pid.value))
        return True

    ctypes.set_last_error(0)
    if not user.EnumWindows(inspect_window,0):
        error=ctypes.get_last_error()
        if error:
            raise StopRun('Cannot verify that the computer-use overlay is closed.',kind='setup')
    return tuple(sorted(set(pids)|overlay_pids))


def ensure_no_computer_use_controller():
    pids=active_computer_use_controller_pids()
    if pids:
        joined=', '.join(map(str,pids))
        raise StopRun(f'Active computer-use controller detected (PIDs {joined}); close it before guarded input.',
                      kind='setup')


KEYS = {**{c: ord(c) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ12345"}, "SPACE": 0x20,
        "ENTER": 0x0D, "TAB": 0x09, "BACKSPACE": 0x08, "BACKSLASH": 0xDC, "CTRL": 0x11,
        "LEFT": 0x25, "UP": 0x26, "RIGHT": 0x27, "DOWN": 0x28}


class GuardedInput:
    def __init__(self, expected: phase1.Window, platform):
        self.expected = expected
        self.platform = platform
        self.before_click = None
        self.external_stop = None

    def check(self):
        if self.external_stop and self.external_stop():
            raise StopRun("Stop requested by session control.",kind='user_stop')
        if self.platform.stop_requested():
            raise StopRun("Emergency stop requested (F8/Escape).",kind='user_stop')
        current = self.platform.current()
        if not current.foreground:
            raise StopRun('Roblox is not foreground; no further input sent.',kind='focus_lost')
        if current != self.expected:
            expected,actual=asdict(self.expected),asdict(current)
            changes=', '.join(f'{key} {expected[key]}->{actual[key]}' for key in expected if expected[key]!=actual[key])
            raise StopRun(f'Roblox window changed ({changes}); no further input sent.',kind='window_changed')

    def wait(self, seconds):
        if not math.isfinite(seconds) or not 0 <= seconds <= 10:
            raise StopRun("Wait must be finite and bounded to ten seconds.")
        deadline = self.platform.now() + seconds
        self.check()
        while (remaining := deadline - self.platform.now()) > 0:
            interval = min(0.025, remaining)
            self.platform.sleep(interval)
            self.check()

    def move(self, x: int, y: int):
        if not (isinstance(x, int) and isinstance(y, int)
                and 0 <= x < self.expected.width and 0 <= y < self.expected.height):
            raise StopRun("Click is outside the Roblox client.")
        self.check()
        self.platform.emit("move", self.expected.x + x, self.expected.y + y)
        self.wait(0.10)
        self.platform.emit("relative", 1, 0)
        self.wait(0.08)
        self.platform.emit("relative", -1, 0)
        self.wait(0.18)  # Let the game render the moved pointer before pressing.

    def click(self, x: int, y: int):
        self.move(x, y)
        if self.before_click:
            self.before_click()
        self.check()
        self.check()
        try:
            self.platform.emit("left_down")
            self.wait(0.10)
        finally:
            # Release only, including on focus loss: never leave a held button.
            self.platform.emit("left_up")
        self.check()

    def key(self, key: str, seconds: float = 0.10):
        if key not in KEYS or not math.isfinite(seconds) or not 0 <= seconds <= 10:
            raise StopRun("Unsupported key or unbounded key hold.")
        self.check()
        try:
            self.platform.emit("key_down", key)
            self.wait(seconds)
        finally:
            self.platform.emit("key_up", key)
        self.check()

    def text(self, text: str):
        """Literal lowercase letters/spaces for a visually verified search field."""
        if not re.fullmatch(r"[a-z ]{1,64}", text, flags=re.ASCII):
            raise StopRun("Map search accepts only 1..64 lowercase ASCII letters/spaces.")
        for char in text:
            self.key("SPACE" if char == " " else char.upper(), 0.04)
            self.wait(0.025)

    def select_all(self):
        """Only for a visually verified search field; always release both keys."""
        self.check()
        try:
            self.platform.emit('key_down', 'CTRL')
            self.platform.emit('key_down', 'A')
            self.wait(.10)
        finally:
            self.platform.emit('key_up', 'A')
            self.platform.emit('key_up', 'CTRL')
        self.check()

    def orbit(self, dx: int, dy: int):
        if not all(isinstance(v, int) and abs(v) <= 1000 for v in (dx, dy)):
            raise StopRun("Camera delta must be bounded to 1000 pixels per axis.")
        self.check()
        self.platform.emit("move", self.expected.x + self.expected.width // 2,
                           self.expected.y + self.expected.height // 2)
        self.wait(0.1)
        try:
            self.platform.emit("right_down")
            self.wait(0.1)
            for index in range(1, 11):
                previous = index - 1
                self.platform.emit("relative", round(dx * index / 10) - round(dx * previous / 10),
                                   round(dy * index / 10) - round(dy * previous / 10))
                self.wait(0.04)
        finally:
            self.platform.emit("right_up")
        self.check()

    def zoom(self, notches: int):
        if not isinstance(notches, int) or not -20 <= notches <= 20:
            raise StopRun("Zoom must be bounded to twenty notches.")
        self.check()
        for _ in range(abs(notches)):
            self.platform.emit("wheel", 120 if notches > 0 else -120)
            self.wait(0.08)

    def zoom_fine(self, delta: int):
        """One small wheel step for verified, zero-tower camera alignment."""
        if type(delta) is not int or not 0 < abs(delta) <= 20:
            raise StopRun('Fine zoom must be a nonzero integer within twenty wheel units.')
        self.check()
        self.platform.emit('wheel',delta)
        self.wait(.08)


class WindowsOS:
    hotkey_id = 0x5444

    def __init__(self, *, stop_hotkey=False):
        ensure_no_computer_use_controller()
        self.stopped = False
        self.hotkey_registered = False
        phase1.USER.GetAsyncKeyState.argtypes = [ctypes.c_int]
        phase1.USER.GetAsyncKeyState.restype = ctypes.c_short
        if stop_hotkey:
            phase1.USER.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int,
                                                   wintypes.UINT, wintypes.UINT]
            phase1.USER.RegisterHotKey.restype = wintypes.BOOL
            phase1.USER.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
            phase1.USER.UnregisterHotKey.restype = wintypes.BOOL
            phase1.USER.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND,
                                                wintypes.UINT, wintypes.UINT, wintypes.UINT]
            phase1.USER.PeekMessageW.restype = wintypes.BOOL
            if not phase1.USER.RegisterHotKey(None, self.hotkey_id, 0x4000, 0x77):
                raise StopRun('Cannot register F8 stop; another macro or application may own it.')
            self.hotkey_registered = True

    def close(self):
        if self.hotkey_registered:
            phase1.USER.UnregisterHotKey(None, self.hotkey_id)
            self.hotkey_registered = False

    def current(self):
        return phase1.locate_roblox()

    def stop_requested(self):
        if self.hotkey_registered:
            message = wintypes.MSG()
            while phase1.USER.PeekMessageW(ctypes.byref(message), None, 0x0312, 0x0312, 1):
                if message.wParam == self.hotkey_id:
                    self.stopped = True
        # Read both keys each poll; the high bit reports the physical held state.
        pressed = [phase1.USER.GetAsyncKeyState(v) & 0x8000 for v in (0x77, 0x1B)]
        self.stopped = self.stopped or any(pressed)
        return self.stopped

    sleep = staticmethod(time.sleep)
    now = staticmethod(time.monotonic)

    def emit(self, kind, *args):
        if kind == "move":
            phase1.send_absolute_pointer(*args)
            return
        if kind == "relative":
            event = phase1._Input(0, phase1._InputData(mouse=phase1._MouseInput(args[0], args[1], 0, 0x2001, 0, None)))
        elif kind == "wheel":
            event = phase1._Input(0, phase1._InputData(mouse=phase1._MouseInput(0, 0, args[0] & 0xFFFFFFFF, 0x0800, 0, None)))
        elif kind in ("left_down", "left_up", "right_down", "right_up"):
            flags = {"left_down": 2, "left_up": 4, "right_down": 8, "right_up": 16}[kind]
            event = phase1._Input(0, phase1._InputData(mouse=phase1._MouseInput(0, 0, 0, flags, 0, None)))
        elif kind in ("key_down", "key_up"):
            class Keyboard(ctypes.Structure):
                _fields_ = [("vk", ctypes.c_ushort), ("scan", ctypes.c_ushort),
                            ("flags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                            ("extra", ctypes.c_void_p)]
            event = phase1._Input()
            event.type = 1
            phase1.USER.MapVirtualKeyW.argtypes = [ctypes.c_uint, ctypes.c_uint]
            phase1.USER.MapVirtualKeyW.restype = ctypes.c_uint
            scan = phase1.USER.MapVirtualKeyW(KEYS[args[0]], 0)
            flags = 8 | (2 if kind == "key_up" else 0)
            if args[0] in {"LEFT", "UP", "RIGHT", "DOWN"}:
                flags |= 1
            keyboard = Keyboard(0, scan, flags, 0, None)
            ctypes.memmove(ctypes.byref(event.data), ctypes.byref(keyboard), ctypes.sizeof(keyboard))
        else:
            raise StopRun("Unsupported OS event.")
        if phase1.USER.SendInput(1, ctypes.byref(event), ctypes.sizeof(event)) != 1:
            raise StopRun("Windows rejected an input event.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--click", nargs=2, type=int, metavar=("X", "Y"))
    parser.add_argument("--key", choices=sorted(KEYS))
    parser.add_argument("--confirm-start", action="store_true")
    parser.add_argument("--activate", action="store_true", help="Activate once at explicit start; never refocus mid-run")
    parser.add_argument("--expect-size", nargs=2, required=True, type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.confirm_start or bool(args.click) == bool(args.key):
        parser.error("Choose exactly one action and --confirm-start; F8/Escape stops.")
    platform = None
    try:
        platform = WindowsOS(stop_hotkey=True)
        window = phase1.locate_roblox()
        if args.activate:
            phase1.USER.SetForegroundWindow(window.hwnd)
            time.sleep(0.3)
            window = phase1.locate_roblox()
        if (window.width, window.height) != tuple(args.expect_size):
            raise StopRun("Client size does not match the explicit expected geometry.")
        driver = GuardedInput(window, platform)
        driver.check()
        before = phase1.capture(window)
        args.output.mkdir(parents=True, exist_ok=True)
        before.save(args.output / "before.png")
        if args.click:
            driver.click(*args.click)
        else:
            driver.key(args.key)
        for index, delay in enumerate((0.2, 0.6, 1.2, 3.0), 1):
            driver.wait(delay)
            phase1.capture(window).save(args.output / f"after_{index}.png")
        (args.output / "geometry.json").write_text(json.dumps(asdict(window), indent=2), encoding="utf-8")
        print(json.dumps({"status": "ONE_ACTION_SENT_NOT_VERIFIED", "evidence": str(args.output), "client": asdict(window)}))
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"CONTROL_STOP: {exc}")
        return 2
    finally:
        if platform:
            platform.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
