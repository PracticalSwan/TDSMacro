# Setup

**FINAL OWNER v0.3.1 DECISION (2026-11-21 17:44 ICT; supersedes earlier conditional OCR proposals):** **Remove automatic game-version OCR completely, now.** v0.3.1 must use **one fixed Wretched Front candidate route**, never select or retry routes from version text and never perform even one-time version detection. It is still **NOT an accepted route** until the native proof of **RIGHT onto rock tops → DOWN across the pale/white boulder beside the old gate → DOWN ends ON path → LEFT to original placement pose**, plus two fresh-spawn guarded repetitions and unchanged three-rock camera/drift checks. Terrain mismatch, lost foreground/client identity, unknown Ready/zero-tower state or failed placement checks must stop; non-version gameplay OCR stays. The candidate source has removed version-OCR route dispatch; **no live match, optional XP, final build, CI or release success is claimed**. This instruction now authorizes implementation and native calibration in separate guarded batches, not weakening safety or changing published v0.3.0.

**v0.3.1 navigation plan (2026-11-21 15:49 ICT; not currently supported):** The new Hardcore entry is **RIGHT onto rock tops from spawn → DOWN on top of the white/light boulder beside the earlier gate → DOWN ends on the path → LEFT to the original placement pose**. Do not manually infer or substitute directions from the earlier outside-edge probe. Only a native-accepted configured route may eventually dispense with automatic route-version OCR; until accepted, use at most a verified one-time-per-client version check if needed and stop on unknown terrain. This is documentation only; no playable route or executable was changed. Refer to [execution checkpoints](plans/2026-11-21-v0.3.1-execution-checkpoints.md).

**v0.3.1 setup status (November 21, 2026; source candidate only):** Equip towers manually. Auto Equip is unavailable on the current TDS inventory because five positive EMPTY labels cannot be verified, and the disabled GUI checkbox cannot launch it. Hardcore uses Boomerang (slot 1), regular Crook Boss (slot 2), Farm (slot 3), optional evolution tower (slot 4), and empty slot 5; exact Search + UNEQUIP and in-match tooltips govern tower identity and order. A fourth tower must be positively named before the one bounded phase-12 placement attempt (historical wave 24-26); actual placed-until-result XP evidence is still missing. Golden 10 Scouts/L4/E has three v2.20.2 victories; new-game v2.20.3 compatibility remains unverified. The v2.20.3 Hardcore middle route is not repeatable from fresh spawn, and right-flank recalibration is pending. Published v0.3.0 remains last stable. See [execution checkpoints](plans/2026-11-21-v0.3.1-execution-checkpoints.md).



Current 2.20.0 UI note: Play may open the Survival grid directly; Equip text and slot rows vary with the selected tower. Only use a build positively verified for the current UI. If menu/slot recognition stops, do not guess or repeat input. Preserve the required 1920x991 at 120 DPI and exact required equipment.

**Local maintainer install, November 21, 2026:** The v0.3.0 release ZIP was verified and promoted to dist/TDSMacro; the prior v0.2.4 installation was moved intact to dist/TDSMacro-previous-v0.2.4-20261121. Desktop shortcuts TDS Macro v0.2.3, v0.2.4 and v0.3.0 point to their respective preserved versions. The installed v0.3.0 self-check and GUI launch/close passed. These local paths are not part of the public release download.

**v0.3.0 strategies:** The Windows release includes the original nine-Golden-Scout Dead Ahead Solo/Easy strategy and the new Hardcore Gem Grind Wretched Front Solo strategy. The requested ten-Golden-Scout revamp remains reserved for v0.3.1. Hardcore's 10-match real-game acceptance passed on November 20 with 75 confirmed actions and a natural wave-30 137-displayed-Gem result in each match. Result-screen rewards do not independently prove wallet credit.

**Hardcore setup:** Equip regular Boomerang in slot 1, regular Crook Boss in slot 2, and Farm in slot 3. Slot 5 must be empty; optional slot 4 is accepted only if independently verified and calibrated. Use normal 1× speed, English TDS and the same supported 1920×991/120-DPI foreground client. The fixed 14-phase plan targets 10 Farms level 3, 3 Boomerangs level 4 and 5 Crook Bosses level 3. After exactly 75 confirmed actions and a wave-30 natural result displaying 137 Gems, the unattended worker uses the in-game **Restart Match** button. It does not visit the lobby or poll the player-list cash/wallet between successful results; the displayed rewards are not independently audited wallet deposits. If Roblox disconnects (including error 277), the camera becomes unreadable, or a purchase cannot be verified, the worker stops rather than guessing. See [Hardcore strategy](strategies.md) and [verification status](verification.md).

The following baseline table and first-run steps focus on Golden Scout. Hardcore requires the separate loadout and map listed above, with the same calibrated Roblox window and TDS settings.

