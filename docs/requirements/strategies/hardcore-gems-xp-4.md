# Hardcore Gems + Tower XP — Slot 4 / Solo

**Executable selector:** `Hardcore Gems + Tower XP — Slot 4 / Solo`; strategy ID `hardcore_gem_xp_wretched_front_v2`. Same pinned 14-phase core plan as the 3-tower variant, with a separate optional-XP decision and calibrated placement point.

## Requirements before Start

| Requirement | Required condition | Evidence / limitation |
| --- | --- | --- |
| Queue / map | **Hardcore / Solo / Wretched Front**, no modifiers | Same verified map, solo count, 1x speed, right/down/left route and final camera |
| Core loadout | 1 **regular Boomerang**, 2 **regular Crook Boss**, 3 **Farm** | Exact identities and ordering; never substitute Golden Crook Boss |
| XP loadout | Slot 4 a positively recognized supported eligible XP tower; slot 5 **empty** | User's native-proven example: **Juggernaut** |
| Four-Farm opening | At least **$1,200 observed cash before Ready** | See [3-tower cash eligibility](hardcore-gems-3.md); all three Economy-skill issues carry over |
| Optional cost | Actual slot-4 base price within **$200–$10,000** inclusive, read and unchanged immediately before placement; sufficient live surplus after the next verified core quote | Juggernaut observed at **$10,000**; no hardcoded generic XP-tower price |
| Optional placement | Only after required critical core levels / at least ~70 core actions and a live valid preview | X1 path-side coordinate **(976,580)**, zero-level placement only, no optional upgrades |
| Game settings | 1920x991 @120 DPI, compatible English HUD/OCR, 1x speed, foreground Roblox, no conflicting controller | Uncertain cash/tower/level/preview = no paid action |

## Outcomes: distinguish Gem success from XP success

- The 3-tower defense remains the foundation: ten Farms L3, B1 L4, B2/B3 L3, C1/C2 L3 and C3/C4/C5 L2 **before the optional purchase**. v0.5.2 reserves the next verified core upgrade quote before X1 spending; unaffordable or uncertain X1 is deferred or skipped. The final permitted wave-30 C5 upgrade remains guarded.
- A **Gem-successful** run requires the exact verified natural **wave-30 Defeat** and **137 displayed Gems**, as the current `result_verified` policy permits after all required levels or XP critical defense verification.
- **XP placement success** means the optional X1 tower was positively placed and the action receipt confirmed its identity/level/tower count. The current `xp_placement_cycles` counter means *placements*, **not a parsed Tower XP reward**.
- An **XP-reward-successful** run for future v1.0 rotation must **also verify a positive tower-specific XP award on the result screen** (or an independent authorized proof) and the expected tower identity. The current runtime does *not* generally parse or audit XP rewards. Do not conflate these three metrics.
- If X1 cannot be bought safely, preserve a valid Gem run and report XP-unplaced, rather than counting it as XP-successful. Never invent XP for an unplaced tower.
- In released v0.5.2, available surplus must cover X1 after reserving the next verified core-upgrade quote. The $10,000 Juggernaut can remain unplaced when current income leaves too little for defense. The same eligible tower, slot, price range and placement point apply.
- On the tested account, the v0.5.2 native acceptance trial confirmed Scout level 0 as tower 19 on wave 25 after spending $250 with a $14,000 core reserve. The same cycle completed 75 core actions and earned the 137-Gem result. [Native verification](../../verification.md)

## Planned v1.0 explicit slot-4 profile

The [slot-4 selection plan](../../plans/2026-11-25-v1.0-slot4-tower-selection.md) adds a GUI choice bound to a verified tower/perk and a validated cost, point/footprint and purchase window. Five intended v1.0 choices: Juggernaut ($10,000 observed), Golden Scout ($250 Scout quote observed; exact Golden perk still to verify), Operator ($300 reference), Enforcer ($3,000 reference), and Kingpin ($3,600 reference). The three evolved towers require native verification of ownership, exact variant, price, footprint, placement and reward. Kingpin must coexist with regular Crook Boss in slot 2; otherwise leave Kingpin unavailable. Reference: [Operator](https://tds.wiki/w/Operator), [Enforcer](https://tds.wiki/w/Enforcer), [Kingpin](https://tds.wiki/w/Kingpin), checked 2026-11-27. Minigunner ($1,850 historical) is a later requalification candidate. Reuse live HUD cash, protect the next core quote, and verify actual price, identity, preview and postcondition before any paid action. No automatic selection of a substitute, no generic catalog expansion based on OCR names alone. Released v0.5.5 behavior is unchanged; no explicit per-tower dropdown exists yet.

## Economy and multi-account suitability

Earlier $10,000 Juggernaut placements and positive XP displays were repeatedly validated on the owner's high-income account (Bigger Budget 25/25, Stonks 20/20, Scavenger 9/20). Other skill levels and other $200–$10,000 eligible XP towers are not guaranteed to reach a purchase window before wave 30. Initial $1,200 eligibility is necessary but not sufficient. Its optional affordability is **live and conditional**; the v1.0 requirements UI must explicitly flag this limitation.

Sources: `src/tds_auto/hardcore_match.py`, `src/tds_auto/hardcore_vision.py`, `src/tds_auto/session.py`, `docs/verification.md`, [3-tower requirements](hardcore-gems-3.md).
