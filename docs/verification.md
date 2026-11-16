# Verification

## 2026-11-16 — Post-release local v0.2.3 GUI installation verification

The local `dist/TDSMacro/TDSMacro.exe` was an older build after v0.2.3 was published. The executable inside the published release ZIP matched the existing `dist/candidate-v0.2.3-r2/TDSMacro/TDSMacro.exe` at SHA-256 `ddf76edbb7b440c83fc61b48635d18a24574cff86c7d1e3de826dd49416f4624`. The verified existing build was moved to the standard local `dist/TDSMacro/` path. The previous standard directory was archived as `dist/TDSMacro-previous-20261116/`. A desktop shortcut with the correct target and working directory was created and tested. These paths are local, ignored build/install artifacts and not release contents.

The installed executable's `--self-check` exited 0, reporting frozen mode, **44 operations**, **16 observer states**, local OCR reading `Play Again`, Tcl 8.6.15 and strategy hash `59548c3cf386f63eb0ae9f820ec165747c600706bbb59c7ce6acbd4da133eafb`. A launch **through the actual shortcut** created a visible, responsive `TDS Strategy Macro` Tk GUI with Golden Scout selection, F1/F2 controls, recovery checked and Ready status. An earlier successfully launched GUI was behind another foreground application, rather than crashing. The previous binary was preserved, and diagnostic screenshots were removed after review.

**Scope:** This was a Windows launcher/GUI test with Roblox closed; it does not establish a new match victory or retest gameplay. No source code, published ZIP/tag, Windows display scaling or Roblox settings were modified. The release's existing 301 automated tests and live match/focus-recovery verification remain documented below.

## 0.2.3 — Foreground recovery with modifiers deferred

Verified on 16 November 2026 with Python 3.14.2, Windows 11, English Store Roblox GDK/TDS 2.19.1, physical 1920×991/120 DPI, UI Scale Large, vertical upgrades and Golden Scout alone in slot 1. The owner deferred modifier settings because the required challenges are not unlocked. The strategy/profile and its SHA remain unchanged. Committed + Limitation + Hidden Enemies + Glass has no accepted selection, full-combination win or reward measurement. Historical references below to partial account modifiers do not establish Challenge Trial unlocks or a verified selectable set.

The final packaged candidate completed **Dead Ahead / Survival / Easy, wave 20, in 7m39s for 450 coins**, with all **44 actions** confirmed: nine Scouts, the first eight level 4 and the ninth level 3. No recovery occurred before that win. The result was checked both from the parsed outcome and the saved result image. Normal Play Again returned to map voting, re-established the target and a fresh zero-tower camera, and confirmed the first three actions of the next match. These two setups used physical board 1.

During that second match, the owner briefly switched foreground away and back. The guard reported `focus_lost` at three confirmed actions and abandoned the attempt. The same process/window/geometry returned and passed two observations after **1.51 seconds**. The worker closed the original client normally, waited for process exit and **60 seconds** of launcher settling, launched the official URI once and reached a stable new foreground lobby in **101.48 seconds from the interruption gate**. The client process/window changed; the worker did not. Its fresh attempt completed loadout, Solo/Easy menus, physical-board-4 Dead Ahead voting and zero-tower overhead setup, then confirmed **19 actions on seven new Scouts** before native F2 stopped it. The partial match was never resumed. This was one deliberate recovery, not a natural failure needed to obtain the win.

Native F1 started the packaged worker. Native F2 cancelled startup in a separate bounded check and later stopped the recovered game with `user_stop`, leaving the Roblox window unchanged and causing no further recovery. Closing the verified GUI during another startup stopped its only child before game input; both processes exited. F8/Escape, pause, stop markers, held-key/mouse release, persistent foreground loss, geometry/identity changes and the three-relaunch budget have focused automated coverage. The brief live interruption does not prove every notification or mid-hold timing; those boundaries remain distinct from the fake-platform tests.

The final full local suite passed **301/301 tests in 58.458 seconds**, with the GUI/worker stopped. Compilation and whitespace checks exited zero. The environment has no `pip` module, so `python -m pip check` could not run; **`uv pip check --python .\.venv\Scripts\python.exe` passed for all 18 installed packages** without dependency changes. Behavior regressions failed before the fixes and passed afterward. A focused independent static review found an identity-anchor race across temporary client absence; retaining the original anchor through cooldown fixes it, including a regression that previously closed a replacement fake client. Setup/loadout and navigation-PNG failures now retain protected setup/storage classifications.

