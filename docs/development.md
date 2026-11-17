# Development

Use Windows 11, Python 3.14 x64 with Tkinter and local English Windows OCR. The release bundles Python; source development uses an isolated environment.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-runtime.txt -r requirements-build.txt
.\.venv\Scripts\python.exe tds_launcher.py
```

No training, GPU runtime, credentials or cloud OCR is needed.

| Component | Responsibility |
|---|---|
| tds_launcher.py / app.py | Tk selector, global F1/F2, child worker lifecycle |
| session.py / navigation.py / maps.py | Lobby, Login Rewards, loadout, menus, four-board/VIP voting, replay branches |
| recovery.py | Cancellable process close/relaunch, verified new lobby, fresh attempts and shared totals |
| phase1.py / control.py | Identity/capture, physical coordinates, guarded ordinary input, stop/release |
| observer.py / resources.py / loadout.py / hotbar.py / results.py | Local visual/OCR readers |
| strategy.py / calibration.py / run.py / match.py / timing.py | Strict parser, camera binding, ordered confirmed actions, deadlines |
| recording.py | Lossless latest-frame diagnostics with bounded PNG write frequency |
| calibrations / assets / tests/fixtures | Sanitized UI/world regions and independent regressions |

Strategy commands use a whitelist and are never evaluated as code. Runtime strategy hashes are mandatory. Strategy/scene/landmark paths are confined to their directories. Initial source-scene binding verifies pose; drift uses a fixed prepared frame, never rebound after placement.

Camera feature extraction uses the same masked map regions with padded native-resolution crops; keypoints are restored to client coordinates. Fresh zero-tower setup may guide a bounded zoom correction using matching terrain, but placement acceptance and prepared-frame drift limits are unchanged. Retained restarts do not correct the camera.

Playback classifies each captured frame once and saves its diagnostic latest PNG at most once per second, using lossless fast compression. Every frame is still captured and checked; critical evidence remains separate and the actual last frame is flushed at exit. A failed final PNG write preserves an already confirmed result and stops the session as a storage error before replay. Navigation keeps fresh diagnostics on every capture with fast compression.

Navigation evidence saves share one storage-error boundary; an unwritable PNG stops instead of reopening Roblox. Unverified loadout/hotbar preflight is a setup stop after the existing bounded observations.

The input guard still raises `focus_lost` immediately and releases held controls through its existing cleanup. Only the explicitly started continuous recovery supervisor can observe the same original window passively for five seconds, requiring two foreground samples 200 ms apart before a fresh session. Persistent loss, changed identity/geometry, manual stop, pause and storage/setup errors stop. The original client anchor survives disappearance through the close cooldown, so a replacement client cannot be closed. The reopened lobby must be stable on the same new window before the next attempt. No focus activation is part of recovery. If the known Roblox disconnect modal blocks normal close, recovery accepts only the calibrated `disconnect` state and exact `Disconnected`, `Leave`, and `Reconnect` labels, rechecks them immediately before one guarded Leave click, and never repeats Leave. After Leave, the same foreground client must show all four exact Roblox Home-navigation anchors on two reads before recovery posts one additional ordinary WM_CLOSE to that verified client. An exact Roblox close dialog may instead proceed through its existing guarded click. Unknown screens, focus/identity/geometry changes, cancellation, and a client that remains open stop; verified process exit remains mandatory before the official URI relaunch.

Computer-use tools (`cua_repl`, `@oai/sky`, CUA/computer-use or desktop browser-act) are available for ordinary project work and preparatory UI/setup while no macro run is active. They must not perform, verify or calibrate macro actions. Before F1 or any live macro run, close all computer-use sessions/surfaces and overlays across agents; then recheck the Roblox foreground identity, client geometry/DPI and a clean native capture. During the run no agent may use or attempt computer-use, activate windows, or calibrate from its overlays. Live macro verification uses the existing `GuardedInput`/`WindowsOS` and native capture path. Recovery never activates Roblox. If computer-use starts or affects the client mid-run, stop through guarded F2, retain evidence, and require a fresh verified session before resuming.

## Checks and build

**Post-handoff priorities (2026-11-17):** The v0.2.4 candidate has 10 recorded live 44/44 wins with zero recoveries and a verified F2 stop, but the changed Roblox disconnect → Home → guarded process close → fresh lobby path has only offline checks and **is not yet live-proven**. A small follow-up reduces `Session.vote_count`'s red-badge scan to a verified target-centered ROI without changing the vote-one/zero thresholds. Its session-focused 72-test suite and seven saved frame outcomes passed locally. After building a new candidate, prioritize supervised Roblox navigation/recovery on **that exact binary** rather than repeated general unit tests; the present `dist/` candidates predate this ROI edit. Preserve fail-closed behavior and record precise unverified gates.

**Efficiency and cleanup:** For screenshot/OCR/scan/PNG hotspots, compare actual real-frame outputs before and after optimization and report measured processing time or bytes, never infer server-paced match time improvement. Retain critical named checkpoints, private match/recovery JSONL records, original strategies and v0.2.3 release. After completing a task, clean disposable temporary scratch and verified redundant generated packages **only** after checking ownership, hashes, active readers and a retained last-good build; do not prune historical run evidence or all of `dist/` merely to save space. Source/test/CI verification runs must not compete with a running F1/F2 worker. See `AGENTS.md`.


Menu transitions retain two source observations 200 ms apart; the click follows the second without another unobserved delay. The normal polling cadence and action guards remain. Map detection converts only the existing header bands to RGB arrays and restores contour coordinates before OCR, avoiding full-frame allocations without reducing the four-board checks.

Sideways voting-room alignment requires a ten-pixel lower stone margin in addition to the original floor supports; a supported edge receives forward correction before another strafe. The post-vote header band remains expanded from y=315 to y=360. After live evidence showed the prior 0.5-second S retreat lost the safe floor, the candidate shortens it to 0.15 seconds; the later trial preserved both floor supports. That view's badge OCR was blank and its raw normalized digit overlap was 0.87694, below the unchanged 0.90 threshold. Allowing at most two pixels of template registration raises the observed badge 1 to 0.92323 while both neighboring zero badges stay below 0.77. The sanitized frame now has a red-to-green offline regression; a packaged live replay and extended run are still required. Normal board selection and physical-index establishment use the original band.

After the single vote E and short S backstep, a missing unique Dead Ahead title gets fresh stationary reads at 200 ms intervals for up to two seconds. Each capture checks the guarded client and map-vote state; the vote action is never retried. A missing badge allows one D view adjustment only when map-vote and the two-sided strafe margin are confirmed, then the title and badge are read again. Ready still requires one exact badge on the unique title. VIP recognition keeps the 0.93 E-template threshold and literal caption requirement; the bounded search extends to y=720 for the measured keycap at y=662, and exact adjacent Override/Map crops recover the late-step text. The existing two-prompt stability check and 12-D movement cap remain.

The stationary title poll still captures each frame, but coalesces `latest.png` writes and saves only the final polled frame. At the maximum ten rereads this avoids nine redundant PNG encodes/writes while retaining the same final diagnostic file and all input/state checks; it does not change retained run-folder size. The sanitized A/B/C, VIP, disconnect-dialog and Roblox Home fixtures contain only the board-title, vote-badge, prompt, modal or intermediate Home-navigation regions needed by the regressions.

Navigation failure snapshots retain only bounded scalar explanations in `status.json` and the existing stop reason: stage, physical board when known, target/badge read flags, badge value, keycap score, literal-caption flag, header count, observation count and movement count. The only OCR text retained is the whitelisted map-title tokens `dead` and `ahead`; arbitrary OCR text is not added to ledgers. Named checkpoint PNGs remain in the local run/attempt folders for private visual diagnosis. Recovery ledger rows add a UTC event time, app-run-relative elapsed seconds, cumulative recoveries and the configured recovery limit; per-attempt match elapsed values remain local to each attempt.

Stop the GUI and worker before the full suite: native tests require exclusive F1/F2/F8 ownership. Tests use fake input except named native hotkey registration/latch checks, which send no gameplay actions.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q src tests tds_launcher.py
.\.venv\Scripts\python.exe -m pip check
.\scripts\build-app.ps1 -Destination dist\new-build
Start-Process dist\new-build\TDSMacro\TDSMacro.exe -ArgumentList '--self-check', 'package-check.json' -Wait
```

