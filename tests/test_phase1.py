"""Offline checks for Phase 1 only. No game interaction or OS input."""
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tds_auto.phase1 import Window, normalized_point, locate_green_play_button, roi_delta, encode_virtual_point, capture, take_live, send_absolute_pointer


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
