"""Native wave-23 failure: first Boomerang L2 was deferred from wave 5 to 9."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from tds_auto.hardcore_match import HardcoreMatchV2
from tds_auto.hardcore_plan_v2 import load_hardcore_plan_v2


class EarlyBoomerangProtectionTests(unittest.TestCase):
    def worker(self):
        worker = HardcoreMatchV2.__new__(HardcoreMatchV2)
        plan = load_hardcore_plan_v2()
        worker.plan_actions = {
            (action.tower_id, action.level or 0): action
            for phase in plan.phases for action in phase.actions
        }
        worker.levels = {'B1': 1}
        return worker

    @staticmethod
    def quote(action, level):
        return {'B1': {1: 750, 2: 2500}, 'C1': {None: 2250, 0: 1500, 1: 2750}}[
            action.tower_id][level]

    def test_wave_five_prioritizes_first_boomerang_l2_before_farm_or_crook(self):
        due, action, price = self.worker().urgent_defense(5, self.quote, 1000)
        self.assertEqual((due, action.tower_id, action.level, price), (7, 'B1', 2, 750))

    def test_wave_eight_crook_urgency_does_not_bypass_unfinished_boomerang_l2(self):
        due, action, price = self.worker().urgent_defense(8, self.quote, 5000)
        self.assertEqual((due, action.tower_id, action.level, price), (7, 'B1', 2, 750))

    def test_wave_eight_allows_phase_three_farm_completion_after_boomerang_l2(self):
        worker = self.worker()
        worker.levels['B1'] = 2
        # The credited run completed F5 L3 before C1 took priority;
        # the failed runs postponed F5 L3 until wave 11.
        self.assertEqual(worker.urgent_defense(8, self.quote, 5000),
                         (None, None, None))

    def test_wave_nine_crook_deadline_still_applies(self):
        worker = self.worker()
        worker.levels['B1'] = 2
        due, action, price = worker.urgent_defense(9, self.quote, 3000)
        self.assertEqual((due, action.tower_id, action.operation, price),
                         (11, 'C1', 'place', 2250))

    def test_unaffordable_boomerang_quote_is_reserved_not_guessed(self):
        due, action, price = self.worker().urgent_defense(5, self.quote, 600)
        self.assertEqual((due, action, price), (7, None, 750))


if __name__ == '__main__':
    unittest.main()