An existing environment created by uv can omit the `pip` module. In that case, `uv pip check --python .\.venv\Scripts\python.exe` checks the same installed environment without installing or upgrading packages. Record the command actually used.

Build into a fresh destination; old packages are preserved. The builder includes only the calibrated nine-Scout strategy. A release ZIP must exclude captures, private originals, history, personal paths and diagnostic self-check files. Include license/notices/setup, validate the package and publish SHA-256. Inspect the actual artifact, not just its build script.

**Post-release local install check (2026-11-16):** A stale `dist/TDSMacro` folder can remain after a new release candidate is built. Identify the actual release by comparing the complete extracted app and its EXE SHA-256 with the release ZIP, run `--self-check`, and separately launch and inspect the GUI before promoting a candidate as the local standard. The verified v0.2.3 executable hash is `ddf76edbb7b440c83fc61b48635d18a24574cff86c7d1e3de826dd49416f4624`. The maintainer's previous standard was preserved as `dist/TDSMacro-previous-20261116/`; a desktop shortcut points to the current `dist/TDSMacro/TDSMacro.exe` and sets its working directory. This local repair is ignored by Git and **does not modify the published release**. Do not hard-code this machine's paths into the distributed binary.

CI runs Windows core tests, syntax checks and packaging. Full OCR/image checks and live games require the supported interactive environment; CI does not prove wins. Fix demonstrated causes, preserve small sanitized regressions and update changelog/verification. Gameplay changes warrant a live win/replay; cosmetic docs do not warrant restarting long soaks. See AGENTS.md for automatic commit/push rules.

## Release security

Untrusted strategy/profile data reaches strict parsing and guarded input, not arbitrary code evaluation. Community files are not auto-loaded. Fork PR jobs use a read-only token, pinned action commits, no persisted checkout credentials and no repository secrets, following [GitHub secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use). Core changes are owner-maintained.

Another viewport requires new fixtures/calibration, guard tests and supervised live proof, not proportional clicking.
