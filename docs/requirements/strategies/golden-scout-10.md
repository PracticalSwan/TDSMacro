# Golden Scout — 10 Max (current)

**Executable selector:** `Golden Scout — 10 Max / Dead Ahead / Easy`; controller strategy `golden_scout`, distinguished from legacy by the exact profile `calibrations/dead_ahead_vertical_ten_v031_v2202_trial.json`. Strategy steps: `strategies/GOLDIE SCOUTO.vertical-ten-slot1-v031-2202.strat`. **Do not identify the Golden variant by `golden_scout` alone.**

## Requirements before Start

| Requirement | Required condition | Evidence / limitation |
| --- | --- | --- |
| Tower ownership and perk | Scout equipped in **slot 1**, Golden perk active (not merely a gold-themed skin); slots **2–5 empty** | Exact inventory Scout / Golden / UNEQUIP and match hotbar, not portraits |
| Gameplay | Survival **Easy**, **Solo**, **Dead Ahead** | Verified map vote, selected difficulty and result |
| Map access | VIP-assisted selection available where required for deterministic Dead Ahead access | Existing selected-map flow; do not assume it is free on every account |
| Economy skills | **No fixed Bigger Budget / Stonks / Scavenger level in code** | Lowest-skill full Victory has not been natively tested |
| Cash before first placement | **At least $250** at the first Scout placement, before waves start | Strategy's first action is SpawnTower; current Golden Scout placement quote is $250 |
| Upgrades | Sufficient verified live cash for each of **40 upgrades**; runner waits for observed affordability within timeout | Dynamic cash/quote reading; later timings not guaranteed for all skill combinations |
| Geometry | 1920x991 @ 120 DPI, supported terrain landmarks and calibrated overhead camera, 1x normal pace | Pinned profile; changed camera or preview stops |
| Modifiers | None; do not assume a modifier challenge is supported | Existing calibrated strategy has blank modifiers |

**Known v0.5.1 reliability caveat (November 24):** The executor currently deselects/reselects before every E upgrade and sometimes fails to verify a TRIUMPH result when a selected Scout tooltip obscures the panel. Also see the separate count-10 and camera bugs. These are documented as **open, not patched** in [the bug register](../../../BUGS_FOUND.md) and [planned v0.5.2 fix](../../plans/2026-11-24-v0.5.2-golden-upgrade-selection-revamp.md).

The separate v0.5.2 candidate reuses a still-proven selection for E and credits a Victory after all 50 actions and a verified Coin receipt. See [candidate verification](../../verification.md) for current evidence.

## Native result / success definition

- First placement and all subsequent purchases must be positively confirmed; intended path: **10 placements + 40 upgrades = 50** actions, with 10 Scouts at **level 4**.
- Positive **wave-20 Victory** on Easy Solo Dead Ahead and readable nonnegative Coin reward on the result panel. A result banner alone is insufficient.
- The current worker reports a `victory` and coins after result verification; **v1.0 rotation should additionally require the expected action and final-level evidence** before counting a leg success, and should not silently infer it from a profile name.
- On success, the existing strategy can Play Again. v1.0 rotation must instead return to a verified lobby if the *next* strategy differs.

## Skill compatibility assessment

**Expected / unverified for zero Economy skills**, not “guaranteed for any perks.” TDS Easy's published starting cash ($500 without group bonus/skills) exceeds the verified $250 first purchase. Subsequent purchases are guarded by live resources; nevertheless, decreased wave/kill income and loss of other offensive skills can shift upgrade timing or cause a Defeat. Accept a skill-neutral claim only after fresh zero/low-skill native full runs with the current game version.

## Evidence and source

The project's v0.3.1/v0.5.1 records contain earlier 50/50-action ten-level-4 victories on the tested account; they do **not** represent multi-account or zero-skill certification. See `src/tds_auto/app.py`, `src/tds_auto/session.py`, `src/tds_auto/match.py`, and `docs/verification.md`. Reconfirm the saved profile and UI after TDS updates.
