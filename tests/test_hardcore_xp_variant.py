"""Safe four-slot XP strategy contracts; no live Roblox inputs."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from tds_auto.app import Controller, STRATEGIES
from tds_auto.hardcore_plan_v2 import PLAN_ID, XP_PLAN_ID, is_hardcore_v2
from tds_auto.loadout import verify_hardcore_loadout
from tds_auto.hardcore_match import HardcoreMatchV2, optional_placement_budget


class XPVariantTests(unittest.TestCase):
    def test_two_explicit_hardcore_selectors_share_the_pinned_core_plan(self):
        self.assertTrue(is_hardcore_v2(PLAN_ID))
        self.assertTrue(is_hardcore_v2(XP_PLAN_ID))
        self.assertFalse(is_hardcore_v2('golden_scout'))
        self.assertNotEqual(PLAN_ID, XP_PLAN_ID)
        labels=[name for name,sid in STRATEGIES.items() if sid in (PLAN_ID,XP_PLAN_ID)]
        self.assertEqual(len(labels),2)
        self.assertIn('XP',next(label for label in labels if STRATEGIES[label]==XP_PLAN_ID))

    def test_xp_gui_starts_continuous_worker_with_separate_id(self):
        with tempfile.TemporaryDirectory() as t:
            launcher=Mock(return_value=Mock(poll=Mock(return_value=None)))
            from tds_auto.phase1 import Window
            window=Window(101,202,0,29,1920,991,120,True)
            controller=Controller(Path(t),launcher,preflight=lambda **_kw:window)
            label=next(k for k,v in STRATEGIES.items() if v==XP_PLAN_ID)
            self.assertTrue(controller.start(label))
            args=launcher.call_args.args[0]
            self.assertEqual(args[args.index('--strategy')+1],XP_PLAN_ID)
            self.assertIn('--continuous',args)
            self.assertIn('--auto-recover',args)
            self.assertNotIn('--auto-equip',args)

    def test_explicit_three_slot_and_four_slot_loadouts_cannot_cross_modes(self):
        base=('boomerang','crook boss','farm','','')
        xp=('boomerang','crook boss','farm','juggernaut','')
        self.assertIsNone(verify_hardcore_loadout(base,require_optional=False))
        self.assertIsNotNone(verify_hardcore_loadout(xp,require_optional=False))
        self.assertIsNone(verify_hardcore_loadout(xp,optional_tower='juggernaut',require_optional=True))
        self.assertIsNotNone(verify_hardcore_loadout(base,require_optional=True))
        self.assertIsNotNone(verify_hardcore_loadout(xp,optional_tower='scout',require_optional=True))
        self.assertIsNotNone(verify_hardcore_loadout((*base[:4],'scout'),require_optional=True))

    def test_native_juggernaut_price_quote_10000_is_read_without_guessing(self):
        from PIL import Image
        from tds_auto.hardcore_vision import wretched_price
        from tds_auto.resources import LocalOCR
        with Image.open(Path('tests/fixtures/hardcore_slot4_juggernaut_10000_native_price.png')) as crop:
            frame=Image.new('RGB',(1920,991))
            frame.paste(crop,(990,932))
        self.assertEqual(wretched_price(frame,4,LocalOCR()),10000)

    def test_late_wave_slot4_quote_10000_falls_back_to_two_matching_green_masks(self):
        from PIL import Image
        from tds_auto.hardcore_vision import wretched_price
        from tds_auto.resources import LocalOCR
        with Image.open(Path('tests/fixtures/hardcore_slot4_juggernaut_10000_latewave_native_price.png')) as crop:
            frame=Image.new('RGB',(1920,991))
            frame.paste(crop,(1000,940))
        self.assertEqual(wretched_price(frame,4,LocalOCR()),10000)

    def test_optional_cash_guard_protects_next_mandatory_upgrade(self):
        for price in (200,1850,10000):
            with self.subTest(price=price):
                self.assertFalse(optional_placement_budget(price,price+13999,14000,24))
                self.assertTrue(optional_placement_budget(price,price+14000,14000,24))
                self.assertTrue(optional_placement_budget(price,price,0,29))
                self.assertFalse(optional_placement_budget(price,price+40000,None,24))
                self.assertFalse(optional_placement_budget(price,price+40000,14000,30))
        self.assertFalse(optional_placement_budget(199,100000,0,24))
        self.assertFalse(optional_placement_budget(10001,100000,0,24))
        self.assertFalse(optional_placement_budget(None,100000,0,24))
        self.assertFalse(optional_placement_budget(True,100000,0,24))
        self.assertFalse(optional_placement_budget(10000,9000,0,24))

    def test_next_core_cost_is_unknown_if_quote_cannot_be_proven(self):
        runner=HardcoreMatchV2.__new__(HardcoreMatchV2)
        runner.plan=SimpleNamespace(phases=(SimpleNamespace(step=13,actions=(
            SimpleNamespace(tower_id='C3',operation='upgrade',level=3,optional=False),)),))
        runner.levels={'C3':2}
        self.assertIsNone(runner.next_core_price(lambda *_:None))
        self.assertEqual(runner.next_core_price(lambda *_:14000),14000)
        runner.levels['C3']=3
        self.assertEqual(runner.next_core_price(lambda *_:None),0)

    def test_gui_loadout_summary_matches_the_selected_mode(self):
        from tds_auto.app import App
        panel=App.__new__(App)
        panel.strategy=Mock()
        panel.loadout_summary=Mock()
        for variant,expected in ((XP_PLAN_ID,'Juggernaut'),(PLAN_ID,'Slots 4')):
            panel.strategy.get.return_value=next(k for k,v in STRATEGIES.items() if v==variant)
            panel._strategy_changed()
            summary=panel.loadout_summary.set.call_args.args[0]
            self.assertIn(expected,summary)
            if variant==PLAN_ID:self.assertNotIn('XP tower',summary)

    def test_xp_strategy_protects_early_defense_milestones_before_10000_placement(self):
        from tds_auto.hardcore_match import XP_CRITICAL_LEVELS
        runner=HardcoreMatchV2.__new__(HardcoreMatchV2)
        runner.levels=dict(XP_CRITICAL_LEVELS)
        self.assertTrue(runner.xp_critical_defense_verified())
        for tower,level in XP_CRITICAL_LEVELS:
            runner.levels[tower]=level-1
            self.assertFalse(runner.xp_critical_defense_verified(),tower)
            runner.levels[tower]=level

    def test_juggernaut_xp_priority_only_after_milestones_even_if_late_upgrade_pending(self):
        from tds_auto.hardcore_match import XP_CRITICAL_LEVELS
        runner=HardcoreMatchV2.__new__(HardcoreMatchV2)
        runner.session=SimpleNamespace(strategy_id=XP_PLAN_ID,status=Mock())
        runner.recorded_wait=set()
        runner.levels=dict(XP_CRITICAL_LEVELS)
        runner.optional_tower='Juggernaut'
        runner.completed=70
        runner.plan=SimpleNamespace(finish_wave=30)
        runner.last_wave=25
        runner.plan_actions={('X1',0):SimpleNamespace(tower_id='X1',operation='place')}
        runner.towers={'X1':SimpleNamespace(tower_id='X1')}
        runner.place=Mock(return_value=True)
        runner.next_core_price=Mock(return_value=14000)
        quote=lambda *_:10000
        runner.levels['C5']=1
        self.assertFalse(runner.try_optional_placement('frame',SimpleNamespace(cash=20000,wave=25),quote))
        runner.place.assert_not_called()
        runner.levels['C5']=2
        self.assertTrue(runner.try_optional_placement('frame',SimpleNamespace(cash=10000,wave=25),quote))
        runner.place.assert_called_once_with(runner.towers['X1'],29)

    def test_optional_purchase_requires_surplus_and_verified_core_quote(self):
        runner=HardcoreMatchV2.__new__(HardcoreMatchV2)
        runner.optional_tower='Juggernaut'
        runner.levels={'C3':2}
        runner.completed=70
        runner.last_wave=24
        runner.plan=SimpleNamespace(finish_wave=30)
        runner.plan_actions={('X1',0):SimpleNamespace(tower_id='X1',operation='place')}
        runner.towers={'X1':SimpleNamespace(tower_id='X1')}
        runner.session=Mock()
        runner.place=Mock(return_value=True)
        runner.next_core_price=Mock(return_value=14000)
        quote=lambda *_:10000
        for cash in (9999,23999):
            self.assertFalse(runner.try_optional_placement('frame',SimpleNamespace(cash=cash,wave=24),quote))
        runner.next_core_price.return_value=None
        self.assertFalse(runner.try_optional_placement('frame',SimpleNamespace(cash=25000,wave=24),quote))
        runner.place.assert_not_called()
        runner.next_core_price.return_value=14000
        self.assertTrue(runner.try_optional_placement('frame',SimpleNamespace(cash=24000,wave=24),quote))
        runner.place.assert_called_once_with(runner.towers['X1'],29)
        runner.session.status.assert_called_once()

    def test_xp_variant_credits_gems_even_if_no_cash_was_safe_for_xp_tower(self):
        from tds_auto.session import Session
        for placed in (False,True):
            with self.subTest(placed=placed),tempfile.TemporaryDirectory() as t:
                session=Session.__new__(Session)
                session.output=Path(t)
                session.strategy_id=XP_PLAN_ID
                session.totals={'attempts':0,'matches_completed':0,'wins':0,'coins_total':0}
                session.hardcore_plan=SimpleNamespace(finish_wave=30,map_name='Wretched Front')
                session.preflight_hardcore=Mock()
                session.choose_map=Mock()
                session.prepare_hardcore_match=Mock(return_value={'status':'prepared'})
                session.verify_hardcore_hotbar=Mock()
                session.status=Mock()
                session.transition=Mock()
                result={'status':'result_verified','displayed_gems':137,'confirmed_actions':76 if placed else 75,
                        'optional_tower_placed':placed,'result_wave':30}
                with patch('tds_auto.hardcore_match.HardcoreMatchV2') as runner:
                    runner.return_value.run.return_value=result
                    summary=session.play_hardcore_v2(1,continuous=False)
                self.assertEqual(summary['status'],'result_verified')
                self.assertEqual(summary['gem_cycles'],1)
                self.assertEqual(summary['gems_total'],137)
                self.assertEqual(summary['xp_placement_cycles'],int(placed))
                self.assertEqual(summary['xp_unplaced_cycles'],int(not placed))
                session.transition.assert_not_called()

    def test_xp_result_credits_real_wave30_gems_with_deferred_late_upgrades(self):
        from tds_auto.hardcore_match import XP_CRITICAL_LEVELS, HardcoreMatch
        from tds_auto.results import HardcoreResult
        runner=HardcoreMatchV2.__new__(HardcoreMatchV2)
        runner.levels={**dict(XP_CRITICAL_LEVELS),'X1':0}
        runner.optional_tower='Juggernaut'
        runner.plan=SimpleNamespace(finish_wave=30,final_required_levels=(('C5',3),))
        runner.session=Mock(strategy_id=XP_PLAN_ID)
        runner.session.now.return_value=0
        runner.missed_defense_deadlines=set()
        runner.target_observations=2
        runner.min_target_observations=2
        runner.driver=Mock()
        runner.ocr=Mock()
        with patch.object(HardcoreMatch,'run',return_value={
                'status':'unverified_reward','target_wave_verified':True,
                'confirmed_actions':71}),patch('tds_auto.hardcore_match.read_hardcore_result',
                return_value=HardcoreResult('defeat',30,463,137)):
            result=runner.run()
        self.assertEqual(result['status'],'result_verified')
        self.assertFalse(result['required_levels_verified'])
        self.assertTrue(result['xp_critical_defense_verified'])
        self.assertTrue(result['optional_tower_placed'])
        self.assertEqual(result['displayed_gems'],137)
        runner.levels['C5']=1
        self.assertFalse(runner.xp_critical_defense_verified())

    def test_xp_tower_remains_optional_for_gem_credit_but_xp_is_counted_separately(self):
        from tds_auto.results import HardcoreResult
        from tds_auto.hardcore_match import HardcoreMatch
        for placed in (False,True):
            with self.subTest(placed=placed):
                runner=HardcoreMatchV2.__new__(HardcoreMatchV2)
                runner.plan=SimpleNamespace(finish_wave=30,final_required_levels=(('F1',3),))
                runner.levels={'F1':3,'X1':0} if placed else {'F1':3}
                runner.optional_tower='Juggernaut'
                runner.missed_defense_deadlines=set()
                runner.target_observations=2
                runner.min_target_observations=2
                runner.session=Mock()
                runner.session.now.return_value=0
                runner.driver=Mock()
                runner.ocr=Mock()
                expected=HardcoreResult('defeat',30,463,137)
                with (patch.object(HardcoreMatch,'run',return_value={
                        'status':'unverified_reward','target_wave_verified':True,
                        'confirmed_actions':75}) as _base,
                      patch('tds_auto.hardcore_match.read_hardcore_result',return_value=expected)):
                    result=runner.run()
                self.assertEqual(result['status'],'result_verified')
                self.assertEqual(result['optional_tower_placed'],placed)
                self.assertEqual(result['displayed_gems'],137)


if __name__=='__main__':unittest.main()
