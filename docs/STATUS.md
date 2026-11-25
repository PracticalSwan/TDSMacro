# Current project status - November 25, 2026 (Asia/Bangkok)

> Timestamped evidence; check current processes, Git status and newest session receipts before starting, stopping or replacing any worker.

## Latest state (08:29 ICT)

- Installed stable remains **v0.5.1** at `dist/TDSMacro/TDSMacro.exe`. Roblox PID 48972 was present; no TDSMacro GUI or gameplay worker was running. The last installed Golden session ended by user control at 06:23:54 with 30 verified wins, 13,500 displayed Coins, 32 attempts and four relaunches.
- **v0.5.2 corrective candidate** has changes for all eight original defects. The latest candidate three-tower Hardcore retry completed a natural wave-30 Defeat at 08:13:36: all 75 core actions and levels, 137 displayed Gems, 463 seconds, one credited cycle. The preceding finite trial stopped safely on foreground loss at 70 actions; the later wave-28/127-Gem outcome was uncredited.
- Independent review at 08:24: **694 tests passed in 108.331 seconds**, all 18 dependencies compatible via `uv pip check`. The 477 compared source/asset/test/strategy/calibration/workflow files matched hosted candidate commit `bae3634ade57a08b14ea6594a2c0b4292b957b00` byte-for-byte except normalized line endings. Hosted Windows CI [45449064340](https://github.com/PracticalSwan/TDSMacro/actions/runs/45449064340) completed successfully (680 tests, build). The local installed app has not been replaced.
- Latest stable failure evidence: match-ready timeout (saved frame in_match with zero cash/count), inventory timeout (saved lobby frame), count-10 failure (candidate rereads 10/40), map target failure (candidate rereads Dead Ahead). The first two are unproven root causes; no blind retries added.
- The review corrected missing packaged requirements, stale quick-start instructions and relative build destination resolution. The isolated v0.5.2 final-review ZIP at `dist/v0.5.2-final-review-20261125/TDSMacro-0.5.2-candidate-windows-x64.zip` contains 1,318 files; every entry passed CRC and SHA-256 comparison. Frozen self-check passed, all 12 bundled Markdown files passed local-link/repository-source-target validation, and no prohibited private-file entries were found. SHA-256 `174c4ddfe1af13b7dfa0a5d62b02a1eed8cd239b5ae75fa14ce8ec18bb3d4eb0`. The repository-only online URLs require the corresponding reviewed docs to be published before release.

## Candidate evidence and release boundary

| Defect | Candidate evidence / limitation |
| --- | --- |
| BUG-001 | Six original count-10 frames and latest overnight frame read 10; full native Golden wins |
| BUG-002 | Eight archived native camera failures replayed through actual alignment guard; two direct binds, six single guarded corrections in input recorder. Native strict bind and out-of-range/drift rejection proven. Physical effect of the narrow 10-12 px south correction remains unverified. |
| BUG-003 | Both original board-3 sequences pass the actual Ready gate in an offline input recorder; live votes on boards 1, 2 and 4 proven. Fresh exact board-3 event remains unverified. |
| BUG-004 | Native 50-action Golden 10 matches: 34 selection clicks instead of 80, 40 E keys, all ten Scouts L4. |
| BUG-005 | Original severe overlay receipt and fresh native tooltip Victory with 450 Coins verified; normal live Play Again verified. Exact combined tooltip + readable Coin + live Play Again still unverified. Clipped Coin amounts remain uncredited and trigger safe recovery. |
| BUG-006 | Native uncredited direct restart and one guarded client relaunch followed by exact-once 137-Gem credit. |
| BUG-007 | Original wave29/133-Gem receipt now parsed; no improper credit. |
| BUG-008 | Native Gem+XP with expensive Juggernaut deferred and with affordable Scout X1 both earned 137 Gems; three-tower profile now also verified. Original wave29 causality not uniquely established; missed deadline 18 remains a warning in successful matches. |

**No endless random-condition trials.** Use captured-frame regressions for exact historical failures, representative native end-to-end results for integration, and explicit residual-risk labels. If a rare condition is not reproduced within a bounded targeted trial, retain its native-verification gap; do not regenerate identical docs or rerun unchanged tests indefinitely. Never weaken paid-action, terrain, result, focus or stop guards to obtain a passing screenshot.

The candidate is locally packaged and verified, but not released or installed. The hosted runtime candidate passed CI; the subsequent build/documentation changes have only been validated locally. No new commit, push, public release or installation was performed in this review. Finish the [release checklist](PLAN.md) as authorized; do not claim exact rare native coverage or publication without proof. Existing plans for **v1.0** remain planning-only: [loadout switching](plans/2026-11-23-v1.0-loadout-switching.md) and [successful-run rotation](plans/2026-11-23-v1.0-successful-run-rotation.md). See [bug register](../BUGS_FOUND.md), [verification history](verification.md) and [changelog](../CHANGELOG.md). Preserve all existing dirty work and the experimental untracked calibration; runtime captures remain private.
