# Setup

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

## First run

1. Extract the whole release ZIP into a writable local folder. Do not run inside the ZIP; keep `_internal`, `assets`, `calibrations`, and `strategies` together.
2. Join the TDS lobby. Complete one-time Easy tutorials/dialogues manually before repeated games. The macro checks Login Rewards, claims an available reward once and closes an already-claimed popup when needed.
3. Equip Golden Scout in slot 1 and empty the other slots. The macro confirms Scout/Golden labels in Items. The tested skin is Intern; portrait changes have automated coverage, but other skins need live trials.
4. Use default camera/keyboard controls, English UI and the TDS settings below. Keep normal HUD and tower prices/levels visible. Do not change camera/UI scale during play.
5. Open TDSMacro.exe, choose Golden Scout and press F1. Put Roblox in front during the five-second countdown. Do not move the mouse, character or camera while it plays.
6. Observe a full match and replay on your account. Stop if settings, modifiers or network conditions produce a defeat or unexplained behavior.

The macro selects an existing Dead Ahead board or uses VIP, then confirms its title and solo vote. It prepares an overhead view before every new match. No character movement is needed during tower placement.

Leave the voting-room camera in its default third-person configuration. Navigation checks the stone walkway beside the avatar before moving sideways toward a board. Unusual avatar proportions or a different voting-room camera zoom have not been separately verified and may require calibration.

## Avatar height and camera alignment

Avatar height can affect the view even at the same window size: Roblox scales the body through [HeightScale](https://create.roblox.com/docs/reference/engine/classes/HumanoidDescription#HeightScale), positions the rig above the floor through [HipHeight](https://create.roblox.com/docs/reference/engine/classes/Humanoid#HipHeight), and defines camera zoom relative to the character. See the [camera documentation](https://create.roblox.com/docs/workspace/camera). The implication for this macro is a possible change in the apparent ground scale or position; it does not establish the behavior of every TDS avatar.

The macro checks actual terrain rather than assuming a particular avatar height. Before Ready, with zero towers confirmed, a matching scene with a small centered scale difference can receive at most six fine zoom steps. Placement still requires the original strict pose check. Unknown terrain, a displaced/rotated view or an exhausted adjustment budget stops setup. Retained-camera restarts only verify the pose and never adjust it.

The owner's existing avatar is unchanged. TDS Character Scale is not required or purchased. Different Roblox bundles/heights and the paid TDS scale option still require separate live trials; a safe rejection is preferable to placing at an unverified position.

## During play

F2 requests a stop at any time. F8 is the worker's queued emergency stop; Escape is also checked. Held inputs are released on exit. App close stops its worker. Switching focus away from Roblox also stops the run; it never refocuses.

Play Again continues only while each result, reward and next state is confirmed. With **Recover game failures automatically** checked (the default), defeat, disconnect, failed actions or unreadable game state end the current attempt. After a five-second cancellable countdown, the worker closes Roblox, handles the recognized Close Roblox confirmation if present, waits for that process to exit, then allows 60 seconds for the Store launcher to settle before opening TDS once through its official launch link. It accepts a supported foreground lobby or Login Rewards screen, binds the new window and starts the full lobby/loadout/map/camera checks again. It never repeats an uncertain purchase in the old game.

The Login Rewards check runs on each lobby entry. Two consecutive exact Claim readings on the green button authorize one guarded claim click. The popup may close automatically; otherwise the macro waits for grey Close before dismissing it once. An already-claimed Close screen is dismissed directly. An unreadable or delayed claim is never clicked again. An ordinary lobby skips reward input.

F2, F8/Escape, app close, focus loss, geometry changes, setup/storage errors and pause cancel recovery. There is no automatic refocus or force termination. A close timeout or unreadable reopened lobby stops. At most three automatic relaunches are allowed without a confirmed win; a win resets that consecutive-failure limit. Uncheck recovery before F1 to stop on the first game failure instead.

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
