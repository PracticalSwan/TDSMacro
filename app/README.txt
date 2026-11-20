TDS Macro — Windows v0.3.0

Extract and keep this entire folder together: TDSMacro.exe, _internal,
assets, calibrations, strategies and docs. Do not run directly from a ZIP
or move only the executable. Double-click TDSMacro.exe; use Alt+Tab if
the app window opens behind another program.

Choose ONE strategy in the app, then press F1 to start:
  Golden Scout — Dead Ahead / Survival / Easy / Solo
    Unchanged Golden Scout v0.2.4 behavior: nine Scouts, 44 actions.
    Requires Golden Scout in slot 1, other slots empty, VIP map access.
  Hardcore Gem Grind — Wretched Front / Hardcore / Solo
    Hardcore v0.3.0: Boomerang in slot 1, regular Crook Boss
    in slot 2 and Farm in slot 3, slot 5 empty; no golden towers required.
    Targets ten Farms level 3, three Boomerangs level 4, five regular Crook
    Bosses level 3 (75 confirmed actions). 1x game speed, wave-30 natural
    result with 137 Gems displayed. Ten consecutive real-game matches
    passed November 20 acceptance; game updates may change results.
    After an exact qualifying result, use Restart Match on the same map
    with a fresh camera and zero-tower check. No lobby/wallet polling.

Both strategies require English TDS, Windows 11, Microsoft Store Roblox,
a foreground game client measuring EXACTLY 1920x991 at 120 DPI (125%
display scaling), and the calibrated UI settings in docs/setup.md.
Do not change camera, display scaling, or game UI during a run.

F1 starts the selected strategy. F2 requests a safe stop. F8 or Escape
are additional worker emergency stops. Closing the app requests a stop.
The macro checks focus, window identity, camera, actual bottom-HUD cash
and in-game purchase evidence; it stops on an uncertain action or result.
It never uses the rounded player-list cash for Hardcore purchases.

Normal game errors may trigger bounded official-client recovery, but an
interrupted match never counts as a completed cycle. Roblox network error
277 is external; no software camera adjustment fixes a disconnect.
Only verified natural result-screen rewards count in the displayed Gems
total; the app does not audit Gems credited to the account wallet.

Local evidence is stored under captures/runs next to this executable.
Keep screenshot evidence private; it may contain account or game details.
No Roblox password or session token is stored. For instructions, visit
docs/setup.md and docs/troubleshooting.md in this folder.

Golden Scout's tenth-placement/max-upgrade revamp is reserved for v0.3.1.
It is NOT part of v0.3.0.
