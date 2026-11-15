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
| calibrations / assets / tests/fixtures | Sanitized UI/world regions and independent regressions |

Strategy commands use a whitelist and are never evaluated as code. Runtime strategy hashes are mandatory. Strategy/scene/landmark paths are confined to their directories. Initial source-scene binding verifies pose; drift uses a fixed prepared frame, never rebound after placement.

## Checks and build

Stop the GUI and worker before the full suite: native tests require exclusive F1/F2/F8 ownership. Tests use fake input except named native hotkey registration/latch checks, which send no gameplay actions.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q src tests tds_launcher.py
.\.venv\Scripts\python.exe -m pip check
.\scripts\build-app.ps1 -Destination dist\new-build
Start-Process dist\new-build\TDSMacro\TDSMacro.exe -ArgumentList '--self-check', 'package-check.json' -Wait
```

Build into a fresh destination; old packages are preserved. The builder includes only the calibrated nine-Scout strategy. A release ZIP must exclude captures, private originals, history, personal paths and diagnostic self-check files. Include license/notices/setup, validate the package and publish SHA-256. Inspect the actual artifact, not just its build script.

CI runs Windows core tests, syntax checks and packaging. Full OCR/image checks and live games require the supported interactive environment; CI does not prove wins. Fix demonstrated causes, preserve small sanitized regressions and update changelog/verification. Gameplay changes warrant a live win/replay; cosmetic docs do not warrant restarting long soaks. See AGENTS.md for automatic commit/push rules.

## Release security

Untrusted strategy/profile data reaches strict parsing and guarded input, not arbitrary code evaluation. Community files are not auto-loaded. Fork PR jobs use a read-only token, pinned action commits, no persisted checkout credentials and no repository secrets, following [GitHub secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use). Core changes are owner-maintained.

Another viewport requires new fixtures/calibration, guard tests and supervised live proof, not proportional clicking.
