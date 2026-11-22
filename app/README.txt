TDS Macro - Windows v0.3.1

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
  Three-tower 75-action baseline was verified on game v2.20.0;
  newer game camera layouts may require recalibration.
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
