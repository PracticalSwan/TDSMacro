# Current project status - November 26, 2026 (Asia/Bangkok)

## v0.5.3 receipt corrections

[Windows v0.5.3 release](https://github.com/PracticalSwan/TDSMacro/releases/tag/v0.5.3) restores the bounded Golden Coin scroll and corrects the verified Hardcore result-map OCR failure. The [defect register](../BUGS_FOUND.md) records OBS-010 and OBS-012 as unresolved observations. See the [verification record](verification.md) for observed results, remaining coverage gaps and the publication/install record.

Loadout switching, successful-run rotation, explicit slot-4 selection and legacy consolidation remain v1.0 planning items.

> Timestamped evidence; check current processes, Git status and newest session receipts before starting, stopping or replacing any worker.

## Released and installed v0.5.2 ? November 25, 2026

- Stable release: [v0.5.2](https://github.com/PracticalSwan/TDSMacro/releases/tag/v0.5.2), tag commit `41d9e0944fa2e9e8278d615e39662aee0a8ef8ab`. Exact-commit [Windows CI 45527548654](https://github.com/PracticalSwan/TDSMacro/actions/runs/45527548654) passed tests, build and artifact upload; the earlier identical-runtime local suite passed 694/694. The release contains 1,322 files, including the legitimate WinRT runtime dependencies, with CRC, per-file digest, privacy inventory, 82 link checks and staged self-check verified.
- Official ZIP SHA-256 `efc7d86802847b26bca44a7a9745b716b23b40a1906d44c888e6a8b721b47864`; both public assets independently downloaded and checked against GitHub digests and the checksum. Standard installation `dist/TDSMacro` matched all 1,322 published files and passed its own v0.5.2 frozen self-check. One Desktop shortcut still targets that installation. Previous v0.5.1 installation and captures preserved in `dist/TDSMacro-previous-before-v0.5.2-20261125_084643-35784`.
- Owner-requested native loadout change: Juggernaut exact inventory title and EQUIP control verified; one Equip click yielded two fresh UNEQUIP confirmations. The unchanged core is Boomerang, regular Crook Boss, Farm; Juggernaut slot 4, slot 5 empty. No saved preset was overwritten. The continuous GUI worker was launched at 08:48:49 ICT through the installed dashboard, with automatic recovery enabled. The worker must verify the actual hotbar and cash before purchases.
- Last observed session `app_20261125_084849_082330` at 08:51:02 ICT: phase `hardcore_camera_route`, attempts 1, credited Gem cycles 0, displayed Gems 0, recoveries 0. Fresh Wretched Front board-3 voting and Ready passed with no view clearing; exact in-match hotbar verified Boomerang, regular Crook Boss, Farm, Juggernaut and empty slot 5. GUI 9004, worker 22224, Roblox 25268 at launch (recheck historical PIDs). The sole continuous worker remains undisturbed; optional Juggernaut placement is conditional on verified spare cash after reserving core defense.
- The latest candidate three-tower Hardcore retry before release earned 137 Gems at wave 30 with 75/75 actions in 463s. Previous installed Golden session ended normally by user stop with 30 wins and four relaunches. The rare exact native camera, board-3 and tooltip-plus-replay paths remain separately documented below; other unresolved timeout observations are retained in [BUGS_FOUND.md](../BUGS_FOUND.md).

## Released fixes and residual verification limitations

| Defect | Evidence / limitation |
| --- | --- |
| BUG-001 | Six original count-10 frames and latest overnight frame read 10; full native Golden wins |
| BUG-002 | Eight archived native camera failures replayed through actual alignment guard; two direct binds, six single guarded corrections in input recorder. Native strict bind and out-of-range/drift rejection proven. Physical effect of the narrow 10-12 px south correction remains unverified. |
| BUG-003 | Both original board-3 sequences pass the actual Ready gate in an offline input recorder; live votes on boards 1, 2 and 4 proven. Fresh Wretched Front physical board 3 passed on the installed release; exact original visual variation and fresh Dead Ahead board 3 remain unverified. |
| BUG-004 | Native 50-action Golden 10 matches: 34 selection clicks instead of 80, 40 E keys, all ten Scouts L4. |
| BUG-005 | Original severe overlay receipt and fresh native tooltip Victory with 450 Coins verified; normal live Play Again verified. Exact combined tooltip + readable Coin + live Play Again still unverified. Clipped Coin amounts remain uncredited and trigger safe recovery. |
| BUG-006 | Native uncredited direct restart and one guarded client relaunch followed by exact-once 137-Gem credit. |
| BUG-007 | Original wave29/133-Gem receipt now parsed; no improper credit. |
| BUG-008 | Native Gem+XP with expensive Juggernaut deferred and with affordable Scout X1 both earned 137 Gems; three-tower profile now also verified. Original wave29 causality not uniquely established; missed deadline 18 remains a warning in successful matches. |

**No endless random-condition trials.** Use captured-frame regressions for exact historical failures, representative native end-to-end results for integration, and explicit residual-risk labels. If a rare condition is not reproduced within a bounded targeted trial, retain its native-verification gap; do not regenerate identical docs or rerun unchanged tests indefinitely. Never weaken paid-action, terrain, result, focus or stop guards to obtain a passing screenshot.

The corrective release is published and installed. No source or strategy changes were made after the release tag. Existing plans for **v1.0** remain planning-only: [loadout switching](plans/2026-11-23-v1.0-loadout-switching.md) and [successful-run rotation](plans/2026-11-23-v1.0-successful-run-rotation.md). See [bug register](../BUGS_FOUND.md), [verification history](verification.md) and [changelog](../CHANGELOG.md). Preserve the experimental untracked calibration and private captures; do not replace the active installation while the worker runs.
