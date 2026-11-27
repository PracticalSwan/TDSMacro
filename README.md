# TDS Macro

Windows automation for **Roblox Tower Defense Simulator** using guarded mouse/keyboard inputs and screenshots/OCR to verify cash, prices, loadouts, placement, upgrades and results. Requires the official Windows Roblox client; **no injection or modified client**.

**Latest stable v0.5.5 (November 27, 2026).** [Download the Windows release](https://github.com/PracticalSwan/TDSMacro/releases/tag/v0.5.5) · [Setup](docs/setup.md) · [Project status](docs/STATUS.md) · [Defect register](BUGS_FOUND.md) · [Verification and limitations](docs/verification.md)

## Supported strategies

| GUI selection | Map / mode | Equipment (ordered slots) | Successful result |
| --- | --- | --- | --- |
| **Golden Scout — 10 Max** | Dead Ahead / Easy Solo | 1 Golden Scout; 2–5 empty | Wave-20 Victory with 10 Scouts at level 4 (50 actions) and readable Coin reward |
| Golden Scout — 9 Scouts (legacy fallback) | Dead Ahead / Easy Solo | Same as above | Wave-20 Victory; 9 Scouts, 44 actions |
| Hardcore Gem Grind — 3 Towers | Wretched Front / Hardcore Solo | 1 Boomerang; 2 regular Crook Boss; 3 Farm; 4–5 empty | Natural wave-30 Defeat with all 75 core actions and 137 Gems **displayed** |
| Hardcore Gems + Tower XP — Slot 4 | Wretched Front / Hardcore Solo | Same first three; 4 verified eligible XP tower; 5 empty | Natural wave-30 Gem result; optional XP placement is separately verified |

**Full account, cash and skill prerequisites:** [per-strategy requirements](docs/requirements/strategies/README.md). Golden Scout's first placement costs $250. Hardcore's four pre-Ready Farms need **at least $1,200 in actual starting cash**, so not all players or Economy skill levels can run its unchanged opening. Other game/skill configurations need native verification; account success is not a universal guarantee.

## Getting started

1. On Windows 11, download and extract the **entire** release folder. Keep `TDSMacro.exe`, `_internal`, assets, calibration, strategy files and notices together. For the maintainer, the standard installation is `dist/TDSMacro`.
2. Launch the official Store Roblox TDS client, enter the lobby, configure English UI, **1920×991 physical client at 120 DPI**, **UI Scale Large**, vertical upgrades and supported normal-speed mode. Keep Roblox unobstructed and in the foreground during gameplay.
3. **Equip manually** the exact tower order and perk for the selected strategy. Auto-Equip is disabled because the game does not expose independently verified empty-slot labels. Golden Scout requires an active Golden perk.
4. Select a strategy on the **Run setup** dashboard. Press **Start / F1**; Roblox must remain the sole foreground input target. Use **F2** for safe stop, **F8/Escape** for emergency stop. Closing the app requests a stop.
5. Observe a native match and result. The worker confirms actions instead of blindly repeating uncertain purchases, can recover a verified client failure within a limited budget, and repeats successful matches until stopped or a safety gate fails.

### Dashboard and updates

The dashboard shows selected strategy/loadout, active phase, actions, waves, rewards and recovery count. **Diagnostics** and **Updates** open as separate utility windows. Automatic release updates are **OFF by default**; verified updates install only while gameplay is idle and retain prior installations for rollback. The maintainer uses one current `TDS Macro.lnk` Desktop shortcut.

Continuous mode permits two guarded direct replays and up to three guarded client relaunches without a new credited cycle (relaunch requires automatic recovery). The optional XP tower is bought only with verified surplus after reserving the next core-upgrade quote; deferred XP does not invalidate a qualifying Gem result.

The reported Coins/Gems are **verified result-screen displays**, not a separate wallet audit. For XP strategies, the current XP-placement counter does not itself prove the numerical XP reward. The macro may stop safely on unexpected UI/game versions, terrain, network, focus, unsupported skill economy or unreadable results.

## Roadmap and contribution

**v1.0.0 planning only:** [safe loadout switching](docs/plans/2026-11-23-v1.0-loadout-switching.md), [successful-run rotation](docs/plans/2026-11-23-v1.0-successful-run-rotation.md), and [explicit slot-4 tower selection](docs/plans/2026-11-25-v1.0-slot4-tower-selection.md), such as five verified Golden Scout wins followed by five verified Hardcore Gem runs, then repeat. **These features are not implemented.** The planned slot-4 selector uses reviewed tower profiles and preserves the core-defense reserve and live purchase guards. Fixes and independent changes continue in ordinary v0.x releases (v0.5.3, v0.6.0, etc.).

Contributions are limited to reviewed strategy submissions and suggestions: [Contributing](CONTRIBUTING.md) · [Strategy credit/provenance](docs/strategies.md) · [Development](docs/development.md) · [Changelog](CHANGELOG.md) · [Security](SECURITY.md) · [License/notices](NOTICE.md). Raw screenshots, captures and logs are private and must not be published.

This is an unofficial automation project; users should assess Roblox/TDS rules and account risks before use.

**v1.0 consolidation (planning only):** [Legacy removal and project consolidation](docs/plans/2026-11-25-v1.0-legacy-consolidation.md) evaluates retiring superseded profiles and duplicate compatibility code while preserving safe update rollback and required evidence. All four released v0.5.2 strategies remain unchanged.
