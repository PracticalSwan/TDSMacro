# Verification

Observed 15–16 November 2026: Windows 11, Microsoft Store Roblox GDK, English TDS v2.19.1, physical client 1920×991/120 DPI, local English Windows OCR, default controls, UI Scale Large and the settings in setup.md. Golden Scout Intern skin occupied slot 1; slots 2–5 were empty. The account had partial active modifiers.

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
