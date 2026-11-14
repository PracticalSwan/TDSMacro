import sys
import unittest
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
try:
    from tds_auto.calibration import CameraGate, valid_preview, load_profile
except ImportError:
    CameraGate = None


class CalibrationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(CameraGate, "camera and placement gates have not been implemented")

    def test_fixed_camera_passes_independent_capture_and_shift_fails(self):
        gate = CameraGate(ROOT / "calibrations/dead_ahead_vertical_nine_v4.json")
        with Image.open(ROOT / "tests/fixtures/camera_independent.png") as frame:
            self.assertTrue(gate.check(frame))
            self.assertFalse(gate.check(ImageChops.offset(frame, 15, 0)))
            self.assertFalse(gate.check(frame.resize((1002, 750))))

    def test_blank_view_is_never_calibrated(self):
        gate = CameraGate(ROOT / "calibrations/dead_ahead_vertical_nine_v4.json")
        self.assertFalse(gate.check(Image.new("RGB", (1920, 991))))

    def test_red_road_preview_rejected_and_white_ground_preview_accepted(self):
        for name, point, expected in (("preview_red", (925,330), False), ("preview_white", (1020,330), True)):
            with Image.open(ROOT / "tests/fixtures" / f"{name}.png") as frame:
                self.assertEqual(valid_preview(frame, *point), expected)

    def test_absent_preview_never_accepted(self):
        self.assertFalse(valid_preview(Image.new("RGB", (1920, 991)), 1020, 330))
        with Image.open(ROOT / "tests/fixtures/preview_absent_selected.png") as frame:
            self.assertFalse(valid_preview(frame, 855, 330))

    def test_green_path_arrow_does_not_obscure_white_place_prompt(self):
        for name in ('preview_arrow_overlap','preview_mouse_icon'):
            with Image.open(ROOT/'tests/fixtures'/f'{name}.png') as frame:
                self.assertTrue(valid_preview(frame,855,327))

    def test_existing_tower_red_exclusion_circle_does_not_reject_valid_neighbour(self):
        with Image.open(ROOT/'tests/fixtures/preview_neighbour_circle.png') as frame:
            self.assertTrue(valid_preview(frame,810,327))
        with Image.open(ROOT/'tests/fixtures/preview_vertical_neighbour.png') as frame:
            self.assertTrue(valid_preview(frame,855,372))

    def test_candidate_is_provenanced_but_not_marked_full_strategy_verified(self):
        profile, strategy = load_profile(ROOT / "calibrations/dead_ahead_vertical_nine_v4.json")
        self.assertEqual((strategy.source_width, strategy.source_height), (1920,991))
        self.assertEqual({s.args[2] for s in strategy.steps if s.operation=='SpawnTower'}, {1})
        self.assertEqual(profile["status"], "calibrated_current_setup")
        self.assertEqual(profile["first_verified_placement"], [855,330])

    def test_small_view_offset_is_bound_once_and_points_are_adjusted(self):
        gate=CameraGate(ROOT / "calibrations/dead_ahead_vertical_nine_v4.json")
        with Image.open(ROOT / "calibrations/scene.png") as reference:
            frame=ImageChops.offset(reference,5,-4)
            self.assertTrue(gate.bind(frame))
            x,y=gate.map_point((855,330))
            self.assertAlmostEqual(x,860,delta=1)
            self.assertAlmostEqual(y,326,delta=1)
            self.assertTrue(gate.check(frame))
            self.assertFalse(gate.check(ImageChops.offset(frame,10,0)))

    def test_fresh_match_view_can_be_calibrated_within_strict_bounds(self):
        for name in ("camera_fresh_match", "camera_fresh_match_settled"):
            gate=CameraGate(ROOT / "calibrations/dead_ahead_vertical_nine_v4.json")
            with Image.open(ROOT / "tests/fixtures" / f"{name}.png") as frame:
                self.assertTrue(gate.bind(frame))
                self.assertTrue(gate.check(frame))

    def test_ui_outside_map_regions_does_not_change_camera_calibration(self):
        gate=CameraGate(ROOT / "calibrations/dead_ahead_vertical_nine_v4.json")
        with Image.open(ROOT / "tests/fixtures/camera_fresh_match.png") as source:
            frame=Image.new("RGB",source.size,"white")
            for box in gate.profile["scene_rois"]:
                frame.paste(source.crop(box),box[:2])
            self.assertTrue(gate.bind(frame))

    def test_large_offset_cannot_be_bound_as_a_new_camera(self):
        gate=CameraGate(ROOT / "calibrations/dead_ahead_vertical_nine_v4.json")
        with Image.open(ROOT / "calibrations/scene.png") as reference:
            self.assertFalse(gate.bind(ImageChops.offset(reference,30,0)))
            self.assertFalse(gate.bind(reference.rotate(6)))

    def test_large_range_circle_keeps_static_world_pose_but_shift_still_fails(self):
        gate=CameraGate(ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
        with Image.open(ROOT/'tests/fixtures/camera_vertical_initial.png') as initial:
            self.assertTrue(gate.bind(initial))
        for name in ('camera_large_range_circle','camera_lower_range_circle'):
            with Image.open(ROOT/'tests/fixtures'/f'{name}.png') as frame:
                self.assertTrue(gate.check(frame))
                self.assertFalse(gate.check(ImageChops.offset(frame,10,0)))

    def test_drift_uses_the_entire_vertical_placement_extent(self):
        import numpy as np
        from unittest.mock import patch
        gate=CameraGate(ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
        gate.bound=np.float64([[1,0,0],[0,1,0]])
        angle=.012
        linear=np.float64([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
        pivot=np.float64([980,420])
        current=np.column_stack((linear,pivot-linear@pivot))
        # The full placement extent moves >2px while the central reference corners do not.
        with patch.object(gate,'estimate',return_value=current):
            self.assertFalse(gate.check(Image.new('RGB',(1920,991))))

    def test_public_profile_runs_without_private_reference_file(self):
        import tempfile,json,shutil
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'strategies').mkdir()
            profile=json.loads((ROOT/'calibrations/dead_ahead_vertical_nine_v4.json').read_text())
            shutil.copy2(ROOT/profile['strategy'],root/profile['strategy'])
            path=root/'profile.json';path.write_text(json.dumps(profile))
            with patch('tds_auto.calibration.ROOT',root):
                _,strategy=load_profile(path)
                self.assertEqual(len(strategy.steps),44)
                self.assertEqual(profile['provenance']['original_author'],'gall')
                (root/profile['strategy']).write_text('tampered')
                with self.assertRaisesRegex(ValueError,'integrity changed'):load_profile(path)

    def test_scene_cannot_escape_profile_directory(self):
        import tempfile,json
        with tempfile.TemporaryDirectory() as temporary:
            profile=json.loads((ROOT/'calibrations/dead_ahead_vertical_nine_v4.json').read_text())
            profile['scene']='../outside.png'
            path=Path(temporary)/'profile.json';path.write_text(json.dumps(profile))
            with self.assertRaisesRegex(ValueError,'Scene path'):CameraGate(path)

    def test_three_scout_range_retains_camera_evidence_but_real_shift_is_rejected(self):
        gate=CameraGate(ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
        with Image.open(ROOT/'tests/fixtures/camera_board4_initial.png') as frame:
            self.assertTrue(gate.bind(frame))
        with Image.open(ROOT/'tests/fixtures/camera_three_scout_range.png') as frame:
            self.assertTrue(gate.check(frame))
            self.assertFalse(gate.check(ImageChops.offset(frame,10,0)))
            self.assertFalse(gate.check(ImageChops.offset(frame,0,10)))

    def test_unreadable_camera_is_distinct_from_a_measured_shift(self):
        from unittest.mock import patch
        import numpy as np
        gate=CameraGate(ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
        gate.bound=np.float64([[1,0,0],[0,1,0]])
        frame=Image.new('RGB',(1920,991))
        with patch.object(gate,'estimate',return_value=None):self.assertIsNone(gate.check(frame))
        with patch.object(gate,'estimate',return_value=np.float64([[1,0,10],[0,1,0]])):
            self.assertIs(gate.check(frame),False)

    def test_actual_prepared_reference_survives_preview_but_rejects_real_drift(self):
        gate=CameraGate(ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
        with Image.open(ROOT/'tests/fixtures/camera_prepared_48.png') as initial:
            self.assertTrue(gate.bind(initial))
        with Image.open(ROOT/'tests/fixtures/camera_preview_48.png') as frame:
            self.assertTrue(gate.check(frame))
            self.assertIs(gate.check(ImageChops.offset(frame,10,0)),False)
            self.assertIs(gate.check(ImageChops.offset(frame,0,10)),False)
            self.assertIs(gate.check(frame.rotate(1)),False)