The final app built successfully; frozen self-check confirmed **44 actions, 16 observer states, English Play Again OCR, Tcl 8.6.15** and strategy SHA `59548c3cf386f63eb0ae9f820ec165747c600706bbb59c7ce6acbd4da133eafb`. Its **20 source hashes and 73 runtime-data hashes** matched the workspace, and the package retained **58 dependency/Python notices**. Release source-commit metadata, archive checksums and hosted CI are verified separately during publication; local and gameplay success do not establish hosted success.

Computer-control sessions were found to contaminate the Items hover capture with their pointer/blue effect. After ending that session, a clean native capture matched the existing hover reference at **1.0**. The proposed contaminated reference, fixture and test were removed; the original recognition assets are unchanged. Future verification must use the project's guarded input and native captures, following the explicit prohibition in AGENTS.md and development.md. The earlier contaminated candidate's stop is not counted as a normal-game recognition defect.

These are finite trials. There is no automatic foreground reclamation, universal unattended-recovery guarantee, four-modifier payout formula or universal coins/hour claim. Other geometry/DPI, all skins, severe live network faults and current-release live routes through physical boards 2 and 3 remain unverified; previous route evidence and automated guards are retained. The recovered third match was deliberately stopped before a complete result. Private captures and the original strategy remain excluded from public source and packages.

Observed 15–16 November 2026: Windows 11, Microsoft Store Roblox GDK, English TDS v2.19.1, physical client 1920×991/120 DPI, local English Windows OCR, default controls, UI Scale Large and the settings in setup.md. Golden Scout Intern skin occupied slot 1; slots 2–5 were empty. The account had partial active modifiers.

## 0.2.2 follow-up after extended running

The unchanged 0.2.1 app continued to **31 confirmed wins / 13,950 coins**, with all 44 actions confirmed in every completed match. Observed durations were 7m38s–7m42s. This was not an uninterrupted run: after the initial deliberate recovery, six natural map-setup stops occurred. Every recovery closed/reopened TDS successfully; two failures occurred back-to-back before another win. The final run was stopped normally after win 31 for validation.

Four stops followed sideways movement at the curved stone/grass edge. The original floor probes still passed just before the final strafe (left support 71–80%), then both supports disappeared. Extending the strafe probes ten pixels downward rejects each unsafe predecessor frame (left support 58–66%). The patch requires that additional margin before A/D, corrects forward while the original support permits it and retains the original lost-support stop. Sanitized edge/interior fixtures and a controller regression verify correction before strafing; all four saved traces retain their stop on the later lost-support frame.

Two stops followed a successful vote and the normal backward step. That step lowered the ribbon to y=282/290; the normal band ending at y=315 cut the title crop. A post-vote-only band ending at y=360 reads the full title in both actual failure frames. Erasing Ahead still rejects the target. Normal four-board navigation keeps its existing band, and the controller still requires the unique full target and one vote before Ready. The original physical index is retained.

A focused independent static review found no material issue. It did not provide live-game proof; local tests and packaged live checks are reported separately.

The complete local suite passed **286/286 tests** in 73.553 seconds with the GUI/worker stopped. Compilation, the 18-package dependency check and whitespace validation exited zero. The 0.2.2 candidate built successfully and its self-check reported 44 actions, 16 observer states, English Play Again OCR and Tcl 8.6.15. Twenty source hashes and 73 runtime-data hashes matched; the previous 0.2.1 app and its complete 31-win evidence were preserved before installing the candidate.

The candidate was started through native F1 from a verified lobby. It completed loadout, Survival/Easy/Solo, VIP Dead Ahead selection, physical-board-1 voting and fresh overhead setup, then won **7m43s / 450 coins with all 44 actions and zero recoveries**. The first live route did not reproduce the narrow edge or lowered-title failure geometry; the six original failure cases have saved-frame/controller regression coverage. The continuous worker then began Play Again. This is a finite baseline trial, not proof that every voting-room perspective is fixed.

A clean public export passed **41 focused checks** across maps, strategy, the vertical profile and the two new controller regressions without the private original. Its 254 files and 182 PNGs passed private-pattern/metadata checks. The final candidate's duplicate executable/runtime was removed after installing and hash-checking the identical app, freeing a further 176,694,518 bytes while preserving candidate data, the active app and 12 protected paths, including the full 0.2.1 fallback/evidence.

## 0.2.1 checks and measurements

The final packaged app's recovered match won **7m41s / 450 coins** on Dead Ahead / Survival / Easy, wave 20. All 44 actions were confirmed: nine vertical Scouts, eight level 4 and the ninth level 3. Normal Play Again returned to map voting. The same worker re-established the four-board row, selected/voted Dead Ahead through VIP, verified a fresh zero-tower overhead setup and confirmed the first placement and upgrade in match 2 without manual correction. These two setups used physical board 1; this release trial does not claim fresh live coverage of all four positions. The one recovery was deliberately triggered before that match; it is separate from normal replay.

