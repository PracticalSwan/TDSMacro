"""Isolated v0.3.1 Golden Scout candidate; published v0.2.4 stays unchanged."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tds_auto.calibration import load_profile
from tds_auto.control import GuardedInput
from tds_auto.match import MatchRunner,Snapshot
from tds_auto.resources import Hud
from test_control import FakeOS
from test_navigation import Clock


class GoldenTenV031Tests(unittest.TestCase):
    def test_candidate_is_ten_vertical_scouts_and_fifty_level_actions(self):
        profile,strategy=load_profile(ROOT/'calibrations/dead_ahead_vertical_ten_v5_candidate.json')
        old,original=load_profile(ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
        self.assertEqual(old['status'],'calibrated_current_setup')
        self.assertEqual(len(original.steps),44)
        self.assertEqual((len(strategy.steps),profile['slot']),(50,1))
        self.assertEqual((strategy.map_name,strategy.difficulty),('Dead Ahead','Easy'))
        positions=[s.args for s in strategy.steps if s.operation=='SpawnTower']
        self.assertEqual(len(positions),10)
        self.assertEqual(len(set(x[:2] for x in positions)),10)
        self.assertEqual(positions[:9],[s.args for s in original.steps if s.operation=='SpawnTower'])
        self.assertEqual(positions[9],(1020,465,1,10))
        levels={}
        for step in strategy.steps:
            if step.operation=='SpawnTower':
                levels[step.args[3]]=0
            else:
                levels[step.args[0]]+=1
        self.assertEqual(levels,{idx:4 for idx in range(1,11)})
        self.assertIn('pending_native',profile['status'])

    def test_native_v2202_profile_uses_fifty_actions_and_original_camera_safety(self):
        profile,strategy=load_profile(ROOT/'calibrations/dead_ahead_vertical_ten_v031_v2202_trial.json')
        self.assertTrue(profile['status'].startswith('v031_candidate_v2202'))
        self.assertEqual(profile['setup']['post_alignment_moves'],[['S',750],['D',100]])
        from tds_auto.app import GOLDEN_V031_ACCEPTED_SHA
        self.assertEqual(profile['strategy_sha256'],GOLDEN_V031_ACCEPTED_SHA)
        self.assertEqual(len(strategy.steps),50)
        places=[step.args[:2] for step in strategy.steps if step.operation=='SpawnTower']
        self.assertEqual(len(places),len(set(places)))
        self.assertEqual(places[0],(862,323))
        self.assertEqual(places[-1],(1032,462))
        self.assertEqual(profile['calibration_method']['version_observed'],'TDS v2.20.2')

    def test_descriptive_status_does_not_control_golden_e_or_inventory_mode(self):
        from tds_auto.calibration import golden_ten_enabled, GOLDEN_V031_ACCEPTED_SHA
        profile, strategy=load_profile(ROOT/'calibrations/dead_ahead_vertical_ten_v031_v2202_trial.json')
        self.assertEqual(profile['strategy_sha256'],GOLDEN_V031_ACCEPTED_SHA)
        self.assertTrue(golden_ten_enabled(profile,strategy))
        self.assertTrue(golden_ten_enabled({**profile,'status':'renamed by owner'},strategy))
        self.assertFalse(golden_ten_enabled({**profile,'strategy_sha256':'0'*64},strategy))
        legacy, old=load_profile(ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
        self.assertFalse(golden_ten_enabled(legacy,old))

    def test_placement_and_two_same_tower_upgrades_need_no_selection_click(self):
        from types import SimpleNamespace
        from tds_auto.run import Progress, run_sequence
        from tds_auto.strategy import Step

        platform, clock = FakeOS(), Clock()
        def read():
            placed = ('left_down',) in platform.events
            level = platform.events.count(('key_down', 'E'))
            if platform.events.count(('left_down',)) == 2:
                return Snapshot('in_match', Hud(10000, 1, wave=20), True)
            hud = Hud(10000, int(placed), 'Scout' if placed else None,
                      level if placed else None, 150 if placed else None, 20, placed)
            return Snapshot('in_match', hud, True, True, True, 250)

        runner = MatchRunner(GuardedInput(platform.window, platform), read, clock.now, clock.sleep,
                             hover_check=lambda point: True, use_e_upgrades=True)
        strategy = SimpleNamespace(steps=(Step('SpawnTower', (1020, 465, 1, 5)),
                                          Step('UpgradeTower', (5,)), Step('UpgradeTower', (5,))))
        progress = run_sequence(strategy, runner, Progress(), lambda point: point, 3)
        self.assertEqual(progress.levels, {5: 2})
        self.assertEqual(platform.events.count(('key_down', 'E')), 2)
        self.assertEqual(platform.events.count(('left_down',)), 1)

    def test_wave_twenty_active_hud_allows_single_e_upgrade(self):
        platform,clock=FakeOS(),Clock()
        level3=Snapshot('in_match',Hud(20000,10,'Scout',3,4000,20,True),True)
        level4=Snapshot('in_match',Hud(16000,10,'Scout',4,None,20,False,True),True)
        def read():
            if platform.events.count(('left_down',))==1:
                return Snapshot('in_match',Hud(20000,10,wave=20),True)
            return level4 if ('key_down','E') in platform.events else level3
        runner=MatchRunner(GuardedInput(platform.window,platform),read,
                           clock.now,clock.sleep,slot=1,use_e_upgrades=True,hover_check=lambda point: True)
        result=runner.upgrade((1020,465),3,10,timeout=2,tower_id=5)
        self.assertEqual(result.level,4)
        self.assertEqual(platform.events.count(('key_down','E')),1)
        self.assertEqual(platform.events.count(('left_down',)),2)

    def test_e_is_never_sent_when_fresh_level_or_cost_changes(self):
        platform,clock=FakeOS(),Clock()
        first=Snapshot('in_match',Hud(20000,10,'Scout',2,4000,19,True),True)
        changed=Snapshot('in_match',Hud(20000,10,'Scout',1,4000,19,True),True)
        def read():
            clicks=platform.events.count(('left_down',))
            if clicks==1:
                return Snapshot('in_match',Hud(20000,10,wave=19),True)
            return changed if clicks>=2 else first
        runner=MatchRunner(GuardedInput(platform.window,platform),read,
                           clock.now,clock.sleep,slot=1,use_e_upgrades=True,hover_check=lambda point: True)
        from tds_auto.control import StopRun
        with self.assertRaises(StopRun):
            runner.upgrade((1020,465),2,10,timeout=2,tower_id=5)
        self.assertNotIn(('key_down','E'),platform.events)

    def test_same_level_of_a_different_scout_does_not_prove_a_switch(self):
        from tds_auto.control import StopRun

        platform,clock=FakeOS(),Clock()
        old_panel=Snapshot('in_match',Hud(5000,2,'Scout',2,150,8,True),True)
        runner=MatchRunner(GuardedInput(platform.window,platform),lambda:old_panel,
                           clock.now,clock.sleep,hover_check=lambda point:True,use_e_upgrades=True)
        runner.selected=(1,(855,330),2)
        with self.assertRaisesRegex(StopRun,'cleared panel'):
            runner.upgrade((1020,330),2,2,tower_id=2)
        self.assertEqual(platform.events.count(('left_down',)),1)
        self.assertNotIn(('key_down','E'),platform.events)
        self.assertIsNone(runner.selected)

    def test_fresh_unaffordable_quote_invalidates_reused_panel_without_e(self):
        from tds_auto.control import StopRun

        platform,clock=FakeOS(),Clock()
        point=(855,330)
        affordable=Snapshot('in_match',Hud(750,1,'Scout',2,600,6,True),True)
        changed=Snapshot('in_match',Hud(500,1,'Scout',2,600,6,False),True)
        snapshots=iter([affordable,affordable,affordable,changed])
        runner=MatchRunner(GuardedInput(platform.window,platform),lambda:next(snapshots),
                           clock.now,clock.sleep,use_e_upgrades=True)
        runner.selected=(1,point,1)
        with self.assertRaisesRegex(StopRun,'precondition changed'):
            runner.upgrade(point,2,1,tower_id=1)
        self.assertEqual(platform.events,[])
        self.assertIsNone(runner.selected)

if __name__=='__main__':
    unittest.main()
