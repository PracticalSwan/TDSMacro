"""Offline strategy-import tests; no Roblox input or file mutation."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tds_auto.strategy import StrategyError, parse_strategy, preflight, read_strategy

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "strategies" / "GOLDIE SCOUTO.vertical-nine-slot1.strat"

GOOD = """[Info]
title=Fixture
[Settings]
map=Dead Ahead
difficulty=Easy
requiredTowers=Scout
autoSkip=ON
moveEnabled=1
moveDirection=W
moveDuration=950
[DO NOT EDIT]
width=1920
height=1009
[Steps]
SpawnTower(881,364,1,1)
UpgradeTower(1)
"""


class StrategyTests(unittest.TestCase):
    def test_user_strategy_imports_without_execution(self):
        strat = read_strategy(FILE)
        summary = preflight(strat, 1920, 991)
        self.assertEqual((strat.map_name, strat.difficulty), ("Dead Ahead", "Easy"))
        self.assertEqual(strat.required_towers, ("Scout",))
        self.assertEqual(summary["spawn_count"], 9)
        self.assertEqual(summary["upgrade_count"], 35)
        self.assertEqual(summary["steps"], 44)
        self.assertEqual(summary["slots_used"], [1])
        self.assertEqual(summary["max_tower_id"], 9)
        self.assertFalse(summary["ready_for_automatic_execution"])
        self.assertFalse(any(x.startswith("GEOMETRY_MISMATCH") for x in summary["warnings"]))

    def test_matching_geometry_still_requires_confirmation(self):
        summary = preflight(parse_strategy(GOOD), 1920, 1009)
        self.assertFalse(summary["ready_for_automatic_execution"])
        self.assertFalse(any(x.startswith("GEOMETRY_MISMATCH") for x in summary["warnings"]))

    def test_untrusted_calls_are_never_executed(self):
        with self.assertRaisesRegex(StrategyError, "unsupported operation"):
            parse_strategy(GOOD + "RunCommand(123)\n")

    def test_unknown_upgrade_id_rejected(self):
        with self.assertRaisesRegex(StrategyError, "unknown tower ID"):
            parse_strategy(GOOD.replace("UpgradeTower(1)", "UpgradeTower(999)"))

    def test_nonsequential_tower_id_rejected(self):
        with self.assertRaisesRegex(StrategyError, "sequential"):
            parse_strategy(GOOD.replace("881,364,1,1", "881,364,1,3"))

    def test_out_of_bounds_position_rejected(self):
        with self.assertRaisesRegex(StrategyError, "outside source geometry"):
            parse_strategy(GOOD.replace("881,364", "4000,364"))

    def test_invalid_slot_rejected(self):
        with self.assertRaisesRegex(StrategyError, "tower slot"):
            parse_strategy(GOOD.replace("881,364,1,1", "881,364,6,1"))

    def test_missing_section_rejected(self):
        with self.assertRaisesRegex(StrategyError, "missing one"):
            parse_strategy(GOOD.replace("[DO NOT EDIT]\nwidth=1920\nheight=1009\n", ""))

    def test_missing_geometry_pair_rejected(self):
        with self.assertRaisesRegex(StrategyError, "together"):
            preflight(parse_strategy(GOOD), client_width=1920)

    def test_invalid_movement_rejected(self):
        with self.assertRaisesRegex(StrategyError, "moveDirection"):
            parse_strategy(GOOD.replace("moveDirection=W", "moveDirection=EVAL"))

    def test_strict_limit_rejects_huge_input(self):
        with self.assertRaisesRegex(StrategyError, "maximum allowed size"):
            parse_strategy(GOOD + ("#" + "a"*201000))


if __name__ == "__main__":
    unittest.main()
