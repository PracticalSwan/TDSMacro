# Troubleshooting

## Roblox error 278 after extended inactivity

Roblox may disconnect from an unattended lobby after 20 minutes of inactivity, displaying **Error Code 278** and the native **Disconnected / Leave / Reconnect** dialog. This is a different condition from the network failure Error 277 and does not indicate a camera calibration defect. If Roblox is in the verified foreground with the supported geometry, a *single* guarded Reconnect click can return to the TDS lobby, but the resulting state must be confirmed stable before any automation. If Reconnect fails, stop; never click through an unknown screen. A prior interrupted ten-match streak does not carry over.

## Roblox error 277 during a Hardcore match

Roblox may display its native **Disconnected** dialog with **Error Code: 277** if the network connection drops. The Wretched Front terrain behind this dialog is blurred; do not adjust camera calibration to fix it. v0.3.0 identifies the exact Disconnected, Leave and Reconnect labels and stops without guessing any tower position or spending cash. A stopped run is **not** an accepted 10-match streak. Once connectivity is restored, use the guarded official-client recovery and verify the foreground 1920×991 / 120-DPI TDS lobby before starting a **new** bounded ten-match session. Keep the private failure image in captures/runs; do not upload it into public releases.

## Hardcore v0.3.0 Restart Match

After 75 confirmed actions, a natural wave-30 Defeat, and exactly 137 Gems on the result screen, the macro clicks Restart Match once. It verifies the fresh Wretched Front Ready screen with zero towers and rebinds the camera before re-placing any towers. It does not return to lobby or check wallet balances between successful cycles. Result reward totals reflect displayed Gems, not account-wallet audits. If the result is early or unreadable, or the match/camera/tower identity is uncertain, the macro stops rather than restarting blindly.

## Hardcore cash unreadable

The v0.3.0 Hardcore reader uses the bottom-right in-match cash counter only. It strips OCR punctuation and compares normal/inverted readings of two bottom-HUD crops, using one contrast-enhanced read only if needed. It does not use rounded player-list money. Missing or unresolved values stop spending safely. Keep the private hardcore_hud_unreadable.png from a failing run when troubleshooting. Never alter the display scaling or camera while the macro is running.

**Current Roblox Store/tray launch boundary (November 19 evening):** An official `roblox://experiences/start?placeId=3260590327` activation was accepted by Windows AppModel and created a short-lived Store application process, but no supported foreground TDS lobby was confirmed within 120 seconds. Later the Store Roblox client became visible at 1920×991 and 120 DPI but remained **background**, while another desktop application owned focus. This is **not** evidence that the TDS gameplay macro clicked the wrong Play button or that the game place ID changed. Do not repeatedly activate the URI, force terminate the tray process, reinstall Roblox, alter graphics drivers, or bypass the foreground guard automatically. The next safe step is a user-verified foreground TDS lobby and no other input controller; otherwise record a setup/focus blocker and stop. The unfinished v0.3.0 build/test improvements are preserved, with no release or unattended automation claimed.

**Hardcore Ready check (November 19):** After a successful guarded camera route and four L0 opening Farms, the macro can stop on `Wretched Front Ready changed before click` if one live frame is unreadable. The latest retained F4 and post-stop images showed a legitimate Ready prompt; the specific rejected frame was not captured, so do not assume an actual click-hover defect. The source now retries at most two brief **read-only** observations using one frame for readiness and evidence, saving `hardcore_ready_preclick_unverified.png` and stopping if none verify. Never click through an unknown Ready state or restart a worker from a partially purchased match. Use the verified official client-recovery path to restart a fresh match.

**Wretched v0.3.0 camera stops (November 19):** A wave-28 range-circle effect can obscure the broad first terrain landmark, while the narrower rock strip can itself match the wrong offset during the final route camera turn (checkpoint 8). The current source uses both first-landmark templates, but approves neither unless **three independently matched landmark offsets agree within 2px**. Preserve the captured failure frame and bound/observed offsets. Do not treat a single stronger template peak as a valid camera, rebind on the fly, click on unverified position, or bypass the foreground/speed/stop gates. Targeted regressions pass but the full native result still requires verification. See the [active plan](plans/2026-11-19-v0.3.0-hardcore-10-farm-revision.md).

