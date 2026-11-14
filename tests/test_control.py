"""Input boundary tests: fake OS, real guard and event ordering; never send input."""
import sys
import unittest
import ctypes
from ctypes import wintypes
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tds_auto.phase1 import Window
try:
    from tds_auto.control import GuardedInput, StopRun, WindowsOS
except ImportError:
    GuardedInput = None
    StopRun = RuntimeError


class FakeOS:
    def __init__(self):
        self.window = Window(1, 2, 0, 29, 1920, 991, 120, True)
        self.events = []
        self.stopped = False
        self.on_sleep = None
        self.clock = 0.0

    def current(self):
        return self.window

    def stop_requested(self):
        return self.stopped

    def emit(self, kind, *args):
        self.events.append((kind, *args))

    def sleep(self, seconds):
        self.clock += seconds
        if self.on_sleep:
            self.on_sleep(self)

    def now(self):
        return self.clock


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(GuardedInput, "guarded input has not been implemented")
        self.os = FakeOS()
        self.driver = GuardedInput(self.os.window, self.os)

    def test_click_uses_client_origin_and_separate_move_down_up(self):
        self.driver.click(960, 780)
        self.assertEqual(self.os.events, [("move", 960, 809), ("relative", 1, 0), ("relative", -1, 0), ("left_down",), ("left_up",)])

    def test_focus_loss_never_sends_input(self):
        self.os.window = replace(self.os.window, foreground=False)
        with self.assertRaises(StopRun):
            self.driver.click(960, 780)
        self.assertEqual(self.os.events, [])

    def test_visual_gate_after_pointer_motion_prevents_a_popup_click(self):
        self.driver.before_click = lambda: (_ for _ in ()).throw(StopRun('popup'))
        with self.assertRaisesRegex(StopRun, 'popup'):
            self.driver.click(960, 780)
        self.assertNotIn(('left_down',), self.os.events)

    def test_external_stop_is_checked_inside_a_hold_and_releases(self):
        self.driver.external_stop = lambda: self.os.clock >= .05
        with self.assertRaises(StopRun):
            self.driver.key('W', .95)
        self.assertEqual(self.os.events, [('key_down','W'), ('key_up','W')])

    def test_select_all_releases_both_keys_on_interruption(self):
        self.os.on_sleep = lambda os: setattr(os, 'stopped', True)
        with self.assertRaises(StopRun):
            self.driver.select_all()
        self.assertEqual(self.os.events[-2:], [('key_up','A'), ('key_up','CTRL')])

    def test_resize_move_dpi_or_identity_change_aborts(self):
        for changed in (dict(width=1800), dict(height=1009), dict(x=5), dict(dpi=96), dict(pid=9), dict(hwnd=3)):
            self.os.window = replace(self.driver.expected, **changed)
            with self.assertRaises(StopRun):
                self.driver.click(960, 780)
        self.assertEqual(self.os.events, [])

    def test_outside_client_refused(self):
        for point in ((1920, 700), (-1, 500), (500, 991), (500, -1)):
            with self.assertRaises(StopRun):
                self.driver.click(*point)
        self.assertEqual(self.os.events, [])

    def test_stop_before_action_never_sends_input(self):
        self.os.stopped = True
        with self.assertRaises(StopRun):
            self.driver.click(960, 780)
        self.assertEqual(self.os.events, [])

    def test_stop_after_mouse_down_always_releases(self):
        self.os.on_sleep = lambda os: setattr(os, "stopped", len(os.events) >= 4)
        with self.assertRaises(StopRun):
            self.driver.click(960, 780)
        self.assertEqual(self.os.events[-1], ("left_up",))
        self.assertEqual(len(self.os.events), 5)

    def test_focus_loss_after_move_prevents_button_press(self):
        self.os.on_sleep = lambda os: setattr(os, "window", replace(os.window, foreground=False))
        with self.assertRaises(StopRun):
            self.driver.click(960, 780)
        self.assertEqual(self.os.events, [("move", 960, 809)])

    def test_key_is_released_on_stop(self):
        self.os.on_sleep = lambda os: setattr(os, "stopped", True)
        with self.assertRaises(StopRun):
            self.driver.key("W", 0.95)
        self.assertEqual(self.os.events, [("key_down", "W"), ("key_up", "W")])

    def test_unknown_key_or_unbounded_hold_refused(self):
        for key, seconds in (("ALT", 0.1), ("W", 11), ("W", -1)):
            with self.assertRaises(StopRun):
                self.driver.key(key, seconds)
        self.assertEqual(self.os.events, [])

    def test_windows_key_events_use_physical_scan_codes(self):
        from tds_auto import phase1
        events = []
        def record(count, pointer, size):
            event = ctypes.cast(pointer, ctypes.POINTER(phase1._Input)).contents
            raw = ctypes.string_at(ctypes.byref(event.data), 8)
            events.append((event.type, int.from_bytes(raw[:2], "little"),
                           int.from_bytes(raw[2:4], "little"), int.from_bytes(raw[4:8], "little")))
            return 1
        with patch.object(phase1.USER, "SendInput", side_effect=record):
            platform = WindowsOS()
            platform.emit("key_down", "W")
            platform.emit("key_up", "W")
        self.assertEqual(events, [(1, 0, 0x11, 8), (1, 0, 0x11, 10)])

    def test_interaction_key_is_supported_and_released(self):
        self.driver.key("E", 0.1)
        self.assertEqual(self.os.events, [("key_down", "E"), ("key_up", "E")])

    def test_map_search_text_uses_bounded_literal_keys_without_enter(self):
        self.driver.text("dead ahead")
        self.assertEqual(self.os.events[:4], [("key_down", "D"), ("key_up", "D"), ("key_down", "E"), ("key_up", "E")])
        self.assertEqual(len(self.os.events), 20)
        self.assertIn(("key_down", "SPACE"), self.os.events)
        self.assertNotIn(("key_down", "ENTER"), self.os.events)

    def test_search_text_rejects_control_characters_and_long_input(self):
        for text in ("dead\nahead", "x" * 65, "https://example.com", ""):
            with self.assertRaises(StopRun):
                self.driver.text(text)
        self.assertEqual(self.os.events, [])

    def test_camera_drag_releases_right_button_even_when_stopped(self):
        self.os.on_sleep = lambda os: setattr(os, "stopped", ("right_down",) in os.events)
        with self.assertRaises(StopRun):
            self.driver.orbit(0, 420)
        self.assertEqual(self.os.events[-1], ("right_up",))

    def test_zoom_is_bounded_and_checks_stop_each_notch(self):
        self.driver.zoom(-3)
        self.assertEqual(self.os.events, [("wheel", -120)] * 3)
        with self.assertRaises(StopRun):
            self.driver.zoom(100)

    def test_placement_preview_move_never_presses_a_button(self):
        self.driver.move(855, 330)
        self.assertEqual(self.os.events, [("move", 855, 359), ("relative", 1, 0), ("relative", -1, 0)])

    def test_hold_duration_accounts_for_guard_and_scheduler_overhead(self):
        self.os.on_sleep = lambda os: setattr(os,"clock",os.clock+0.02)
        self.driver.wait(0.95)
        self.assertLessEqual(self.os.clock,0.98)

    def test_f8_message_survives_a_busy_interval_and_latches(self):
        # Exercise the actual native message queue without sending keyboard input.
        from tds_auto import phase1
        platform = WindowsOS(stop_hotkey=True)
        try:
            kernel = ctypes.WinDLL('kernel32')
            kernel.GetCurrentThreadId.restype = wintypes.DWORD
            phase1.USER.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT,
                                                       wintypes.WPARAM, wintypes.LPARAM]
            self.assertTrue(phase1.USER.PostThreadMessageW(
                kernel.GetCurrentThreadId(), 0x0312, platform.hotkey_id, 0))
            # The physical key is already up when the capture/OCR returns.
            with patch.object(phase1.USER, 'GetAsyncKeyState', return_value=0):
                self.assertTrue(platform.stop_requested())
                self.assertTrue(platform.stop_requested())
        finally:
            platform.close()
        again = WindowsOS(stop_hotkey=True)
        again.close()

    def test_failed_f8_registration_refuses_to_start(self):
        from tds_auto import phase1
        with patch.object(phase1.USER, 'RegisterHotKey', return_value=0):
            with self.assertRaisesRegex(StopRun, 'F8'):
                WindowsOS(stop_hotkey=True)


if __name__ == "__main__":
    unittest.main()
