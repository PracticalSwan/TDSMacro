TDS Macro - Windows v0.5.0

Version 0.5.0 adds a separate Wretched Front Hardcore Gems + Tower XP mode.
Choose it only with a known XP tower (such as Juggernaut) equipped in
slot 4; slots 1–3 remain Boomerang, regular Crook Boss, Farm, slot 5 empty.
Slot 4 has a live $200–$10,000 placement quote (Juggernaut: $10,000).
The XP strategy first verifies all protected Farm and combat milestones,
then buys the optional level-0 XP tower when affordable, even if that defers
one or more of the five expensive final upgrades. It never sells/upgrades
the XP tower. Unsafe or unaffordable placements are deferred; Gems count
only after a verified natural wave-30 137-Gem result. The native trial
confirmed 137 Gems plus 106 Juggernaut XP on its result screen.
The normal 3-tower strategy still requires empty slots 4–5.
The only Windows Desktop shortcut is TDS Macro, pointing to the current
standard installation; historical installations stay inside dist.

This patch accepts a strictly bounded, native-tested Wretched Front
map label OCR variant on the Hardcore wave-30 results screen. Other
mode, difficulty, duration, wave, reward and safe-stop guards remain.
The source strategy, tower loadout, route and auto-update controls are
unchanged.

This patch addresses a documented early-Defeat stop after 29 complete
three-tower Hardcore cycles. Two consecutive verified early Defeats may
trigger direct Restart Match; a third consecutive one stops for review.
Early results do not count as complete cycles or full-cycle Gems.
A native wave-11 OCR ambiguity now requires agreement between exact,
independently bounded text crops. Hardcore HUD verification allows up to
7 seconds of passive rereading across wave changes, without any inputs
or guesses; persistent unknown values still stop safely.
The Overview, Diagnostics and Updates GUI defaults to Wretched Front Hardcore Solo.
Updates tab: Automatic updates OFF by default. Enable for official stable
GitHub release checks at startup and every six hours; Check now also works
manually. Download/install are deferred while gameplay is running. Both
GitHub asset digests and SHA256SUMS must agree, the ZIP is validated, and
the new frozen app must pass self-check. The old complete installation is
kept as backup; the replacement GUI starts idle without restarting Roblox.
Equip Boomerang 1, regular Crook Boss 2, Farm 3; leave slots 4 and 5 EMPTY.
Auto-Equip remains disabled. A frozen candidate completed 75/75 actions,
natural wave-30 Defeat, 137 Gems displayed and direct Restart Match.
Displayed Gems are not independently wallet-audited. Client recovery stays
bounded to three relaunches; unknown focus, terrain, prices, purchases,
selected towers or results stop safely.



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
  The corrected frozen GUI baseline completed 75/75 actions and wave-30
  Defeat with 137 Gems displayed, and restarted another match.
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
