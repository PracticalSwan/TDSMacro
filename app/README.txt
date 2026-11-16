TDS Strategy Macro — Windows

Keep this entire folder together. Double-click TDSMacro.exe.
Choose Golden Scout, open Roblox at the TDS lobby, then press F1.
F2 stops the macro. Closing the app also requests a safe stop.
Start gives you five seconds to put Roblox in front.

Supported setup: English TDS, Solo Survival/Easy, Dead Ahead,
Golden Scout only in slot 1, other slots empty, 1920x991 client at 120 DPI.
TDS UI Scale Large, Prefer vertical upgrades on; see docs/setup.md for all settings.
The macro sets the overhead view and uses vertical placements.
It reads current cash and prices. Different modifiers can change results.
Recover game failures automatically is checked by default. A failed game
is closed and TDS reopens into a fresh lobby session. Login Rewards is
checked when present: Claim once if available, or dismiss grey Close.
F2 cancels recovery as well as normal play.
Lost foreground releases input immediately. With recovery enabled, the same
client must return naturally within five seconds (two verified observations)
before a fresh-session recovery. The interrupted strategy never resumes.
Manual stop, persistent focus loss, identity/geometry changes, setup/storage
errors and three relaunches without a win stop the run. No automatic refocus
or force kill. Modifier selection is deferred pending challenge unlocks;
this app does not configure modifiers or claim four-modifier wins.
F8/Escape remain additional emergency stops inside the game worker.

The app runs continuously until stopped. Local progress and results are
saved under captures/runs beside this executable. No account login is stored.
