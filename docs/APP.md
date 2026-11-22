# Windows application

**CURRENT RELEASE TARGET — v0.3.2, 2026-11-22 ICT:** Public **v0.3.1 is already published** at commit `1439ee91` and must remain immutable. The subsequent three-tower Wretched Front/GUI fixes are in reviewed commit `951ac6c`; hosted Windows CI run `44993592295` succeeded. The exact frozen candidate independently completed **two consecutive 75/75-action, 18-tower, wave-30 Solo Hardcore results**, each displaying **137 Gems** (274 total), with **zero recoveries** and automatic Restart Match into cycle 3. Required loadout is **Boomerang slot 1 / regular Crook Boss slot 2 / Farm slot 3 / slots 4 and 5 empty**; no optional XP tower is used. Auto-Equip stays disabled because TDS does not expose all five explicit EMPTY labels. Preserve independent text, terrain, focus, cash, tower and confirmation guards; max-three recovery remains bounded, not an indefinite failure-free guarantee. These fixes require a distinct **v0.3.2 patch release**, never a replacement for existing v0.3.1 tag/assets. Displayed Gems are not independently wallet-audited.



**FINAL OWNER v0.3.1 DECISION (2026-11-21 17:44 ICT; supersedes earlier conditional OCR proposals):** **Remove automatic game-version OCR completely, now.** v0.3.1 must use **one fixed Wretched Front candidate route**, never select or retry routes from version text and never perform even one-time version detection. It is still **NOT an accepted route** until the native proof of **RIGHT onto rock tops → DOWN across the pale/white boulder beside the old gate → DOWN ends ON path → LEFT to original placement pose**, plus two fresh-spawn guarded repetitions and unchanged three-rock camera/drift checks. Terrain mismatch, lost foreground/client identity, unknown Ready/zero-tower state or failed placement checks must stop; non-version gameplay OCR stays. The candidate source has removed version-OCR route dispatch; **no live match, optional XP, final build, CI or release success is claimed**. This instruction now authorizes implementation and native calibration in separate guarded batches, not weakening safety or changing published v0.3.0.

**v0.3.1 planning note (2026-11-21 15:49 ICT; not shipped):** The revised Wretched Front path is RIGHT **on top of rocks**, DOWN across the **light boulder beside the old gate**, DOWN finishing **on the path**, then LEFT to the existing strict placement camera. A single accepted route should eliminate **route-version OCR**, not the OCR needed for hotbar, prices, results, etc. Until native route proof, the existing code is not approved for current-version unattended Hardcore. The [acceptance plan](plans/2026-11-21-v0.3.1-execution-checkpoints.md) governs; GUI/release behavior described below is source-candidate status only.

## Version status

- **Published stable:** v0.3.1, with Golden ten and optional XP features; current three-tower reliability corrections will be in v0.3.2.
- **Local v0.3.2 patch candidate (not yet published):** 960x690 Overview/Diagnostics GUI, native-tested ten-Scout Golden route, guarded three-tower Hardcore baseline and optional XP capability (unused for the current three-tower run).
- The ten-Scout route has **16 independently verified 50/50-action wave-20 Victories on TDS v2.20.3** (7,200 Coins displayed).
- A v2.20.3 native Hardcore 75+1 optional Minigunner match previously reached wave 30 with 137 Gems and +106 XP displayed. That earlier wave-19 count bug is now fixed; the new frozen GUI completed **two consecutive 75/75-action wave-30 three-tower results** (274 Gems displayed) with zero recoveries, and automatically began cycle 3.

## Start and controls

