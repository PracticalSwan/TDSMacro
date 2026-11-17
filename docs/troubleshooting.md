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
| Board/VIP/vote unreadable | Four physical positions, the unique complete Dead Ahead title and exactly one target vote must be verified. After one E, the title may be re-read while stationary for up to two seconds; E is never repeated. An unreadable badge permits one D view-clear only on the confirmed map-vote state and two-sided stone margin. The digit matcher allows at most a two-pixel registration shift but retains its 0.90 template threshold; it does not treat a zero or unreadable badge as one. VIP requires the actual E + literal Override Map prompt twice, with at most 12 D steps. Otherwise the macro stops without Ready or another E. |
| VIP proximity / voting floor | The actual Override Map prompt and flat stone walkway are required. The macro stops instead of continuing onto decorations. Keep the documented camera/settings baseline and report a redacted stop reason; do not bypass the floor check. |
| Camera changed | Do not move or touch camera during placement. Two-sided terrain must match the prepared frame. |
| Cash/price/count unreadable | Keep HUD visible; animations receive bounded no-input observation. |
| Action unconfirmed | The server may have applied it. Inspect actual state; begin a fresh match for ordinary use. Never blindly repeat purchases. |
| Defeat / income timeout | Modifiers affect timing/viability. Current-account wins do not establish every modifier configuration. |
| Modifier settings | Automatic modifier selection and four-modifier win/reward validation are deferred pending challenge unlocks. The current release does not select or change modifiers. |
| Result/reward unreadable | The app stops before replay. Send a redacted stop reason through a suggestion issue. |
| Recovery limit / close or lobby timeout | Three relaunches without a win exhaust the limit. Check the original reason and settings before F1 again. Unknown dialogs receive no click; the client is never force-killed. |
| Roblox disconnect dialog during recovery | The calibrated disconnect screen is accepted only with exact `Disconnected`, `Leave`, and `Reconnect` labels. Recovery rechecks before one guarded Leave click. If the same foreground client reaches Roblox Home, it requires four exact navigation labels in two reads before one additional normal close request; an exact Roblox close confirmation uses its existing guarded click. Leave is never repeated, and the same process must exit before the official relaunch. Unknown screens, changed identity/geometry/focus, cancellation, or a client that stays open stop without force termination. |
| Vote badge unreadable after voting | The macro never repeats E or clicks Ready. It may clear the view once with D only after confirming the two-sided voting-floor margin. If that margin is absent, the attempt stops and retains `before_vote.png`, `after_vote.png`, and the status/recovery records. |
| Roblox launch error 0x800705b4 / already running | Recovery waits for process exit and then 60 seconds before one launch. F2 cancels that wait. If it still fails, stop and open Roblox normally; do not repeatedly launch over a stuck instance. |

## Candidate follow-up: disconnect-to-Home still requires live acceptance

The 2026-11-17 candidate's first live Error 278 recovery reached Roblox Home after one verified Leave click but initially failed to close the client. The revised state reader permits a second ordinary close only after **two exact Home observations on the same verified foreground Roblox process** and then handles a recognized close confirmation without repeating Leave. This path has focused synthetic/real-frame checks but **has not yet completed a fresh live Home→process-exit→lobby trial**. Treat any stop here as evidence to inspect, not permission for force termination, background input, repeated Leave or uncontrolled relaunch. Live-test it on the rebuilt candidate using clean native captures after the app/worker is uniquely started.

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

### Local run data: purpose, store and retention

The GUI writes one local run directory under `captures/runs/app_<timestamp>/`; recovery attempts use child `attempt_<number>/` folders. Its worker log is the sibling `captures/runs/app_<timestamp>.log`. The app uses local Windows OCR and has no upload or cloud OCR path. The `captures/` tree is ignored by Git. Full-screen PNGs can contain player/account UI, so keep them local and share only a redacted stop reason.

