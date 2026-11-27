# Golden Scout — 9 Scouts (legacy fallback)

> Fallback remains supported in released v0.5.2. Future retirement conditional on [consolidation acceptance](../../plans/2026-11-25-v1.0-legacy-consolidation.md); do not remove or silently substitute it.

**Executable selector:** `Golden Scout — 9 Scouts (legacy fallback)`; controller strategy `golden_scout`, uniquely identified by profile `calibrations/dead_ahead_vertical_nine_v4.json`, with steps `strategies/GOLDIE SCOUTO.vertical-nine-slot1.strat`. This fallback must not be silently replaced by the 10-Scout variant.

## Requirements before Start

| Requirement | Required condition | Evidence / limitation |
| --- | --- | --- |
| Tower and perk | Scout in **slot 1** with active **Golden** perk; slots 2–5 **empty** | Exact inventory Scout/Golden/UNEQUIP plus hotbar |
| Match | Dead Ahead / Survival Easy / Solo | Exact mode/map/player checks; VIP-assisted deterministic map access where needed |
| Economy | Live cash **at least $250** before initial Scout placement; each subsequent purchase positively affordable | TDS Easy published start $500; no minimum Economy-skill level encoded |
| Performance/environment | Current supported 1920x991 120-DPI UI, pinned camera and available landmarks, normal speed, no modifiers | This is an older separate calibration; must pass contemporary UI checks |
| Loadout state | No leftover Hardcore tower in any other slot | Do not infer empty slot from a blank-looking tile alone |

## Success definition and limitations

- Execute and positively confirm the legacy **44 actions**: **9 Scout placements + 35 upgrades**.
- Final intended levels: eight Scouts at level 4, ninth Scout at level 3.
- Verify **Easy Solo Dead Ahead wave-20 Victory**, all 44 confirmed actions (full_strategy_verified=True) and readable nonnegative Coin reward before counting a run. v0.5.2 keeps the separate legacy mouse-upgrade path.
- Lower skill levels might still be affordable because the first $250 placement is below baseline Easy starting cash, but **a complete zero-skill victory is unverified**. Never claim this strategy is automatically viable on all accounts.
- Do not change its source, calibrated positions, or purchase policy when implementing the v1.0 selector or rotation. The future success key must include the exact **profile hash**, not just `golden_scout`.

Source: `src/tds_auto/app.py`, `src/tds_auto/match.py`, `calibrations/dead_ahead_vertical_nine_v4.json`, `docs/strategies.md`. Legacy success claims come from historical tests, not universal/perk-independent acceptance.
