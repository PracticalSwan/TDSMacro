# <Strategy display name> — execution requirements

**Status:** Proposed / implementation / native-verified for stated account / released. **Strategy ID:** `<id>`. **Exact immutable profile or plan:** `<path + hash>`. **Maintainer:** <person or project>. **Last verified:** <date/game client version>.

## Preconditions

| Category | Exact requirement | How verified | Proof status |
| --- | --- | --- | --- |
| Game/map/mode/party | <map/difficulty/Solo etc.> | <positive readback> | <status> |
| Towers/perks | <ordered slots, empty slots, upgrades/evolutions> | <text identity + hotbar> | <status> |
| Account/game access | <VIP, mode unlock, inventory access> | <positive check> | <status> |
| Starting cash | <minimum observed live cash; formula only for illustration> | <HUD cash + price> | <status> |
| Cash skills | <Bigger Budget, Stonks, Scavenger and enabled/disabled> | <settings or observational proof> | <status> |
| Other relevant skills | <damage/range/health/placement cap> | <native outcomes> | <status> |
| Technical setup | <resolution/DPI/HUD/camera/speed/locale> | <preflight> | <status> |
| Modifiers/player count | <supported exact set> | <positive readback> | <status> |

## Strategy steps and stopping conditions

- Opening actions and **exact pre-Ready cash requirement**:
- Number of placements/upgrades, expected final levels, target wave:
- Dynamic affordability/defense priorities and conditional purchases:
- Unknown/wrong input, changed UI/terrain, missed upgrades and recovery policy:

## Definition of one successful run

**Required in-game outcome:** <Victory/Defeat and wave>, mode/map, reward label and amount, required towers/levels, verified screenshot(s). Distinguish displayed rewards, wallet credit and tower XP. Provide an **unambiguous success predicate** for any v1.0 rotation.

**Do not count:** partial match, unknown result, recovery, idle period, optional placement without XP evidence, etc.

## Evidence status and compatibility matrix

- Native trial records: <paths/cycle IDs; private data excluded from public docs>
- Skill combinations actually tested: <exact settings; including Skills Enabled and group bonus>
- Unsupported combinations: <what was verified impossible>
- Unverified combinations: <explicitly, do not claim universality>
- Proven bounded recoveries and stop behavior:
- Required new negative/low-skill/multi-account trials:

## Source of truth and update procedure

Link exact strategy JSON/.strat, calibration, executor, relevant tests, game references, date/version, and independent result evidence. Update this sheet whenever a game/client change or strategy release affects requirements. Before including in a v1.0 rotation: native equipment switching must be demonstrably safe, and this document must identify the exact success predicate.