| Fields or record | Purpose and store | Update and retention |
|---|---|---|
| `status.json`: `phase`, local `runner_pid`, elapsed seconds, counters, and current checkpoint detail | Latest GUI/worker status in the run directory; the app reads it to display progress | Atomic replacement overwrites the prior snapshot. Retained with the run directory. |
| `result.json`: final status/reason, counters, and a `matches` list | Run summary at the run root; an additional result is written per recovery attempt | Rewritten as matches finish and at run end. `matches` is a last-20 window; cumulative counters are separate. |
| `matches.jsonl`: `match`, `elapsed_seconds`, and result fields such as status/reward | Per-match history in the run directory | One JSON row is appended per completed match. |
| `sessions.jsonl`: attempt folder, attempt result and cumulative totals | Recovery-attempt history at the run root | One JSON row is appended per attempt. |
| `recovery.jsonl`: UTC event time, app-run elapsed seconds, local PID, cumulative totals, recoveries, recovery limit, reason, stop kind and consecutive recovery number | Recovery checkpoints at the run root | One JSON row is appended for each reported recovery event. A confirmed win can reset the consecutive recovery number; the cumulative recovery count does not reset. |
| `app_<timestamp>.log` | Worker stdout/stderr beside the run directory; includes status and error text | New log per GUI run; kept until manually removed. Redact local paths before sharing. |
| `latest.png` and named PNG checkpoints | Visual evidence in the run/attempt folder for navigation and match diagnosis | Some paths are overwritten as the run progresses; named snapshots and match evidence remain with the folder. Screenshots are not automatically uploaded or deleted. |
| `captures/last_session.txt` | Pointer to the most recent run directory | Replaced when a new run starts; the stored path is local metadata. |

Navigation status snapshots also include bounded diagnostics: stage, physical board when known, whether the title/badge was recognized, badge value, keycap score, literal-caption result, header count, observation count and bounded movement count. `badge_read` is true only when a numeric badge value was recognized, including zero; an unknown `null` count keeps it false. OCR text is restricted to the two expected title tokens `dead` and `ahead`; arbitrary OCR output is not written to summaries. Inspect the local named PNG sequence when image-level diagnosis is needed:

- Post-vote title/badge: `before_vote.png`, `after_vote.png`, `after_vote_clear.png` when used, and the final `latest.png`.
- VIP approach: `vip_step_00.png` through the last observed step, with no more than the existing 12 D movements.
- Recovery: the attempt's `result.json`, root `sessions.jsonl`, `recovery.jsonl`, and the sibling worker log.

This inventory describes writer fields and retention behavior from source code; the example below is fabricated and contains no live session values:

```json
{"phase":"post_vote_badge_unconfirmed","runner_pid":1234,"elapsed_seconds":12.3,"wins":0,"coins_total":0,"physical_board":2,"target_recognized":true,"badge_read":false,"badge_count":null,"title_observations":3,"view_clear_steps":1}
{"match":1,"elapsed_seconds":12.3,"result":{"status":"stopped","stop_kind":"failure"}}
```

The app writes `matches.jsonl` elapsed values relative to the current attempt. Recovery rows use `event_time_utc` plus elapsed seconds from the supervised app run, so events can be correlated with timestamps without treating a system monotonic counter as a wall clock. `result.json` keeps only its last 20 match summaries while `matches.jsonl` and the recovery/attempt ledgers retain their append-only history; totals in those rows are cumulative snapshots and must not be summed together.

Run directories, JSON/JSONL records, and named PNG evidence are intentionally retained for future tests and diagnosis. No automatic run-folder cleanup is implemented, and screenshots are never uploaded by the app. To reclaim space, stop the GUI/worker first and remove only a specifically selected completed `captures/runs/app_<timestamp>/` folder and its matching sibling `.log`. If `captures/last_session.txt` still points to that exact folder, remove that stale pointer too. Preserve the shared `captures/` root, other runs, release folders, original strategy and any evidence still needed for verification. The macro itself deletes only the pause marker when resuming.
