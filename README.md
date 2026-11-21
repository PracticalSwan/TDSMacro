# TDS Macro

**v0.3.1 source candidate (not yet released, November 21, 2026):** The ten Golden Scouts v2.20.2 profile completed three independently verified 50-action, ten-Level-4, wave-20 Victories (150/150 guarded actions and 1,350 Coins displayed in result screens). The GUI includes Overview/Diagnostics tabs, privacy-filtered local diagnostics, and an Auto Equip checkbox that defaults **OFF**. Auto Equip deliberately stops when the current inventory lacks five explicit EMPTY labels; it has **not** passed a real-game auto-equip acceptance. Hardcore's optional user-equipped slot-4 evolution tower pathway is implemented in source but its v2.20.1-v2.20.3 Wretched Front terrain route has **not** been accepted. Do not infer tower XP, current Hardcore reliability, or v0.3.1 publication from source-only evidence. [Current checkpoints](docs/plans/2026-11-21-v0.3.1-execution-checkpoints.md).

**Latest published stable release: v0.3.0.** Its three-slot Hardcore baseline reached ten consecutive wave-30 results on game v2.20.0, before subsequent TDS UI/camera changes. The published ZIP contains the nine-Scout Golden fallback; current source changes and the v2.20.2 profile are not yet part of that download.

A Windows 11 macro for **Roblox Tower Defense Simulator**, using screenshot/OCR-verified actions, calibrated positions and strict foreground safeguards. Published v0.3.0 supports two Solo strategies; the unreleased v0.3.1 source adds the ten-Scout candidate and optional Hardcore slot 4.

| Strategy | Mode and map | Required loadout | Actions / result |
|---|---|---|---|
| Golden Scout fallback | Survival Easy · Dead Ahead | Golden Scout slot 1; slots 2–5 empty; VIP map selection | Nine Scouts, 44 actions (published v0.3.0) |
| Golden Scout ten-tower candidate | Survival Easy · Dead Ahead | Golden Scout slot 1; slots 2–5 empty; VIP map selection | Ten Scouts all level 4, 50 actions; three native v2.20.2 Victories (v0.3.1 candidate only) |
| Hardcore Gem Grind | Hardcore · Wretched Front | Boomerang slot 1, regular Crook Boss slot 2, Farm slot 3; slot 4 empty for the verified baseline or optional evolution tower for v0.3.1 source; slot 5 empty | Baseline: 18 towers/75 actions, wave 30 and 137 Gems displayed on v2.20.0. Optional slot 4 adds one guarded placement, not yet validated on current game. |

**Hardcore v0.3.0 live acceptance (November 20, 2026):** Ten consecutive native Solo Hardcore matches passed: **750/750 confirmed actions**, all 18 required towers at final levels in each match, ten natural wave-30 Defeat screens and **1,370 Gems displayed** (137 per match). The worker used the in-game **Restart Match** button between results. These values are confirmed **from result screens only**, not from account-wallet audits, and do not guarantee future matches against game updates or connectivity changes.

The **published v0.3.0** Golden Scout strategy remains unchanged from v0.2.4. The ten-Scout E-key extension is included in the **unreleased v0.3.1 source**, not the public v0.3.0 executable.

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
| Strategy | Published Golden fallback: 44 actions. v0.3.1 source candidate: 50 actions. Hardcore baseline: 75 actions; slot-4 candidate adds one placement. |

The client area excludes title bar/borders. A 1920×1080 display is tested; a “1920×992 window” is not an equivalent measurement. Fullscreen, other sizes/DPI, macOS and mobile are unsupported. Read [setup](docs/setup.md) first.

## Verified behavior and limits

The app reads live cash (only the bottom HUD for Hardcore), prices, tower state and results before sending each guarded action. It stops on unknown states, lost foreground, changed identity, unsupported geometry or unconfirmed purchases. Recovery never refocuses Roblox or repeats an uncertain action. **v0.2.4** verified a natural Error 278 disconnect, guarded Leave → Roblox Home → close → relaunch → stable lobby, and a subsequent 44/44-action win. A separate Error 277 recovery stopped because a foreground lobby could not be verified; automatic recovery from that case is **not** established. See [verification](docs/verification.md) for the exact evidence, release checks and unverified boundaries.

Cash/prices are read from the game; starting cash is not fixed. Tower identity uses labels and levels rather than skin portraits. **Modifier selection is deferred pending challenge unlocks.** Committed + Limitation + Hidden Enemies + Glass remains a future target requiring separate win/reward validation. This release retains the existing profile and does not configure modifiers or claim a reward boost. Other modifier combinations and skins still need live trials. UI changes may require recalibration.

Uncertain map, pose, resources or action confirmation stops the current attempt. A delayed purchase is observed without clicking again. Foreground loss immediately releases input. With recovery enabled, the same client must return naturally within five seconds, confirmed twice, before a fresh-session restart; the app never brings Roblox forward. Manual stop/pause, persistent focus loss, changed identity/geometry, setup/storage errors and the recovery limit stop the run. This unofficial project does not guarantee Roblox/TDS permission or account safety; review the [Community Standards](https://about.roblox.com/community-standards) and [exploiting guidance](https://en.help.roblox.com/hc/en-us/articles/203312450-Cheating-and-Exploiting).

## Contribute

Contributions are **suggestions and new strategies only**. Use the [issue forms](https://github.com/PracticalSwan/tds-macro/issues/new/choose); strategy PRs follow [CONTRIBUTING.md](CONTRIBUTING.md). Core implementation is owner-maintained.

[Build/development](docs/development.md) · [Strategy credit](docs/strategies.md) · [Changelog](CHANGELOG.md) · [Security](SECURITY.md) · [License/notices](NOTICE.md)
