"""Strict data-only contract for the built-in Wretched Front gem plan."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


MAX_PLAN_BYTES = 200_000
PLAN_ID = "hardcore_gem_grind_wretched_front"
PROFILE_ID = "wretched_front_hardcore_v1"
REQUIRED_LOADOUT = ((1, "Boomerang"), (2, "Crook Boss"), (3, "Farm"))
OPTIONAL_SLOT = 4
EMPTY_SLOTS = (5,)
FINISH_WAVE = 29
ROOT = Path(__file__).resolve().parents[2]
PLAN_RELATIVE_PATH = Path("strategies/hardcore_wretched_front_boomerang_crook_farm_v1.json")
PLAN_SHA256 = "17b36a2fce4051fd9dd3683378f77a613dadffec61d24804fdd729d522c49bd5"
PLACEMENT_IDS = {
    **{f"F{number}": f"farm_outer_pad_{number:02d}" for number in range(1, 9)},
    **{f"B{number}": f"boomerang_bend_{number:02d}" for number in range(1, 6)},
    **{f"C{number}": f"crook_intercept_{number:02d}" for number in range(1, 6)},
    "X1": "exp_rear_exit_01",
}
REQUIRED_STAGE_WINDOWS = (
    (0, 0), (1, 4), (5, 6), (7, 9), (10, 10), (11, 13),
    (14, 15), (16, 16), (17, 18), (19, 21), (22, 22), (23, 28), (29, 29),
)
FARM_CHECK_IDS = tuple(f"F{number}" for number in range(1, 9))
PLACE_WINDOWS = {
    **{f"F{number}": (0, 0) for number in range(1, 5)},
    "B1": (5, 6), "F5": (5, 6), "F6": (11, 13), "F7": (11, 13),
    "C1": (11, 13), "F8": (11, 13), "B2": (16, 16), "C2": (16, 16),
    **{f"B{number}": (17, 18) for number in range(3, 6)},
    **{f"C{number}": (19, 21) for number in range(3, 6)},
    "X1": (22, 22),
}
UPGRADE_WINDOWS = {
    **{(f"F{number}", 1): (1, 4) for number in range(1, 5)},
    **{(f"F{number}", 2): (1, 4) for number in range(1, 4)},
    ("F4", 2): (5, 6), ("F5", 1): (5, 6), ("F5", 2): (5, 6),
    **{(f"F{number}", 3): (7, 9) for number in range(1, 6)},
    ("B1", 1): (5, 6), ("B1", 2): (5, 6), ("B1", 3): (10, 10),
    **{(f"F{number}", level): (11, 13)
       for number in (6, 7) for level in range(1, 4)},
    **{("F8", level): (14, 15) for level in range(1, 4)},
    ("C1", 1): (11, 13), ("C1", 2): (11, 13),
    **{("B2", level): (16, 16) for level in range(1, 4)},
    ("C2", 1): (16, 16), ("C2", 2): (16, 16),
    **{(f"B{number}", level): (17, 18)
       for number in range(3, 6) for level in range(1, 4)},
    **{(f"C{number}", level): (19, 21)
       for number in range(3, 6) for level in range(1, 3)},
    ("C1", 3): (23, 28), ("C2", 3): (23, 28),
    **{(f"B{number}", 4): (23, 28) for number in range(1, 6)},
}


@dataclass(frozen=True)
class HardcoreTower:
    tower_id: str
    tower_type: str
    slot: int
    optional: bool


@dataclass(frozen=True)
class HardcoreOperation:
    operation: str
    tower_id: str
    level: int | None = None
    optional: bool = False


@dataclass(frozen=True)
class HardcoreCheck:
    operation: str
    tower_ids: tuple[str, ...]
    level: int


@dataclass(frozen=True)
class HardcoreStage:
    first_wave: int
    last_wave: int
    actions: tuple[HardcoreOperation, ...]
    checks: tuple[HardcoreCheck, ...]


@dataclass(frozen=True)
class HardcorePlan:
    strategy_id: str
    profile_id: str
    map_name: str
    mode: str
    squad_size: int
    required_loadout: tuple[tuple[int, str], ...]
    optional_slot: int
    empty_slots: tuple[int, ...]
    placements: tuple[tuple[str, str], ...]
    skip_mode: str
    finish_wave: int
    min_wave_29_observations: int
    towers: tuple[HardcoreTower, ...]
    stages: tuple[HardcoreStage, ...]

    @property
    def tower_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for tower in self.towers:
            if not tower.optional:
                counts[tower.tower_type] = counts.get(tower.tower_type, 0) + 1
        return counts


class HardcorePlanError(ValueError):
    """Invalid or unsupported built-in Hardcore plan data."""


def _require_object(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise HardcorePlanError(f"{label} must contain exactly: {', '.join(sorted(keys))}.")
    return value


def _require_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise HardcorePlanError(f"{label} must be an integer in {minimum}..{maximum}.")
    return value


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise HardcorePlanError(f"duplicate JSON key {key!r}.")
        result[key] = value
    return result


def _expected_towers() -> dict[str, tuple[str, int, bool]]:
    expected = {
        f"F{number}": ("Farm", 3, False) for number in range(1, 9)
    }
    expected.update({
        f"B{number}": ("Boomerang", 1, False) for number in range(1, 6)
    })
    expected.update({
        f"C{number}": ("Crook Boss", 2, False) for number in range(1, 6)
    })
    expected["X1"] = ("EXP", 4, True)
    return expected


def parse_hardcore_plan(source: str) -> HardcorePlan:
    """Parse and validate only the fixed Hardcore plan schema; never executes data."""
    if not isinstance(source, str):
        raise HardcorePlanError("plan must be UTF-8 JSON text.")
    try:
        encoded = source.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise HardcorePlanError("plan must be valid UTF-8 text.") from exc
    if len(encoded) > MAX_PLAN_BYTES:
        raise HardcorePlanError("plan exceeds maximum allowed size.")
    try:
        data = json.loads(source, object_pairs_hook=_unique_json_object)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise HardcorePlanError("plan is not valid JSON.") from exc

    keys = {
        "schema_version", "strategy_id", "profile_id", "map", "mode", "squad_size",
        "required_loadout", "optional_slot", "slots_must_be_empty", "placements",
        "skip_policy", "finish_policy", "towers", "stages",
    }
    data = _require_object(data, keys, "plan")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise HardcorePlanError("unsupported plan schema version.")
    if data["strategy_id"] != PLAN_ID:
        raise HardcorePlanError("unrecognized Hardcore strategy ID.")
    if data["profile_id"] != PROFILE_ID:
        raise HardcorePlanError("profile ID must identify the fixed Wretched Front Hardcore profile.")
    if data["map"] != "Wretched Front":
        raise HardcorePlanError("map must be Wretched Front.")
    if data["mode"] != "Hardcore":
        raise HardcorePlanError("mode must be Hardcore.")
    if type(data["squad_size"]) is not int or data["squad_size"] != 1:
        raise HardcorePlanError("squad size must be exactly one player.")

    loadout = data["required_loadout"]
    if not isinstance(loadout, list):
        raise HardcorePlanError("required loadout must be a list.")
    parsed_loadout = []
    for entry in loadout:
        entry = _require_object(entry, {"slot", "tower"}, "loadout entry")
        slot = _require_int(entry["slot"], "loadout slot", 1, 5)
        if not isinstance(entry["tower"], str):
            raise HardcorePlanError("loadout tower names must be text.")
        parsed_loadout.append((slot, entry["tower"]))
    if tuple(parsed_loadout) != REQUIRED_LOADOUT:
        raise HardcorePlanError("required loadout must be Boomerang, regular Crook Boss, Farm in slots 1..3.")

    if type(data["optional_slot"]) is not int or data["optional_slot"] != OPTIONAL_SLOT:
        raise HardcorePlanError("optional tower slot must be 4.")
    empty_slots = data["slots_must_be_empty"]
    if (not isinstance(empty_slots, list) or len(empty_slots) != 1
            or type(empty_slots[0]) is not int or empty_slots[0] != 5):
        raise HardcorePlanError("slot 5 must be empty for the first supported profile.")

    raw_placements = data["placements"]
    if not isinstance(raw_placements, dict) or raw_placements != PLACEMENT_IDS:
        raise HardcorePlanError("placements must use the fixed named Wretched Front point references.")

    skip_policy = _require_object(
        data["skip_policy"], {"mode", "max_clicks_per_wave"}, "skip policy"
    )
    if skip_policy["mode"] != "auto_then_one_per_wave" or type(skip_policy["max_clicks_per_wave"]) is not int or skip_policy["max_clicks_per_wave"] != 1:
        raise HardcorePlanError("skip policy must use confirmed auto-skip or at most one click per wave.")

    finish = _require_object(
        data["finish_policy"],
        {"target_wave", "result", "minimum_positive_wave_observations"},
        "finish policy",
    )
    finish_wave = _require_int(finish["target_wave"], "finish wave", 29, 29)
    if finish["result"] != "natural_result":
        raise HardcorePlanError("finish policy must wait for the natural match result.")
    min_wave_29_observations = _require_int(
        finish["minimum_positive_wave_observations"],
        "positive wave-29 observations",
        2,
        2,
    )

    expected = _expected_towers()
    raw_towers = data["towers"]
    if not isinstance(raw_towers, list) or len(raw_towers) != len(expected):
        raise HardcorePlanError("tower roster must contain exactly the 18 required towers and optional X1.")
    tower_by_id: dict[str, HardcoreTower] = {}
    for raw_tower in raw_towers:
        raw_tower = _require_object(
            raw_tower, {"id", "type", "slot", "optional"}, "tower entry"
        )
        tower_id = raw_tower["id"]
        if not isinstance(tower_id, str) or tower_id not in expected:
            raise HardcorePlanError("tower ID is not in the fixed F1-F8, B1-B5, C1-C5, X1 roster.")
        if tower_id in tower_by_id:
            raise HardcorePlanError(f"duplicate tower ID {tower_id}.")
        tower_type, slot, optional = expected[tower_id]
        if (raw_tower["type"], raw_tower["slot"], raw_tower["optional"]) != (tower_type, slot, optional):
            raise HardcorePlanError(f"tower type, slot, or optional flag is wrong for {tower_id}.")
        if type(raw_tower["slot"]) is not int or type(raw_tower["optional"]) is not bool:
            raise HardcorePlanError(f"tower slot and optional flag must have strict types for {tower_id}.")
        tower_by_id[tower_id] = HardcoreTower(tower_id, tower_type, slot, optional)
    if set(tower_by_id) != set(expected):
        raise HardcorePlanError("tower roster does not match the fixed required counts.")
    canonical_tower_order = tuple(expected)
    if tuple(tower_by_id) != canonical_tower_order:
        raise HardcorePlanError("tower roster must use the canonical F1-F8, B1-B5, C1-C5, X1 order.")

    raw_stages = data["stages"]
    if not isinstance(raw_stages, list) or not raw_stages:
        raise HardcorePlanError("plan must contain wave stages.")
    stages: list[HardcoreStage] = []
    placed: set[str] = set()
    scheduled_upgrades: set[tuple[str, int]] = set()
    levels = {tower_id: 0 for tower_id in tower_by_id}
    previous_last_wave = -1
    observed_windows: list[tuple[int, int]] = []

    for raw_stage in raw_stages:
        raw_stage = _require_object(raw_stage, {"waves", "actions", "checks"}, "stage")
        waves = raw_stage["waves"]
        if not isinstance(waves, list) or len(waves) != 2:
            raise HardcorePlanError("wave window must contain exactly two bounds.")
        first_wave = _require_int(waves[0], "wave window start", 0, 45)
        last_wave = _require_int(waves[1], "wave window end", first_wave, 45)
        if last_wave > finish_wave:
            raise HardcorePlanError(f"wave window cannot extend beyond finish wave {finish_wave}.")
        if first_wave <= previous_last_wave:
            raise HardcorePlanError("wave windows must be strictly increasing and nonoverlapping.")
        previous_last_wave = last_wave
        observed_windows.append((first_wave, last_wave))
        raw_actions = raw_stage["actions"]
        raw_checks = raw_stage["checks"]
        if not isinstance(raw_actions, list) or not isinstance(raw_checks, list):
            raise HardcorePlanError("stage actions and checks must be lists.")
        if (first_wave, last_wave) == (14, 15) and not raw_checks:
            raise HardcorePlanError("wave 14-15 must verify all eight Farms at level 3.")
        if not raw_actions and not raw_checks and (first_wave, last_wave) not in {(22, 22), (finish_wave, finish_wave)}:
            raise HardcorePlanError("every required wave stage must contain actions or checks.")
        actions: list[HardcoreOperation] = []
        checks: list[HardcoreCheck] = []

        for raw_action in raw_actions:
            if not isinstance(raw_action, dict):
                raise HardcorePlanError("stage action must be an object.")
            operation = raw_action.get("op")
            if not isinstance(operation, str) or operation not in {"place", "upgrade"}:
                raise HardcorePlanError("unsupported plan operation.")
            action_keys = {"op", "tower_id", "level"} if operation == "upgrade" else {"op", "tower_id"}
            if not isinstance(raw_action, dict) or frozenset(raw_action) not in {
                frozenset(action_keys), frozenset(action_keys | {"optional"})
            }:
                raise HardcorePlanError("stage action contains unknown or missing fields.")
            optional = raw_action.get("optional", False)
            if type(optional) is not bool or ("optional" in raw_action and not optional):
                raise HardcorePlanError("optional actions must mark optional=true explicitly.")
            tower_id = raw_action["tower_id"]
            if not isinstance(tower_id, str) or tower_id not in tower_by_id:
                raise HardcorePlanError("operation references an unknown tower ID.")
            tower = tower_by_id[tower_id]

            permitted_optional = (
                (operation == "place" and tower_id == "X1")
                or (operation == "upgrade" and tower.tower_type == "Boomerang"
                    and raw_action.get("level") == 4)
            )
            if optional and not permitted_optional:
                raise HardcorePlanError(f"optional flag is not allowed for {operation} on {tower_id}.")
            if permitted_optional and not optional:
                raise HardcorePlanError(f"{operation} on {tower_id} must be explicitly optional.")

            if operation == "place":
                if last_wave >= finish_wave:
                    raise HardcorePlanError("placement is not allowed after the finish phase begins.")
                if (first_wave, last_wave) != PLACE_WINDOWS[tower_id]:
                    raise HardcorePlanError(f"{tower_id} placement is outside its required wave window.")
                if tower_id in placed:
                    raise HardcorePlanError(f"duplicate placement for tower {tower_id}.")
                if tower.optional and not (first_wave <= 22 <= last_wave):
                    raise HardcorePlanError("optional EXP tower placement must be in the wave-22 window.")
                placed.add(tower_id)
                actions.append(HardcoreOperation(operation, tower_id, optional=optional))
            else:
                level = _require_int(raw_action["level"], "upgrade level", 1, 4)
                max_level = {"Farm": 3, "Boomerang": 4, "Crook Boss": 3, "EXP": 4}[tower.tower_type]
                if last_wave >= finish_wave or tower_id not in placed:
                    raise HardcorePlanError("upgrade requires a placed tower before the finish phase.")
                if level != levels[tower_id] + 1 or level > max_level:
                    raise HardcorePlanError(f"upgrade level must increase by one and stay within the limit for {tower_id}.")
                if UPGRADE_WINDOWS.get((tower_id, level)) != (first_wave, last_wave):
                    raise HardcorePlanError(f"{tower_id} level {level} upgrade is outside its required wave window.")
                levels[tower_id] = level
                scheduled_upgrades.add((tower_id, level))
                actions.append(HardcoreOperation(operation, tower_id, level, optional))

        for raw_check in raw_checks:
            raw_check = _require_object(
                raw_check, {"op", "tower_ids", "level"}, "stage check"
            )
            if raw_check["op"] != "verify_tower_levels":
                raise HardcorePlanError("unsupported stage check.")
            tower_ids = raw_check["tower_ids"]
            if not isinstance(tower_ids, list) or any(
                not isinstance(tower_id, str) or tower_id not in tower_by_id
                for tower_id in tower_ids
            ):
                raise HardcorePlanError("stage check references an unknown tower ID.")
            if len(set(tower_ids)) != len(tower_ids):
                raise HardcorePlanError("stage check contains duplicate tower IDs.")
            level = _require_int(raw_check["level"], "check level", 1, 4)
            if (first_wave, last_wave) != (14, 15) or tuple(tower_ids) != FARM_CHECK_IDS or level != 3:
                raise HardcorePlanError("the only supported check is all eight Farms at level 3 on waves 14-15.")
            if any(tower_id not in placed or levels[tower_id] != level for tower_id in tower_ids):
                raise HardcorePlanError("Farm level checkpoint failed against the preceding action ledger.")
            checks.append(HardcoreCheck("verify_tower_levels", tuple(tower_ids), level))

        if (first_wave, last_wave) == (14, 15) and len(checks) != 1:
            raise HardcorePlanError("wave 14-15 must verify all eight Farms at level 3.")
        if (first_wave, last_wave) != (14, 15) and checks:
            raise HardcorePlanError("Farm checkpoint is supported only on waves 14-15.")

        stages.append(HardcoreStage(first_wave, last_wave, tuple(actions), tuple(checks)))

    if tuple(observed_windows) != REQUIRED_STAGE_WINDOWS:
        raise HardcorePlanError("plan must contain the exact required wave-stage windows, including 14-15.")

    required_ids = {tower_id for tower_id, (_, _, optional) in expected.items() if not optional}
    if not required_ids.issubset(placed):
        raise HardcorePlanError("plan must place every required tower exactly once.")
    required_upgrades = {
        key for key in UPGRADE_WINDOWS if not (key[0].startswith("B") and key[1] == 4)
    }
    if not required_upgrades.issubset(scheduled_upgrades):
        raise HardcorePlanError("plan omits a required upgrade from the fixed stage schedule.")

    return HardcorePlan(
        strategy_id=PLAN_ID,
        profile_id=PROFILE_ID,
        map_name="Wretched Front",
        mode="Hardcore",
        squad_size=1,
        required_loadout=REQUIRED_LOADOUT,
        optional_slot=OPTIONAL_SLOT,
        empty_slots=EMPTY_SLOTS,
        placements=tuple(PLACEMENT_IDS.items()),
        skip_mode=skip_policy["mode"],
        finish_wave=finish_wave,
        min_wave_29_observations=min_wave_29_observations,
        towers=tuple(tower_by_id[tower_id] for tower_id in canonical_tower_order),
        stages=tuple(stages),
    )


def validate_hardcore_plan(plan: HardcorePlan) -> HardcorePlan:
    """Revalidate a typed plan using the same strict fixed-schema checks."""
    if not isinstance(plan, HardcorePlan):
        raise HardcorePlanError("plan must be a HardcorePlan instance.")
    source = {
        "schema_version": 1,
        "strategy_id": plan.strategy_id,
        "profile_id": plan.profile_id,
        "map": plan.map_name,
        "mode": plan.mode,
        "squad_size": plan.squad_size,
        "required_loadout": [
            {"slot": slot, "tower": tower} for slot, tower in plan.required_loadout
        ],
        "optional_slot": plan.optional_slot,
        "slots_must_be_empty": list(plan.empty_slots),
        "placements": dict(plan.placements),
        "skip_policy": {"mode": plan.skip_mode, "max_clicks_per_wave": 1},
        "finish_policy": {
            "target_wave": plan.finish_wave,
            "result": "natural_result",
            "minimum_positive_wave_observations": plan.min_wave_29_observations,
        },
        "towers": [
            {"id": tower.tower_id, "type": tower.tower_type, "slot": tower.slot,
             "optional": tower.optional}
            for tower in plan.towers
        ],
        "stages": [
            {
                "waves": [stage.first_wave, stage.last_wave],
                "actions": [
                    {"op": action.operation, "tower_id": action.tower_id,
                     **({"level": action.level} if action.level is not None else {}),
                     **({"optional": True} if action.optional else {})}
                    for action in stage.actions
                ],
                "checks": [
                    {"op": check.operation, "tower_ids": list(check.tower_ids),
                     "level": check.level}
                    for check in stage.checks
                ],
            }
            for stage in plan.stages
        ],
    }
    try:
        return parse_hardcore_plan(json.dumps(source, ensure_ascii=True))
    except (TypeError, ValueError, RecursionError) as exc:
        if isinstance(exc, HardcorePlanError):
            raise
        raise HardcorePlanError("typed plan contains invalid values.") from exc


def load_hardcore_plan(path: str | Path | None = None) -> HardcorePlan:
    """Load only the hash-pinned built-in plan, never a community-supplied file."""
    canonical = (ROOT / PLAN_RELATIVE_PATH).resolve()
    try:
        candidate = canonical if path is None else Path(path).resolve()
    except (OSError, TypeError, ValueError) as exc:
        raise HardcorePlanError("only the built-in Hardcore plan can be loaded.") from exc
    if candidate != canonical:
        raise HardcorePlanError("only the built-in Hardcore plan can be loaded.")
    try:
        source = candidate.read_bytes()
    except OSError as exc:
        raise HardcorePlanError("built-in Hardcore plan is unavailable.") from exc
    if len(source) > MAX_PLAN_BYTES:
        raise HardcorePlanError("built-in plan exceeds maximum allowed size.")
    if hashlib.sha256(source).hexdigest() != PLAN_SHA256:
        raise HardcorePlanError("built-in plan integrity changed; recalibration required.")
    try:
        return parse_hardcore_plan(source.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise HardcorePlanError("built-in plan must be UTF-8 JSON.") from exc