**Wave28 camera unverified (2026-11-19):** In a supervised native Wretched Front run all 18 towers had been placed, but a late-wave attack-range arc temporarily crossed the full first rock template, producing a false `(-25,-13)` offset while the other two landmarks still matched the original overhead view. Current v2 source now reads the **stationary lower edge of landmark 1** and still requires all three fixed regions to agree within original strict tolerance. No click or rebind if any landmark genuinely moves; stop-on-uncertain remains. Tests reproduce wave27/28 original pose, reject +8px camera drift and missing first/third landmark; 4/4 focused tests pass. A current live wave30 gem-cycle regression is still needed. Do not infer failure from masked HUD evidence images, which deliberately black out the camera scene.

**Hardcore route checkpoint 4 — November 19 11:20:** When Wretched Front stops with `back-path terrain did not verify at checkpoint 4`, inspect the preserved `hardcore_camera_before_normalizing.png` and `hardcore_route_04_unverified.png`, not just the newest image. Native comparison found the stable left terrain matched the accepted view (0.955) while right-side animated scenery degraded the full tile. The current v2 recognizer uses a measured **checkpoint-4-only static right-side subsection and entire left terrain** without lowering matching threshold. The old camera normalization was incorrectly available mid-route; it is now restricted to initial zero-progress spawn. If neither ROI verifies after bounded rereads, stop safely. Do not press additional movement keys, redo orbit or skip terrain checkpoints blindly; restart from a verified new lobby and retain this failure evidence.

The Hardcore candidate checks the readable tooltip name over each occupied match-ready hotbar slot before buying or pressing Ready. Check the selected inventory name and `Unequip` state separately from the slot tooltip. If a Ready or zero-count read flickers, the worker waits for fresh matching reads while the pointer stays on that slot.

