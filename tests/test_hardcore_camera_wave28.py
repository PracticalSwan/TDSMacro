"""Keep all three fixed camera landmarks verifiable near late-wave effects."""
import sys
import unittest
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2
from tds_auto.hardcore_vision import WretchedCamera

class WretchedCameraWave28Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camera=WretchedCamera(load_hardcore_plan_v2())
        with Image.open(ROOT/"tests"/"fixtures"/"hardcore_camera_wave28_static_landmarks.png") as im:
            cls.failed=im.copy()
        with Image.open(ROOT/"tests"/"fixtures"/"hardcore_camera_wave27_static_landmarks.png") as im:
            cls.prior=im.copy()

    def test_wave27_and_wave28_see_same_stationary_three_landmark_pose(self):
        self.assertEqual(self.camera.estimate(self.prior),(-17,-6))
        self.assertEqual(self.camera.estimate(self.failed),(-17,-6))

    def test_new_wave28_range_ring_occlusion_preserves_stationary_camera(self):
        with Image.open(ROOT/'tests'/'fixtures'/'hardcore_camera_wave28_range_ring_20261120.png') as im:
            frame=im.copy()
        self.assertEqual(self.camera.estimate(frame),(-14,-7))
        self.assertTrue(self.camera.bind(frame))
        self.assertFalse(self.camera.check(ImageChops.offset(frame,8,0)))

    def test_native_slot_four_range_ring_keeps_original_camera_bound(self):
        # Sanitized fixed-rock crops from the same native match before and
        # after Minigunner X1 placement; no account HUD or user data.
        with Image.open(ROOT/'tests/fixtures/wretched_v031_x1_camera_before_rocks_native.png') as image:
            before=image.copy()
        with Image.open(ROOT/'tests/fixtures/wretched_v031_x1_camera_after_rocks_native.png') as image:
            after=image.copy()
        self.assertEqual(self.camera.estimate(before),(-1,-13))
        self.assertTrue(self.camera.bind(before))
        self.assertTrue(self.camera.check(after))
        self.assertFalse(self.camera.check(ImageChops.offset(after,8,0)))

    def test_measured_camera_drift_still_fails_bound_check(self):
        self.assertTrue(self.camera.bind(self.prior))
        self.assertFalse(self.camera.check(ImageChops.offset(self.failed,8,0)))

    def test_missing_third_landmark_still_fails(self):
        frame=self.failed.copy()
        ImageDraw.Draw(frame).rectangle((1420,520,1610,770),fill="black")
        self.assertIsNone(self.camera.estimate(frame))

    def test_missing_static_first_landmark_still_fails(self):
        frame=self.failed.copy()
        ImageDraw.Draw(frame).rectangle((490,710,670,850),fill="black")
        self.assertIsNone(self.camera.estimate(frame))

if __name__=="__main__":
    unittest.main()