The final source passed **282/282 full local tests** in 84.436 seconds with the GUI/worker stopped. Compilation, dependency compatibility (18 packages) and `git diff --check` exited zero. The frozen app built successfully and its self-check reported 44 actions, 16 observer states, local English OCR of Play Again, Tcl 8.6.15 and the expected strategy hash. All 20 source hashes and 73 runtime data hashes matched the workspace. A clean public export passed 56 selected checks (11 strategy, 20 calibration, one vertical profile and 24 recovery), with the private original absent. Its 250 public files and 178 PNGs passed the private-pattern/embedded-metadata scan.

Login Rewards was claimed live with **one guarded click**. TDS closed that popup automatically. Reopening the panel confirmed grey Close, and the macro dismissed that already-claimed page once. Initial trials stopped before claiming because the normal hover font differed and the left button padding triggered an avatar profile tooltip. An exact hover reference and the tested right padding fix those causes without reducing recognition thresholds. Tests cover automatic closure, Claim-to-Close, absent rewards, grey-button rejection, changed/unreadable captions, interrupted confirmation sequences and delayed claims without another click.

A three-second post-exit relaunch repeatedly left a Store activation process without a game window; further launches displayed **0x800705b4 / already running**. After one separately authorized manual cleanup, a normal-close trial with a **60-second post-exit wait** launched once and reached a new verified foreground lobby in 92.33 seconds overall. The macro now uses that cancellable settle before every recovery launch, including when the old game has already disappeared. It contains no force termination. Fake-clock regressions failed at the old delay and passed with the new delay, including cancellation during the wait.

The final packaged GUI was then started with native F1 from a deliberately open Settings screen. It detected that invalid starting state, closed the verified client normally, waited 60 seconds and launched once. A different process/window reached a verified lobby in 85.29 seconds overall. The same worker resumed loadout, Survival/Easy/Solo, VIP Dead Ahead selection, physical-board-1 voting and a fresh zero-tower overhead setup without manual correction.

Performance measurements used the same two preserved game frames, real local OCR/observer/HUD/hotbar/camera checks and PNG diagnostics, with 12 measured reads per frame/version:

| Composed gameplay read | 0.2.0 median | Optimized median | Reduction |
|---|---:|---:|---:|
| Initial frame | 901.10 ms | 395.70 ms | 56.1% |
| Action-25 frame | 825.55 ms | 513.87 ms | 37.8% |

State, cash, HUD, hotbar and camera results were equivalent for every measured read. This was one local benchmark round, with concurrent game preparation possible; it does not establish universal CPU performance or coins per hour. Later claim/recovery changes do not alter that gameplay read path.

The distant board-row detector's median fell from 28.35 to 3.52 ms in a separate 12-sample comparison. Four-board reading, dominated by OCR, measured 174.09 versus 181.21 ms under variable load, so an end-to-end board-reading speedup is **not established**. Menu transitions remove one unobserved 200 ms wait after the second source confirmation while retaining both spaced observations, the final click guard and normal polling.

The camera feature crop processes 864×768 pixels (34.9% of the frame) with the same masked terrain and client-coordinate keypoints. A live +20 wheel-unit perturbation failed strict binding, received one -10 correction and then passed. A larger +40 perturbation lacked enough matching terrain and stopped safely; the baseline was subsequently restored. Avatar settings were unchanged, and no TDS Character Scale option was used. Other avatar bundles/heights still lack live proof.

Local cleanup removed **4,069,345,408 bytes (3.79 GiB)** of verified duplicate/obsolete binary payloads, including superseded 0.2.1 candidates and the final candidate's duplicate executable/runtime after installing the identical tested app. Captures, original/history data, release archives and protected fallback/source trees were preserved and checked. The two final candidate cleanups verified unchanged evidence/data in five package folders and unchanged protected paths, including the active app's static runtime. This is removed payload size, not net disk savings after new builds.

## 0.2.0 live acceptance

The final app completed **three consecutive wins with zero recoveries**: **7m43s, 7m44s and 7m44s**, each awarding 450 coins, for **1,350 coins**. Every match confirmed all 44 actions, nine Scouts, eight level-4 Scouts and one level-3 Scout, Dead Ahead / Survival / Easy and wave 20. This is a finite trial on this account, not a universal income or win-rate claim.

Normal Play Again returned to map voting. The same worker selected/voted the target and established a fresh overhead pose for matches 2, 3 and 4 without manual correction. The first placement/upgrade in match 4 was confirmed. Saved route checkpoints confirm that stone support was never lost after entering the walkway and that running source hashes matched the tested package. These routes used physical board 1: the first three setups used VIP, while match 4 found Dead Ahead already present and skipped VIP. Earlier live routing exercised all four physical positions, including a complete board-3 win.

