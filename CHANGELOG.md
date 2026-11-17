# Changelog

## 0.2.4 candidate — not released

- Recover the exact Dead Ahead title from both recorded post-vote OCR failures with a final thresholded, 2× local header read. Complete-title and unique-target checks stay unchanged.
- Fix the recorded VIP false negative: the late E keycap was clipped by the y=700 search edge, and whole-caption OCR mixed with the adjacent prompt. Extend only the search edge to y=720 and accept two exact, keycap-anchored words as a fallback; retain the 0.93 keycap threshold and literal Override Map requirement.
- After one E, allow at most two seconds of stationary title rereads with stop, foreground and map-vote checks. An unreadable badge permits one floor-checked D view-clear only. Ready still requires the same unique target and vote badge 1.
- The supervised live trial showed that the previous 0.5-second post-vote S retreat removed the required two-sided floor support (from 100%/100% to under 8%/0%) while the title remained readable and the badge stayed unknown. Shorten that retreat to 0.15 seconds; keep the safe-floor check, one-D limit, and no-Ready-on-unknown rule.
- A later trial preserved the floor and safely used its one D view-clear, but still failed to read a visible badge 1: OCR was blank and the normalized digit overlap was 0.87694 against the 0.90 cutoff. Allow at most a two-pixel template registration shift without lowering the cutoff; the same frame then scores 0.92323 and its two visible zero badges stay below 0.77. A sanitized positive-plus-neighbor-negative regression covers that view, and the subsequent packaged replay evidence is recorded in `docs/verification.md`.
- Recognize the calibrated Roblox disconnect modal during explicitly started recovery only with exact `Disconnected`, `Leave`, and `Reconnect` labels. After one rechecked Leave click, require two exact Roblox Home-navigation reads on the same foreground client before one additional ordinary WM_CLOSE; an exact Roblox close confirmation uses its existing guarded click. Never repeat Leave, and require process exit before the official URI. Unknown screens, cancellation, identity/geometry changes and unclosed clients stop without force termination.
- Classify status, match, recovery-ledger, progress and image write failures as protected storage stops. Preserve an already confirmed result when its final diagnostic image cannot be written, and stop before replay.
- Coalesce repeated `latest.png` writes during that bounded reread, preserving the final frame while avoiding up to nine redundant encodes/writes. No retained run history or user captures were removed.
- Add privacy-bounded navigation failure fields, including an allowlist of the map-title tokens, and clearer recovery ledger timing: UTC event time, app-run-relative elapsed seconds and cumulative recovery count. Keep detailed screenshots and append-only records local for future troubleshooting; never persist arbitrary OCR streams.
- Add sanitized A/B/C, disconnect-dialog and Roblox Home regressions plus no-second-vote, no-Ready, F2, floor-margin, final-step VIP, 12-D-cap, changed-dialog and protected storage-failure checks. Full acceptance, live gameplay, CI and publication status are recorded in `docs/verification.md`; this candidate does not replace v0.2.3.
- Packaged live trial 5 completed the owner-approved ten-match gate: 10 consecutive 44/44 Dead Ahead/Easy wave-20 wins, 4,500 coins and zero navigation recoveries. The registered F2 hotkey then stopped match 11 safely. The corrected disconnect-to-Home recovery still lacks fresh live relaunch proof; v0.2.3 remains the published release.

## 2026-11-16 — Post-release local launcher correction (v0.2.3 unchanged)

- Resolved a confusing local launch setup: the generic `dist/TDSMacro` executable was still a v0.2.2-era copy even though a correct v0.2.3 build existed separately. Verified that the release's executable SHA-256 is `ddf76edbb7b440c83fc61b48635d18a24574cff86c7d1e3de826dd49416f4624` and that the bundled OCR, Tcl/Tk, 44 operations, 16 observer states and strategy hash pass its frozen self-check.
- Promoted the verified **existing** v0.2.3 release build to the local standard `dist/TDSMacro/` folder, retaining the previous folder as `dist/TDSMacro-previous-20261116/`. Created and tested a local desktop shortcut with the correct executable and working directory. Verified a responsive, visible Tk GUI from that shortcut with no Roblox game input.
- The GUI initially opened behind another window; a visible window is not necessarily the foreground one. No app source, strategy, Windows scaling or published ZIP was changed. The installed binary and desktop shortcut are local, ignored files, not repository/release assets.
- Version the existing optional project-local debugging, unittest and verification skill guidance under `.agents/skills/` with its original source references and MIT license notices. These are documentation only and do not change dependencies or runtime behavior.

## 0.2.3 — Passive foreground recovery and protected stops

- Add passive recovery after foreground interruption: immediately release input, wait up to five seconds for the same verified client to return naturally, then restart from a fresh session. Preserve manual stop/pause, geometry/identity, setup/storage and three-relaunch limits. No automatic refocus or interrupted purchase resumption.
- Keep the original client identity through disappearance and the recovery cooldown; reject a replacement before closing. Require two stable observations of the same reopened lobby window.
- Stop for unverified loadout/hotbar setup and failed navigation evidence writes instead of treating them as recoverable game failures.
- Require clean native captures for verification and prohibit computer-control sessions whose pointer/blue effects can contaminate recognition. Preserve the existing Items references; a clean hover still matches at 1.0.
- Defer modifier configuration and four-modifier win/reward validation pending challenge unlocks. Retain the existing nine-Scout, 44-action strategy and v4 profile.
- Verify a clean 7m39s / 450-coin, 44-action win and normal Play Again. A manual foreground interruption returned to the same client in 1.51 seconds, then recovered through a new verified lobby, full setup and 19 confirmed actions before native F2 stopped the trial. Native F2 and app close also cancel startup without game input. Full local suite: 301 passing tests.

