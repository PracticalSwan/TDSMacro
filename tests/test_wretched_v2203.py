"""Current v2.20.3 Wretched Front route and strict camera regression checks."""
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


class WretchedV2203Tests(unittest.TestCase):
    def test_one_pinned_v031_route_without_a_game_version_parameter(self):
        from tds_auto.hardcore_vision import WretchedRoute, ROUTE_STEPS_V031, ROUTE_STEPS
        route = WretchedRoute('wretched_front_hardcore_v2')
        self.assertEqual(route.steps, ROUTE_STEPS_V031)
        self.assertEqual(len(route.steps), 11)
        self.assertEqual(route.steps[0], (('key', 'D', .30),))
        self.assertEqual(route.steps[3], (('key', 'D', .22),))
        self.assertEqual(route.steps[-1], (('key', 'S', .12),))
        self.assertEqual(WretchedRoute('wretched_front_hardcore_v1').steps, ROUTE_STEPS)
        with self.assertRaises(TypeError):
            WretchedRoute('wretched_front_hardcore_v2', game_version='v2.20.4')
        with self.assertRaises(ValueError):
            WretchedRoute('unknown-profile')

    def test_all_native_pinned_checkpoints_are_unique_and_shift_fail_closed(self):
        from tds_auto.hardcore_vision import WretchedRoute, ROUTE_SIDES, ROUTE_TILE_SIZE
        route=WretchedRoute('wretched_front_hardcore_v2')
        width,height=ROUTE_TILE_SIZE
        with Image.open(ROOT/'calibrations/wretched_front_hardcore_v031_single_route.route.png') as atlas:
            self.assertEqual(atlas.size,(264,11*height))
            for index in range(11):
                with self.subTest(checkpoint=index):
                    frame=Image.new('L',(1920,991))
                    for i,(x0,y0,x1,y1) in enumerate(ROUTE_SIDES):
                        tile=atlas.crop((i*width,index*height,(i+1)*width,(index+1)*height))
                        frame.paste(tile.resize((x1-x0,y1-y0),Image.Resampling.NEAREST),(x0,y0))
                    self.assertEqual(route.matching_steps(frame,range(11)),[index])
                    if index in (0,3,5,8,10):
                        self.assertEqual(route.matching_steps(ImageChops.offset(frame,24,0),range(11)),[])
                        self.assertEqual(route.matching_steps(ImageChops.offset(frame,0,24),range(11)),[])

    def test_fresh_rock_frame_matches_gray_terrain_without_edge_fallback(self):
        from tds_auto.hardcore_vision import WretchedRoute, ROUTE_SIDES, ROUTE_TILE_SIZE
        route = WretchedRoute('wretched_front_hardcore_v2')
        frame = Image.new('L', (1920, 991))
        width, height = ROUTE_TILE_SIZE
        with Image.open(ROOT/'tests/fixtures/wretched_v031_right_rock_fresh_tiles.png') as tiles:
            for i, (x0,y0,x1,y1) in enumerate(ROUTE_SIDES):
                part = tiles.crop((i*width,0,(i+1)*width,height))
                frame.paste(part.resize((x1-x0,y1-y0), Image.Resampling.NEAREST),(x0,y0))
        self.assertEqual(route.matching_steps(frame,range(11)),[3])
        self.assertEqual(route.matching_steps(ImageChops.offset(frame,24,0),range(11)),[])
        self.assertEqual(route.matching_steps(ImageChops.offset(frame,0,24),range(11)),[])

    def test_corrected_right_boulder_and_lower_path_landmarks(self):
        from tds_auto.hardcore_vision import WretchedRoute, ROUTE_SIDES, ROUTE_TILE_SIZE
        route = WretchedRoute('wretched_front_hardcore_v2')
        width, height = ROUTE_TILE_SIZE
        for name, expected in (('wretched_v031_extra_right_native.png', 4),
                               ('wretched_v031_extra_right_fresh_match2_native.png', 4),
                               ('wretched_v031_white_boulder_native.png', 6),
                               ('wretched_v031_white_boulder_fresh4_native.png', 6),
                               ('wretched_v031_lower_path_native.png', 8),
                               ('wretched_v031_lower_path_fresh_native.png', 8),
                               ('wretched_v031_lower_path_fresh2_native.png', 8)):
            with self.subTest(landmark=name):
                frame = Image.new('L', (1920, 991))
                with Image.open(ROOT/'tests/fixtures'/name) as tiles:
                    for i, (x0, y0, x1, y1) in enumerate(ROUTE_SIDES):
                        part = tiles.crop((i*width, 0, (i+1)*width, height))
                        frame.paste(part.resize((x1-x0, y1-y0), Image.Resampling.NEAREST),
                                    (x0, y0))
                self.assertEqual(route.matching_steps(frame, range(11)), [expected])
                self.assertEqual(route.matching_steps(ImageChops.offset(frame, 24, 0),
                                                      range(11)), [])
                self.assertEqual(route.matching_steps(ImageChops.offset(frame, 0, 24),
                                                      range(11)), [])

    def test_native_checkpoint_nine_left_transition_same_pose_needs_exact_second_view(self):
        from tds_auto.hardcore_vision import WretchedRoute, ROUTE_SIDES, ROUTE_TILE_SIZE
        route=WretchedRoute('wretched_front_hardcore_v2')
        width,height=ROUTE_TILE_SIZE
        frame=Image.new('L',(1920,991))
        with Image.open(ROOT/'tests/fixtures/wretched_v031_left_checkpoint9_fresh_tiles.png') as tiles:
            for i,(x0,y0,x1,y1) in enumerate(ROUTE_SIDES):
                part=tiles.crop((i*width,0,(i+1)*width,height))
                frame.paste(part.resize((x1-x0,y1-y0),Image.Resampling.NEAREST),(x0,y0))
        self.assertEqual(route.matching_steps(frame,range(11)),[9])
        self.assertEqual(route.matching_steps(ImageChops.offset(frame,24,0),range(11)),[])
        self.assertEqual(route.matching_steps(ImageChops.offset(frame,0,24),range(11)),[])

    def test_selected_minigunner_range_ring_keeps_three_rock_camera_consensus(self):
        from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2
        from tds_auto.hardcore_vision import WretchedCamera
        camera=WretchedCamera(load_hardcore_plan_v2())
        with Image.open(ROOT/'tests/fixtures/wretched_v031_pre_x1_3rock_masked.png') as before:
            self.assertTrue(camera.bind(before))
        with Image.open(ROOT/'tests/fixtures/wretched_v031_post_x1_ring_3rock_masked.png') as after:
            self.assertTrue(camera.check(after))
            self.assertFalse(camera.check(ImageChops.offset(after,24,0)))
            self.assertFalse(camera.check(ImageChops.offset(after,0,24)))

    def test_same_three_rock_gate_and_cross_frame_drift_on_native_pose(self):
        from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2
        from tds_auto.hardcore_vision import WretchedCamera
        camera = WretchedCamera(load_hardcore_plan_v2())
        with Image.open(ROOT / 'tests/fixtures/wretched_v2203_final_3rocks.png') as frame:
            self.assertEqual(camera.estimate(frame), (3, 14))
            self.assertTrue(camera.bind(frame))
            self.assertTrue(camera.check(frame))
            self.assertFalse(camera.check(ImageChops.offset(frame, 3, 0)))
            self.assertFalse(camera.check(ImageChops.offset(frame, 8, 0)))

    def test_route_is_constructed_without_game_version_ocr_or_frame_read(self):
        from tds_auto.hardcore_match import HardcoreMatchV2
        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.plan = Mock(profile_id='wretched_front_hardcore_v2')
        worker.session = Mock()
        worker.driver = Mock()
        with patch('tds_auto.hardcore_match.WretchedRoute',
                   side_effect=RuntimeError('route selected')) as constructor:
            with self.assertRaisesRegex(RuntimeError,'route selected'):
                worker.align_camera()
        constructor.assert_called_once_with('wretched_front_hardcore_v2')
        worker.session.frame.assert_not_called()
        worker.driver.assert_not_called()

    def test_unrecognized_terrain_stops_without_movement_or_purchase(self):
        from tds_auto.hardcore_match import HardcoreMatchV2
        from tds_auto.control import StopRun
        from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2
        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.plan = load_hardcore_plan_v2()
        worker.session = Mock()
        worker.driver = Mock()
        worker.settled_camera_view = Mock(return_value=(
            Image.new('RGB',(1920,991)),None,None,False))
        with self.assertRaisesRegex(StopRun,'terrain did not verify'):
            worker.align_camera()
        worker.driver.key.assert_not_called()
        worker.driver.click.assert_not_called()
        worker.driver.orbit.assert_not_called()
        worker.session.save_frame.assert_called_once()

if __name__ == '__main__':
    unittest.main()