**Golden Scout 2026-11-19 recovery stall:** If the game successfully reopens Roblox and the TDS lobby but then hangs at the orange Tower Defense Simulator loading splash after Solo, the macro may time out at `map_vote`. In one observed run the subsequent ordinary WM_CLOSE did not exit Roblox; native logs also reported server NoResponse. A candidate recovery fix performs a single standard Windows system Close only after two verified `loading` reads of the *same* foreground window five seconds after WM_CLOSE, then insists on actual exit, the Store broker settling and the official TDS URI before rejoining. It never force-terminates, retries Play blindly, bypasses a changed client, or exceeds the three-recovery ceiling. It is not yet a published v0.2.4 fix. See the [dated verification](verification.md#golden-scout-loadingrecovery-fix--november-19-2026-isolated-candidate-not-published). In a real network outage, even guarded relaunch may fail and should stop with evidence.

**Current v0.3.0 native failure notes (2026-11-19):** A B2 coordinate accepted in an earlier occupied view rendered a **red, rock-adjacent placement preview** in the latest fresh-spawn camera at wave 15. Confirm exact camera/landmark offset and the **armed white footprint with existing towers present**; do not infer clearance from center distance, a single historical preview or an attack-range ring. Prefer one directly guarded placement from the verified armed preview; cancelling and reselecting wastes time and increases leakage risk. A briefly unreadable tower panel may use one bounded neutral-cursor/read-only retry, but no blind purchase repetition. Avoid excessive Farm upgrades at the expense of defense milestones; quotes can change during wave income and must be rechecked immediately before clicks. Preserve a capture of red and accepted footprints for focused regressions. [Current plan](plans/2026-11-19-v0.3.0-hardcore-10-farm-revision.md). The public v0.2.4 troubleshooting remains separate.

**v0.3.0 development-only known boundaries (2026-11-19):** If the macro appears to wait until a stage's first wave, inspect the candidate `affordable_purchase` and stage upper-deadline checks, observed price/cash, prerequisites and current action ledger; stage starts must not lock early eligible purchases. On a Farm budget wait, try other eligible affordable Farm actions with fresh price/level confirmation rather than idling. If a combat tower cannot be placed in the tight center group, inspect the live white/red footprint with existing towers present, owner-reference orientation (Crook left, Boomerang right), B1 lane coverage and camera landmarks. A native controller guard refusal, unknown identity, crossfade wave OCR or uncertain post-click state is a safe stop, not a reason to bypass the guard. Keep private frames/logs. Reward and replay are not yet v0.3.0 verified; released v0.2.4 Golden Scout troubleshooting below remains authoritative for end users.

## Application does not open or appear

1. Confirm you extracted **the complete published release folder**. Do not run `TDSMacro.exe` from inside the ZIP or move the EXE without `_internal`, `assets`, `calibrations`, and `strategies`.
2. Check **Alt+Tab and the taskbar**; Windows may create the `TDS Strategy Macro` window behind another app. If it is visible there, bring it forward normally.
3. Ensure a desktop shortcut targets the current executable and sets **Start in** to the containing `TDSMacro` directory. Multiple files named `TDSMacro.exe` in older build folders are not necessarily the published release.
4. If the process starts but the window still fails, close any competing `TDSMacro` instance (global F1/F2 registration is exclusive) and record the exact Windows error or dialog. Inspect Event Viewer → Windows Logs → Application when an actual crash is reported. Do not disable Windows protections or fetch unofficial DLLs.
5. For development builds, use the documented `--self-check` on the **specific executable** to verify the frozen strategy, Tcl/Tk, OCR and resources. This is a package integrity check, not a guarantee that the normal GUI opens or gameplay works.

On 2026-11-16, a local launch complaint was resolved without code changes: both existing copies passed self-check, the old generic `dist/TDSMacro` was replaced by the verified v0.2.3 release build, the original was archived, and a desktop shortcut and visible responsive GUI were tested. The reported problem was **not** reproduced as an application crash. This local repair did not change the published v0.2.3 ZIP or run Roblox. On 2026-11-18, the maintainer's standard `dist/TDSMacro/` was updated to the published v0.2.4 binary after file-count/hash verification. The prior v0.2.3 installation and its private captures remain archived, and each versioned desktop shortcut now points to its corresponding install. A successful install or self-check is not a substitute for a guarded live game trial.

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
| Natural AFK recovery acceptance | `--idle-lobby-seconds` is a one-time developer acceptance option for a stable TDS lobby, limited to 1200–1800 seconds with continuous auto-recovery enabled. It sends no input while monitoring and remains pending across a startup recovery until its interval completes or two exact modal reads confirm the natural disconnect. If Roblox does not disconnect by timeout, the run records that result and continues its normal preflight; an unreadable modal or other state stops safely. |
| Vote badge unreadable after voting | The macro never repeats E or clicks Ready without badge 1 on the unique target. It may make one 0.10-second W correction if either-side floor support remains, then rereads state, title and badge. A single D view-clear remains gated by the stricter two-sided strafe margin. If support or identity is lost, the attempt stops and retains the relevant named frames and status/recovery records. |
| Roblox launch error 0x800705b4 / already running | Recovery waits for process exit and then 60 seconds before one launch. F2 cancels that wait. If it still fails, stop and open Roblox normally; do not repeatedly launch over a stuck instance. |

## Recent recovery evidence

The fresh r4 package completed a genuine Error 278 recovery through one guarded Leave, two Roblox Home reads, ordinary close, process exit, the 60-second launcher settle, official URI launch and two stable foreground lobby reads; its next match won 44/44. A later Error 277 appeared during another match. The same recovery flow relaunched Roblox, but the bounded lobby wait ended without a verified foreground lobby, and the worker stopped safely. The post-stop native probe found the client open at calibrated geometry but in the background. Recovery never steals focus; if this happens again, preserve the run evidence and stop unless Roblox returns naturally to the verified foreground. Do not click the background client or repeat Leave.

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

See the [field-level local diagnostic data map](diagnostic-data.md) for the source-derived writer inventory and synthetic records.

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

Navigation status snapshots also include bounded diagnostics: stage, physical board when known, whether the title/badge was recognized, badge value, keycap score, literal-caption result, header count, observation count and bounded movement count. `badge_read` is true only when a numeric badge value was recognized, including zero; an unknown `null` count keeps it false. The `title` status value comes from OCR on the board-header crop and can include recognized words around the expected Dead Ahead phrase. Review status and worker logs before sharing them; `title_tokens` diagnostics are normalized to the expected title tokens. Inspect the local named PNG sequence when image-level diagnosis is needed:

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
