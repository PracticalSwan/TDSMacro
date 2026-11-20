# TDS Macro

A Windows 11 macro for **Roblox Tower Defense Simulator**, using screenshot/OCR-verified actions, calibrated positions and strict foreground safeguards. **v0.3.0** supports two Solo strategies.

| Strategy | Mode and map | Required loadout | Actions / result |
|---|---|---|---|
| Golden Scout | Survival Easy · Dead Ahead | Golden Scout slot 1; slots 2–5 empty; VIP map selection | Nine Scouts, 44 actions (existing v0.2.4 behavior) |
| Hardcore Gem Grind | Hardcore · Wretched Front | Boomerang slot 1, regular Crook Boss slot 2, Farm slot 3; slot 5 empty | 18 towers, 75 actions; natural wave 30, 137 Gems displayed |

**Hardcore v0.3.0 live acceptance (November 20, 2026):** Ten consecutive native Solo Hardcore matches passed: **750/750 confirmed actions**, all 18 required towers at final levels in each match, ten natural wave-30 Defeat screens and **1,370 Gems displayed** (137 per match). The worker used the in-game **Restart Match** button between results. These values are confirmed **from result screens only**, not from account-wallet audits, and do not guarantee future matches against game updates or connectivity changes.

The Golden Scout strategy remains unchanged from v0.2.4. The requested tenth Golden Scout and additional maximum upgrades are reserved for **v0.3.1**, not included in v0.3.0.

**[Download Windows release](https://github.com/PracticalSwan/tds-macro/releases/latest)** · [Setup](docs/setup.md) · [Troubleshooting](docs/troubleshooting.md) · [Verification evidence](docs/verification.md)

## Start playing

1. Download and extract the full release ZIP to a writable folder. Keep the executable and its _internal, assets, calibrations, strategies and docs folders together; the executable cannot run alone.
2. Launch the official Microsoft Store Roblox client and join the TDS lobby.
3. Equip the desired strategy's loadout as specified above. Choose **Golden Scout** or **Hardcore Gem Grind** in TDSMacro.exe. The macro rechecks the configured towers before playing.
4. Press **F1** to start. Keep Roblox visible and foreground with the calibrated geometry throughout play. **F2** stops; **F8/Escape** are emergency stops. Closing the app requests a safe stop.
5. The macro chooses the corresponding map and starts an automatically verified match. Hardcore uses the game's **Restart Match** button after an exact qualifying result, without unnecessary lobby wallet polling. Any uncertain purchase, focus change, disconnect or result stops or invokes the bounded configured recovery policy.

For Hardcore, the displayed Gems counter is **not** a wallet balance. Game updates, unusual settings, network interruptions and different camera/display geometry may stop the macro safely. Read [setup](docs/setup.md) before the first run.

## Required setup

| Setting | Supported configuration |
|---|---|
| System / client | Windows 11, Microsoft Store Roblox GDK |
| Roblox client area | **1920 × 991 physical pixels, 120 DPI** (125% scaling) |
| Window / language | Windowed, fully visible and foreground; English TDS and local English Windows OCR |
| TDS settings | UI Scale **Large**, vertical upgrades; [full baseline](docs/setup.md#tds-settings-baseline) |
| Game / account | Solo; VIP required for Golden Scout map selection; Hardcore uses its own Solo loadout |
| Strategy | Golden Scout: Dead Ahead/Easy, 44 actions. Hardcore: Wretched Front/Hardcore, 75 actions |

The client area excludes title bar/borders. A 1920×1080 display is tested; a “1920×992 window” is not an equivalent measurement. Fullscreen, other sizes/DPI, macOS and mobile are unsupported. Read [setup](docs/setup.md) first.

## Verified behavior and limits

The app reads live cash (only the bottom HUD for Hardcore), prices, tower state and results before sending each guarded action. It stops on unknown states, lost foreground, changed identity, unsupported geometry or unconfirmed purchases. Recovery never refocuses Roblox or repeats an uncertain action. **v0.2.4** verified a natural Error 278 disconnect, guarded Leave → Roblox Home → close → relaunch → stable lobby, and a subsequent 44/44-action win. A separate Error 277 recovery stopped because a foreground lobby could not be verified; automatic recovery from that case is **not** established. See [verification](docs/verification.md) for the exact evidence, release checks and unverified boundaries.

Cash/prices are read from the game; starting cash is not fixed. Tower identity uses labels and levels rather than skin portraits. **Modifier selection is deferred pending challenge unlocks.** Committed + Limitation + Hidden Enemies + Glass remains a future target requiring separate win/reward validation. This release retains the existing profile and does not configure modifiers or claim a reward boost. Other modifier combinations and skins still need live trials. UI changes may require recalibration.

Uncertain map, pose, resources or action confirmation stops the current attempt. A delayed purchase is observed without clicking again. Foreground loss immediately releases input. With recovery enabled, the same client must return naturally within five seconds, confirmed twice, before a fresh-session restart; the app never brings Roblox forward. Manual stop/pause, persistent focus loss, changed identity/geometry, setup/storage errors and the recovery limit stop the run. This unofficial project does not guarantee Roblox/TDS permission or account safety; review the [Community Standards](https://about.roblox.com/community-standards) and [exploiting guidance](https://en.help.roblox.com/hc/en-us/articles/203312450-Cheating-and-Exploiting).

## Contribute

Contributions are **suggestions and new strategies only**. Use the [issue forms](https://github.com/PracticalSwan/tds-macro/issues/new/choose); strategy PRs follow [CONTRIBUTING.md](CONTRIBUTING.md). Core implementation is owner-maintained.

[Build/development](docs/development.md) · [Strategy credit](docs/strategies.md) · [Changelog](CHANGELOG.md) · [Security](SECURITY.md) · [License/notices](NOTICE.md)