Match this measured configuration before pressing F1.

| Requirement | Value |
|---|---|
| OS / client | Windows 11 x64, Microsoft Store Roblox GDK |
| Physical client area | **1920×991 pixels, 120 DPI** (125% scaling) |
| Display tested | 1920×1080; maximized windowed Roblox |
| UI / OCR | English TDS; local English Windows OCR available |
| Game | Survival → Easy → Solo; Dead Ahead |
| Account | VIP map selection access; Golden Scout perk equipped |
| Loadout | Scout slot 1, slots 2–5 empty; tower hotbar; default shortcuts |

Windows distinguishes the client area from the outer window and scales logical coordinates according to DPI. This app uses physical client pixels and checks actual DPI. See Microsoft's [window description](https://learn.microsoft.com/en-us/windows/win32/winmsg/window-features) and [DPI explanation](https://learn.microsoft.com/en-us/windows/win32/learnwin32/dpi-and-device-independent-pixels).

Maximized windowed mode at the tested display/scaling produced 1920×991. A restored window is acceptable only if the measured client size and DPI are exactly the same, fully on-screen and unobscured; that restored configuration has not been separately tested. Fullscreen and 1920×992 clients are unsupported. Moving/resizing the window during a run stops it. Do not change global display settings just to bypass a check.

From source, inspect geometry without input:

```powershell
.\.venv\Scripts\python.exe src\tds_auto\phase1.py inspect
```

The worker reports actual versus required geometry if they differ. Other monitor arrangements, DPI values and resolutions need new calibration and live verification. Automatic coordinate scaling is absent.

## Opening the installed Windows app

