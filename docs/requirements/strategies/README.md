# Strategy execution requirements

**Status:** reviewed against released v0.5.2 on 2026-11-25 (Thailand). These requirements document existing guards; automatic loadout switching, strategy rotation and [explicit slot-4 tower selection](../../plans/2026-11-25-v1.0-slot4-tower-selection.md) are not implemented. The live profiles remain the executable source of truth.

Each selectable strategy has a separate requirement sheet:

| GUI selection | Requirements | Verified success target |
| --- | --- | --- |
| Golden Scout — 10 Max / Dead Ahead / Easy | [golden-scout-10.md](golden-scout-10.md) | Easy Solo Dead Ahead, wave-20 Victory, 10 Scouts at level 4; 50 actions |
| Golden Scout — 9 Scouts (legacy fallback) | [golden-scout-9.md](golden-scout-9.md) | Same game result; 9 Scouts, first 8 at level 4, ninth at level 3; 44 actions |
| Hardcore Gem Grind — 3 Towers / Solo | [hardcore-gems-3.md](hardcore-gems-3.md) | Hardcore Solo Wretched Front, wave-30 natural Defeat, 137 Gems displayed; 75 core actions |
| Hardcore Gems + Tower XP — Slot 4 / Solo | [hardcore-gems-xp-4.md](hardcore-gems-xp-4.md) | Same Gem result plus a separately verified eligible XP tower placement; 75 core + 1 optional action when placed |

**New strategies MUST begin with a copy of [_TEMPLATE.md](_TEMPLATE.md)**, stored in this directory with an unambiguous strategy ID. A future strategy is not eligible for automatic rotation until its requirements, failure conditions, preflight checks, success predicate, and native acceptance tests exist.

## Common non-negotiable execution conditions

- Windows 11 x64 and supported Microsoft Store Roblox GDK client; **1920 x 991 physical client pixels at 120 DPI** (125% display scaling in tested configuration). Other geometry requires separate calibration.
- Roblox stays the verified foreground window with default supported English UI, unmodified HUD and input bindings, stable camera, correct game speed, and exactly one macro worker/input controller.
- Strategy, map, difficulty, Solo player count, and equipment **order** are explicitly verified. An inventory icon, portrait, color, or unexplained empty-looking tile does not prove slot identity.
- Mode access, map selection (including VIP when the calibrated flow requires it), and required towers/perks must exist on the account. Skills can be disabled in TDS Settings; owning a skill level does not prove it is active.
- **Cash and price are authoritative only when read from the current match.** Published formulas and skill levels are screening information, not permission to buy. The worker must not send a paid action when price, cash, selected tower/level, preview, camera, focus, or postcondition is uncertain.
- No unvalidated modifiers, event-only game modes, non-Solo queues, alternate UI scales/skins that break text recognition, changed input bindings, or client modifications.
- F2 safe stop, F8/Escape emergency stop, restricted restart, up to two direct uncredited replays and three guarded client relaunches in released v0.5.2, and private result diagnostics remain available. Never silently retry an uncertain upgrade or placement.
- A successful run means a **positively verified strategy-specific result**. Attempts, incomplete results, early Defeats, unattended idle time, and recovery are not successes by themselves. A deferred optional XP tower does not invalidate an otherwise qualifying Hardcore Gem result; it is not an XP placement success.
- Result-screen Gems/Coins are not independent wallet audits. Any v1.0 requirements UI must say *displayed rewards* unless separately verified.

## Economy evidence and compatibility labels

- Official TDS documentation presently lists Easy starting cash as **$500** and Hardcore Solo as **$900**, with an additional **$100 group-membership bonus**. Bigger Budget gives +1% starting cash per level (after any group bonus); Stonks affects wave income; Scavenger affects selected enemy-kill income.
- Because starting cash can vary, requirements specify a **minimum observed in-match cash** for the opening, not an absolute minimum skill level. A lower-skill account may be supported if the observed cash and subsequent defense timeline are actually sufficient.
- Use **Proven** only for a completed verified native run in the specified account/skill/UI configuration; **Expected / unverified** for arithmetic and source logic; **Unsupported** for an explicitly known violation. Do not use a universal “works for every player” claim from a single account.
- Additional skills can alter effective combat strength or base health. These may help, but no level range is universally validated for these four strategies.

### Source references

- [Local setup](../../setup.md), [strategy implementation provenance](../../strategies.md), [native verification](../../verification.md).
- [v1.0 loadout switching plan](../../plans/2026-11-23-v1.0-loadout-switching.md) and [v1.0 successful-run rotation plan](../../plans/2026-11-23-v1.0-successful-run-rotation.md).
- External rules (must be rechecked after TDS changes): https://tds.wiki/w/Waves ; https://tds.wiki/w/Skills ; https://tds.wiki/w/Golden_Scout ; https://tds.wiki/w/V1.89.0 .

**v1.0 planning:** [Legacy consolidation](../../plans/2026-11-25-v1.0-legacy-consolidation.md) evaluates conditional retirement of Golden 9 and older preparation-only profiles; no current requirement or strategy removed.
