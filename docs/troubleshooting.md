# Troubleshooting

## Application does not open or appear

1. Confirm you extracted **the complete v0.2.3 release folder**. Do not run `TDSMacro.exe` from inside the ZIP or move the EXE without `_internal`, `assets`, `calibrations`, and `strategies`.
2. Check **Alt+Tab and the taskbar**; Windows may create the `TDS Strategy Macro` window behind another app. If it is visible there, bring it forward normally.
3. Ensure a desktop shortcut targets the current executable and sets **Start in** to the containing `TDSMacro` directory. Multiple files named `TDSMacro.exe` in older build folders are not necessarily the published release.
4. If the process starts but the window still fails, close any competing `TDSMacro` instance (global F1/F2 registration is exclusive) and record the exact Windows error or dialog. Inspect Event Viewer → Windows Logs → Application when an actual crash is reported. Do not disable Windows protections or fetch unofficial DLLs.
5. For development builds, use the documented `--self-check` on the **specific executable** to verify the frozen strategy, Tcl/Tk, OCR and resources. This is a package integrity check, not a guarantee that the normal GUI opens or gameplay works.

On 2026-11-16, a local launch complaint was resolved without code changes: both existing copies passed self-check, the old generic `dist/TDSMacro` was replaced by the verified v0.2.3 release build, the original was archived, and a desktop shortcut and visible responsive GUI were tested. The reported problem was **not** reproduced as an application crash. This local repair did not change the published v0.2.3 ZIP or run Roblox.

Read the last reason in the app. Use F2 before adjusting the game. With recovery enabled, a game failure starts a fresh lobby session after closing the failed client. It never resumes a partial match or repeats an uncertain purchase. Disable recovery before starting if you want to inspect the first failure in place.

| Stop / condition | Check |
|---|---|
| Geometry or DPI mismatch | Physical client must be 1920×991 at 120 DPI. Window borders are excluded. |
| Foreground interrupted | Input stops immediately. With recovery enabled, the same verified client must return naturally within five seconds, twice observed, before a fresh session can start. If it does not, return to the lobby and press F1 when ready. The macro cannot bring Roblox to the foreground. |
| Window / identity changed | Position, size, DPI or client identity changes stop recovery. Restore the supported setup before F1. Only an armed recovery may bind its newly launched client. |
| Hotkey registration failed | Close another controller that owns F1/F2/F8; never overlap workers. |
| OCR unavailable | English Windows OCR must be available locally; no cloud fallback. |
| Login/tutorial overlay | An available green Claim is clicked once; a recognized grey Close is dismissed. Unreadable or delayed claims stop without a second claim. Clear unfamiliar first-play dialogues manually. |
| Loadout / hotbar | Golden Scout slot 1 only, remaining tower slots empty; tower rather than item bar. |
| Storage / evidence write failed | Check that the app's captures folder is writable and the disk has at least 2 GiB free. This stops the run; reopening Roblox cannot repair local storage. |
| Board/VIP/vote unreadable | Four physical positions, target title and one solo vote must be verified. Decorations/UI changes may need recalibration. No guessed board. |
| VIP proximity / voting floor | The actual Override Map prompt and flat stone walkway are required. The macro stops instead of continuing onto decorations. Keep the documented camera/settings baseline and report a redacted stop reason; do not bypass the floor check. |
| Camera changed | Do not move or touch camera during placement. Two-sided terrain must match the prepared frame. |
| Cash/price/count unreadable | Keep HUD visible; animations receive bounded no-input observation. |
| Action unconfirmed | The server may have applied it. Inspect actual state; begin a fresh match for ordinary use. Never blindly repeat purchases. |
| Defeat / income timeout | Modifiers affect timing/viability. Current-account wins do not establish every modifier configuration. |
| Modifier settings | Automatic modifier selection and four-modifier win/reward validation are deferred pending challenge unlocks. The current release does not select or change modifiers. |
| Result/reward unreadable | The app stops before replay. Send a redacted stop reason through a suggestion issue. |
| Recovery limit / close or lobby timeout | Three relaunches without a win exhaust the limit. Check the original reason and settings before F1 again. Unknown close dialogs receive no click; the client is never force-killed. |
| Roblox launch error 0x800705b4 / already running | Recovery waits for process exit and then 60 seconds before one launch. F2 cancels that wait. If it still fails, stop and open Roblox normally; do not repeatedly launch over a stuck instance. |

## Slow connections and animation

| Boundary | Maximum observation window |
|---|---|
| Ordinary menu transition | 45 seconds |
| Solo / Play Again / return loading | 180 seconds |
| Match Ready arrival after voting | 180 seconds |
| Ready click → active-wave HUD | 60 seconds |
| Transient HUD/camera evidence | 5 seconds per read |
| Selection panel | 8 seconds; one evidence-gated selection-only retry |
| Sufficient cash | 180 seconds per action |
| Placement/upgrade acknowledgement | 20 seconds after one purchase click |
| Result details settling | 20 seconds |
| Final result after strategy completes | 900 seconds |

These are bounded waits, not network-performance guarantees. Capture/OCR adds processing time; unexpected states can stop earlier. Focus, identity, geometry and stop checks remain active. A late purchase is observed without clicking again.

Synthetic tests cover a 125-second teleport, 30-second wave start and 7-second placement/upgrade acknowledgements. Real severe packet loss, overloaded machines, all overlays and lag levels have not been reproduced. Supervise the first match on each setup.

## Developer controls and reports

`scripts/tds.ps1` also supports bounded runs and local status/pause/resume/stop. Pause takes effect between atomic actions; TDS time continues. A pause longer than five minutes stops. Use the GUI/F2 for ordinary operation.

Reports should include release, measured geometry/DPI, language, phase, modifiers and last stop reason. Remove usernames, balances, chat, account identifiers and personal paths from any excerpt. Never send credentials or raw Roblox/session files.
