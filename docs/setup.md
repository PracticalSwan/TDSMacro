# Setup — TDS Macro Windows

Install the **complete** [v0.5.3 Windows ZIP](https://github.com/PracticalSwan/TDSMacro/releases/tag/v0.5.3); do not run just the EXE. Keep `TDSMacro.exe`, `_internal/`, `assets/`, `calibrations/`, `strategies/`, docs and notices together. The maintainer's installed version is `dist/TDSMacro/` with one `TDS Macro.lnk` Desktop shortcut. The latest verified previous installation is retained for rollback; older non-runtime diagnostic evidence is archived privately rather than retained as duplicate executable installations.

## Required computer and game setup

| Setting | Required / tested |
| --- | --- |
| OS and game client | Windows 11 x64; **official Microsoft Store Roblox GDK** |
| Client view | **1920×991 physical client pixels, 120 DPI** (typically 1920×1080 screen at 125% scaling), fully visible **windowed** |
| Language/OCR | English Roblox/TDS; local English Windows OCR available |
| TDS settings | **UI Scale Large**, **Prefer vertical upgrades On**, fixed default keybinds, no changed HUD/camera during gameplay |
| Gameplay | **Solo**, supported map and difficulty, normal **1×** speed |
| Account | Own required towers, active Golden perk where selected, permitted map access including VIP for Golden Dead Ahead voting, available group/skill bonuses as applicable |
| Concurrent control | Exactly one foreground Roblox client and **one** TDS Macro worker/input controller |

The client area is not the decorated window size. Fullscreen, resized/restored unknown geometry, alternative DPI and unsupported UI scale are not calibrated. The macro verifies focus/window identity/geometry before sending input. New avatars, skins, camera states and game updates may require separate evidence/recalibration.

## TDS settings baseline

The previously native-tested owner setup uses:

| Setting | Value |
| --- | --- |
| Skills Enabled | On |
| Camera shake / Dialog | Off / Off |
| Auto Skip | On |
| Hide Suggestions / Hide tower rings | Off / Off |
| Show nametags / flair / tower pets | Off |
| Show currency drops / shadows | Off |
| Equip tower pets | Off |
| HQ explosions / effects | Off |
| Particle LOD / Show tower options | On / On |
| Always display tower buffs | Off |
| Prefer vertical upgrades | **On** |
| Bullet trails / Low quality rings | Off |
| UI Scale | **Large** |

Different configurations are **not automatically validated**, particularly if Skills Enabled is Off. Golden Scout's active Golden perk and initial cash must be confirmed, and Hardcore Economy skills can determine whether the opening is affordable.

## Exact loadouts

| Strategy | Tower slots | Starting affordability |
| --- | --- | --- |
| Golden Scout — 10 Max | **1 Scout with Golden perk**, 2–5 empty | First placement currently **$250**; Easy baseline can cover it, later upgrades still depend on live income |
| Golden Scout — 9 fallback | Same | Same first placement, separate 44-step calibration |
| Hardcore Gem Grind — 3 Towers | **1 Boomerang; 2 regular Crook Boss; 3 Farm; 4–5 empty** | Four $300 Farms **before Ready**: need **≥$1,200 observed cash** |
| Hardcore Gems + Tower XP — Slot 4 | Same 1–3; **4 supported verified XP tower** (Juggernaut proven); **5 empty** | Same $1,200 opening; optional X1 requires exact observed price $200–$10,000 and sufficient surplus after reserving the next verified core-upgrade quote |

**Auto-Equip is disabled**. Change loadouts manually in Roblox inventory before starting, and confirm the intended slot ordering/empty slots and Golden perk. The macro rejects unreadable names or unsupported extra towers. Do not assume all accounts and skill combinations can run Hardcore: see [per-strategy requirements](requirements/strategies/README.md).

## Start

1. Open the official Roblox TDS experience and enter its lobby. Finish any tutorials/overlays manually. The macro recognizes supported Login Rewards conditions.
2. Equip the selected five-slot loadout. Keep camera controls/default keybinds and Solo map/mode available. A nonstandard avatar height or camera pose may fail terrain recognition.
3. Launch `TDSMacro.exe`; in **Run setup** select the matching strategy and leave recovery enabled if desired. Press **Start run / F1**.
4. Do not touch Roblox, move the cursor over game OCR regions, show interfering overlays or change its focus while the worker owns it. Observe the GUI status/logs passively.
5. **F2** requests a safe stop; **F8/Escape** emergency stops. Closing the GUI requests worker stop. A stopped run does **not** resume automatically after an update.

The map and camera are checked before placement. The Golden strategy uses separate Dead Ahead overhead calibration; Hardcore uses one pinned Wretched Front RIGHT→DOWN→LEFT route and final strict terrain check. Unknown/changed terrain stops the worker rather than trying alternate routes.

## Recovery and limitations

- An enabled recovery option permits bounded official client relaunch after verified game failures. The worker must positively identify the same Roblox client; recognized disconnect dialogs are clicked only after exact-text checks. The worker never force-kills, steals focus during play or resumes an uncertain spent action.
- A foreground interruption releases input; any short natural return must be verified before a **fresh session** is started. Persistent focus loss, changed geometry/window identity, manual stop, setup/storage errors or exhausted recovery budget stop safely. At most **two** verified direct replays and **three** guarded relaunches without a credited success; relaunch requires the recovery option.
- Result-screen Coins/Gems are displayed rewards, **not** independently audited wallet credit. A wave-30 natural Defeat with 137 Gems is intentional for Hardcore Gem farming. Optional tower placement does not by itself establish a numerical Tower XP award.
- Modifiers/challenges and alternate player counts are outside the currently verified strategy set. Do not enable them without a separate native trial.

Private `captures/`, logs and session results live alongside the installed app and may contain account information. Keep them out of Git, public issues and release archives.

[Windows app guide](APP.md) · [Troubleshooting](troubleshooting.md) · [Project status](STATUS.md) · [Verification](verification.md) · [v1.0 plans, not implemented](PLAN.md)
