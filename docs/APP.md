# Windows application

## Version status

- **Published stable:** v0.3.0, with the original nine-Scout fallback and v2.20.0-era three-slot Hardcore route.
- **Local v0.3.1 candidate (not yet published):** responsive compact two-tab GUI, native-tested ten-Scout Golden route, diagnostics, and guarded optional Hardcore slot 4.
- The ten-Scout route has **three verified native wins on TDS v2.20.2**. The live game later displayed v2.20.3, which has not yet received the same acceptance run.
- The **Hardcore v2.20.1–v2.20.3 spawn/camera route is not accepted**. Slot-4 XP placement and actual XP awards remain unverified. Do not claim current Hardcore farming compatibility from earlier v2.20.0 results.

## Start and controls

1. Extract the entire Windows application folder; keep TDSMacro.exe, _internal, assets, calibrations, strategies, docs, and license notices together.
2. Open the Store version of Roblox Tower Defense Simulator in English. Required foreground client is **1920×991 pixels at 120 DPI**, on Windows 11, with the configured Solo tower loadout.
3. In **Overview**, select **Golden Scout — 10 Max / Dead Ahead / Easy** (default), **Golden Scout — 9 Scouts (legacy fallback)**, or **Hardcore Gem Grind — Wretched Front / Solo**.
4. Verify recovery and Auto Equip options, then select **Start / F1**. You have five seconds to put Roblox in front; the app minimizes as the separate guarded worker takes control.
5. **Stop / F2** requests an orderly stop. **F8 / Escape** are emergency-stop controls. Never compete with the active worker for Roblox input or change camera/geometry mid-run.

The **SESSION** area shows actions, match count, displayed results, status, and stop reasons. READY, RUNNING, STOPPING, and STOPPED describe the controller, not server availability or verified reward credit. A successful result-screen reward is **not** automatically proof of a wallet credit.

## Strategies and evidence

| Choice | Required manual equipment | What has actually been verified |
|---|---|---|
| Golden 10 Max | Golden Scout slot 1, slots 2–5 empty | Ten placements and forty once-only E-key upgrades; all ten level 4; wave-20 Victory in three v2.20.2 native matches |
| Golden 9 legacy | Golden Scout slot 1, slots 2–5 empty | Original 44-action fallback from the published v0.3.0 |
| Hardcore Gem Grind | Boomerang slot 1, regular Crook Boss slot 2, Farm slot 3, slot 5 empty | Three-tower 75-action path: ten v2.20.0 native wave-30 results; current Wretched Front camera not yet accepted |
| Hardcore optional XP | Above Hardcore equipment plus a supported, independently verified evolution tower in slot 4 | Implemented only as a guarded branch; **not yet live accepted**. Placement and actual XP gain must not be assumed |

The Golden 10 profile uses a separately calibrated v2.20.2 scene. It stops if map, camera, hover, price, funds, tower identity, count, or upgrade result cannot be verified. The legacy nine-Scout profile remains separate.

## Auto Equip

**OFF by default.** When OFF, the app does not send Equip actions. When ON, it still requires independent, exact readable EMPTY labels on **all five** inventory hotbar slots, exact Search/text identity for each required tower, a dynamically located Equip label, and post-click slot verification. Partially occupied, unlabelled, or ambiguous hotbars are never overwritten.

The currently observed TDS inventory presents blank-looking empty tiles, **without five explicit EMPTY text labels**. In that UI, Auto Equip intentionally refuses to act. Equip manually. Do not loosen this requirement by using skins, icons, borders, card ordering, or model appearance.

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