Use the complete [current Windows release](https://github.com/PracticalSwan/tds-macro/releases/latest), not a lone executable from an older build. Extract the ZIP to a writable local folder; `TDSMacro.exe`, `_internal/`, `assets/`, `calibrations/`, and `strategies/` must stay together. A desktop shortcut must point to that executable **and** use its containing folder as the working directory. If no GUI appears, inspect Alt+Tab/taskbar first: the app may have opened behind another window. See [troubleshooting](troubleshooting.md#application-does-not-open-or-appear).

**Maintainer's local installation (2026-11-18):** `dist/TDSMacro/` now contains the verified v0.2.4 package (EXE SHA-256 `51edd086a7208cd698c72ff59d94813b9a6feb17459c573851718aa3f065c482`). The previous v0.2.3 install, including its private captures, is archived at `dist/TDSMacro-previous-v0.2.3-20261118/`. A new `TDS Macro v0.2.4.lnk` desktop shortcut targets the current standard directory; the older v0.2.3 shortcut targets the archived version. This replaces the historical v0.2.3 local-install checkpoint from 2026-11-16 without deleting its evidence. These ignored local paths and shortcuts are **not included in the public release ZIP** and do not imply a new gameplay run. No global display-scaling change is needed to open the GUI.

**v0.3.0 GUI preflight:** before starting a worker, the GUI may make one ordinary foreground request for an already located Roblox client, then verifies the same supported window on two reads and a clean native capture before handing its anchor to the worker. For setup, use the official Roblox experience page; if browser Play fails or the client is closed, the approved native launcher path is the fallback. Recognized disconnect recovery remains guarded and bounded. This behavior is not present in the published v0.2.4 executable.

## First run

1. Extract the whole release ZIP into a writable local folder. Do not run inside the ZIP; keep `_internal`, `assets`, `calibrations`, and `strategies` together.
2. Join the TDS lobby. Complete one-time Easy tutorials/dialogues manually before repeated games. The macro checks Login Rewards, claims an available reward once and closes an already-claimed popup when needed.
3. Equip Golden Scout in slot 1 and empty the other slots. The macro confirms Scout/Golden labels in Items. The tested skin is Intern; portrait changes have automated coverage, but other skins need live trials.
4. Use default camera/keyboard controls, English UI and the TDS settings below. Keep normal HUD and tower prices/levels visible. Do not change camera/UI scale during play.
5. Open the official TDS experience. If browser Play fails, use the project's official native launcher fallback; verify the supported client and stable lobby before starting. Open TDSMacro.exe, choose Golden Scout and press F1. The published v0.2.4 executable requires Roblox in front before F1; the v0.3.0 source candidate can make one verified pre-start foreground request. ChatGPT Computer Use (CUA) is permitted for setup, observation or other desktop tasks **only while non-interfering** with OCR, screen captures, game focus and the macro. During a macro run, CUA must remain passive and must not send Roblox input, move its cursor over game recognition regions, show a blue-cursor effect that contaminates captures, or change focus. A failing native controller guard still blocks startup; do not bypass it, and resolve interference before retrying.
6. Observe a full match and replay on your account. Stop if settings, modifiers or network conditions produce a defeat or unexplained behavior.

The macro selects an existing Dead Ahead board or uses VIP, then confirms its title and solo vote. It prepares an overhead view before every new match. No character movement is needed during tower placement.

Leave the voting-room camera in its default third-person configuration. Navigation checks the stone walkway beside the avatar before moving sideways toward a board. Unusual avatar proportions or a different voting-room camera zoom have not been separately verified and may require calibration.

## Avatar height and camera alignment

Avatar height can affect the view even at the same window size: Roblox scales the body through [HeightScale](https://create.roblox.com/docs/reference/engine/classes/HumanoidDescription#HeightScale), positions the rig above the floor through [HipHeight](https://create.roblox.com/docs/reference/engine/classes/Humanoid#HipHeight), and defines camera zoom relative to the character. See the [camera documentation](https://create.roblox.com/docs/workspace/camera). The implication for this macro is a possible change in the apparent ground scale or position; it does not establish the behavior of every TDS avatar.

The macro checks actual terrain rather than assuming a particular avatar height. Before Ready, with zero towers confirmed, a matching scene with a small centered scale difference can receive at most six fine zoom steps. Placement still requires the original strict pose check. Unknown terrain, a displaced/rotated view or an exhausted adjustment budget stops setup. Retained-camera restarts only verify the pose and never adjust it.

The owner's existing avatar is unchanged. TDS Character Scale is not required or purchased. Different Roblox bundles/heights and the paid TDS scale option still require separate live trials; a safe rejection is preferable to placing at an unverified position.

## During play

F2 requests a stop at any time. F8 is the worker's queued emergency stop; Escape is also checked. Held inputs are released on interruption. App close stops its worker. Losing Roblox foreground immediately stops input and abandons that attempt. The v0.3.0 source candidate can focus Roblox only before worker launch; it never reactivates the client during a run.

With automatic recovery enabled, the worker passively waits up to **five seconds** for the same Roblox window to return to foreground naturally. Two observations must confirm the original process, window, position, size and DPI. A verified return starts the normal fresh-session recovery below; it never resumes the interrupted placement or purchase. If focus stays elsewhere, or the window changes or becomes unverifiable, the run stops without closing or reopening Roblox. A notification that leaves foreground unchanged has no effect. Disable recovery before F1 to stop immediately on any focus loss.

Play Again continues only while each result, reward and next state is confirmed. With **Recover game failures automatically** checked (the default), defeat, disconnect, failed actions or unreadable game state end the current attempt. After a five-second cancellable countdown, the worker closes Roblox, handles the recognized Close Roblox confirmation if present, waits for that process to exit, then allows 60 seconds for the Store launcher to settle before opening TDS once through its official launch link. It accepts a supported foreground lobby or Login Rewards screen, binds the new window and starts the full lobby/loadout/map/camera checks again. It never repeats an uncertain purchase in the old game.

The Login Rewards check runs on each lobby entry. Two consecutive exact Claim readings on the green button authorize one guarded claim click. The popup may close automatically; otherwise the macro waits for grey Close before dismissing it once. An already-claimed Close screen is dismissed directly. An unreadable or delayed claim is never clicked again. An ordinary lobby skips reward input.

F2, F8/Escape, app close, persistent focus loss, identity/geometry changes, setup/storage errors and pause cancel recovery. An invalid loadout stops after bounded verification; correct it before F1 again. A session evidence-write failure is a storage stop. Recovery may launch only through the official native path after the verified client exits; it never force-terminates or refocuses a changed client. A close timeout or unreadable reopened lobby stops. At most three automatic relaunches are allowed without a confirmed win; a win resets that consecutive-failure limit. Uncheck recovery before F1 to stop on the first game failure instead.

Modifier selection is deferred until the required challenges are unlocked. This release retains the existing strategy and does not configure modifiers. Committed + Limitation + Hidden Enemies + Glass is a future target requiring separate UI and win/reward verification. Current account settings can affect results; no four-modifier win or reward boost is claimed.

Local status, results, logs and screenshots are saved under `captures` beside the app. They can contain account information and are private by default. Do not upload that folder.

## TDS settings baseline

The owner supplied this configuration for release verification. Other combinations have not been fully exercised; UI Scale and upgrade layout directly affect coordinates/recognition.

| Setting | Value |
|---|---|
| Skills Enabled | On |
| Camera shake | Off |
| Dialog | Off |
| Auto Skip | On |
| Hide Suggestions | Off |
| Hide tower rings | Off |
| Show nametags / Show flair / Show tower pets | Off |
| Show currency drops / Show shadows | Off |
| Equip tower pets | Off |
| HQ explosions / HQ effects | Off |
| Particle LOD | On |
| Show tower options | On |
| Always display tower buffs | Off |
| Prefer vertical upgrades | On |
| Bullet trails / Low quality rings | Off |
| **UI Scale** | **Large** |