1. Extract the entire Windows application folder; keep TDSMacro.exe, _internal, assets, calibrations, strategies, docs, and license notices together.
2. Open the Store version of Roblox Tower Defense Simulator in English. Required foreground client is **1920×991 pixels at 120 DPI**, on Windows 11, with the configured Solo tower loadout.
3. In **Overview**, select **Golden Scout — 10 Max / Dead Ahead / Easy**, **Golden Scout — 9 Scouts (legacy fallback)**, or **Hardcore Gem Grind — Wretched Front / Solo**.
4. Verify recovery and Auto Equip options, then select **Start / F1**. You have five seconds to put Roblox in front; the app minimizes as the separate guarded worker takes control.
5. **Stop / F2** requests an orderly stop. **F8 / Escape** are emergency-stop controls. Never compete with the active worker for Roblox input or change camera/geometry mid-run.

The **SESSION** area shows actions, match count, displayed results, status, and stop reasons. READY, RUNNING, STOPPING, and STOPPED describe the controller, not server availability or verified reward credit. A successful result-screen reward is **not** automatically proof of a wallet credit.

## Strategies and evidence

| Choice | Required manual equipment | What has actually been verified |
|---|---|---|
| Golden 10 Max | Golden Scout slot 1, slots 2–5 empty | Ten placements and forty once-only E-key upgrades; all ten level 4; wave-20 Victory in 16 native v2.20.3 continuous matches |
| Golden 9 legacy | Golden Scout slot 1, slots 2–5 empty | Original 44-action fallback from the published v0.3.0 |
| Hardcore Gem Grind | Boomerang slot 1, regular Crook Boss slot 2, Farm slot 3, slots 4–5 empty for the requested run | Two v2.20.3 GUI three-tower native 75/75 results, 137 Gems displayed each, auto Restart Match |
| Hardcore optional XP | Above Hardcore equipment plus a supported, independently verified evolution tower in slot 4 | A v2.20.3 $1,850 Minigunner X1 native run recorded 76/76 core+optional actions, wave30, +106 XP displayed; the requested three-tower run leaves slot 4 empty |

The Golden 10 profile uses a separately calibrated v2.20.2 scene. It stops if map, camera, hover, price, funds, tower identity, count, or upgrade result cannot be verified. The legacy nine-Scout profile remains separate.

## Auto Equip

**OFF by default.** When OFF, the app does not send Equip actions. When ON, it still requires independent, exact readable EMPTY labels on **all five** inventory hotbar slots, exact Search/text identity for each required tower, a dynamically located Equip label, and post-click slot verification. Partially occupied, unlabelled, or ambiguous hotbars are never overwritten.

The currently observed TDS inventory presents blank-looking empty tiles, **without five explicit EMPTY text labels**. The GUI checkbox is disabled and Controller rejects Auto-Equip activation. Equip manually. Do not loosen this requirement by using skins, icons, borders, card ordering, or model appearance.

## Diagnostics and privacy

The **Diagnostics** tab is a read-only, scrollable report of bounded allowlisted session fields and recent events. **Copy diagnostics** copies sanitized text; **Export .txt** opens a local save dialog. There is **no command interpreter** and no remote diagnostics transmission. Local screenshots and full run logs remain under captures/runs and are **not** included in the public release.

Do not publicly paste unfiltered raw logs or screenshots. See [diagnostic-data.md](diagnostic-data.md), [setup.md](setup.md), and [troubleshooting.md](troubleshooting.md).

## Build and check

From the Windows repository root, with the project virtual environment installed:

~~~powershell
.\scriptsuild-app.ps1 -Destination 'dist
ew-review-build'
~~~

The builder refuses to overwrite an existing app directory. The resulting TDSMacro.exe supports --self-check output.json without launching gameplay or creating a GUI; it verifies bundled strategy/calibration data, local OCR and Tcl. Final acceptance additionally requires a real Tk GUI open/close, source tests, privacy scan, exact commit-based hosted Windows CI, and native current-version gameplay evidence. A successful self-check alone **does not authorize publication**.

For chronological experiments and acceptance details, refer to [verification.md](verification.md) and the [v0.3.1 execution checkpoints](plans/2026-11-21-v0.3.1-execution-checkpoints.md).
