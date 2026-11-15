# Troubleshooting

Read the last reason in the app. Use F2 before adjusting the game. With recovery enabled, a game failure starts a fresh lobby session after closing the failed client. It never resumes a partial match or repeats an uncertain purchase. Disable recovery before starting if you want to inspect the first failure in place.

| Stop / condition | Check |
|---|---|
| Geometry or DPI mismatch | Physical client must be 1920×991 at 120 DPI. Window borders are excluded. |
| Foreground / window changed | Keep Roblox visible, unobscured and focused. Manual focus/geometry changes stop and require F1 again. Only an armed recovery may bind a newly launched client. |
| Hotkey registration failed | Close another controller that owns F1/F2/F8; never overlap workers. |
| OCR unavailable | English Windows OCR must be available locally; no cloud fallback. |
| Login/tutorial overlay | Recognized Login Rewards is dismissed once; clear unfamiliar first-play dialogues manually. |
| Loadout / hotbar | Golden Scout slot 1 only, remaining tower slots empty; tower rather than item bar. |
| Board/VIP/vote unreadable | Four physical positions, target title and one solo vote must be verified. Decorations/UI changes may need recalibration. No guessed board. |
| VIP proximity / voting floor | The actual Override Map prompt and flat stone walkway are required. The macro stops instead of continuing onto decorations. Keep the documented camera/settings baseline and report a redacted stop reason; do not bypass the floor check. |
| Camera changed | Do not move or touch camera during placement. Two-sided terrain must match the prepared frame. |
| Cash/price/count unreadable | Keep HUD visible; animations receive bounded no-input observation. |
| Action unconfirmed | The server may have applied it. Inspect actual state; begin a fresh match for ordinary use. Never blindly repeat purchases. |
| Defeat / income timeout | Modifiers affect timing/viability. Current-account wins do not establish every modifier configuration. |
| Result/reward unreadable | The app stops before replay. Send a redacted stop reason through a suggestion issue. |
| Recovery limit / close or lobby timeout | Three relaunches without a win exhaust the limit. Check the original reason and settings before F1 again. Unknown close dialogs receive no click; the client is never force-killed. |

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
