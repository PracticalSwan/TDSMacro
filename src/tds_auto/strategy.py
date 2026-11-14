"""Strict, read-only parser for Ultimate Macro-style .strat files.

Imported strategies are DATA. Never eval/exec any operation or follow arbitrary
instructions from the input. Future playback requires separate implementation.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import json
import re
import sys

MAX_BYTES = 200_000
MAX_STEPS = 2000
SECTION = re.compile(r"^\[([^\]]+)\]$")
ACTION = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\((.*)\)$")
INT = re.compile(r"^[0-9]+$")
ALLOWED_ACTIONS = {"SpawnTower": 4, "UpgradeTower": 1}


@dataclass(frozen=True)
class Step:
    operation: str
    args: tuple[int, ...]


@dataclass(frozen=True)
class Strategy:
    title: str
    author: str
    description: str
    claimed_income: str
    claimed_duration: str
    map_name: str
    difficulty: str
    required_towers: tuple[str, ...]
    modifiers: tuple[str, ...]
    auto_skip: bool
    move_enabled: bool
    move_direction: str
    move_duration_ms: int
    source_width: int
    source_height: int
    steps: tuple[Step, ...]


class StrategyError(ValueError):
    """Invalid or unsupported input; do not attempt to play."""


def _number(value: str, label: str, minimum: int, maximum: int) -> int:
    if not INT.fullmatch(value.strip()):
        raise StrategyError(f"{label}: expected an unsigned integer")
    n = int(value)
    if not minimum <= n <= maximum:
        raise StrategyError(f"{label}: expected {minimum}..{maximum}, got {n}")
    return n


def _switch(value: str, label: str) -> bool:
    if value.strip().upper() not in {"ON", "OFF", "0", "1"}:
        raise StrategyError(f"{label}: expected ON/OFF/0/1")
    return value.strip().upper() in {"ON", "1"}


def parse_strategy(source: str) -> Strategy:
    if len(source.encode("utf-8")) > MAX_BYTES:
        raise StrategyError("strategy exceeds maximum allowed size")
    sections: dict[str, dict[str, str]] = {}
    steps: list[Step] = []
    current: str | None = None
    existing_ids: set[int] = set()
    for line_number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(("#", ";")):
            continue
        match = SECTION.fullmatch(line)
        if match:
            current = match.group(1)
            if current not in {"Info", "Settings", "DO NOT EDIT", "Steps"}:
                raise StrategyError(f"line {line_number}: unsupported section [{current}]")
            if current in sections:
                raise StrategyError(f"line {line_number}: duplicate section [{current}]")
            sections[current] = {}
            continue
        if current is None:
            raise StrategyError(f"line {line_number}: content outside a section")
        if current == "Steps":
            match = ACTION.fullmatch(line)
            if not match:
                raise StrategyError(f"line {line_number}: malformed strategy operation")
            operation, values = match.groups()
            if operation not in ALLOWED_ACTIONS:
                raise StrategyError(f"line {line_number}: unsupported operation {operation!r}")
            parts = [v.strip() for v in values.split(",")]
            if len(parts) != ALLOWED_ACTIONS[operation]:
                raise StrategyError(f"line {line_number}: incorrect argument count")
            args = tuple(_number(part, f"line {line_number} argument", 0, 100000) for part in parts)
            if operation == "SpawnTower":
                x, y, slot, ident = args
                if not (1 <= slot <= 5):
                    raise StrategyError(f"line {line_number}: tower slot must be 1..5")
                if ident != len(existing_ids) + 1:
                    raise StrategyError(f"line {line_number}: tower IDs must be sequential and unique")
                existing_ids.add(ident)
            else:
                if args[0] not in existing_ids:
                    raise StrategyError(f"line {line_number}: upgrade targets an unknown tower ID")
            steps.append(Step(operation, args))
            if len(steps) > MAX_STEPS:
                raise StrategyError("strategy contains too many steps")
        else:
            if "=" not in line:
                raise StrategyError(f"line {line_number}: expected key=value")
            key, value = line.split("=", 1)
            key = key.strip()
            if not key or key in sections[current]:
                raise StrategyError(f"line {line_number}: empty or duplicate setting key")
            sections[current][key] = value.strip()

    if not {"Info", "Settings", "DO NOT EDIT", "Steps"}.issubset(sections):
        raise StrategyError("missing one of the four required sections")
    info, opts, geometry = (sections[n] for n in ("Info", "Settings", "DO NOT EDIT"))
    width = _number(geometry.get("width", ""), "source width", 600, 8192)
    height = _number(geometry.get("height", ""), "source height", 400, 8192)
    if not steps:
        raise StrategyError("empty steps list")
    for idx, step in enumerate(steps, 1):
        if step.operation == "SpawnTower":
            x, y, _, _ = step.args
            if not 0 <= x < width or not 0 <= y < height:
                raise StrategyError(f"step {idx}: spawn point is outside source geometry")
    map_name = opts.get("map", "").strip()
    difficulty = opts.get("difficulty", "").strip()
    if not map_name or not difficulty:
        raise StrategyError("map and difficulty are required")
    tower_names = tuple(t.strip() for t in opts.get("requiredTowers", "").split(",") if t.strip())
    if not tower_names:
        raise StrategyError("requiredTowers is empty; cannot validate loadout")
    move_enabled = _switch(opts.get("moveEnabled", "0"), "moveEnabled")
    move_direction = opts.get("moveDirection", "").strip().upper()
    if move_enabled and move_direction not in {"W", "A", "S", "D"}:
        raise StrategyError("moveDirection must be W, A, S or D")
    move_duration = _number(opts.get("moveDuration", "0"), "moveDuration", 0, 30000)
    return Strategy(
        title=info.get("title", ""), author=info.get("author", ""),
        description=info.get("desc", ""),
        claimed_income=info.get("income", ""),
        claimed_duration=info.get("time", ""),
        map_name=map_name, difficulty=difficulty,
        required_towers=tower_names,
        modifiers=tuple(x.strip() for x in opts.get("modifiers", "").split(",") if x.strip()),
        auto_skip=_switch(opts.get("autoSkip", "OFF"), "autoSkip"),
        move_enabled=move_enabled, move_direction=move_direction,
        move_duration_ms=move_duration, source_width=width, source_height=height,
        steps=tuple(steps)
    )


def read_strategy(path: Path) -> Strategy:
    if not path.is_file():
        raise StrategyError("strategy file does not exist")
    if path.stat().st_size > MAX_BYTES:
        raise StrategyError("strategy exceeds maximum allowed size")
    try:
        data = path.read_text(encoding="utf-8-sig")
    except (UnicodeError, OSError) as exc:
        raise StrategyError(f"cannot read strategy: {type(exc).__name__}") from exc
    return parse_strategy(data)


def preflight(strategy: Strategy, client_width: int | None = None,
              client_height: int | None = None) -> dict:
    counts = Counter(step.operation for step in strategy.steps)
    warnings: list[str] = []
    if client_width is not None and client_height is not None:
        if (client_width, client_height) != (strategy.source_width, strategy.source_height):
            warnings.append(
                f"GEOMETRY_MISMATCH: strategy={strategy.source_width}x{strategy.source_height}; "
                f"observed={client_width}x{client_height}; placement calibration required"
            )
    elif client_width is not None or client_height is not None:
        raise StrategyError("client width and height must be supplied together")
    warnings += [
        "LOADOUT_UNVERIFIED: required slot/tower identity has not been confirmed in game",
        "MODE_MAP_UNVERIFIED: target mode/map selection has not been confirmed in game",
        "NO_TIMING_GATES: steps include no wave, cash or placement-success conditions",
        "MODIFIER_UNVERIFIED: listed modifiers must be checked against in-game availability",
        "REWARDS_UNVERIFIED: income and duration are author estimates, not measured results",
    ]
    return {
        "title": strategy.title,
        "author": strategy.author,
        "mode": strategy.difficulty,
        "map": strategy.map_name,
        "required_towers": list(strategy.required_towers),
        "modifiers": list(strategy.modifiers),
        "auto_skip": strategy.auto_skip,
        "initial_movement": {
            "enabled": strategy.move_enabled,
            "direction": strategy.move_direction,
            "duration_ms": strategy.move_duration_ms,
        },
        "geometry": {"width": strategy.source_width, "height": strategy.source_height},
        "steps": len(strategy.steps),
        "spawn_count": counts["SpawnTower"],
        "upgrade_count": counts["UpgradeTower"],
        "slots_used": sorted({s.args[2] for s in strategy.steps if s.operation == "SpawnTower"}),
        "max_tower_id": max((s.args[3] for s in strategy.steps if s.operation == "SpawnTower"), default=0),
        "claimed_income": strategy.claimed_income,
        "claimed_duration": strategy.claimed_duration,
        "ready_for_automatic_execution": False,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect a .strat file without executing game actions.")
    parser.add_argument("file", type=Path)
    parser.add_argument("--client-width", type=int)
    parser.add_argument("--client-height", type=int)
    args = parser.parse_args(argv)
    try:
        result = preflight(read_strategy(args.file), args.client_width, args.client_height)
    except StrategyError as exc:
        print(f"STRATEGY_INVALID: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
