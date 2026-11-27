import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tds_auto.control import GuardedInput, StopRun
from tds_auto.resources import Hud
from test_control import FakeOS
from test_navigation import Clock
try:
    from tds_auto.match import MatchRunner, Snapshot
except ImportError:
    MatchRunner = None


class MatchTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(MatchRunner, "supervised match action gates are not implemented")
        self.platform, self.clock = FakeOS(), Clock()

    def make(self, snapshots):
        iterator = iter(snapshots)
        last = snapshots[-1]
        def read():
            nonlocal last
            last = next(iterator, last)
            return last
        return MatchRunner(GuardedInput(self.platform.window, self.platform), read,
                           self.clock.now, self.clock.sleep,slot=2)

    def shot(self, cash=350, count=1, level=1, cost=600, camera=True, state="in_match", preview=True, hotbar=True,placement=250):
        return Snapshot(state, Hud(cash, count, "Scout", level, cost, 2,cash is not None and cost is not None and cash>=cost), camera, preview, hotbar,placement)

    def test_upgrade_waits_for_cash_and_confirms_increment_once(self):
        run = self.make([self.shot(), self.shot(), self.shot(cash=650), self.shot(cash=660), self.shot(cash=60,level=2,cost=2000)])
        result = run.upgrade((855,330), expected_level=1, count=1, timeout=3)
        self.assertEqual(result.level, 2)
        self.assertEqual(self.platform.events.count(("left_down",)), 3)  # deselect, select, one upgrade

    def test_upgrade_normalizes_open_selection_before_selecting_target(self):
        run=self.make([self.shot(), self.shot(), self.shot(cash=700), self.shot(cash=700), self.shot(level=2)])
        run.upgrade((855,330),1,1)
        moves=[event for event in self.platform.events if event[0]=='move']
        self.assertEqual(moves[:2], [('move',1450,529),('move',855,359)])

    def test_one_verified_hovered_scout_can_be_reselected_without_retrying_spend(self):
        from types import SimpleNamespace
        initial=self.shot(cash=5000,count=8,level=2,cost=4000)
        hidden=SimpleNamespace(state='in_match',hud=Hud(5000,8,None,None,None,12),camera_ok=True,hovered_scout=True)
        selected=self.shot(cash=5000,count=8,level=2,cost=4000)
        upgraded=self.shot(cash=1000,count=8,level=3,cost=4000)
        def read():
            clicks=self.platform.events.count(('left_down',))
            return initial if clicks<2 else hidden if clicks==2 else selected if clicks==3 else upgraded
        run=MatchRunner(GuardedInput(self.platform.window,self.platform),read,self.clock.now,self.clock.sleep,slot=2,hover_check=lambda point:True)
        self.assertEqual(run.upgrade((1020,328),expected_level=2,count=8,timeout=10).level,3)
        self.assertEqual(self.platform.events.count(('left_down',)),4)  # Deselect, select, reselect, one purchase

    def test_missing_hover_evidence_stops_without_another_selection_click(self):
        from types import SimpleNamespace
        initial=self.shot(cash=5000,count=8,level=2,cost=4000)
        hidden=SimpleNamespace(state='in_match',hud=Hud(5000,8,None,None,None,12),camera_ok=True,hovered_scout=False)
        def read():return initial if self.platform.events.count(('left_down',))<2 else hidden
        run=MatchRunner(GuardedInput(self.platform.window,self.platform),read,self.clock.now,self.clock.sleep,slot=2,hover_check=lambda point:False)
        with self.assertRaisesRegex(StopRun,'Selected tower/level/count'):
            run.upgrade((1020,328),expected_level=2,count=8,timeout=10)
        self.assertEqual(self.platform.events.count(('left_down',)),2)

    def test_upgrade_waits_for_panel_animation_without_reclicking(self):
        run=self.make([self.shot(),self.shot(level=None,cost=None),self.shot(cash=700),self.shot(cash=700),self.shot(level=2)])
        self.assertEqual(run.upgrade((855,330),1,1).level,2)
        self.assertEqual(self.platform.events.count(('left_down',)),3)

    def test_insufficient_cash_times_out_without_upgrade_click(self):
        with self.assertRaisesRegex(StopRun, "cash"):
            self.make([self.shot()]).upgrade((855,330), 1, 1, timeout=1)
        self.assertEqual(self.platform.events.count(("left_down",)), 2)

    def test_wrong_camera_or_state_sends_no_input(self):
        for shot in (self.shot(camera=False), self.shot(camera=None), self.shot(state="unknown")):
            with self.assertRaises(StopRun):
                self.make([shot]).upgrade((855,330), 1, 1)
        self.assertEqual(self.platform.events, [])

    def test_missing_cash_or_wrong_selected_level_stops(self):
        for shot in (self.shot(cash=None), self.shot(level=0)):
            self.platform.events.clear()
            with self.assertRaises(StopRun):
                self.make([shot]).upgrade((855,330), 1, 1)
            self.assertLessEqual(self.platform.events.count(("left_down",)), 2)

    def test_upgrade_failure_never_retries(self):
        with self.assertRaisesRegex(StopRun, "confirm"):
            self.make([self.shot(cash=700)]).upgrade((855,330), 1, 1, timeout=1)
        self.assertEqual(self.platform.events.count(("left_down",)), 3)

    def test_valid_placement_confirms_count_and_tower_name(self):
        run=self.make([self.shot(cash=500), self.shot(cash=500), self.shot(cash=500), self.shot(cash=250,count=2,level=0,cost=150)])
        self.assertEqual(run.place((1020,330), slot=2, count=1).tower_count, 2)
        self.assertEqual(self.platform.events.count(("left_down",)), 1)

    def test_golden_placement_guard_logs_predicates_without_click(self):
        events=[]
        run=self.make([self.shot(cash=500),self.shot(cash=500),self.shot(cash=500),
                       self.shot(cash=500,preview=False)])
        run.use_e_upgrades=True
        run.selection_event=lambda **event:events.append(event)
        with self.assertRaisesRegex(StopRun,'precondition changed'):
            run.place((1020,330),slot=2,count=1,tower_id=2)
        self.assertEqual(self.platform.events.count(('left_down',)),0)
        self.assertEqual(events,[dict(event='placement_guard_rejected',point=(1020,330),
            tower_id=2,expected_count=1,observed_count=1,expected_price=250,
            observed_price=250,cash=500,preview_ok=False,hotbar_ok=True)])

    def test_golden_placement_reobserves_transient_preview_before_single_click(self):
        run=self.make([self.shot(cash=555)]*3+
                      [self.shot(cash=555,preview=False),
                       self.shot(cash=555),
                       self.shot(cash=305,count=2,level=0)])
        run.use_e_upgrades=True
        result=run.place((1020,330),slot=2,count=1,tower_id=2)
        self.assertEqual((result.tower_count,result.level),(2,0))
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_golden_placement_reobservation_rejects_changed_quote(self):
        run=self.make([self.shot(cash=555)]*3+
                      [self.shot(cash=555,preview=False),
                       self.shot(cash=555,placement=300)])
        run.use_e_upgrades=True
        with self.assertRaisesRegex(StopRun,'precondition changed'):
            run.place((1020,330),slot=2,count=1,tower_id=2)
        self.assertEqual(self.platform.events.count(('left_down',)),0)

    def test_golden_hover_rejection_logs_target_without_click(self):
        events=[]
        shot=Snapshot('in_match',Hud(500,1,None,None,None,2),True)
        run=self.make([shot])
        run.use_e_upgrades=True
        run.hover_check=lambda point:False
        run.selection_event=lambda **event:events.append(event)
        with self.assertRaisesRegex(StopRun,'Owned Scout hover'):
            run.select_scout((855,330),1)
        self.assertEqual(self.platform.events.count(('left_down',)),0)
        self.assertEqual(events,[dict(event='selection_hover_rejected',point=(855,330),count=1)])

    def test_invalid_preview_never_clicks(self):
        run=self.make([self.shot(cash=500), self.shot(cash=500), self.shot(cash=500,preview=False)])
        with self.assertRaisesRegex(StopRun,"preview"):
            run.place((1020,330), slot=2, count=1)
        self.assertEqual(self.platform.events.count(("left_down",)), 0)

    def test_consumable_hotbar_refuses_all_slot_input(self):
        run=self.make([self.shot(cash=500,hotbar=False)])
        with self.assertRaisesRegex(StopRun,"hotbar"):
            run.place((1020,330),slot=2,count=1)
        self.assertEqual(self.platform.events,[])

    def test_transient_resource_animation_is_observed_again_before_any_input(self):
        run=self.make([self.shot(cash=None),self.shot(cash=500)])
        self.assertEqual(run.checked().hud.cash,500)
        self.assertEqual(self.platform.events,[])

    def test_transient_hud_anchor_animation_waits_without_input(self):
        run=self.make([self.shot(state='unknown'),self.shot()])
        self.assertEqual(run.checked().state,'in_match')
        self.assertEqual(self.platform.events,[])

    def test_transient_camera_confidence_loss_is_observed_without_input(self):
        run=self.make([self.shot(camera=None),self.shot()])
        self.assertTrue(run.checked().camera_ok)
        self.assertEqual(self.platform.events,[])

    def test_cash_ocr_alone_cannot_trigger_disabled_upgrade(self):
        shot=Snapshot('in_match',Hud(900,1,'Scout',1,600,2,False),True)
        with self.assertRaisesRegex(StopRun,'cash'):
            self.make([shot]).upgrade((855,330),1,1,timeout=1)
        self.assertEqual(self.platform.events.count(('left_down',)),2)

    def test_maxed_scout_is_verified_twice_without_purchase_click(self):
        shot=Snapshot('in_match',Hud(1000,1,'Scout',4,None,16,False,True),True)
        result=self.make([shot]).upgrade((855,330),4,1)
        self.assertEqual(result.level,4)
        self.assertEqual(self.platform.events.count(('left_down',)),2)

    def test_price_ocr_mismatch_waits_for_observed_cost_without_purchase_retry(self):
        run=self.make([self.shot(cash=900),self.shot(cash=900,cost=60),self.shot(cash=900),self.shot(cash=900),self.shot(level=2)])
        self.assertEqual(run.upgrade((855,330),1,1).level,2)
        self.assertEqual(self.platform.events.count(('left_down',)),3)

    def test_discounted_placement_and_upgrade_use_actual_ui_prices(self):
        run=self.make([self.shot(cash=200,placement=175),self.shot(cash=200,placement=175),self.shot(cash=200,placement=175),self.shot(cash=25,count=2,level=0)])
        self.assertEqual(run.place((1020,330),2,1,timeout=3).tower_count,2)
        run=self.make([self.shot(cash=500,cost=450),self.shot(cash=500,cost=450),self.shot(cash=500,cost=450),self.shot(cash=50,level=2)])
        self.assertEqual(run.upgrade((855,330),1,1,timeout=3).level,2)

    def test_delayed_server_confirmation_does_not_repeat_placement_or_purchase(self):
        for action in ('place','upgrade'):
            with self.subTest(action=action):
                self.platform.events.clear();self.clock.value=0
                sent_at=[None]
                def read():
                    clicks=self.platform.events.count(('left_down',))
                    sent=clicks >= (1 if action=='place' else 3)
                    if sent and sent_at[0] is None:sent_at[0]=self.clock.now()
                    confirmed=sent and self.clock.now()-sent_at[0]>=7
                    if action=='place':return self.shot(cash=500,count=2 if confirmed else 1,level=0)
                    return self.shot(cash=1000,count=1,level=2 if confirmed else 1)
                run=MatchRunner(GuardedInput(self.platform.window,self.platform),read,self.clock.now,self.clock.sleep,slot=2)
                if action=='place':result=run.place((1020,330),2,1)
                else:result=run.upgrade((855,330),1,1)
                self.assertEqual(result.tower_count,2 if action=='place' else 1)
                self.assertEqual(self.platform.events.count(('left_down',)),1 if action=='place' else 3)

    def test_stop_during_delayed_confirmation_does_not_repeat_purchase(self):
        sent_at=[None]
        def read():
            if self.platform.events.count(('left_down',))>=3:
                if sent_at[0] is None:sent_at[0]=self.clock.now()
                if self.clock.now()-sent_at[0]>=6:self.platform.stopped=True
            return self.shot(cash=1000)
        run=MatchRunner(GuardedInput(self.platform.window,self.platform),read,self.clock.now,self.clock.sleep,slot=2)
        with self.assertRaisesRegex(StopRun,'Emergency stop'):
            run.upgrade((855,330),1,1)
        self.assertEqual(self.platform.events.count(('left_down',)),3)
