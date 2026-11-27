# TDS Macro Windows application

**Published stable:** [v0.5.3](https://github.com/PracticalSwan/TDSMacro/releases/tag/v0.5.3). The installed maintainer candidate is v0.5.5 at `dist/TDSMacro/TDSMacro.exe` with one `TDS Macro.lnk` shortcut. For a timestamped live observation, see [project status](STATUS.md); never infer the worker is still running from this page alone.

## GUI

The main **Strategy dashboard** has **Run setup** (strategy, loadout summary, recovery checkbox, Start) and **Live session** (status, confirmed actions/wave, Gems/Coins and recovery count). **Diagnostics** and **Updates** are separate header windows. The dashboard reports the worker's stop reason or exit code, rather than showing an idle/ready state after a failed launch.

The released dashboard reports an uncredited result and the two direct replay attempts separately from credited wins and Gems. Automatic recovery still requires its checkbox. See [verification](verification.md) for released evidence and residual limits.

| Strategy | Verified loadout | Expected result |
| --- | --- | --- |
| Golden Scout — 10 Max | Golden Scout slot 1; slots 2–5 empty | 10 level-4 Scouts, 50 actions, Easy Solo Dead Ahead wave-20 Victory and displayed Coins |
| Golden Scout — 9 fallback | Same slots/perk | Nine Scouts, 44 actions, Easy Solo Dead Ahead Victory |
| Hardcore Gem Grind — 3 Towers | Boomerang / **regular** Crook Boss / Farm / empty / empty | 75 core actions, wave-30 natural Defeat, 137 Gems displayed |
| Hardcore Gems + Tower XP — Slot 4 | Same three + verified eligible XP tower in slot 4; slot 5 empty | Natural wave30 Gem result; optional slot-4 placement counted separately from actual XP |

Consult [strategy requirements](requirements/strategies/README.md) before enabling a different account or perk configuration. **Auto-Equip is unavailable:** equip manually. Golden Scout needs an active Golden perk, not merely a gold-themed portrait. Hardcore needs **at least $1,200 observed initial cash** for four pre-Ready Farms. Low-skill multi-account compatibility is not established.

## Planned v1.0: explicit slot-4 tower selection

For Hardcore Gems + Tower XP only, the future read-only dropdown will choose an exact, native-qualified tower/variant profile, update the five-slot summary and show the observed base cost. The initial proposed choices are Juggernaut and Golden Scout (exact Golden perk proof required); Minigunner has older native evidence for later requalification. This replaces generic slot-4 discovery/price polling for planning, not live purchase safety. Selection does not equip a tower; verified manual setup or an independently accepted preset switch is still required. Disabled during a run. See [slot-4 plan](plans/2026-11-25-v1.0-slot4-tower-selection.md). Not implemented in v0.5.2.

## Start, stop, recovery

1. Launch Roblox Tower Defense Simulator in the supported Store GDK client, with English UI and the [required screen/game settings](setup.md). Return to the lobby and equip the exact required slot order.
2. Select the strategy in Run setup. The GUI performs setup/foreground preflight and starts the single guarded worker with **Start / F1**.
3. Keep Roblox foreground, visible, at the calibrated geometry. **Stop safely / F2** requests a stop; **F8 / Escape** is the emergency stop. App close also requests stop. Do not send competing game input while a worker is active.
4. With **Recover game failures** selected, the worker can close/relaunch only its verified original client and restart from a confirmed lobby under the **maximum three guarded relaunches without a credited success** policy. Continuous mode may first use up to two positively verified direct replays; only a credited result resets both budgets. In the v0.5.5 candidate, for a foreground interruption, the supervisor waits 30 seconds; if the same verified client remains backgrounded on an unattended desktop, it may request foreground once and require two matching samples before fresh-session recovery. Active desktop, denied activation, uncertain purchase, process change or invalid UI remains a safe stop.

Coins and Gems totals come from **verified result-screen receipts**, not a wallet audit. `xp_placement_cycles` confirms optional tower placements in credited Gem matches, **not the numerical Tower XP reward**.

## Updates and diagnostics

- Automatic updates are **OFF by default**. Use **Updates → Check now** for a manual stable-release check. Opt-in automatic checks use only official GitHub stable releases. Verified ZIP/checksum and frozen self-check are required.
- Updates cannot replace an installation while a worker is active. Previous installations and private captures are preserved for rollback, and the new GUI starts **idle**; the updater never silently resumes farming.
- Diagnostics display sanitized report fields and selected events, with Copy and Export .txt. Full `captures/runs/` logs, screenshots and session data may contain account details; **never publish raw captures**.
- A running worker's exact state is in its newest `captures/runs/<session>/status.json`; a terminal `result.json` and per-match receipts explain previous successes/stops. Confirm the actual PID/parent and status timestamps before decisions.

## Building and testing (maintainers)

From the Windows repository root with its project environment installed:

```powershell
.\scripts\build-app.ps1 -Destination 'dist\new-review-build'
```

The builder refuses to overwrite an existing destination. A frozen self-check validates packaged strategy/calibration data, local OCR and Tcl, but **does not prove native gameplay**. Release gates also require the full relevant source regression, Tk GUI smoke, privacy/package review, hosted Windows CI, native current-client result/restart and verified official release artifact/install.

[Setup](setup.md) · [Troubleshooting](troubleshooting.md) · [Verification history](verification.md) · [Changelog](../CHANGELOG.md) · [v1.0 plans (not implemented)](PLAN.md)

## v1.0 consolidation (planning only)

The [consolidation plan](plans/2026-11-25-v1.0-legacy-consolidation.md) evaluates retiring Golden 9 and obsolete preparation-only paths after native parity and explicit migration checks. The released selector and all four strategies remain unchanged; loadout switching, rotation and slot-4 selection are not implemented.
