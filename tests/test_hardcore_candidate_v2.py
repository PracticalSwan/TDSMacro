"""Read-only contract checks for the proposed Hardcore v2 phase plan.

These tests do not assert that the existing v1 executor can play v2.
"""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
PLAN = ROOT / "strategies/hardcore_wretched_front_boomerang_crook_farm_v2.json"
CALIBRATION = ROOT / "calibrations/wretched_front_hardcore_v2.json"


class HardcoreCandidateV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(PLAN.read_text(encoding="utf-8"))
        cls.calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))

    def test_revised_tower_roster_and_finish(self):
        p = self.plan
        self.assertEqual(p["schema_version"], 2)
        self.assertEqual(p["required_counts"], {"Farm": 10, "Boomerang": 3, "Crook Boss": 5})
        self.assertEqual(p["required_loadout"], [
            {"slot": 1, "tower": "Boomerang"},
            {"slot": 2, "tower": "Crook Boss"},
            {"slot": 3, "tower": "Farm"},
        ])
        expected = {**{f"F{i}": 3 for i in range(1, 11)},
                    **{f"B{i}": 4 for i in range(1, 4)},
                    **{f"C{i}": 3 for i in range(1, 6)}}
        self.assertEqual(p["final_required_levels"], expected)
        self.assertEqual({t["id"] for t in p["towers"]}, set(expected) | {"X1"})
        self.assertEqual(p["finish_policy"]["target_wave"], 30)
        self.assertEqual(p["finish_policy"]["expected_gems"], 137)
        self.assertFalse(p["finish_policy"]["expected_gems_verified"])
        self.assertTrue(p["finish_policy"]["no_selling"])
        self.assertTrue(p["finish_policy"]["replay_requires_independently_credited_gems"])
        self.assertEqual(p["finish_policy"]["game_speed"], "1x")

    def test_all_14_phases_have_valid_dependencies_and_final_levels(self):
        p = self.plan
        phases = p["phases"]
        self.assertEqual([phase["step"] for phase in phases], list(range(1, 15)))
        self.assertTrue(phases[0]["before_ready"])
        self.assertEqual([(a["op"], a["tower_id"]) for a in phases[0]["actions"]],
                         [("place", f"F{i}") for i in range(1, 5)])
        self.assertEqual([(a["tower_id"], a["level"]) for a in phases[1]["actions"]],
                         [("F1", 1), ("F2", 1), ("F3", 1), ("F1", 2),
                          ("F4", 1), ("F2", 2), ("F3", 2)])
        known = {tower["id"]: tower for tower in p["towers"]}
        levels = {}
        for phase in phases:
            for action in phase["actions"]:
                self.assertIn(action["op"], ("place", "upgrade"))
                tower = action["tower_id"]
                self.assertIn(tower, known)
                if action["op"] == "place":
                    self.assertNotIn(tower, levels)
                    levels[tower] = 0
                else:
                    self.assertEqual(levels.get(tower), action["level"] - 1,
                                     f"out-of-order upgrade for {tower}")
                    levels[tower] = action["level"]
                if action.get("optional"):
                    self.assertEqual((tower, action["op"]), ("X1", "place"))
        expected = p["final_required_levels"]
        self.assertEqual({k: v for k, v in levels.items() if k != "X1"}, expected)
        self.assertEqual(levels["X1"], 0)

    def test_optional_experience_placement_never_preempts_required_purchases(self):
        from tds_auto.hardcore_match import HardcoreMatchV2
        from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2
        runner=object.__new__(HardcoreMatchV2)
        runner.plan=load_hardcore_plan_v2()
        runner.optional_tower=None
        original=[p.step for p in runner.execution_phases()]
        self.assertEqual(original,list(range(2,12))+[13,14])
        runner.optional_tower='Scout'
        extended=[p.step for p in runner.execution_phases()]
        self.assertEqual(extended,list(range(2,15)))
        self.assertEqual(len(extended),13)

    def test_optional_tower_and_unaccepted_placement_gates(self):
        p = self.plan
        self.assertEqual(p["optional_slot"], 4)
        self.assertEqual(p["slots_must_be_empty"], [5])
        self.assertEqual(p["phases"][11]["actions"], [
            {"op": "place", "tower_id": "X1", "optional": True}
        ])
        c = self.calibration
        self.assertEqual(c["status"], "native_individual_previews_verified")
        self.assertEqual(c["size"], [1920, 991])
        self.assertEqual(c["dpi"], 120)
        self.assertEqual(c["coordinates"]["B1"], [1106, 371])
        c1, b1 = (c["coordinates"][key] for key in ("C1", "B1"))
        self.assertLess(c1[0], b1[0])
        self.assertLess(b1[0] - c1[0], 70)
        for tower in ("F9", "F10"):
            self.assertGreater(c["coordinates"][tower][1], c["coordinates"]["F8"][1])
        self.assertIsNone(c["coordinates"]["X1"])
        for tower in ("B2", "B3"):
            self.assertGreater(c["coordinates"][tower][0], c["coordinates"]["B1"][0])
        self.assertEqual(set(c["coordinates"]), {t["id"] for t in p["towers"]})

    def test_optional_slot_four_reads_exact_price_before_and_during_native_preview(self):
        # The green-only OCR changes the glyph 1 into 7 while the exact native
        # visible price remains $1,850. Both views must yield the same quote;
        # commit_placement independently rechecks it before any purchase.
        from PIL import Image
        from tds_auto.resources import LocalOCR
        from tds_auto.hardcore_vision import wretched_price, PRICE_BOXES
        ocr=LocalOCR()
        for name in ('hardcore_slot4_price_normal_native.png',
                     'hardcore_slot4_price_armed_native.png'):
            with self.subTest(name=name):
                frame=Image.new('RGB',(1920,991))
                with Image.open(ROOT/'tests'/'fixtures'/name) as crop:
                    frame.paste(crop,PRICE_BOXES[4][:2])
                self.assertEqual(wretched_price(frame,4,ocr),1850)

    def test_optional_price_range_200_through_10000_is_exact_and_fail_closed(self):
        from tds_auto.hardcore_vision import wretched_price
        from PIL import Image
        frame=Image.new('RGB',(1920,991))
        class StubOCR:
            text=''
            def read(self, _image):
                return self.text
        ocr=StubOCR()
        for text,expected in (
            ('$200',200), ('$2,000',2000), ('$10,000',10000),
            ('$10000',10000), ('$199',None), ('$10,001',None),
            ('$0',None), ('10,000',None), ('$1O,000',None),
            ('$10,000 extra',None), ('',None)
        ):
            with self.subTest(ocr=text):
                ocr.text=text
                self.assertEqual(wretched_price(frame,4,ocr),expected)
        # No optional-slot cap is imposed on the three verified core slots.
        ocr.text='$14,000'
        self.assertEqual(wretched_price(frame,3,ocr),14000)

    def test_optional_affordable_low_and_high_prices_enter_same_guarded_path(self):
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud
        for price in (200,10000):
            with self.subTest(price=price):
                worker=HardcoreMatch.__new__(HardcoreMatch)
                worker.levels={}
                worker.recorded_wait=set()
                worker.camera=Mock()
                worker.camera.point.return_value=(1120,660)
                worker.driver=Mock()
                worker.ocr=Mock()
                worker.session=Mock()
                worker.read=Mock(return_value=(None,Hud(cash=price,tower_count=0,wave=24)))
                worker.commit_placement=Mock(return_value=True)
                tower=SimpleNamespace(tower_id='X1',tower_type='Scout',slot=4,optional=True)
                with patch('tds_auto.hardcore_match.wretched_price',return_value=price):
                    self.assertTrue(worker.place(tower,29))
                worker.driver.key.assert_called_once_with('4')
                worker.commit_placement.assert_called_once_with(tower,29,(1120,660),0,price)

    def test_optional_10000_unaffordable_never_arms_the_slot(self):
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud
        worker=HardcoreMatch.__new__(HardcoreMatch)
        worker.levels={}
        worker.recorded_wait=set()
        worker.camera=Mock()
        worker.camera.point.return_value=(1120,660)
        worker.driver=Mock()
        worker.ocr=Mock()
        worker.session=Mock()
        worker.read=Mock(return_value=(None,Hud(cash=9999,tower_count=0,wave=24)))
        worker.commit_placement=Mock()
        tower=SimpleNamespace(tower_id='X1',tower_type='Scout',slot=4,optional=True)
        with patch('tds_auto.hardcore_match.wretched_price',return_value=10000):
            self.assertFalse(worker.place(tower,29))
        worker.driver.key.assert_not_called()
        worker.commit_placement.assert_not_called()
        worker.session.status.assert_called_once()
        self.assertEqual(worker.levels,{})

    def test_optional_10000_quote_is_reverified_in_a_new_frame_before_click(self):
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud
        from tds_auto.control import StopRun
        worker=HardcoreMatch.__new__(HardcoreMatch)
        worker.levels={}
        worker.recorded_wait=set()
        worker.camera=Mock()
        worker.camera.point.return_value=(1120,660)
        worker.driver=Mock()
        worker.ocr=Mock()
        worker.session=Mock()
        worker.session.now.side_effect=[0,3]
        worker.frame=Mock(return_value=None)
        worker.read=Mock(side_effect=[
            (None,Hud(cash=10000,tower_count=0,wave=24)),
            (None,Hud(cash=10000,tower_count=0,wave=24)),
        ])
        worker.click=Mock(side_effect=lambda point, guard: guard())
        worker.confirm=Mock()
        tower=SimpleNamespace(tower_id='X1',tower_type='Scout',slot=4,optional=True)
        with patch('tds_auto.hardcore_match.wretched_price',side_effect=[10000,1000]):
            with self.assertRaisesRegex(StopRun,'Placement price or cash changed'):
                worker.place(tower,29)
        self.assertEqual([item.args for item in worker.driver.key.call_args_list],[('4',),('Q',)])
        worker.confirm.assert_not_called()
        worker.session.save_frame.assert_called_once()
        self.assertEqual(worker.levels,{})

    def test_farm_preview_accepts_one_pixel_caption_registration_only_with_white_footprint(self):
        from PIL import Image,ImageDraw
        from tds_auto.hardcore_vision import wretched_preview
        from tds_auto.resources import LocalOCR

        frame=Image.new('RGB',(1920,991))
        with Image.open(ROOT/'tests/fixtures/hardcore_farm_preview_one_pixel_ocr.png') as crop:
            frame.paste(crop,(658,600))
        self.assertTrue(wretched_preview(frame,(697,640),LocalOCR()))
        blocked=frame.copy()
        ImageDraw.Draw(blocked).rectangle((679,614,720,653),fill=(240,20,55))
        self.assertFalse(wretched_preview(blocked,(697,640),LocalOCR()))

    def test_preview_distinguishes_collisions_and_reads_captions_against_terrain(self):
        from PIL import Image
        from tds_auto.hardcore_vision import wretched_preview
        from tds_auto.resources import LocalOCR

        ocr = LocalOCR()
        for sample, point, expected in (
            ('hardcore_crook_preview_path_units', (913, 344), True),
            ('hardcore_crook_preview_blocked', (1027, 360), False),
            ('hardcore_boomerang_preview_caption', (1112, 415), True),
            ('hardcore_crook_preview_crowded', (997, 290), True),
            ('hardcore_crook_preview_rock', (988, 283), False),
            ('hardcore_minigunner_wave24_white_ring_native', (848, 352), True),
            ('hardcore_minigunner_ready_white_ring_native', (1124, 652), True),
        ):
            with self.subTest(sample=sample):
                with Image.open(ROOT / 'tests' / 'fixtures' / f'{sample}.png') as crop:
                    frame = Image.new('RGB', (1920, 991))
                    frame.paste(crop, (point[0] - 39, point[1] - 40))
                self.assertEqual(wretched_preview(frame, point, ocr, round_footprint=True), expected)

    def test_opening_ready_accepts_native_required_exclamation_ocr(self):
        from PIL import Image
        from tds_auto.hardcore_vision import wretched_ready
        from tds_auto.resources import LocalOCR
        frame=Image.new('RGB',(1920,991))
        with Image.open(ROOT/'tests/fixtures/wretched_ready_required_exclamation_native.png') as crop:
            frame.paste(crop,(819,156))
        self.assertTrue(wretched_ready(frame,LocalOCR()))

    def test_opening_preview_preserves_exact_ready_caption_against_terrain(self):
        from PIL import Image
        from tds_auto.hardcore_vision import wretched_match_ready, wretched_ready
        from tds_auto.resources import LocalOCR

        frame = Image.new('RGB', (1920, 991))
        with Image.open(ROOT / 'tests' / 'fixtures' / 'hardcore_ready_preview_terrain.png') as crop:
            frame.paste(crop, (819, 156))
        ocr = LocalOCR()
        self.assertTrue(wretched_ready(frame, ocr))
        observer = Mock()
        observer.observe.return_value.state = 'unknown'
        self.assertTrue(wretched_match_ready(frame, observer, ocr))
        observer.observe.return_value.state = 'defeat'
        self.assertFalse(wretched_match_ready(frame, observer, ocr))
        observer.observe.return_value.state = 'unknown'
        frame.paste((0, 0, 0), (819, 156, 945, 196))
        self.assertFalse(wretched_match_ready(frame, observer, ocr))

    def test_masked_upgrade_panel_preserves_the_exact_boomerang_and_level(self):
        from PIL import Image
        from tds_auto.resources import HudReader

        with Image.open(ROOT / 'tests' / 'fixtures' / 'hardcore_boomerang_panel_title.png') as panel:
            hud = HudReader(hardcore=True).read(panel)
        self.assertEqual((hud.tower_name, hud.level), ('Boomerang', 2))

    def test_camera_shift_stops_and_records_bound_vs_observed_offsets(self):
        from PIL import Image
        from tds_auto.control import StopRun
        from tds_auto.hardcore_match import HardcoreMatchV2

        worker=HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.camera=Mock()
        worker.camera.offset=(-28,-1)
        worker.camera.estimate.return_value=(-20,-1)
        worker.session=Mock()
        worker.session.now.return_value=0
        worker.session.frame.return_value=Image.new('RGB',(1920,991))
        worker.session.observer.result_banner.return_value=None
        worker.driver=Mock()
        with self.assertRaisesRegex(StopRun,'camera is unverified'):
            worker.frame(require_speed=False)
        worker.session.status.assert_called_once_with(
            'hardcore_camera_unverified',bound_offset=(-28,-1),observed_offset=(-20,-1))
        worker.driver.click.assert_not_called()

    def test_native_disconnect_dialog_is_not_misreported_as_camera_drift(self):
        from PIL import Image
        from tds_auto.control import StopRun
        from tds_auto.hardcore_match import HardcoreMatchV2
        worker=HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.camera=Mock()
        worker.camera.offset=(-23,-15)
        worker.camera.estimate.return_value=None
        worker.session=Mock()
        worker.session.now.side_effect=[0,2]
        with Image.open(ROOT/'tests/fixtures/disconnect_leave_prompt.png') as image:
            worker.session.frame.return_value=image.copy()
        worker.session.observer.result_banner.return_value=None
        worker.last_wave=27
        worker.driver=Mock()
        with self.assertRaises(StopRun) as failure:
            worker.frame(require_speed=False)
        self.assertIn('disconnected',str(failure.exception).lower())
        self.assertEqual(failure.exception.kind,'failure')
        self.assertTrue(worker.session.save_frame.called)
        worker.driver.key.assert_not_called()
        worker.driver.click.assert_not_called()
        worker.driver.move.assert_not_called()

    def test_camera_uses_all_three_landmarks_at_the_first_wave(self):
        from PIL import Image
        from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2
        from tds_auto.hardcore_vision import WretchedCamera

        camera = WretchedCamera(load_hardcore_plan_v2())
        with Image.open(ROOT / 'tests' / 'fixtures' / 'hardcore_camera_three_landmark_consensus.png') as source:
            frame = source.copy()
        self.assertEqual(camera.estimate(frame), (-7, -13))
        frame.paste((0, 0, 0), (1420, 520, 1610, 770))
        self.assertIsNone(camera.estimate(frame))

    def test_shifted_gate_matches_only_the_known_walkway_and_rejects_occlusion(self):
        from PIL import Image
        from tds_auto.hardcore_vision import ROUTE_SIDES, ROUTE_TILE_SIZE, WretchedRoute

        route = WretchedRoute('wretched_front_hardcore_v2')
        width, height = ROUTE_TILE_SIZE
        # The historical v2.20.0 tile atlas is not selectable by the single
        # v0.3.1 route; old gate views must fail closed.
        for sample, expected in (('shifted_gate', []), ('shifted_gate_effect', []), ('occluded_gate', [])):
            with self.subTest(sample=sample):
                frame = Image.new('L', (1920, 991))
                with Image.open(ROOT / 'tests' / 'fixtures' / f'hardcore_route_{sample}.png') as tiles:
                    for index, (x0,y0,x1,y1) in enumerate(ROUTE_SIDES):
                        tile = tiles.crop((index*width,0,(index+1)*width,height))
                        frame.paste(tile.resize((x1-x0,y1-y0),Image.Resampling.NEAREST),(x0,y0))
                self.assertEqual([i for i in range(len(route.steps)) if route.matches(frame,i)], expected)

    def test_single_route_requires_positive_spawn_before_first_right_input(self):
        from PIL import Image
        from tds_auto.control import StopRun
        from tds_auto.hardcore_match import HardcoreMatchV2
        from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2
        from tds_auto.hardcore_vision import ROUTE_STEPS_V031

        for matched in (False,True):
            with self.subTest(matched=matched):
                worker=HardcoreMatchV2.__new__(HardcoreMatchV2)
                worker.plan=load_hardcore_plan_v2()
                worker.session=Mock()
                worker.driver=Mock()
                worker.camera=Mock()
                frame=Image.new('RGB',(1920,991))
                missing=(frame,None,None,False)
                confirmed=(frame,None,0,True)
                worker.settled_camera_view=Mock(side_effect=[confirmed,missing] if matched else [missing])
                route=SimpleNamespace(steps=ROUTE_STEPS_V031)
                with patch('tds_auto.hardcore_match.WretchedRoute',return_value=route):
                    with self.assertRaisesRegex(StopRun,'terrain did not verify'):
                        worker.align_camera()
                if matched:
                    worker.driver.key.assert_called_once_with('D',.30)
                else:
                    worker.driver.key.assert_not_called()
                worker.driver.orbit.assert_not_called()
                worker.driver.zoom.assert_not_called()
                worker.driver.click.assert_not_called()

    def test_disconnect_during_camera_setup_reaches_transport_recovery_without_input(self):
        from tds_auto.control import StopRun
        from tds_auto.hardcore_match import HardcoreMatchV2

        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.session = Mock()
        worker.session.now.return_value = 0
        worker.driver = Mock()
        worker.route_ready = Mock(return_value=False)
        with patch('tds_auto.recovery.disconnect_prompt', return_value=True) as disconnect:
            with self.assertRaises(StopRun) as stopped:
                worker.settled_camera_view(Mock(), ())
        self.assertEqual(stopped.exception.kind, 'failure')
        self.assertEqual(disconnect.call_count, 2)
        self.assertEqual(worker.driver.method_calls, [unittest.mock.call.wait(.2)])

    def test_runtime_loads_only_the_exact_bundled_v2_sequence(self):
        from tds_auto.hardcore_plan import HardcorePlanError
        from tds_auto.hardcore_plan_v2 import PLAN_PATH, load_hardcore_plan_v2

        plan = load_hardcore_plan_v2()
        self.assertEqual([phase.step for phase in plan.phases], list(range(1, 15)))
        self.assertTrue(plan.phases[0].before_ready)
        self.assertEqual(dict(plan.final_required_levels), self.plan["final_required_levels"])
        self.assertEqual((plan.finish_wave, plan.min_target_observations), (30, 2))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / PLAN_PATH
            candidate.parent.mkdir()
            candidate.write_bytes(PLAN.read_bytes() + b'\n')
            with patch('tds_auto.hardcore_plan_v2.ROOT', root):
                with self.assertRaisesRegex(HardcorePlanError, 'digest changed'):
                    load_hardcore_plan_v2()

    def test_cheapest_farm_upgrade_and_ordered_defense(self):
        from tds_auto.hardcore_match import v2_phase_purchase
        from tds_auto.hardcore_plan import HardcoreOperation

        f1 = HardcoreOperation('upgrade', 'F1', 2)
        f2 = HardcoreOperation('upgrade', 'F2', 1)
        b1 = HardcoreOperation('place', 'B1')
        prices = {'F1': 600, 'F2': 200, 'B1': 550}
        levels = {'F1': 1, 'F2': 0}
        price = lambda action, _: prices[action.tower_id]
        tower = lambda action: 'Boomerang' if action.tower_id == 'B1' else 'Farm'
        self.assertEqual(v2_phase_purchase([f1, f2], levels, tower, price, 900), 1)
        self.assertIsNone(v2_phase_purchase([b1, f2], levels, tower, price, 500))
        self.assertEqual(v2_phase_purchase([b1, f2], levels, tower, price, 550), 0)

    def test_placement_arms_once_then_relies_on_live_preview_cash_guard(self):
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud

        worker=HardcoreMatch.__new__(HardcoreMatch)
        worker.levels={}
        worker.recorded_wait=set()
        worker.camera=Mock()
        worker.camera.point.return_value=(900,380)
        worker.driver=Mock()
        worker.ocr=Mock()
        worker.session=Mock()
        worker.read=Mock(return_value=(None,Hud(cash=1250,tower_count=0,wave=0)))
        worker.commit_placement=Mock(return_value=True)
        tower=SimpleNamespace(tower_id='F1',tower_type='Farm',slot=3)
        with patch('tds_auto.hardcore_match.wretched_price',return_value=300):
            self.assertTrue(worker.place(tower,29))
        # The commit callback still performs its own independent live quote,
        # preview/footprint and post-click count/level verification.
        worker.read.assert_called_once_with({0},29)
        worker.driver.key.assert_called_once_with('3')
        worker.commit_placement.assert_called_once_with(tower,29,(900,380),0,300)

    def test_placement_rechecks_cash_after_slot_before_any_mouse_down(self):
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud
        from tds_auto.control import StopRun

        worker=HardcoreMatch.__new__(HardcoreMatch)
        worker.levels={}
        worker.recorded_wait=set()
        worker.camera=Mock()
        worker.camera.point.return_value=(900,380)
        worker.driver=Mock()
        worker.ocr=Mock()
        worker.session=Mock()
        worker.session.now.side_effect=[0,3]
        worker.frame=Mock(return_value=None)
        worker.read=Mock(side_effect=[
            (None,Hud(cash=1250,tower_count=0,wave=0)),
            (None,Hud(cash=100,tower_count=0,wave=0)),
        ])
        worker.click=Mock(side_effect=lambda point, guard: guard())
        worker.confirm=Mock()
        tower=SimpleNamespace(tower_id='F1',tower_type='Farm',slot=3)
        with patch('tds_auto.hardcore_match.wretched_price',return_value=300):
            with self.assertRaisesRegex(StopRun,'Placement price or cash changed'):
                worker.place(tower,29)
        worker.click.assert_called_once()
        worker.confirm.assert_not_called()
        worker.session.save_frame.assert_called_once()
        self.assertEqual(worker.levels,{})

    def test_armed_placement_rechecks_transient_missing_price_before_click(self):
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud

        worker=HardcoreMatch.__new__(HardcoreMatch)
        worker.levels={}
        worker.recorded_wait=set()
        worker.camera=Mock()
        worker.camera.point.return_value=(900,380)
        worker.driver=Mock()
        worker.ocr=Mock()
        worker.session=Mock()
        worker.session.now.return_value=0
        worker.read=Mock(side_effect=[
            (None,Hud(cash=1250,tower_count=0,wave=0)),
            (None,Hud(cash=1250,tower_count=0,wave=0)),
            (None,Hud(cash=1250,tower_count=0,wave=0)),
        ])
        worker.click=Mock(side_effect=lambda point,guard: guard())
        worker.confirm=Mock(return_value=Hud(cash=950,tower_count=1,tower_name='Farm',level=0,wave=0))
        worker.record=Mock()
        tower=SimpleNamespace(tower_id='F1',tower_type='Farm',slot=3)
        with patch('tds_auto.hardcore_match.wretched_price',side_effect=[300,None,300]) as quote:
            with patch('tds_auto.hardcore_match.wretched_preview',return_value=True) as preview:
                self.assertTrue(worker.place(tower,29))
        self.assertEqual(quote.call_count,3)
        preview.assert_called_once()
        worker.driver.key.assert_called_once_with('3')
        worker.driver.wait.assert_called_once_with(.15)
        worker.click.assert_called_once()
        self.assertEqual(worker.levels,{'F1':0})

    def test_placement_cursor_moves_once_only_if_the_confirmed_count_lacks_a_panel(self):
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud

        placement = SimpleNamespace(tower_id='F1', tower_type='Farm')
        confirmed = Hud(tower_count=1, tower_name='Farm', level=0)
        for unconfirmed in ([], [Hud(tower_count=1), Hud(tower_count=1)]):
            with self.subTest(unconfirmed=len(unconfirmed)):
                worker = HardcoreMatch.__new__(HardcoreMatch)
                worker.session = Mock()
                worker.session.now.return_value = 0
                worker.driver = Mock()
                worker.read = Mock(side_effect=[(None, hud) for hud in [*unconfirmed, confirmed]])
                self.assertEqual(worker.confirm(placement, 0, {0, 1}, timeout=2, evidence=None), confirmed)
                self.assertEqual(worker.driver.move.call_count, min(1, len(unconfirmed)))
                worker.driver.click.assert_not_called()

    def test_hardcore_count_retains_literal_fraction_when_ocr_reads_the_slash_as_one(self):
        from PIL import Image
        from tds_auto.resources import HudReader, parse_count

        frame = Image.new('RGB', (1920, 991))
        with Image.open(ROOT / 'assets' / 'ui_2191' / 'count_14.png') as crop:
            frame.paste(crop, (1274, 940))
        reader = HudReader(hardcore=True)
        self.assertIsNone(parse_count('14 1 40'))
        self.assertEqual(reader.count_from_pixels(frame), 14)
        self.assertIsNone(HudReader().count_from_pixels(frame))
        frame = Image.new('RGB', (1920, 991))
        with Image.open(ROOT / 'tests' / 'fixtures' / 'hardcore_starting_tower_count.png') as crop:
            frame.paste(crop, (1270, 934))
        self.assertEqual(reader.read(frame).tower_count, 0)

    def test_hardcore_count_eighteen_from_native_text_glyph_not_ocr_guess(self):
        from PIL import Image, ImageChops
        from tds_auto.resources import HudReader, parse_count

        frame = Image.new('RGB', (1920, 991))
        with Image.open(ROOT/'tests/fixtures/hardcore_wave19_count18_native.png') as label:
            frame.paste(label, (1274, 940))
        reader = HudReader(hardcore=True)
        self.assertIsNone(parse_count('18140'))
        self.assertIsNone(parse_count('18 1 40'))
        self.assertEqual(reader.count_from_pixels(frame), 18)
        self.assertEqual(reader.read(frame).tower_count, 18)
        self.assertIsNone(HudReader().count_from_pixels(frame))
        self.assertIsNone(reader.count_from_pixels(ImageChops.offset(frame,24,0)))
        self.assertIsNone(reader.count_from_pixels(ImageChops.offset(frame,0,24)))

    def test_farm_upgrade_reuses_selection_but_checks_for_a_changed_quote_before_click(self):
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud

        worker = HardcoreMatch.__new__(HardcoreMatch)
        worker.levels = {'F1': 1}
        worker.selected = 'F1'
        worker.upgrade_costs = {}
        worker.recorded_wait = set()
        worker.session = Mock()
        worker.session.now.return_value = 0
        original = Hud(cash=600, tower_count=1, tower_name='Farm', level=1,
                       upgrade_cost=600, upgrade_affordable=True)
        changed = Hud(cash=600, tower_count=1, tower_name='Farm', level=1,
                      upgrade_cost=700, upgrade_affordable=False)
        worker.read = Mock(side_effect=[(None, original), (None, changed)])
        worker.driver = Mock()
        worker.click = Mock(side_effect=AssertionError('Upgrade must not move/click pointer'))
        self.assertFalse(worker.upgrade(SimpleNamespace(tower_id='F1', tower_type='Farm'), 2, 29))
        worker.driver.key.assert_not_called()
        self.assertEqual(worker.read.call_count, 2)
        self.assertEqual(worker.levels, {'F1': 1})
        worker.session.save_frame.assert_called_once()

    def test_owned_selection_retries_once_if_panel_stays_closed(self):
        from tds_auto.control import StopRun
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud
        worker=HardcoreMatch.__new__(HardcoreMatch)
        worker.levels={'C3':2}
        worker.selected='C2'
        worker.camera=Mock()
        worker.camera.point.return_value=(917,330)
        worker.ocr=Mock()
        worker.session=Mock()
        worker.session.now.return_value=0
        worker.driver=Mock()
        closed=Hud(cash=17805,tower_count=18,tower_name=None,level=None)
        opened=Hud(cash=17805,tower_count=18,tower_name='Crook Boss',level=2)
        worker.read=Mock(return_value=(object(),closed))
        worker.click=Mock(side_effect=lambda point,guard:guard())
        worker.confirm=Mock(side_effect=[
            StopRun('Could not confirm C3 level 2; no repeat click sent.'),
            opened])
        tower=SimpleNamespace(tower_id='C3',tower_type='Crook Boss')
        with patch('tds_auto.hardcore_match.wretched_hover',return_value=True) as hover:
            self.assertIs(worker.select(tower,25),opened)
        self.assertEqual(worker.click.call_count,2)
        self.assertEqual(worker.selected,'C3')
        self.assertGreaterEqual(hover.call_count,2)
        worker.driver.key.assert_not_called()
        worker.session.save_frame.assert_not_called()

    def test_selection_does_not_retry_third_time_after_second_failed_click(self):
        from tds_auto.control import StopRun
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud
        worker=HardcoreMatch.__new__(HardcoreMatch)
        worker.levels={'C3':2}
        worker.selected='C2'
        worker.camera=Mock()
        worker.camera.point.return_value=(917,330)
        worker.ocr=Mock()
        worker.session=Mock()
        worker.session.now.return_value=0
        worker.driver=Mock()
        worker.read=Mock(return_value=(object(),Hud(cash=17805,tower_count=18)))
        worker.click=Mock(side_effect=lambda point,guard:guard())
        worker.confirm=Mock(side_effect=StopRun('Could not confirm C3 level 2; no repeat click sent.'))
        with patch('tds_auto.hardcore_match.wretched_hover',return_value=True):
            with self.assertRaises(StopRun):
                worker.select(SimpleNamespace(tower_id='C3',tower_type='Crook Boss'),25)
        self.assertEqual(worker.click.call_count,2)
        self.assertEqual(worker.confirm.call_count,2)
        self.assertEqual(worker.selected,'C2')
        worker.driver.key.assert_not_called()

    def test_selection_never_retries_if_a_different_tower_panel_is_open(self):
        from tds_auto.control import StopRun
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud
        worker=HardcoreMatch.__new__(HardcoreMatch)
        worker.levels={'C3':2}
        worker.selected='C2'
        worker.camera=Mock()
        worker.camera.point.return_value=(917,330)
        worker.ocr=Mock()
        worker.session=Mock()
        worker.session.now.return_value=0
        worker.driver=Mock()
        closed=Hud(cash=17805,tower_count=18,tower_name=None,level=None)
        wrong=Hud(cash=17805,tower_count=18,tower_name='Farm',level=3,upgrade_cost=0)
        worker.read=Mock(side_effect=[(object(),closed),(object(),closed),
                                      (object(),wrong)])
        worker.click=Mock(side_effect=lambda point,guard:guard())
        worker.confirm=Mock(side_effect=StopRun('Could not confirm C3 level 2; no repeat click sent.'))
        with patch('tds_auto.hardcore_match.wretched_hover',return_value=True):
            with self.assertRaises(StopRun):
                worker.select(SimpleNamespace(tower_id='C3',tower_type='Crook Boss'),25)
        worker.click.assert_called_once()
        worker.driver.key.assert_not_called()
        self.assertEqual(worker.selected,'C2')

    def test_upgrade_rechecks_transient_unreadable_selected_level(self):
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud
        worker=HardcoreMatch.__new__(HardcoreMatch)
        worker.levels={'F2':1}
        worker.recorded_wait=set()
        worker.upgrade_costs={}
        worker.session=Mock()
        worker.session.now.return_value=0
        worker.driver=Mock()
        original=Hud(cash=1100,tower_count=1,tower_name='Farm',level=1,
                     upgrade_cost=600,upgrade_affordable=True)
        unreadable=Hud(cash=1100,tower_count=1,tower_name='Farm',level=None,
                       upgrade_cost=600,upgrade_affordable=True)
        worker.select=Mock(return_value=original)
        worker.read=Mock(side_effect=[(None,unreadable),(None,original)])
        worker.confirm=Mock(return_value=Hud(tower_count=1,tower_name='Farm',level=2))
        worker.record=Mock()
        tower=SimpleNamespace(tower_id='F2',tower_type='Farm')
        self.assertTrue(worker.upgrade(tower,2,29))
        worker.driver.wait.assert_called_once_with(.15)
        worker.driver.key.assert_called_once_with('E',.10)
        worker.session.save_frame.assert_not_called()

    def test_upgrade_persistent_wrong_tower_never_sends_e(self):
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud
        from tds_auto.control import StopRun
        worker=HardcoreMatch.__new__(HardcoreMatch)
        worker.levels={'F2':1}
        worker.recorded_wait=set()
        worker.upgrade_costs={}
        worker.session=Mock()
        worker.session.now.side_effect=[0,3]
        worker.driver=Mock()
        original=Hud(cash=1100,tower_count=1,tower_name='Farm',level=1,
                     upgrade_cost=600,upgrade_affordable=True)
        wrong=Hud(cash=1100,tower_count=1,tower_name='Crook Boss',level=1,
                  upgrade_cost=600,upgrade_affordable=True)
        worker.select=Mock(return_value=original)
        worker.read=Mock(return_value=(None,wrong))
        worker.confirm=Mock()
        with self.assertRaisesRegex(StopRun,'Upgrade tower or level changed'):
            worker.upgrade(SimpleNamespace(tower_id='F2',tower_type='Farm'),2,29)
        worker.driver.key.assert_not_called()
        worker.confirm.assert_not_called()
        worker.session.save_frame.assert_called_once()

    def test_verified_selected_upgrade_uses_e_without_pointer_movement(self):
        from tds_auto.hardcore_match import HardcoreMatch
        from tds_auto.resources import Hud

        worker=HardcoreMatch.__new__(HardcoreMatch)
        worker.levels={'F1':1}
        worker.recorded_wait=set()
        worker.upgrade_costs={}
        worker.session=Mock()
        worker.session.now.return_value=0
        worker.driver=Mock()
        original=Hud(cash=1100,tower_count=1,tower_name='Farm',level=1,
                     upgrade_cost=600,upgrade_affordable=True)
        upgraded=Hud(cash=500,tower_count=1,tower_name='Farm',level=2)
        worker.select=Mock(return_value=original)
        worker.read=Mock(return_value=(None,original))
        worker.click=Mock(side_effect=AssertionError('Upgrade should not click'))
        worker.confirm=Mock(return_value=upgraded)
        worker.record=Mock()
        tower=SimpleNamespace(tower_id='F1',tower_type='Farm')
        self.assertTrue(worker.upgrade(tower,2,29))
        worker.driver.key.assert_called_once_with('E',0.10)
        worker.click.assert_not_called()
        worker.confirm.assert_called_once()
        self.assertTrue(worker.confirm.call_args.kwargs['evidence'].endswith('.jpg'))
        self.assertEqual(worker.levels,{'F1':2})

    def test_overdue_defense_keeps_priority_until_affordable(self):
        from tds_auto.hardcore_match import HardcoreMatchV2
        from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2

        plan=load_hardcore_plan_v2()
        worker=HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.levels={'F1':1}
        worker.plan_actions={(a.tower_id,a.level or 0):a
                             for phase in plan.phases for a in phase.actions}
        price=lambda action,level:550
        self.assertEqual(worker.urgent_defense(2,price,550),(None,None,None))
        self.assertEqual(worker.urgent_defense(3,price,500),(4,None,550))
        due,action,_=worker.urgent_defense(3,price,550)
        self.assertEqual((due,action.tower_id,action.operation),(4,'B1','place'))
        self.assertEqual(worker.urgent_defense(5, price, 500), (4, None, 550))
        due, action, _ = worker.urgent_defense(5, price, 550)
        self.assertEqual((due, action.tower_id), (4, 'B1'))
        worker.levels['B1'] = 2
        self.assertEqual(worker.urgent_defense(7, price, 2500), (None, None, None))
        # Keep wave 8 for finishing F5's affordable farm upgrades; Crook
        # reservation begins at wave 9 and remains overdue after wave 11.
        self.assertEqual(worker.urgent_defense(8, price, 2500), (None, None, None))
        due, action, _ = worker.urgent_defense(9, price, 2500)
        self.assertEqual((due, action.tower_id, action.operation), (11, 'C1', 'place'))

    def test_phase11_restores_early_b1_max_from_only_credited_run(self):
        from tds_auto.hardcore_match import HardcoreMatchV2, v2_phase_purchase
        from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2
        plan=load_hardcore_plan_v2()
        worker=HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.plan_actions={(a.tower_id,a.level or 0):a
                             for phase in plan.phases for a in phase.actions}
        worker.levels={'B1':3,'C1':2,'C2':2,'B2':3,'B3':3,
                       'C3':2,'C4':2,'C5':2}
        price=lambda action,level:7000 if action.tower_id=='B1' else 14000
        phase=plan.phases[10]
        self.assertEqual([(a.tower_id,a.level) for a in phase.actions],
                         [('B1',4),('C1',3),('C2',3)])
        self.assertEqual(worker.urgent_defense(21,price,7000),(None,None,None))
        self.assertEqual(v2_phase_purchase(
            phase.actions,worker.levels,lambda action:'Crook Boss' if action.tower_id!='B1' else 'Boomerang',
            price,7000),0)
        self.assertEqual(v2_phase_purchase(
            phase.actions,worker.levels,lambda action:'Crook Boss' if action.tower_id!='B1' else 'Boomerang',
            price,14000),0)
        worker.levels['B1']=4
        self.assertEqual(v2_phase_purchase(
            phase.actions[1:],worker.levels,lambda action:'Crook Boss',
            price,14000),0)

    def test_proven_boomerang_first_late_order_preserved(self):
        phases=self.plan['phases']
        self.assertEqual([ (a['tower_id'],a.get('level')) for a in phases[12]['actions']],
                         [('C3',3),('B2',4),('B3',4)])
        self.assertEqual([ (a['tower_id'],a.get('level')) for a in phases[13]['actions']],
                         [('C4',3),('C5',3)])

    def test_farm_investment_preserves_quotes_and_pays_back_before_spending_stops(self):
        from tds_auto.hardcore_match import farm_investment_fits

        self.assertTrue(farm_investment_fits(200,40,5826,3560,400,13))
        self.assertTrue(farm_investment_fits(200,40,2000,3560,14000,9))
        self.assertFalse(farm_investment_fits(200,40,250,3560,3800,12))
        self.assertFalse(farm_investment_fits(600,125,800,3560,None,4))
        # A $200 Farm investment briefly pushes a $1,550 defense from
        # immediately affordable to one payout away. It is acceptable only
        # when that payout still precedes the observed defense deadline.
        self.assertFalse(farm_investment_fits(200,40,1600,1000,1550,11))
        self.assertTrue(farm_investment_fits(
            200,40,1600,1000,1550,11,defense_slack_payouts=1))
        self.assertFalse(farm_investment_fits(
            200,40,1600,1000,1550,11,defense_slack_payouts=0))

    def test_farm_economy_does_not_jump_ahead_to_f9_before_phase_eight(self):
        from tds_auto.hardcore_match import HardcoreMatchV2
        from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2

        plan = load_hardcore_plan_v2()
        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.plan = plan
        worker.towers = {tower.tower_id: tower for tower in plan.towers}
        worker.levels = {'B1': 3, 'C1': 2, 'F6': 0, 'F9': 2}
        worker.later_farm_actions = tuple(
            (phase.step, action) for phase in plan.phases for action in phase.actions
            if action.tower_id in plan.highest_upgrade_first)
        def price(action, current):
            return {1: 200, 2: 600, 3: 1250}.get(action.level, 300)
        chosen = worker.farm_economy_purchase(16, 5000, price, 20000, 6)
        self.assertEqual((chosen.tower_id, chosen.level), ('F6', 1))

    def test_overdue_unaffordable_defense_still_checks_safe_farm_investments(self):
        from tds_auto.hardcore_match import HardcoreMatchV2, TargetWaveReached
        from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2
        from tds_auto.resources import Hud

        plan = load_hardcore_plan_v2()
        phase = plan.phases[5]  # F6/F7/F8 farm window
        farm = next(a for a in phase.actions if a.tower_id == 'F6' and a.level == 1)
        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.plan = plan
        worker.levels = {'F6': 0}
        worker.towers = {tower.tower_id: tower for tower in plan.towers}
        worker.session = Mock()
        worker.session.now.return_value = 0
        worker.frame = Mock()
        worker.read = Mock(side_effect=[
            (None, Hud(cash=2000, tower_count=1, wave=20)),
            TargetWaveReached(),
        ])
        worker.driver = Mock()
        worker.missed_defense_deadlines = {18}
        worker.urgent_defense = Mock(return_value=(18, None, 6500))
        worker.crook_upgrade_priority = Mock(return_value=(False, None))
        worker.farm_economy_purchase = Mock(return_value=farm)
        worker.upgrade = Mock(return_value=True)
        with self.assertRaises(TargetWaveReached):
            worker.play_phase(phase, 20)
        worker.farm_economy_purchase.assert_called_once()
        worker.upgrade.assert_called_once()

    def test_each_placed_crook_holds_budget_until_its_second_upgrade(self):
        from tds_auto.hardcore_match import HardcoreMatchV2
        from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2

        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.plan = load_hardcore_plan_v2()
        worker.towers = {tower.tower_id:tower for tower in worker.plan.towers}
        worker.plan_actions = {(action.tower_id,action.level or 0):action
                               for phase in worker.plan.phases for action in phase.actions}
        worker.levels = {'C1':2,'C2':2,'C3':0,'B1':3,'F8':1}
        price = lambda action, current: (1500,2750)[current]
        due, action = worker.crook_upgrade_priority(price, 1500)
        self.assertTrue(due)
        self.assertEqual((action.tower_id,action.level),('C3',1))
        worker.levels['C3'] = 1
        self.assertEqual(worker.crook_upgrade_priority(price, 2500), (True,None))
        due, action = worker.crook_upgrade_priority(price, 2750)
        self.assertTrue(due)
        self.assertEqual((action.tower_id,action.level),('C3',2))
        worker.levels['C3'] = 2
        self.assertEqual(worker.crook_upgrade_priority(price, 2750), (False,None))

    def test_later_farms_take_costliest_affordable_upgrade_ahead_of_placement(self):
        from tds_auto.hardcore_match import v2_phase_purchase
        from tds_auto.hardcore_plan import HardcoreOperation

        actions = [HardcoreOperation('place', 'F8', None, False),
                   HardcoreOperation('upgrade', 'F6', 1, False),
                   HardcoreOperation('upgrade', 'F7', 2, False),
                   HardcoreOperation('upgrade', 'F7', 3, False)]
        prices = (300, 200, 600, 1250)
        def pick(cash):
            return v2_phase_purchase(actions, {'F6': 0, 'F7': 1}, lambda _: 'Farm',
                                     lambda action, _: prices[actions.index(action)], cash,
                                     highest_upgrade_first={'F6', 'F7', 'F8', 'F9', 'F10'})

        self.assertEqual(pick(1500), 2)
        self.assertEqual(pick(500), 1)
        self.assertIsNone(pick(100))

    def test_hardcore_wave_transition_confirmation_has_bounded_passive_settle(self):
        from tds_auto.hardcore_match import HardcoreMatchV2
        from tds_auto.resources import Hud
        worker=HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.session=Mock()
        worker.session.now.side_effect=[0,5.1]
        worker.driver=Mock()
        worker.frame=Mock(side_effect=['first_wave12','second_wave12'])
        worker.reader=Mock()
        worker.reader.read.return_value=Hud(cash=3594,tower_count=7,wave=12)
        worker.opening=False
        worker.plan=SimpleNamespace(finish_wave=30)
        worker.last_wave=11
        worker.next_wave=None
        worker.completed=26
        worker.target_observations=0
        frame,hud=worker.read({7})
        self.assertEqual((frame,hud.wave),('second_wave12',12))
        self.assertEqual(worker.last_wave,12)
        worker.driver.wait.assert_called_once_with(.15)
        worker.session.save_frame.assert_not_called()

    def test_hardcore_persistent_wave_unknown_stops_after_bounded_settle(self):
        from tds_auto.hardcore_match import HardcoreMatchV2
        from tds_auto.resources import Hud
        from tds_auto.control import StopRun
        worker=HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.session=Mock()
        worker.session.now.side_effect=[0,1,3,5.5,7.2]
        worker.driver=Mock()
        worker.frame=Mock(return_value='unknown_wave')
        worker.reader=Mock()
        worker.reader.read.return_value=Hud(cash=3594,tower_count=7,wave=None)
        worker.opening=False
        worker.plan=SimpleNamespace(finish_wave=30)
        worker.last_wave=11
        worker.next_wave=None
        worker.target_observations=0
        with self.assertRaisesRegex(StopRun,'unreadable'):
            worker.read({7})
        worker.session.save_frame.assert_called_once_with(
            'unknown_wave','hardcore_hud_unreadable.png')

    def test_wave_advance_at_hud_read_deadline_gets_one_passive_confirmation(self):
        # Native late wave-12 evidence was valid at the exact timeout but
        # needed a second fresh frame to satisfy the monotonic wave gate.
        from tds_auto.hardcore_match import HardcoreMatchV2
        from tds_auto.resources import Hud
        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.plan = SimpleNamespace(finish_wave=30)
        worker.session = Mock()
        worker.session.now.side_effect = [0, 5, 5]
        worker.frame = Mock(side_effect=['wave12_first', 'wave12_second'])
        worker.reader = Mock()
        worker.reader.read.side_effect = [
            Hud(cash=3594, tower_count=7, wave=12),
            Hud(cash=3594, tower_count=7, wave=12)]
        worker.driver = Mock()
        worker.opening = False
        worker.last_wave = 11
        worker.next_wave = None
        worker.completed = 26
        worker.target_observations = 0
        worker.min_target_observations = 2
        frame,hud = worker.read({7},29)
        self.assertEqual((frame,hud.wave),('wave12_second',12))
        self.assertEqual(worker.last_wave,12)
        worker.driver.wait.assert_called_once_with(.15)
        worker.session.save_frame.assert_not_called()
        worker.driver.click.assert_not_called()

    def test_wave_advance_confirmation_does_not_accept_lost_evidence(self):
        from tds_auto.control import StopRun
        from tds_auto.hardcore_match import HardcoreMatchV2
        from tds_auto.resources import Hud
        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.plan = SimpleNamespace(finish_wave=30)
        worker.session = Mock()
        worker.session.now.side_effect = [0, 5, 7.2]
        worker.frame = Mock(side_effect=['wave12_first','unreadable'])
        worker.reader = Mock()
        worker.reader.read.side_effect = [
            Hud(cash=3594, tower_count=7, wave=12),
            Hud(cash=3594, tower_count=7, wave=None)]
        worker.driver = Mock()
        worker.opening = False
        worker.last_wave = 11
        worker.next_wave = None
        worker.completed = 26
        worker.target_observations = 0
        worker.min_target_observations = 2
        with self.assertRaisesRegex(StopRun,'unreadable'):
            worker.read({7},29)
        self.assertEqual(worker.last_wave,11)
        worker.driver.wait.assert_called_once_with(.15)
        worker.session.save_frame.assert_called_once_with('unreadable','hardcore_hud_unreadable.png')
        worker.driver.click.assert_not_called()

    def test_purchase_guard_accepts_overdue_wave_but_stops_at_thirty(self):
        from tds_auto.hardcore_match import HardcoreMatchV2, TargetWaveReached
        from tds_auto.resources import Hud

        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.plan = SimpleNamespace(finish_wave=30)
        worker.session = Mock()
        worker.session.now.return_value = 0
        worker.frame = Mock()
        worker.reader = Mock()
        worker.reader.read.side_effect = [Hud(cash=550, tower_count=4, wave=20),
                                          Hud(cash=550, tower_count=4, wave=30),
                                          Hud(cash=16117, tower_count=19, wave=30),
                                          Hud(cash=16117, tower_count=19, wave=31)]
        worker.opening = False
        worker.observe_wave = Mock(return_value=True)
        self.assertEqual(worker.read({4}, 19)[1].wave, 20)
        with self.assertRaises(TargetWaveReached):
            worker.read({4}, 29)
        self.assertEqual(worker.read({19}, 30)[1].cash, 16117)
        with self.assertRaises(TargetWaveReached):
            worker.read({19}, 30)

    def test_opening_ready_rechecks_one_transient_frame_without_mouse_down(self):
        from tds_auto.hardcore_match import HardcoreMatchV2

        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.frame = Mock(side_effect=['transient', 'ready'])
        worker.ready_frame = Mock(side_effect=[False, True])
        worker.session = Mock()
        worker.driver = Mock()
        worker.confirm_opening_ready()
        self.assertEqual(worker.frame.call_count, 2)
        worker.driver.wait.assert_called_once_with(.2)
        worker.session.save_frame.assert_called_once_with('ready', 'hardcore_opening_farms_ready.png')
        worker.driver.click.assert_not_called()

    def test_opening_ready_recovers_after_multiple_blank_ocr_frames(self):
        from tds_auto.hardcore_match import HardcoreMatchV2
        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.frame = Mock(side_effect=['unreadable']*5+['ready'])
        worker.ready_frame = Mock(side_effect=[False]*5+[True])
        worker.session = Mock()
        worker.driver = Mock()
        worker.confirm_opening_ready()
        self.assertEqual(worker.frame.call_count, 6)
        self.assertEqual(worker.driver.wait.call_count, 5)
        worker.session.save_frame.assert_called_once_with('ready', 'hardcore_opening_farms_ready.png')
        worker.driver.click.assert_not_called()

    def test_opening_ready_persistent_unknown_stops_with_evidence(self):
        from tds_auto.control import StopRun
        from tds_auto.hardcore_match import HardcoreMatchV2

        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.frame = Mock(side_effect=['unknown'+str(i) for i in range(12)])
        worker.ready_frame = Mock(return_value=False)
        worker.session = Mock()
        worker.driver = Mock()
        with self.assertRaisesRegex(StopRun, 'Ready changed before click'):
            worker.confirm_opening_ready()
        self.assertEqual(worker.frame.call_count, 12)
        self.assertEqual(worker.driver.wait.call_count, 11)
        worker.session.save_frame.assert_called_once_with(
            'unknown11', 'hardcore_ready_preclick_unverified.png')
        worker.driver.click.assert_not_called()


if __name__ == "__main__":
    unittest.main()
