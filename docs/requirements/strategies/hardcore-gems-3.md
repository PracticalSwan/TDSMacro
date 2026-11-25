# Hardcore Gem Grind — 3 Towers / Solo

**Executable selector:** `Hardcore Gem Grind — 3 Towers / Solo`; strategy ID `hardcore_gem_grind_wretched_front_v2`. Pinned core plan: `strategies/hardcore_wretched_front_boomerang_crook_farm_v2.json`. This is the 3-tower mode, not the 4-slot XP mode.

## Requirements before Start

| Requirement | Required condition | Evidence / limitation |
| --- | --- | --- |
| Queue | **Hardcore / Solo / Wretched Front**; account must have mode and map-selection access | Current verified route and positive Solo player-count/map checks |
| Loadout order | Slot 1 **regular Boomerang**; slot 2 **regular Crook Boss**; slot 3 **Farm**; slots **4–5 empty** | Current worker verifies searched tower names and match hotbar tooltips |
| Initial cash | **At least $1,200 in observed cash BEFORE Ready** | Four pre-Ready Farm placements at $300 each; the existing opening cannot proceed with less |
| Economy skills | **No universally sufficient level combination established** | User/account accepted baseline used Bigger Budget 25/25, Stonks 20/20, Scavenger 9/20; other accounts remain unproven |
| Skills toggled | Skill effects relied on for cash must be **enabled** in TDS Settings | Owning perk levels alone is insufficient |
| Game settings | Normal **1x**, English UI, current pinned right/down/left Wretched Front route, calibrated final camera, 1920x991 @ 120 DPI | Terrain and three-landmark agreement required; do not switch versions/routes blindly |
| Modifiers | None; no alternate player count or ability that changes cash/combat | Other configurations require native trials |

## Starting-cash calculation (screening only)

The published TDS reference currently lists **$900 Hardcore Solo base starting cash**, plus **$100** for community-group members. Bigger Budget increases starting cash by **1% per level after that group bonus**. Under those assumptions:

| Group bonus | Bigger Budget 0 | Bigger Budget 20 | Bigger Budget 25 | Four-Farm opening? |
| --- | ---: | ---: | ---: | --- |
| Yes ($1,000 pre-perk) | $1,000 | $1,200 | $1,250 | Only levels 20+ reach the $1,200 minimum |
| No ($900 pre-perk) | $900 | $1,080 | $1,125 | **Not possible at level 25** with the unchanged opening |

This is an arithmetic **eligibility floor, not a proof of eventual wave-30 success**. Live in-match cash is decisive. Stonks affects wave bonuses; Scavenger affects selected enemy kill income. Less income could delay critical defenses and fail the match even when the four Farms are initially affordable.

## Strategy completion and reward

- Four Farms pre-Ready, eventually **10 Farms at level 3, 3 Boomerangs at level 4, and 5 Crook Bosses at level 3**.
- Core purchase sequence totals **75 confirmed actions** and 18 placed towers. Live prices/levels, wave progress, terrain and critical defensive purchases determine timing.
- Intended result is **natural wave-30 Defeat** with **137 Gems displayed**, independently recognized twice in the exact Hardcore/Wretched Front result. This is a *successful Gem grind* even though the game says Defeat.
- The current code increments `gem_cycles` only for `result_verified` with 137 displayed Gems; it does not independently audit wallet balances.
- Early Defeats, malformed result screenshots, action uncertainties and failed purchases **do not count**. Bounded recovery/restart behavior does not make an account with insufficient starting cash compatible.

## Validation gap for public users

The demonstrated repeated successes use the owner's account and current game/UI. Before marking a lower-income account eligible, verify its exact four-Farm opening, sufficient critical defense timing, 75/75 completion, wave-30 outcome and rewards over multiple runs. Do not advertise this as foolproof across all Economy skill configurations.

Sources: `src/tds_auto/hardcore_plan_v2.py`, `src/tds_auto/hardcore_match.py`, `src/tds_auto/session.py`, `docs/verification.md`, https://tds.wiki/w/Waves , https://tds.wiki/w/Skills .
