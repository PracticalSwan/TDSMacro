"""Checkpoint-eight camera must recognize the original pose without weakening drift guards."""
import sys
import unittest
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from tds_auto.hardcore_vision import WretchedCamera
from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2

class FinalCameraRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camera=WretchedCamera(load_hardcore_plan_v2())
        with Image.open(ROOT/"tests/fixtures/hardcore_camera_final_checkpoint08_static_landmarks.png") as im:
            cls.final=im.copy()

    def test_final_checkpoint_eight_uses_full_static_landmark_consensus(self):
        self.assertEqual(self.camera.estimate(self.final),(-16,-7))

    def test_final_camera_shift_still_rejected_by_original_bound(self):
        self.assertEqual(self.camera.estimate(self.final),(-16,-7))
        self.camera.offset=(-18,-7)
        self.assertFalse(self.camera.check(ImageChops.offset(self.final,9,0)))

    def test_three_pixel_second_to_third_spread_keeps_original_median_gate(self):
        # Both stable landmarks can differ by 3px while each is within
        # the original 2px consensus limit of the full three-view median.
        with Image.open(ROOT/"tests/fixtures/hardcore_camera_final_checkpoint08_shifted_pose.png") as im:
            shifted=im.copy()
        self.assertEqual(self.camera.estimate(shifted),(-30,-4))
        self.camera.offset=(-18,-7)
        self.assertFalse(self.camera.check(shifted))

    def test_replay_second_cycle_checkpoint_eight_with_rock_parallax(self):
        with Image.open(ROOT/"tests/fixtures/hardcore_camera_final_checkpoint08_second_cycle_rocks.png") as im:
            image=im.copy()
        self.assertEqual(self.camera.estimate(image),(-18,-17))

    def test_checkpoint_eight_parallax_does_not_allow_camera_drift(self):
        with Image.open(ROOT/"tests/fixtures/hardcore_camera_final_checkpoint08_second_cycle_rocks.png") as im:
            image=im.copy()
        self.camera.offset=(-18,-17)
        self.assertFalse(self.camera.check(ImageChops.offset(image,8,0)))

    def test_new_checkpoint_eight_right_rock_disagreement_is_recognized(self):
        with Image.open(ROOT/'tests/fixtures/hardcore_camera_checkpoint08_right_rock_precise.png') as im:
            frame=im.copy()
        self.assertEqual(self.camera.estimate(frame),(-23,-14))
        self.camera.offset=(-23,-14)
        self.assertFalse(self.camera.check(ImageChops.offset(frame,8,0)))

    def test_missing_third_landmark_still_rejected(self):
        altered=self.final.copy()
        ImageDraw.Draw(altered).rectangle((1280,700,1500,890),fill="black")
        self.assertIsNone(self.camera.estimate(altered))

if __name__=="__main__":
    unittest.main()
