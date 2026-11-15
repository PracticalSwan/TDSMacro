# TDS Macro

A Windows app for **Golden Scout · Dead Ahead · Survival / Easy / Solo** in Roblox Tower Defense Simulator. It selects the map, prepares an overhead view, places nine Scouts vertically along the path, and repeats successful matches with Play Again.

**[Download the Windows app](https://github.com/PracticalSwan/tds-macro/releases/latest)** · [Setup](docs/setup.md) · [Troubleshooting](docs/troubleshooting.md) · [Verification](docs/verification.md)

![Strategy selector with F1 Start and F2 Stop](docs/images/app.png)

## Start playing

1. Extract the release ZIP. Keep the entire `TDSMacro` folder together.
2. Open `TDSMacro.exe` and choose Golden Scout.
3. Open the TDS lobby with **Golden Scout in slot 1 and slots 2–5 empty**.
4. Press **F1**, then put Roblox in front during the five-second countdown.
5. Keep Roblox focused. **F2 stops**; closing the app also stops its worker. F8/Escape are additional emergency stops.

The app repeats successful matches and displays confirmed progress, wins and coins. **Recover game failures automatically** is enabled by default: a failed game is closed, TDS is reopened and the strategy starts fresh from the lobby. F2 cancels both play and recovery. No separate Python installation is needed.

## Required setup

| Setting | Supported configuration |
|---|---|
| System / client | Windows 11, Microsoft Store Roblox GDK |
| Roblox client area | **1920 × 991 physical pixels, 120 DPI** (125% scaling) |
| Window / language | Windowed, fully visible and foreground; English TDS and local English Windows OCR |
| TDS settings | UI Scale **Large**, vertical upgrades; [full baseline](docs/setup.md#tds-settings-baseline) |
| Game / account | Solo; VIP map selection; Golden Scout only in slot 1 |
| Strategy | Dead Ahead, Survival / Easy; nine Scouts, 44 actions |

The client area excludes title bar/borders. A 1920×1080 display is tested; a “1920×992 window” is not an equivalent measurement. Fullscreen, other sizes/DPI, macOS and mobile are unsupported. Read [setup](docs/setup.md) first.

## Verified behavior and limits

Version 0.2.2 completed a live **7m43s / 450-coin win with all 44 actions confirmed and zero recoveries**. It adds a safer walkway margin and a complete post-vote title crop to the processing improvements, Login Reward claiming and launcher recovery from 0.2.1. See [verification](docs/verification.md) for actual trials, the extended 31-win run that exposed these navigation faults, earlier release evidence and finite test scope.

Cash/prices are read from the game; starting cash is not fixed. Tower identity uses labels and levels rather than skin portraits. Wins with every modifier configuration, no modifiers, or other skins have **not** been established. UI changes may require recalibration.

Uncertain map, pose, resources or action confirmation stops the current attempt. A delayed purchase is observed without clicking again. Recovery starts a new session; manual stop, lost focus, changed geometry, setup/storage errors and the recovery limit stop the run. This unofficial project does not guarantee Roblox/TDS permission or account safety; review the [Community Standards](https://about.roblox.com/community-standards) and [exploiting guidance](https://en.help.roblox.com/hc/en-us/articles/203312450-Cheating-and-Exploiting).

## Contribute

Contributions are **suggestions and new strategies only**. Use the [issue forms](https://github.com/PracticalSwan/tds-macro/issues/new/choose); strategy PRs follow [CONTRIBUTING.md](CONTRIBUTING.md). Core implementation is owner-maintained.

[Build/development](docs/development.md) · [Strategy credit](docs/strategies.md) · [Changelog](CHANGELOG.md) · [Security](SECURITY.md) · [License/notices](NOTICE.md)
