"""Phase 1: Windows GDK Roblox client identity, focus, capture, and safe hover probe.

The pre-run focus action may make one bounded native foreground request. This
module never sends clicks or keys, reads Roblox data, injects, or modifies the
client; pointer movement is limited to the explicit Settings hover probe.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageGrab, ImageStat

if sys.platform != "win32":
    raise RuntimeError("This utility supports Windows only.")

from ctypes import wintypes  # noqa: E402

USER = ctypes.WinDLL("user32", use_last_error=True)
KERNEL = ctypes.WinDLL("kernel32", use_last_error=True)
HWND = wintypes.HWND
DWORD = wintypes.DWORD
SUPPORTED_CLIENT = (1920, 991, 120)
FOCUS_TIMEOUT_SECONDS = 2.0
FOCUS_POLL_SECONDS = 0.05
FOCUS_STABLE_SECONDS = 0.2

class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class Rect(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]

USER.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
USER.FindWindowW.restype = HWND
USER.GetForegroundWindow.restype = HWND
USER.GetClientRect.argtypes = [HWND, ctypes.POINTER(Rect)]
USER.GetClientRect.restype = wintypes.BOOL
USER.ClientToScreen.argtypes = [HWND, ctypes.POINTER(Point)]
USER.ClientToScreen.restype = wintypes.BOOL
USER.GetWindowThreadProcessId.argtypes = [HWND, ctypes.POINTER(DWORD)]
USER.GetWindowThreadProcessId.restype = DWORD
USER.GetCursorPos.argtypes = [ctypes.POINTER(Point)]
USER.GetCursorPos.restype = wintypes.BOOL
USER.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
USER.SetCursorPos.restype = wintypes.BOOL
USER.IsWindowVisible.argtypes = [HWND]
USER.IsWindowVisible.restype = wintypes.BOOL
USER.IsIconic.argtypes = [HWND]
USER.IsIconic.restype = wintypes.BOOL
USER.SetForegroundWindow.argtypes = [HWND]
USER.SetForegroundWindow.restype = wintypes.BOOL
KERNEL.OpenProcess.argtypes = [DWORD, wintypes.BOOL, DWORD]
KERNEL.OpenProcess.restype = wintypes.HANDLE
KERNEL.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE, DWORD, wintypes.LPWSTR, ctypes.POINTER(DWORD)
]
KERNEL.QueryFullProcessImageNameW.restype = wintypes.BOOL
KERNEL.CloseHandle.argtypes = [wintypes.HANDLE]
KERNEL.CloseHandle.restype = wintypes.BOOL

try:
    USER.SetProcessDPIAware()  # Process-local scaling, not a system setting.
except OSError:
    pass


@dataclass(frozen=True)
class Window:
    hwnd: int
    pid: int
    x: int
    y: int
    width: int
    height: int
    dpi: int
    foreground: bool


class RobloxWindowUnavailable(RuntimeError):
    """No Roblox client window exists; startup recovery may launch the game."""


def locate_roblox() -> Window:
    hwnd = USER.FindWindowW(None, "Roblox")
    if not hwnd:
        raise RobloxWindowUnavailable("No Roblox client window was found.")
    if not USER.IsWindowVisible(hwnd) or USER.IsIconic(hwnd):
        raise RuntimeError("An existing Roblox window is minimized or hidden; restore it before retrying.")
    pid = DWORD()
    if not USER.GetWindowThreadProcessId(hwnd, ctypes.byref(pid)):
        raise RuntimeError("Could not verify the Roblox process ID.")
    handle = KERNEL.OpenProcess(0x1000, False, pid.value)
    if not handle:
        raise RuntimeError("Could not validate the Roblox executable.")
    try:
        buf = ctypes.create_unicode_buffer(32768)
        n = DWORD(len(buf))
        if not KERNEL.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(n)):
            raise RuntimeError("Could not validate the Roblox executable.")
        if os.path.basename(buf.value).lower() != "robloxplayerbeta.exe":
            raise RuntimeError("Window is not owned by RobloxPlayerBeta.exe.")
    finally:
        KERNEL.CloseHandle(handle)
    client = Rect()
    origin = Point(0, 0)
    if not USER.GetClientRect(hwnd, ctypes.byref(client)):
        raise RuntimeError("GetClientRect failed.")
    if not USER.ClientToScreen(hwnd, ctypes.byref(origin)):
        raise RuntimeError("ClientToScreen failed.")
    width = client.right - client.left
    height = client.bottom - client.top
    if width < 600 or height < 400:
        raise RuntimeError("Roblox client is too small for calibration.")
    get_dpi = getattr(USER, "GetDpiForWindow", None)
    if get_dpi:
        get_dpi.argtypes = [HWND]
        get_dpi.restype = wintypes.UINT
    dpi = int(get_dpi(hwnd)) if get_dpi else 96
    return Window(
        int(hwnd), pid.value, origin.x, origin.y,
        width, height, dpi, USER.GetForegroundWindow() == hwnd
    )


def _window_anchor(window: Window) -> tuple[int, int, int, int, int, int, int]:
    return (
        window.hwnd, window.pid, window.x, window.y,
        window.width, window.height, window.dpi,
    )


def focus_roblox(cancelled: Callable[[], bool] | None = None) -> Window:
    """Focus the verified supported Roblox client once, before a macro starts.

    This preflight helper is not recovery: it makes at most one ordinary
    SetForegroundWindow request, requires the same client/geometry/DPI on two
    foreground reads, and never sends game input or retries activation.
    """
    def check_cancelled() -> None:
        if cancelled is not None and cancelled():
            raise RuntimeError("Roblox focus preflight cancelled.")

    check_cancelled()
    initial = locate_roblox()
    if (initial.width, initial.height, initial.dpi) != SUPPORTED_CLIENT:
        raise RuntimeError("Roblox focus requires the supported 1920x991 client at 120 DPI.")
    anchor = _window_anchor(initial)
    current = initial

    if not initial.foreground:
        # Make one ordinary OS foreground request. Its return value is not
        # proof; the native locator must observe the target foreground.
        USER.SetForegroundWindow(initial.hwnd)
        deadline = time.monotonic() + FOCUS_TIMEOUT_SECONDS
        while True:
            check_cancelled()
            current = locate_roblox()
            if _window_anchor(current) != anchor:
                raise RuntimeError("Roblox focus preflight identity or geometry changed.")
            if current.foreground:
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError("Roblox did not reach the foreground within two seconds.")
            time.sleep(min(FOCUS_POLL_SECONDS, remaining))

    if not current.foreground:
        raise RuntimeError("Roblox focus preflight requires a foreground client.")
    check_cancelled()
    time.sleep(FOCUS_STABLE_SECONDS)
    check_cancelled()
    stable = locate_roblox()
    if _window_anchor(stable) != anchor or not stable.foreground:
        raise RuntimeError("Roblox focus preflight identity, geometry, or foreground changed.")
    return stable


def normalized_point(window: Window, x: float, y: float) -> tuple[int, int]:
    if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
        raise ValueError("Normalized coordinates must be inside the client.")
    return window.x + round(x * (window.width - 1)), window.y + round(y * (window.height - 1))


def encode_virtual_point(x: int, y: int, left: int, top: int,
                         width: int, height: int) -> tuple[int, int]:
    """Convert physical screen pixels to the Windows absolute mouse coordinate space."""
    if width < 2 or height < 2 or not (left <= x < left + width and top <= y < top + height):
        raise ValueError("Pointer target is outside the virtual desktop.")
    return (round((x - left) * 65535 / (width - 1)),
            round((y - top) * 65535 / (height - 1)))


class _MouseInput(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("data", DWORD), ("flags", DWORD), ("time", DWORD),
                ("extra", ctypes.c_void_p)]


class _InputData(ctypes.Union):
    _fields_ = [("mouse", _MouseInput)]


class _Input(ctypes.Structure):
    _fields_ = [("type", DWORD), ("data", _InputData)]


USER.GetSystemMetrics.argtypes = [ctypes.c_int]
USER.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(_Input), ctypes.c_int]
USER.SendInput.restype = wintypes.UINT


def send_absolute_pointer(x: int, y: int) -> None:
    """Move the normal OS cursor using SendInput (not process/client injection).

    On the observed GDK client, SetCursorPos alone did not reliably update
    Roblox's click target; SendInput absolute MOVE did.
    """
    if not locate_roblox().foreground:
        raise RuntimeError("Roblox is no longer foreground; pointer movement refused.")
    left, top, width, height = (USER.GetSystemMetrics(v) for v in (76, 77, 78, 79))
    dx, dy = encode_virtual_point(x, y, left, top, width, height)
    event = _Input(0, _InputData(mouse=_MouseInput(dx, dy, 0, 0xC001, 0, None)))
    if USER.SendInput(1, ctypes.byref(event), ctypes.sizeof(event)) != 1:
        raise RuntimeError("Windows rejected absolute mouse movement.")


class BlankCapture(RuntimeError):
    """A verified foreground client returned a blank/uniform frame."""


def capture(window: Window) -> Image.Image:
    current = locate_roblox()
    if (current.hwnd != window.hwnd or current.pid != window.pid
        or not current.foreground or current.width != window.width
        or current.height != window.height or current.x != window.x
        or current.y != window.y or current.dpi != window.dpi):
        raise RuntimeError("Roblox focus/geometry changed; capture cancelled.")
    bbox = (window.x, window.y, window.x + window.width, window.y + window.height)
    img = ImageGrab.grab(bbox=bbox, all_screens=True).convert("RGB")
    if USER.GetForegroundWindow() != window.hwnd:
        raise RuntimeError("Roblox lost focus during capture; frame discarded.")
    if img.size != (window.width, window.height):
        raise RuntimeError("Capture dimensions do not match the Roblox client.")
    if ImageStat.Stat(img.convert("L")).stddev[0] < 8:
        raise BlankCapture("Captured view is blank or unusually uniform.")
    return img


def locate_green_play_button(image: Image.Image) -> dict | None:
    """Sanity-check a large green PLAY anchor in the *current lobby* layout.

    This is a calibration hint, not an authoritative game-state classifier.
    """
    width, height = image.size
    region = (
        round(width * 0.41), round(height * 0.735),
        round(width * 0.59), round(height * 0.85)
    )
    roi = image.convert("RGB").crop(region)
    hit_x, hit_y = [], []
    for yy in range(0, roi.height, 3):
        for xx in range(0, roi.width, 3):
            r, g, b = roi.getpixel((xx, yy))
            if g >= 120 and g > r * 1.35 and g > b * 1.23:
                hit_x.append(xx)
                hit_y.append(yy)
    count = len(hit_x)
    total = ((roi.width + 2) // 3) * ((roi.height + 2) // 3)
    if count < 50 or count / total < 0.09:
        return None
    cx = region[0] + round((min(hit_x) + max(hit_x)) / 2)
    cy = region[1] + round((min(hit_y) + max(hit_y)) / 2)
    return {
        "relative_center": [round(cx / width, 4), round(cy / height, 4)],
        "green_pixel_fraction": round(count / total, 4)
    }


def roi_delta(a: Image.Image, b: Image.Image, center: tuple[float, float],
              radius: int = 48) -> float:
    if a.size != b.size:
        raise ValueError("Cannot compare differently sized captures.")
    x, y = round(center[0] * a.width), round(center[1] * a.height)
    box = (max(0, x-radius), max(0, y-radius),
           min(a.width, x+radius), min(a.height, y+radius))
    diff = ImageChops.difference(a.crop(box).convert("RGB"), b.crop(box).convert("RGB"))
    return round(sum(ImageStat.Stat(diff).mean) / 3, 3)


def take_live(action: str, activate: bool, output: Path, confirm_hover: bool) -> dict:
    window = locate_roblox()
    original_focus = USER.GetForegroundWindow()
    if action == "hover" and not confirm_hover:
        raise RuntimeError("Hover requires --confirm-hover; no input sent.")
    try:
        if not window.foreground and activate:
            if not USER.SetForegroundWindow(window.hwnd):
                raise RuntimeError("Windows denied temporary foreground activation.")
            deadline = time.monotonic() + 2.0
            while USER.GetForegroundWindow() != window.hwnd and time.monotonic() < deadline:
                time.sleep(0.05)
        window = locate_roblox()
        if not window.foreground:
            raise RuntimeError("Roblox is not foreground; no capture/input sent.")
        before = capture(window)
        output.parent.mkdir(parents=True, exist_ok=True)
        before.save(output)
        result = {"capture": str(output), "client": asdict(window),
                  "play_anchor": locate_green_play_button(before)}
        if action == "hover":
            cursor = Point()
            if not USER.GetCursorPos(ctypes.byref(cursor)):
                raise RuntimeError("Cannot read cursor location; hover cancelled.")
            target = normalized_point(window, 0.98, 0.045)  # Settings icon, seen in live lobby
            try:
                if USER.GetForegroundWindow() != window.hwnd:
                    raise RuntimeError("Focus changed before hover; cancelled.")
                send_absolute_pointer(*target)
                observed = Point()
                if not USER.GetCursorPos(ctypes.byref(observed)):
                    raise RuntimeError("Cursor validation failed.")
                if abs(observed.x-target[0]) > 2 or abs(observed.y-target[1]) > 2:
                    raise RuntimeError("Pointer did not reach the target.")
                time.sleep(0.3)  # A hover frame needs one rendered game tick.
                hovered = capture(window)
                hover_path = output.with_name(output.stem + "_hover.png")
                hovered.save(hover_path)
                result["hover_capture"] = str(hover_path)
                result["hover_roi_delta"] = roi_delta(before, hovered, (0.98, 0.045), 35)
                result["cursor_reached_target"] = True
            finally:
                at_end = Point()
                restored = False
                if (USER.GetForegroundWindow() == window.hwnd
                    and USER.GetCursorPos(ctypes.byref(at_end))
                    and abs(at_end.x - target[0]) <= 2
                    and abs(at_end.y - target[1]) <= 2):
                    send_absolute_pointer(cursor.x, cursor.y)
                    restored = True
                result["cursor_restored_if_unchanged"] = restored
        return result
    finally:
        if original_focus and original_focus != window.hwnd:
            USER.SetForegroundWindow(original_focus)
            if USER.GetForegroundWindow() != original_focus:
                print("WARNING: Windows did not restore the previous foreground window.", file=sys.stderr)


def main() -> int:
    p = argparse.ArgumentParser(description="Inspect Roblox TDS geometry, capture, or perform a harmless UI hover.")
    p.add_argument("action", choices=("inspect", "capture", "hover"))
    p.add_argument("--activate", action="store_true", help="Temporarily foreground Roblox for a visual probe")
    p.add_argument("--confirm-hover", action="store_true", help="Allow one mouse move over the Settings icon (no click)")
    p.add_argument("--output", type=Path, help="Capture destination (never overwritten).")
    args = p.parse_args()
    try:
        if args.action == "inspect":
            print(json.dumps(asdict(locate_roblox()), indent=2))
        else:
            output = args.output or (Path(__file__).resolve().parents[2] / "captures" / "phase1.png")
            print(json.dumps(take_live(args.action, args.activate, output, args.confirm_hover), indent=2))
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"PHASE1_STOP: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