Automatic recovery separately closed a failed Settings session, waited for the verified process to exit, reopened TDS into a different process/window, verified the lobby and resumed the full preflight/map/camera path. That recovered match won **7m44s / 450 coins with all 44 actions confirmed**. A later real map-vote recognition failure also reopened into a new verified lobby. Recovery was not used to count the three clean consecutive wins above.

A native F2 press during a live recovery countdown produced the GUI stop marker and stopped the worker before either closing or launching. The same Roblox process and Settings screen remained. Native F1 started the final clean packaged run. F8/Escape, focus/geometry changes, shared stop markers and lifecycle cleanup have automated coverage.

The current grey Close Login Rewards page was recognized and dismissed live through the Login toggle, both in a bounded check and at the start of the final app run. The existing green Claim variant retains fixture coverage. Both title and control are required; removing either rejects the state. Normal lobby observations skip dismissal input. The macro does not claim rewards.

## Observed failures and corrections

- The avatar previously aligned a side board before reaching the curved stone walkway, climbing the left decoration. Lateral movement now requires two-sided stone support; one-sided support permits a short forward correction, and losing both sides stops.
- Fixed VIP strafing could push into the machine and make the inverse movement overshoot. Short bounded steps now stop on two actual Override Map prompt reads; the return uses that stepped duration.
- Two real views produced only Dead while the complete Dead Ahead title was visible. Tight title and original-RGB word crops recover the full phrase; erased-word negatives reject it. Unreadability permits bounded observation without walking.
- A real Windows read handle reproduced a status-file WinError 5. The writer retries only the same completed atomic replacement, at most five times with 25ms spacing. Persistent denial preserves the prior status and raises; no game action is repeated.
- A correctly registered vote was unreadable at one cleared perspective: OCR was blank and the digit-1 reference overlap was 0.887, below the unchanged 0.90 threshold. A separate exact reference fixes that view; real zero badges and an erased target remain negative.
- Store Roblox can show a Close Roblox confirmation. Recovery verifies its exact title and both buttons before a guarded close click. Window disappearance alone was insufficient: the worker now waits for process exit and a short activation-broker delay before the official launch URI. A deadline-edge negative-sleep defect also has a fail-to-pass regression.
- Login Rewards previously had only a Claim reference. Its existing second anchor now accepts the current Close label as an alternative, alongside the unchanged title anchor.

These changes preserve target identity/vote, overhead pose, actual cash/prices, tower name/level/count, result-before-spending, foreground and stop checks. No uncertain purchase is repeated. Recovery starts a fresh session and never resumes a partial match.

## 0.2.0 automated and package checks

- **256/256 full local tests passed** in 47.886 seconds after the final source and Login Rewards data changes, with the GUI/worker stopped for exclusive native hotkey tests.
- Clean public-source export: **50 checks passed** across strategy (11), calibration (18), nine-Scout profile (1) and recovery (20), with the private original strategy and account captures absent.
- Frozen final app self-check exited zero: 44 actions, 16 observer states, local English OCR of Play Again, Tcl 8.6.15 and the expected calibrated strategy hash.
- Runtime source hashes and all 72 strategy/calibration/UI data files matched the workspace. The source privacy scan checked 246 public files and 176 PNGs without embedded metadata, finding no forbidden private paths, original strategy, known local identities or token/key patterns. New fixtures retain only needed UI/world regions; full frames remain private.
- Recovery tests cover manual stops, focus/window changes, a missing client, failed close, lobby deadline, bounded relaunches, win reset, close-confirmation changes, expected window destruction, process lifetime and cancellation inside waits. Hosted core checks use injected OCR; actual image/OCR regressions run locally.

Windows CI runs the core tests and builds the app; hosted checks do not establish game outcomes. The release archive must contain one calibrated strategy, bundled runtime, setup/troubleshooting and 58 dependency/Python notices, with captures, logs, private originals and historical profiles excluded. Release SHA-256 and source-commit metadata are checked separately from live gameplay.

## Limits

Other skins have portrait-independent automated coverage but no separate complete live match. Other/no modifier combinations, resolutions/DPI, restored-window configurations, non-GDK clients, real severe packet loss, future TDS changes, gem farming, universal hourly income and the original 224-action tail remain unverified. Only reported game failures recover; manual stop, focus/geometry, setup/storage boundaries, close/lobby deadlines and three relaunches without a win stop the run. A confirmed win resets that consecutive-failure budget. No automatic refocus, force kill, anti-idle or account-rule approval is claimed.

Historical 0.1.0 evidence included five consecutive wins before a clipped-board stop and a rebuilt 7m39s/450-coin win/replay with 214 local tests. The observations and failures above supersede that baseline for 0.2.0; history remains in Git.
