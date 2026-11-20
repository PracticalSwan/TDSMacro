"""Strict, data-only Hardcore plan contracts; never perform game input."""
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
PLAN_PATH = ROOT / "strategies/hardcore_wretched_front_boomerang_crook_farm_v1.json"


def valid_plan():
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))


class HardcorePlanTests(unittest.TestCase):
    def api(self):
        try:
            from tds_auto.hardcore_plan import (
                HardcorePlanError,
                load_hardcore_plan,
                parse_hardcore_plan,
                validate_hardcore_plan,
            )
        except ImportError:
            self.fail("the dedicated Hardcore plan parser is not available")
        return HardcorePlanError, load_hardcore_plan, parse_hardcore_plan, validate_hardcore_plan

    def assert_invalid(self, plan, message):
        error, _, parse, _ = self.api()
        with self.assertRaisesRegex(error, message):
            parse(json.dumps(plan))

    @staticmethod
    def stage(plan, window):
        return next(stage for stage in plan["stages"] if stage["waves"] == list(window))

    def test_accepts_the_fixed_wretched_front_gem_grind_contract(self):
        _, _, parse, _ = self.api()
        plan = parse(json.dumps(valid_plan()))
        self.assertEqual(plan.strategy_id, "hardcore_gem_grind_wretched_front")
        self.assertEqual(plan.profile_id, "wretched_front_hardcore_v1")
        self.assertEqual((plan.map_name, plan.mode, plan.squad_size),
                         ("Wretched Front", "Hardcore", 1))
        self.assertEqual(plan.required_loadout,
                         ((1, "Boomerang"), (2, "Crook Boss"), (3, "Farm")))
        self.assertEqual(plan.tower_counts,
                         {"Farm": 8, "Boomerang": 5, "Crook Boss": 5})
        self.assertEqual(dict(plan.placements)["F1"], "farm_outer_pad_01")
        self.assertEqual(plan.finish_wave, 29)
        self.assertEqual(plan.min_wave_29_observations, 2)
        checkpoint = next(stage for stage in plan.stages if stage.first_wave == 14)
        self.assertEqual(checkpoint.checks[0].tower_ids,
                         tuple(f"F{number}" for number in range(1, 9)))

    def test_rejects_wrong_map_mode_player_count_profile_or_loadout(self):
        for field, value, message in (
            ("map", "Dead Ahead", "map"),
            ("mode", "Easy", "mode"),
            ("squad_size", 2, "squad"),
            ("profile_id", "dead_ahead_vertical_nine_v4", "profile ID"),
        ):
            with self.subTest(field=field):
                plan = valid_plan()
                plan[field] = value
                self.assert_invalid(plan, message)

        plan = valid_plan()
        plan["required_loadout"][0]["slot"] = 2
        self.assert_invalid(plan, "loadout")

    def test_rejects_bad_placement_names_and_incomplete_finish_gate(self):
        plan = valid_plan()
        plan["placements"]["F1"] = "some_other_map_coordinate"
        self.assert_invalid(plan, "placements")

        plan = valid_plan()
        plan["finish_policy"]["minimum_positive_wave_observations"] = 1
        self.assert_invalid(plan, "observations")

    def test_rejects_noninteger_empty_slot_values(self):
        for value in (5.0, True, 4):
            with self.subTest(value=value):
                plan = valid_plan()
                plan["slots_must_be_empty"] = [value]
                self.assert_invalid(plan, "slot 5")

    def test_rejects_duplicate_or_unrecognized_tower_ids_and_noncanonical_order(self):
        plan = valid_plan()
        plan["towers"][-1] = copy.deepcopy(plan["towers"][0])
        self.assert_invalid(plan, "duplicate")

        plan = valid_plan()
        plan["towers"][0]["id"] = "CommunityTower1"
        self.assert_invalid(plan, "tower")

        plan = valid_plan()
        plan["towers"][0], plan["towers"][1] = plan["towers"][1], plan["towers"][0]
        self.assert_invalid(plan, "canonical")

    def test_rejects_invalid_or_nonmonotone_wave_windows(self):
        plan = valid_plan()
        plan["stages"][0]["waves"] = [22, 21]
        self.assert_invalid(plan, "wave")

        plan = valid_plan()
        plan["stages"][2]["waves"] = [4, 5]
        self.assert_invalid(plan, "wave")

    def test_rejects_actions_outside_their_calibrated_wave_windows(self):
        plan = valid_plan()
        source = self.stage(plan, (5, 6))["actions"]
        action = next(a for a in source
                      if a["op"] == "upgrade" and a["tower_id"] == "F4"
                      and a.get("level") == 2)
        source.remove(action)
        self.stage(plan, (7, 9))["actions"].insert(0, action)
        self.assert_invalid(plan, "required wave window")

    def test_rejects_unknown_operations_and_unplaced_tower_references(self):
        plan = valid_plan()
        plan["stages"][0]["actions"][0]["op"] = "RunCommand"
        self.assert_invalid(plan, "operation")

        plan = valid_plan()
        plan["stages"][0]["actions"][0]["tower_id"] = "F99"
        self.assert_invalid(plan, "tower")

    def test_rejects_tower_sales_in_every_stage(self):
        for window in ((23, 28), (29, 29)):
            with self.subTest(window=window):
                plan = valid_plan()
                self.stage(plan, window)["actions"].append({"op": "sell", "tower_id": "B1"})
                self.assert_invalid(plan, "unsupported plan operation")

    def test_finish_stage_requires_a_natural_result_and_no_actions(self):
        plan = valid_plan()
        plan["finish_policy"]["result"] = "intentional_loss"
        self.assert_invalid(plan, "natural match result")
        plan = valid_plan()
        self.stage(plan, (29, 29))["actions"].append({"op": "place", "tower_id": "F1"})
        self.assert_invalid(plan, "finish phase")

    def test_requires_wave_14_15_farm_checkpoint_and_correct_prior_levels(self):
        plan = valid_plan()
        self.stage(plan, (14, 15))["checks"] = []
        self.assert_invalid(plan, "must verify")

        plan = valid_plan()
        self.stage(plan, (14, 15))["checks"][0]["level"] = 2
        self.assert_invalid(plan, "only supported check")

    def test_accepts_optional_exp_skip_and_optional_affordability_upgrades(self):
        _, _, parse, _ = self.api()
        plan = valid_plan()
        self.stage(plan, (22, 22))["actions"] = []
        parsed = parse(json.dumps(plan))
        self.assertNotIn("X1", {
            action.tower_id for stage in parsed.stages for action in stage.actions
            if action.operation == "place"
        })

        plan = valid_plan()
        self.stage(plan, (23, 28))["actions"] = [
            action for action in self.stage(plan, (23, 28))["actions"]
            if not (action["op"] == "upgrade" and action.get("level") == 4)
        ]
        parsed = parse(json.dumps(plan))
        self.assertFalse(any(
            action.operation == "upgrade" and action.level == 4
            for stage in parsed.stages for action in stage.actions
        ))

        plan = valid_plan()
        for action in self.stage(plan, (23, 28))["actions"]:
            if action["tower_id"].startswith("B") and action.get("level") == 4:
                action["optional"] = "yes"
                break
        self.assert_invalid(plan, "optional actions")

    def test_rejects_level_downgrades_and_nonoptional_explicit_flag(self):
        plan = valid_plan()
        self.stage(plan, (1, 4))["actions"].append(
            {"op": "upgrade", "tower_id": "F1", "level": 1}
        )
        self.assert_invalid(plan, "level")

        plan = valid_plan()
        self.stage(plan, (5, 6))["actions"][0]["optional"] = False
        self.assert_invalid(plan, "optional actions")

    def test_rejects_duplicate_json_keys_invalid_unicode_and_unknown_fields(self):
        error, _, parse, _ = self.api()
        source = json.dumps(valid_plan()).replace(
            '"mode": "Hardcore"', '"mode": "Hardcore", "mode": "Hardcore"', 1
        )
        with self.assertRaisesRegex(error, "duplicate JSON key"):
            parse(source)
        with self.assertRaises(error):
            parse("\ud800")

        plan = valid_plan()
        plan["unexpected"] = True
        self.assert_invalid(plan, "exactly")

    def test_validate_roundtrips_typed_plan_and_rejects_forged_instance(self):
        error, _, parse, validate = self.api()
        parsed = parse(json.dumps(valid_plan()))
        self.assertEqual(validate(parsed), parsed)
        with self.assertRaisesRegex(error, "profile ID"):
            validate(replace(parsed, profile_id="unreviewed_profile"))

    def test_nonselected_community_plan_cannot_be_loaded(self):
        error, load, _, _ = self.api()
        with tempfile.TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "community-plan.json"
            candidate.write_text(json.dumps(valid_plan()), encoding="utf-8")
            with self.assertRaisesRegex(error, "built-in"):
                load(candidate)

    def test_loads_the_hash_pinned_builtin_plan_and_required_ledger(self):
        _, load, _, _ = self.api()
        plan = load()
        self.assertEqual(plan.strategy_id, "hardcore_gem_grind_wretched_front")
        expected_windows = [
            (0, 0), (1, 4), (5, 6), (7, 9), (10, 10), (11, 13),
            (14, 15), (16, 16), (17, 18), (19, 21), (22, 22), (23, 28), (29, 29),
        ]
        self.assertEqual(
            [(stage.first_wave, stage.last_wave) for stage in plan.stages],
            expected_windows,
        )
        operations = [action for stage in plan.stages for action in stage.actions]
        tower_types = {tower.tower_id: tower.tower_type for tower in plan.towers}
        placed = {}
        for action in operations:
            if action.operation == "place":
                tower_type = tower_types[action.tower_id]
                placed[tower_type] = placed.get(tower_type, 0) + 1
        self.assertEqual(placed, {"Farm": 8, "Boomerang": 5, "Crook Boss": 5, "EXP": 1})
        self.assertEqual([(action.operation, action.tower_id) for action in plan.stages[0].actions],
                         [("place", f"F{number}") for number in range(1, 5)])
        self.assertEqual(plan.stages[-1].actions, ())
        self.assertTrue(all(action.operation in {"place", "upgrade"} for action in operations))
        self.assertTrue(all(
            action.optional for action in operations
            if action.operation == "upgrade" and action.level == 4
        ))

    def test_existing_golden_scout_profile_hash_is_preserved(self):
        profile = json.loads(
            (ROOT / "calibrations/dead_ahead_vertical_nine_v4.json").read_text(encoding="utf-8")
        )
        strategy = ROOT / profile["strategy"]
        expected = "59548c3cf386f63eb0ae9f820ec165747c600706bbb59c7ce6acbd4da133eafb"
        self.assertEqual(profile["strategy_sha256"], expected)
        self.assertEqual(hashlib.sha256(strategy.read_bytes()).hexdigest(), expected)

    def test_farm_budget_uses_cheap_upgrades_before_waiting_for_an_expensive_one(self):
        from tds_auto.hardcore_match import affordable_purchase
        from tds_auto.hardcore_plan import HardcoreOperation

        actions = [(None, action) for action in (
            HardcoreOperation("upgrade", "F1", 2),
            HardcoreOperation("upgrade", "F2", 1),
            HardcoreOperation("upgrade", "F2", 2),
            HardcoreOperation("upgrade", "F3", 1),
        )]

        def price(action, level):
            return {0: 200, 1: 600}[level]

        self.assertEqual(affordable_purchase(actions, {"F1": 1, "F2": 0, "F3": 0}, price, 500), 1)
        actions.pop(1)
        levels = {"F1": 1, "F2": 1, "F3": 0}
        self.assertEqual(affordable_purchase(actions, levels, price, 300), 2)
        self.assertIsNone(affordable_purchase(actions, levels, price, 100))
        self.assertEqual(affordable_purchase(actions, levels, price, 600), 0)

    def test_farm_budget_can_place_before_waiting_and_preserves_upgrade_dependencies(self):
        from tds_auto.hardcore_match import affordable_purchase
        from tds_auto.hardcore_plan import HardcoreOperation

        actions = [(None, action) for action in (
            HardcoreOperation("upgrade", "F1", 2),
            HardcoreOperation("place", "F2"),
            HardcoreOperation("upgrade", "F2", 1),
        )]

        def price(action, level):
            return {None: 300, 0: 200, 1: 600}[level]

        self.assertEqual(affordable_purchase(actions, {"F1": 1}, price, 350), 1)
        self.assertIsNone(affordable_purchase(actions, {"F1": 1}, price, 250))

    def test_an_affordable_defense_action_can_precede_its_stage(self):
        from tds_auto.hardcore_match import affordable_purchase
        _, load, _, _ = self.api()
        plan = load()
        defense = next(stage for stage in plan.stages if stage.first_wave == 5)
        farm = next(stage for stage in plan.stages if stage.first_wave == 1)
        farm_upgrade = next(a for a in farm.actions if a.tower_id == 'F3' and a.level == 2)
        first_boomerang = defense.actions[0]
        pending = [(farm, farm_upgrade), (defense, first_boomerang)]

        def price(action, level):
            return 550 if action.operation == "place" else 600

        self.assertEqual(affordable_purchase(pending, {'F3': 1}, price, 575), 1)


if __name__ == "__main__":
    unittest.main()
