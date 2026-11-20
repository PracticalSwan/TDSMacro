"""Offline checks for Phase 1 only. No game interaction or OS input."""
import io
from contextlib import redirect_stderr, redirect_stdout
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tds_auto.phase1 import Window, normalized_point, locate_green_play_button, roi_delta, encode_virtual_point, capture, take_live, send_absolute_pointer, focus_roblox, main


class Phase1Tests(unittest.TestCase):
    def setUp(self):
        self.window = Window(1, 2, 0, 29, 1920, 991, 96, True)

    def test_client_relative_coordinates(self):
        self.assertEqual(normalized_point(self.window, 0, 0), (0, 29))
        self.assertEqual(normalized_point(self.window, 1, 1), (1919, 1019))
        with self.assertRaises(ValueError):
            normalized_point(self.window, -0.1, 0.5)

    def test_play_anchor_in_synthetic_lobby(self):
        img = Image.new("RGB", (600, 400), (30, 30, 30))
        for y in range(303, 330):
            for x in range(260, 340):
                img.putpixel((x, y), (35, 218, 60))
        anchor = locate_green_play_button(img)
        self.assertIsNotNone(anchor)
        self.assertAlmostEqual(anchor["relative_center"][0], 0.50, delta=0.025)
        self.assertAlmostEqual(anchor["relative_center"][1], 0.79, delta=0.025)

    def test_unknown_ui_does_not_fake_play_anchor(self):
        self.assertIsNone(locate_green_play_button(Image.new("RGB", (600, 400), (0, 0, 0))))

    def test_hover_region_change(self):
        before = Image.new("RGB", (600, 400), (0, 0, 0))
        after = before.copy()
        for y in range(5, 35):
            for x in range(570, 599):
                after.putpixel((x, y), (100, 100, 100))
        self.assertGreater(roi_delta(before, after, (0.98, 0.045), 35), 1.0)
        self.assertEqual(roi_delta(before, before, (0.98, 0.045), 35), 0.0)
        with self.assertRaises(ValueError):
            roi_delta(before, Image.new("RGB", (400, 400)), (0.98, 0.045))

    def test_virtual_desktop_absolute_coordinates(self):
        self.assertEqual(encode_virtual_point(0, 0, 0, 0, 1920, 1080), (0, 0))
        self.assertEqual(encode_virtual_point(1919, 1079, 0, 0, 1920, 1080), (65535, 65535))
        self.assertEqual(encode_virtual_point(-1920, 0, -1920, 0, 3840, 1080), (0, 0))
        with self.assertRaises(ValueError):
            encode_virtual_point(1920, 0, 0, 0, 1920, 1080)
        with self.assertRaises(ValueError):
            encode_virtual_point(0, 0, 0, 0, 1, 1080)

    def test_capture_refuses_lost_focus(self):
        with patch("tds_auto.phase1.locate_roblox", return_value=replace(self.window, foreground=False)):
            with self.assertRaisesRegex(RuntimeError, "focus/geometry"):
                capture(self.window)

    def test_capture_refuses_resized_window(self):
        with patch("tds_auto.phase1.locate_roblox", return_value=replace(self.window, width=1800)):
            with self.assertRaisesRegex(RuntimeError, "focus/geometry"):
                capture(self.window)

    def test_capture_refuses_dpi_change(self):
        with patch("tds_auto.phase1.locate_roblox", return_value=replace(self.window, dpi=120)):
            with self.assertRaisesRegex(RuntimeError, "focus/geometry"):
                capture(self.window)

    def test_missing_versus_minimized_client_is_not_confused(self):
        from tds_auto.phase1 import RobloxWindowUnavailable, locate_roblox
        with patch("tds_auto.phase1.USER.FindWindowW", return_value=0):
            with self.assertRaises(RobloxWindowUnavailable):
                locate_roblox()
        for visible, minimized in ((False, False), (True, True)):
            with self.subTest(visible=visible, minimized=minimized):
                with patch("tds_auto.phase1.USER.FindWindowW", return_value=101):
                    with patch("tds_auto.phase1.USER.IsWindowVisible", return_value=visible):
                        with patch("tds_auto.phase1.USER.IsIconic", return_value=minimized):
                            with self.assertRaisesRegex(RuntimeError, "minimized or hidden") as caught:
                                locate_roblox()
                self.assertNotIsInstance(caught.exception, RobloxWindowUnavailable)

    def test_focus_start_requests_once_and_requires_two_stable_reads(self):
        background = replace(self.window, dpi=120, foreground=False)
        focused = replace(background, foreground=True)
        with patch("tds_auto.phase1.locate_roblox", side_effect=[background, focused, focused]) as locate:
            with patch("tds_auto.phase1.USER.SetForegroundWindow", return_value=False) as activate:
                with patch("tds_auto.phase1.time.sleep") as sleep:
                    result = focus_roblox()
        self.assertEqual(result, focused)
        activate.assert_called_once_with(background.hwnd)
        self.assertEqual(locate.call_count, 3)
        sleep.assert_called_once_with(0.2)

    def test_focus_start_skips_activation_when_already_foreground(self):
        focused = replace(self.window, dpi=120, foreground=True)
        with patch("tds_auto.phase1.locate_roblox", side_effect=[focused, focused]) as locate:
            with patch("tds_auto.phase1.USER.SetForegroundWindow") as activate:
                with patch("tds_auto.phase1.time.sleep"):
                    result = focus_roblox()
        self.assertEqual(result, focused)
        activate.assert_not_called()
        self.assertEqual(locate.call_count, 2)

    def test_focus_start_refuses_unsupported_geometry_before_activation(self):
        background = replace(self.window, width=1800, dpi=120, foreground=False)
        with patch("tds_auto.phase1.locate_roblox", return_value=background):
            with patch("tds_auto.phase1.USER.SetForegroundWindow") as activate:
                with self.assertRaisesRegex(RuntimeError, "1920x991.*120 DPI"):
                    focus_roblox()
        activate.assert_not_called()

    def test_focus_start_refuses_client_identity_change_without_retry(self):
        background = replace(self.window, dpi=120, foreground=False)
        focused = replace(background, foreground=True)
        changes = (
            {"hwnd": 9}, {"pid": 99}, {"x": 1}, {"y": 30},
            {"width": 1919}, {"height": 990}, {"dpi": 96},
        )
        for change in changes:
            with self.subTest(change=change):
                changed = replace(focused, **change)
                with patch("tds_auto.phase1.locate_roblox", side_effect=[background, changed]) as locate:
                    with patch("tds_auto.phase1.USER.SetForegroundWindow") as activate:
                        with self.assertRaisesRegex(RuntimeError, "identity or geometry changed"):
                            focus_roblox()
                activate.assert_called_once_with(background.hwnd)
                self.assertEqual(locate.call_count, 2)

    def test_focus_start_stops_if_foreground_is_lost_between_stable_reads(self):
        background = replace(self.window, dpi=120, foreground=False)
        focused = replace(background, foreground=True)
        lost = replace(focused, foreground=False)
        with patch("tds_auto.phase1.locate_roblox", side_effect=[background, focused, lost]) as locate:
            with patch("tds_auto.phase1.USER.SetForegroundWindow") as activate:
                with patch("tds_auto.phase1.time.sleep"):
                    with self.assertRaisesRegex(RuntimeError, "foreground changed"):
                        focus_roblox()
        activate.assert_called_once_with(background.hwnd)
        self.assertEqual(locate.call_count, 3)

    def test_focus_start_stops_after_one_bounded_activation_attempt(self):
        background = replace(self.window, dpi=120, foreground=False)
        with patch("tds_auto.phase1.locate_roblox", side_effect=[background, background]) as locate:
            with patch("tds_auto.phase1.USER.SetForegroundWindow") as activate:
                with patch("tds_auto.phase1.time.monotonic", side_effect=[0.0, 2.0]):
                    with patch("tds_auto.phase1.time.sleep") as sleep:
                        with self.assertRaisesRegex(RuntimeError, "within two seconds"):
                            focus_roblox()
        activate.assert_called_once_with(background.hwnd)
        self.assertEqual(locate.call_count, 2)
        sleep.assert_not_called()

    def test_focus_start_honors_cancellation_before_activation(self):
        with patch("tds_auto.phase1.locate_roblox") as locate:
            with patch("tds_auto.phase1.USER.SetForegroundWindow") as activate:
                with self.assertRaisesRegex(RuntimeError, "cancelled"):
                    focus_roblox(cancelled=lambda: True)
        locate.assert_not_called()
        activate.assert_not_called()

    def test_standalone_focus_cli_is_not_available_during_a_worker(self):
        with patch("tds_auto.phase1.sys.argv", ["phase1.py", "focus"]):
            with patch("tds_auto.phase1.focus_roblox") as focus:
                with patch("tds_auto.phase1.capture") as native_capture:
                    with redirect_stderr(io.StringIO()):
                        with self.assertRaises(SystemExit) as raised:
                            main()
                    self.assertEqual(raised.exception.code, 2)
        focus.assert_not_called()
        native_capture.assert_not_called()

    def test_capture_refuses_blank_frame(self):
        blank = Image.new("RGB", (1920, 991), (0, 0, 0))
        with patch("tds_auto.phase1.locate_roblox", return_value=self.window):
            with patch("tds_auto.phase1.USER.GetForegroundWindow", return_value=self.window.hwnd):
                with patch("tds_auto.phase1.ImageGrab.grab", return_value=blank):
                    with self.assertRaisesRegex(RuntimeError, "blank or unusually uniform"):
                        capture(self.window)

    def test_capture_refuses_wrong_dimensions(self):
        frame = Image.new("RGB", (100, 100), (200, 200, 200))
        with patch("tds_auto.phase1.locate_roblox", return_value=self.window):
            with patch("tds_auto.phase1.USER.GetForegroundWindow", return_value=self.window.hwnd):
                with patch("tds_auto.phase1.ImageGrab.grab", return_value=frame):
                    with self.assertRaisesRegex(RuntimeError, "dimensions"):
                        capture(self.window)

    def test_hover_requires_explicit_opt_in(self):
        with patch("tds_auto.phase1.locate_roblox", return_value=self.window):
            with self.assertRaisesRegex(RuntimeError, "--confirm-hover"):
                take_live("hover", False, Path("unused.png"), False)

    def test_capture_refuses_focus_lost_during_grab(self):
        frame = Image.new("RGB", (1920, 991), (100, 100, 100))
        with patch("tds_auto.phase1.locate_roblox", return_value=self.window):
            with patch("tds_auto.phase1.USER.GetForegroundWindow", return_value=999):
                with patch("tds_auto.phase1.ImageGrab.grab", return_value=frame):
                    with self.assertRaisesRegex(RuntimeError, "lost focus during capture"):
                        capture(self.window)

    def test_mouse_move_refuses_when_roblox_not_foreground(self):
        with patch("tds_auto.phase1.locate_roblox", return_value=replace(self.window, foreground=False)):
            with patch("tds_auto.phase1.USER.SendInput") as send_input:
                with self.assertRaisesRegex(RuntimeError, "pointer movement refused"):
                    send_absolute_pointer(100, 100)
                send_input.assert_not_called()


if __name__ == "__main__":
    unittest.main()
