"""Load the owner-approved v2 phase schedule from its exact bundled file."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .hardcore_plan import MAX_PLAN_BYTES, ROOT, HardcoreOperation, HardcorePlanError, HardcoreTower


PLAN_ID = 'hardcore_gem_grind_wretched_front_v2'
XP_PLAN_ID = 'hardcore_gem_xp_wretched_front_v2'
HARDCORE_V2_IDS = frozenset((PLAN_ID, XP_PLAN_ID))

def is_hardcore_v2(strategy_id):
    return strategy_id in HARDCORE_V2_IDS

PROFILE_ID = 'wretched_front_hardcore_v2'
PLAN_PATH = Path('strategies/hardcore_wretched_front_boomerang_crook_farm_v2.json')
PLAN_SHA256 = '3bc8761073a85cab3e14d68a547cc8777085c5910459400bd91d85432ef1e1ef'


@dataclass(frozen=True)
class HardcorePhase:
    step: int
    before_ready: bool
    actions: tuple[HardcoreOperation, ...]


@dataclass(frozen=True)
class HardcorePlanV2:
    strategy_id: str
    profile_id: str
    map_name: str
    mode: str
    squad_size: int
    required_loadout: tuple[tuple[int, str], ...]
    optional_slot: int
    empty_slots: tuple[int, ...]
    towers: tuple[HardcoreTower, ...]
    phases: tuple[HardcorePhase, ...]
    highest_upgrade_first: frozenset[str]
    crook_level_before_next_purchase: int
    farm_payout_by_level: tuple[int, ...]
    final_required_levels: tuple[tuple[str, int], ...]
    finish_wave: int
    min_target_observations: int


def load_hardcore_plan_v2():
    """Convert the pinned plan to typed data. External plans are never accepted."""
    with (ROOT / PLAN_PATH).open('rb') as stream:
        raw = stream.read(MAX_PLAN_BYTES + 1)
    if len(raw) > MAX_PLAN_BYTES or hashlib.sha256(raw).hexdigest() != PLAN_SHA256:
        raise HardcorePlanError('The built-in Hardcore v2 plan digest changed.')
    data = json.loads(raw)
    towers = tuple(HardcoreTower(t['id'], t['type'], t['slot'], t['optional']) for t in data['towers'])
    phases = tuple(HardcorePhase(
        phase['step'], phase.get('before_ready', False),
        tuple(HardcoreOperation(action['op'], action['tower_id'], action.get('level'),
                                action.get('optional', False)) for action in phase['actions']),
    ) for phase in data['phases'])
    finish = data['finish_policy']
    return HardcorePlanV2(
        data['strategy_id'], data['profile_id'], data['map'], data['mode'], data['squad_size'],
        tuple((entry['slot'], entry['tower']) for entry in data['required_loadout']),
        data['optional_slot'], tuple(data['slots_must_be_empty']), towers, phases,
        frozenset(data['purchase_policy']['highest_upgrade_first']),
        data['purchase_policy']['crook_level_before_next_purchase'],
        tuple(data['purchase_policy']['farm_payout_by_level']),
        tuple(data['final_required_levels'].items()), finish['target_wave'],
        finish['minimum_positive_wave_observations'],
    )
