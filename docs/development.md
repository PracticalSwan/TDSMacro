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

The input guard still raises `focus_lost` immediately and releases held controls through its existing cleanup. Only the explicitly started continuous recovery supervisor can observe the same original window passively for five seconds, requiring two foreground samples 200 ms apart before a fresh session. Persistent loss, changed identity/geometry, manual stop, pause and storage/setup errors stop. The original client anchor survives disappearance through the close cooldown, so a replacement client cannot be closed. The reopened lobby must be stable on the same new window before the next attempt. No focus activation is part of recovery.

Never use computer-control sessions (`cua_repl`, `@oai/sky`, CUA/computer-use or desktop browser-act) for this project. Their pointer/blue effects can enter native captures, and their input activation can restore or resize a window. Use the existing `GuardedInput`/`WindowsOS` and native capture functions for supervised tests. The owner brings Roblox to the foreground; recovery never does. Establish recognition failures from clean captures without those overlays before changing references or thresholds.

## Checks and build

Menu transitions retain two source observations 200 ms apart; the click follows the second without another unobserved delay. The normal polling cadence and action guards remain. Map detection converts only the existing header bands to RGB arrays and restores contour coordinates before OCR, avoiding full-frame allocations without reducing the four-board checks.

Sideways voting-room alignment requires a ten-pixel lower stone margin in addition to the original floor supports; a supported edge receives forward correction before another strafe. Only post-vote title validation expands the header band from y=315 to y=360 because the backstep lowers the ribbon. Normal board selection and physical-index establishment use the original band.

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

CI runs Windows core tests, syntax checks and packaging. Full OCR/image checks and live games require the supported interactive environment; CI does not prove wins. Fix demonstrated causes, preserve small sanitized regressions and update changelog/verification. Gameplay changes warrant a live win/replay; cosmetic docs do not warrant restarting long soaks. See AGENTS.md for automatic commit/push rules.

## Release security

Untrusted strategy/profile data reaches strict parsing and guarded input, not arbitrary code evaluation. Community files are not auto-loaded. Fork PR jobs use a read-only token, pinned action commits, no persisted checkout credentials and no repository secrets, following [GitHub secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use). Core changes are owner-maintained.

Another viewport requires new fixtures/calibration, guard tests and supervised live proof, not proportional clicking.