## 0.2.2 — Voting walkway margin and post-vote title

- Verify the packaged candidate's 7m43s / 450-coin win, all 44 actions and zero recoveries; leave its continuous Play Again run active.
- Require an additional ten-pixel stone margin before sideways voting-room movement. Near the curved grass edge, take a bounded forward correction first; retain the original two-sided/one-sided support checks and lost-floor stop.
- Use a taller header band only after the vote backstep, preserving the full lowered Dead Ahead title. Keep normal board detection, the physical board index, exact title and one solo vote checks unchanged.
- Add sanitized real-frame regressions for all six observed map-setup stops, including erased-word negatives and physical-index preservation. No vote or purchase action is repeated.
- Extended 0.2.1 soak: 31 confirmed wins / 13,950 coins, all 44 actions in every match. Six natural map-setup stops recovered successfully; these fixes address their two demonstrated causes.

## 0.2.1 — Camera alignment and performance

- Verify a packaged recovery-to-win cycle (7m41s / 450 coins, all 44 actions), followed by normal Play Again through map voting, fresh overhead setup and the first confirmed placement/upgrade in match 2.
- Claim an available Login Reward once after two exact green-button readings and a final guarded check. Accept automatic popup closure or dismiss confirmed Close; skip absent rewards and never repeat an uncertain claim. Recognize the normal Claim hover font and avoid its profile tooltip.
- Wait 60 cancellable seconds after the verified Roblox process exits before one relaunch. This avoids the observed Store activation race and 0x800705b4 error; no force termination is added to the macro.
- Process only the existing 80/135-row map-header bands, restoring screen coordinates and preserving the four-board/title/vote checks.
- Remove the 200 ms unobserved wait after the second menu source confirmation; retain both spaced observations, normal polling and the final click guard.
- Limit camera feature extraction to padded map regions at native resolution, preserving client coordinates, matching requirements and drift limits.
- Remove repeated classification of the same gameplay frame and an extra discarded result-wait read; each measured failure still reaches the guarded action check.
- Use lossless fast PNG compression and bound gameplay latest-frame writes to once per second. Preserve critical evidence and flush the actual final frame.
- Preserve confirmed wins if the final diagnostic PNG write fails, then stop for the storage error before replay or recovery.
- Allow at most six fine zoom adjustments during verified fresh zero-tower setup, followed by the unchanged strict placement pose check. Keep retained restarts check-only and leave avatar settings unchanged.
- Keep lobby, VIP-card and client-close clicks in button/card padding so the pointer leaves verification labels clear.
- Remove verified duplicate local binary payloads while preserving captures, originals, release archives and the current fallback app.

## 0.2.0 — Failure recovery and replay voting-room navigation

- Verified three consecutive 450-coin wins (7m43s/7m44s/7m44s), all 44 actions in each, followed by normal Play Again entry into match 4 with zero recoveries.
- Add default-on, cancellable failure recovery: close the failed client, recognize its Close Roblox confirmation, wait for process exit and reopen TDS into a verified lobby/Login Rewards screen. Preserve attempt evidence and session totals.
- Retain manual stop, focus/geometry, setup/storage and bounded consecutive-failure stops. Native F2 cancelled a real recovery before close/launch; separate recovery trials reopened the client and resumed a winning match.
- Recognize both Claim and Close Login Rewards controls alongside the title. Normal lobby checks send no dismissal input; the macro does not claim rewards.
- Stop the VIP approach on two actual Override Map prompt observations, using short bounded steps and their duration for the return.
- Reach the stone walkway before sideways board alignment; follow its curved edge forward and stop on lost support.
- Recover full Dead Ahead text from tight original word crops; partial titles never authorize walking.
- Add an exact vote-one reference for the observed replay perspective, retaining the existing threshold and zero/erased negatives.
- Retry only transient Windows atomic status-file replacement conflicts without replaying a game action; persistent denial still fails.
- Add sanitized real failure fixtures, bounded private diagnostics and a refreshed app image. Full local suite: 256 passing tests; clean public export: 50 passing checks without the private original.

## 0.1.0 — 2026-11-15

- First public Windows app: one Golden Scout strategy, F1 start/F2 stop, progress and continuous Solo replay.
- Lobby/Login Rewards/loadout checks, four-board/VIP voting, overhead setup and nine vertical Scouts.
- Actual cash/prices, skin-independent identity, prepared-frame drift and result-before-spending checks.
- Fixes for decorated board headers, noisy/animated captions, obscured vote badges and one evidence-gated panel re-selection. No purchase retries.
- Shorter board-reading approach and bounded slow-loading/action-confirmation waits with regressions.
- Public setup/troubleshooting/verification docs, suggestion/strategy-only contributions, Windows core CI/build.
- Original import/history private; public profile independent of private source; confined scene paths and sanitized references.
- Verified a 7m39s/450-coin full win with the owner's Large UI/vertical-upgrade settings. Ignore dim terrain through empty hotbar slots while retaining extra bright-price rejection.
