# TDS Macro

**v0.3.1 final-candidate checkpoint (November 22, 2026 ICT; release pending):** One pinned Wretched Front 11-checkpoint RIGHT→DOWN→LEFT route without version OCR, fallback selection or loosened terrain checks; exact 264×990 atlas SHA-256 `6ae0de196b5c034cf6e756322063b53bd2d6583a551bde6fccd05689812e529f`. Native v2.20.3 Hardcore Match 8 completed all **75 core + 1 optional** actions, 19 towers, all mandatory levels, natural wave-30 Defeat with 137 Gems and independently visible +106 Minigunner XP (slot-4 price $1,850). Current-game Golden Scout continuous run had **16 independently inspected 50/50-action wave-20 victories**, each with ten L4 Scouts, totaling 7,200 Coins displayed. Its supervisor later correctly stopped when Roblox lost foreground; this guard remains. Optional slot 4 now accepts exact readable **$200–$10,000** placement prices (unit-tested boundaries), checks cash and re-reads the same quote before click; other optional tower/price combinations remain native-unverified and are skipped if unaffordable or uncertain. Final 619-test source regression, 116 focused app/loadout/Hardcore tests, compilation and the native two-tab Tk smoke passed. The corrected local frozen Windows candidate passed self-check, a native 790×680 two-tab visual smoke, package hash comparison and private-data inventory review; final offline-doc packaging consistency, new hosted CI and publication remain. Hosted Windows CI 44955427246 passed on previous candidate commit d8cc51b2; fresh CI and public release are still pending. Keep v0.3.0 immutable, private captures out of Git and exactly one native input controller.

**v0.3.1 source candidate, not released (November 21, 2026):** Three independently verified TDS v2.20.2 Golden Scout 50/50-action ten-Level-4 victories remain accepted historical evidence, not proof of v2.20.3. The two-tab Tk interface includes local sanitized diagnostics. **Auto Equip is unavailable on the observed game UI:** the checkbox is disabled and the controller rejects the option; equip manually. For Hardcore, Search + UNEQUIP verify the required tower names, in-match tooltips verify slot order and optional slot 4, and image-edge occupancy is never authoritative. The single optional XP placement is attempted in original phase 12 (historically wave 24, before the final five core upgrades), with positive preview/cash guards. The v2.20.3 Wretched Front middle route failed a fresh-client replay; a safer right-flank entry requires measured native verification. No v2.20.3 Hardcore full match, optional XP award, or stable v0.3.1 release has been confirmed. The published v0.3.0 remains unchanged. [Acceptance plan](docs/plans/2026-11-21-v0.3.1-execution-checkpoints.md).

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
