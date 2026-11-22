TDS Macro - Windows v0.3.1

**NATIVE UPDATE — 2026-11-22 ICT, three-tower frozen GUI verified:** Frozen candidate `dist/v031-hardcore-three-tower-count18-fix-20261122/TDSMacro` on TDS v2.20.3, session `app_20261122_131050_068517`, first fresh Solo Wretched Front cycle: **75/75 ordered confirmed actions**, **18 tower placements**, exact end levels **10 Farms L3 + 3 Boomerangs L4 + 5 Crook Bosses L3**, wave-30 natural Defeat, **137 Gems displayed**, no optional XP tower and **0 recoveries**. An independent file audit checked all 75 monotonic action IDs and `result.json`, SHA-256 `afa6038d3266c297b8b896ca4da182bd0f808ee7ef379be10c2c498a61935056`. The game displayed the result, not an independently audited wallet deposit. Direct Restart Match proceeded to **cycle 2** in the same continuous frozen worker (at least nine separately confirmed actions), still running when checked. Full source **626/626** tests, compile and diff checks passed; frozen --self-check and packaged game asset/pinned plan hashes matched. Keep max-three bounded auto-recovery and exact pre-action safety checks. Public v0.3.1 release and hosted CI remain pending until reviewed Git commit, clean package/privacy checks, and verified CI; current run is not proof of infinite failure-free behavior.


Keep TDSMacro.exe, _internal, assets, calibrations, strategies and docs
together in the extracted folder. Do not run it inside the ZIP.

Choose a strategy in the Overview tab, then press Start or F1.
F2 stops safely; F8 and Escape are emergency stops. Do not send
other Roblox inputs or change game focus while the macro is running.

Golden Scout (nine-tower fallback):
  Original Dead Ahead / Easy / Solo nine-Scout strategy (44 actions).
  Preserved from the previous release. The older camera calibration
  may not match later game updates.

Golden Scout (ten maximum-level Scouts):
  Native-tested v2.20.3 profile, Dead Ahead / Easy / Solo.
  Requires Golden Scout in slot 1 and slots 2-5 empty.
  Ten placements and forty E-key upgrades, individually verified.
  Native win and repeat evidence: see docs/verification.md.
  The app stops if the current terrain, position, cash, selected
  Scout or upgrade quote cannot be positively verified.

Hardcore Gem Grind:
  Wretched Front / Hardcore / Solo; Boomerang slot 1, regular
  Crook Boss slot 2, Farm slot 3, slot 5 empty.
  For the current three-tower GUI run, leave slots 4 AND 5 empty.
  Three-tower source guards include native-tested v2.20.3 route
  checkpoints and a corrected exact 18/40 HUD text template.
  A complete new 75-action GUI result is pending verification.
  An optional evolution tower may be placed in slot 4 once,
  without upgrades, only when its exact tooltip is verified.
  Its exact price must be readable between $200 and $10,000.
  Price/cash are checked again before purchase. Unknown or
  unaffordable prices skip the optional tower; core 75 actions
  continue. No price is assumed from tower name or icons.
  Native v2.20.3 optional Minigunner: 76/76 actions, wave30,
  137 Gems and +106 tower XP displayed in result screenshot.
  XP is not guaranteed by mere equipment; the tower must remain
  placed at match end. No wallet/XP credit claim without evidence.

Auto Equip is disabled because the observed game UI does not expose
five independently text-proven EMPTY slots. Equip towers manually.
The macro never guesses slot occupancy from graphical tiles.

The Diagnostics tab shows bounded, sanitized, read-only status
and recent events. Copy or export only when you choose. Logs
and gameplay captures remain private in local captures/runs.
Never upload account screenshots or raw logs to public issues.

English TDS, Windows 11, Store Roblox, a foreground client area
EXACTLY 1920x991 at 120 DPI and the calibrated UI are required.
On uncertain input, camera, network, or UI states the macro stops.
It does not repeat uncertain paid clicks or upgrades.

Read docs/setup.md, docs/APP.md and docs/troubleshooting.md
for installation, status meanings and recovery guidance.
