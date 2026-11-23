# Windows application

**v0.5.0 application modes (native-accepted, release pending):** Overview separates **3 Towers / Solo Gem Grind** (all 75 mandatory actions; slots4-5 empty) from **Gems + Tower XP / Slot4 Solo** (Boomerang, regular Crook Boss, Farm, known XP tower in 4, slot5 empty). The XP mode protects ten Farms L3 and critical Boomerang/Crook levels, then buys its level-0 tower only with a $200-$10,000 live quote, sufficient cash, verified Place prompt and footprint; optional final upgrades can be deferred. The user-requested X1 location is `(976,580)` near the central route, not the remote right rock. A full native Juggernaut match verified placement on wave25, wave30 137 Gems and +106 tower XP, no recovery. Actual damage total was not audited. Automatic Updates are OFF by default and cannot install during an active worker; maintain one stable Desktop shortcut to the current standard installation.

**v0.4.1 available:** The current [stable Windows ZIP](https://github.com/PracticalSwan/TDSMacro/releases/tag/v0.4.1) fixes exact native Wretched Front wave30 map-label OCR misreads without weakening other result checks. From v0.4.0, use Updates -> Check now and Download/Install only when the gameplay worker is idle; Automatic updates can be enabled manually and remain OFF by default. The official ZIP was independently validated and installed at the standard location without interrupting the separate active three-tower worker. Old v0.4.0 is preserved under the timestamped backup folder and its Desktop shortcut remains available.


**v0.4.1 Hardcore result fix:** The native three-tower Wretched Front Solo session now tolerates a small exact list of observed map-label OCR glyph variants on the completed wave-30 screen. Reward credit still requires correct Hardcore mode/difficulty, verified wave and duration, and one readable Gems amount. This does not send new inputs or alter 75-action strategy. The GUI ran a complete 75/75-action wave-30 result and direct Restart Match with zero client recoveries after one bounded early-Defeat retry. Automatic updates are still user-controlled, OFF by default, and wait for idle gameplay.


**v0.4.1 corrective candidate, November 23 2026:** After 38 verified wave-30 results (5,206 Gems displayed), one further full 75-action natural wave-30 Defeat was not credited because native Wretched Front map-label OCR returned `Mretched Froni`. The saved result visibly contained 137 Gems and strict mode/difficulty/wave/duration/reward text, but existing map recognition rejected the label. Extend only the exact map-label OCR allowlist to the native-observed `Mretched Froni`, `Mretched Frond`, `Nretched Frond` variants, keeping the existing two map-template fallbacks and all result checks. New sanitized panel-only native screenshot fixture reproduces this failure (red before fix, green after fix), with map masking negative. No synthetic credit for old unverified result. Separate Roblox error-277 disconnect occurred after the stopped session and requires normal client recovery. Full regression, frozen build, GUI/native loop and CI gate release; protect old versions and untracked calibration.


**v0.4.0 now released:** Download [v0.4.0](https://github.com/PracticalSwan/TDSMacro/releases/tag/v0.4.0). In Updates, check the OFF-by-default Automatic updates switch to enable stable-release checks (startup and every six hours) or press Check now. The updater verifies official ZIP/checksum and installs only when the gameplay worker is idle; the prior app/captures are backed up. The new GUI starts idle, never restarting Roblox automatically. Manual first install required from pre-v0.4.0 versions.


**v0.4.0 GUI acceptance:** Native Updates tab renders without clipping; OFF→ON→OFF persisted correctly and Check now returned Up to date. A verified update is deferred while any gameplay worker runs. The frozen GUI also passed a 75-action Hardcore match and direct Restart Match. See `verification.md` for evidence; future over-the-network upgrades remain to be observed when a newer release exists.


v0.4.0 UPDATES (candidate): Open the Updates tab to toggle Automatic updates ON/OFF (default OFF). Enabled checks run on app startup and every six hours. Check now queries GitHub manually even when OFF. If a newer stable official release is available, Download update verifies and stages it; Install verified update applies it after the worker is idle. With auto-update ON, preparation and install occur automatically once idle. Continuous gameplay is never interrupted to update. Settings live in LOCALAPPDATA/TDSMacro/settings.json, outside the application. The old installation/captures are preserved as a timestamped backup; the new GUI starts idle. Unknown versions, invalid digests/archives, failed self-checks and installation errors stop without replacing the old version.


**v0.3.4 GUI verified (2026-11-22):** Current standard installation is `dist/TDSMacro` and the v0.3.4 Desktop shortcut targets that application. The frozen GUI verified the exact three-tower loadout, one complete 75-action wave-30 Defeat with 137 Gems displayed and automatic direct Restart Match into cycle 2, with zero recoveries at the accepted result. Auto-Equip remains disabled; the session is continuous until safe stop, an uncertain state or bounded recovery termination.


**Unreleased post-v0.3.3 HUD correction:** The next candidate retains the same three-tower GUI and controls; only wave-fraction sampling and the existing no-input wait are adjusted. Live v0.3.3 evidence includes two complete 75/75 wave-30 results followed by a safely recovered wave-11/12 HUD timeout. Current public v0.3.3 is unchanged; new frozen/native acceptance is required before deploying the candidate.


**v0.3.4 available in the current Windows release:** The Hardcore reader allows up to seven seconds of passive observation when HUD fields are initially unreadable, requiring two valid consecutive wave readings after a transition. A wider alternate text crop recovers the proven native wave-11 fraction only when exact OCR agreement is obtained. Persistent ambiguity, wrong selected tower/cash, missing focus and unknown camera still stop safely. This does not enable Auto-Equip.


**v0.3.3 GUI behavior (November 22, 2026):** For continuous three-tower Hardcore only, a verified early Defeat can show `Restart Match 1/2` or `2/2`; these are not counted in Gem-cycle totals. Three consecutive early Defeats stop instead of looping. Normal three-client-relaunch recovery remains separate; uncertain results and purchases remain terminal. This behavior is new in v0.3.3; the original v0.3.2 package is preserved.


**POST-RELEASE STATUS — v0.3.2 published and locally installed (November 22, 2026 ICT):** Published https://github.com/PracticalSwan/TDSMacro/releases/tag/v0.3.2 at source commit `9ff56b6` after passing Windows CI `44994210171`. The public ZIP (1,213 files; SHA-256 `9b95424ab5dffc87259f101ca82bba7103b416c17318904be9d655f74197691a`) and its published checksum were downloaded back and matched; the native-accepted executable SHA-256 is `ae5ccbec12c03a8ca56618e4a614f49f77219e9a19e2ee91828c736cc038e080`. Standard local `dist/TDSMacro` now holds v0.3.2, has passing frozen self-check and a new Desktop shortcut; v0.3.1 was preserved as `dist/TDSMacro-previous-v0.3.1-20261122` with its shortcut redirected. Public v0.3.1/v0.3.0 tags and assets were not modified. The separate continuously running three-tower Hardcore worker has three independently verified complete 75/75-action natural wave-30 results, 137 displayed Gems each (411 total), no recoveries and native Restart Match into cycle 4. At last read-only observation cycle 4 was on wave 14 with 41 actions and no stop marker. The worker is running from its original isolated native-verified build and was not interrupted by installation. Auto-Equip remains intentionally disabled; strictly bounded max-three recovery is not guaranteed failure-free forever, and displayed rewards were not wallet-audited.



**FINAL OWNER v0.3.1 DECISION (2026-11-21 17:44 ICT; supersedes earlier conditional OCR proposals):** **Remove automatic game-version OCR completely, now.** v0.3.1 must use **one fixed Wretched Front candidate route**, never select or retry routes from version text and never perform even one-time version detection. It is still **NOT an accepted route** until the native proof of **RIGHT onto rock tops → DOWN across the pale/white boulder beside the old gate → DOWN ends ON path → LEFT to original placement pose**, plus two fresh-spawn guarded repetitions and unchanged three-rock camera/drift checks. Terrain mismatch, lost foreground/client identity, unknown Ready/zero-tower state or failed placement checks must stop; non-version gameplay OCR stays. The candidate source has removed version-OCR route dispatch; **no live match, optional XP, final build, CI or release success is claimed**. This instruction now authorizes implementation and native calibration in separate guarded batches, not weakening safety or changing published v0.3.0.

**v0.3.1 planning note (2026-11-21 15:49 ICT; not shipped):** The revised Wretched Front path is RIGHT **on top of rocks**, DOWN across the **light boulder beside the old gate**, DOWN finishing **on the path**, then LEFT to the existing strict placement camera. A single accepted route should eliminate **route-version OCR**, not the OCR needed for hotbar, prices, results, etc. Until native route proof, the existing code is not approved for current-version unattended Hardcore. The [acceptance plan](plans/2026-11-21-v0.3.1-execution-checkpoints.md) governs; GUI/release behavior described below is source-candidate status only.

## Version status

- **Published stable:** v0.3.2, with the redesigned GUI and repaired three-tower Hardcore checks. v0.3.1 is preserved.
- **Published v0.3.2 patch:** 960x690 Overview/Diagnostics GUI, native-tested ten-Scout Golden route, guarded three-tower Hardcore baseline and optional XP capability (unused for the current three-tower run).
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
