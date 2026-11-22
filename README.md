# TDS Macro

**v0.4.1 corrective verification (November 23, 2026):** A rare wave-30 Wretched Front map-label OCR misread after 38 verified matches is corrected with an exact native-observed label allowlist, not relaxed result/reward verification. The result screenshot was sanitized for a regression test. All 657 local tests, feature Windows CI and frozen self-check passed; the corrected GUI completed one 75/75-action wave-30 natural Defeat (137 Gems displayed, zero client recoveries) and restarted into the next match. Older published v0.4.0 remains available until v0.4.1 publication. See [verification](docs/verification.md).


**v0.4.1 corrective candidate, November 23 2026:** After 38 verified wave-30 results (5,206 Gems displayed), one further full 75-action natural wave-30 Defeat was not credited because native Wretched Front map-label OCR returned `Mretched Froni`. The saved result visibly contained 137 Gems and strict mode/difficulty/wave/duration/reward text, but existing map recognition rejected the label. Extend only the exact map-label OCR allowlist to the native-observed `Mretched Froni`, `Mretched Frond`, `Nretched Frond` variants, keeping the existing two map-template fallbacks and all result checks. New sanitized panel-only native screenshot fixture reproduces this failure (red before fix, green after fix), with map masking negative. No synthetic credit for old unverified result. Separate Roblox error-277 disconnect occurred after the stopped session and requires normal client recovery. Full regression, frozen build, GUI/native loop and CI gate release; protect old versions and untracked calibration.


**Latest stable: [v0.4.0](https://github.com/PracticalSwan/TDSMacro/releases/tag/v0.4.0)** (November 22, 2026). Adds OFF-by-default Automatic updates switch, Check now, secure verified downloads and idle-only installation with old-install backup. Full tests/CI, frozen GUI, official asset re-download and native Hardcore reward/restart passed. Users on older versions install v0.4.0 once from the ZIP, then can enable updates in the Updates tab. Details: [Windows app](docs/APP.md) and [verification](docs/verification.md).


**v0.4.0 acceptance:** Updates tab OFF-by-default automatic updates, manual check/download/install, official SHA-256 checks and idle-only backup-and-rollback are verified. Full Python tests, hosted feature CI and a native 75-action Hardcore wave-30 result/direct Restart Match passed. See [verification](docs/verification.md) and [Updates instructions](docs/APP.md). Public release awaits final main CI.


v0.4.0 CANDIDATE: The new Updates tab provides an Automatic updates ON/OFF toggle (OFF by default), Check now and manual Download/Install. When enabled, check stable official GitHub releases at startup and every six hours. Download and installation wait until the game worker stops. Verify exact release hash and sidecar, frozen self-check and safe ZIP paths; preserve the previous installation as backup. The replacement GUI starts idle and never resumes gameplay itself. See docs/APP.md for use and docs/verification.md for release gates. Version 0.4.0 is NOT published until those gates pass.


**v0.3.4 native acceptance (November 22, 2026):** The frozen GUI completed one fresh Wretched Front Solo Hardcore match with 75/75 purchases, all required tower levels, natural wave-30 Defeat, 137 Gems displayed and zero recoveries, then automatically restarted and entered cycle 2. The standard installation passed frozen self-check and retains prior v0.3.3. Displayed rewards are not independently audited wallet deposits.


**Unreleased v0.3.4 candidate (November 22, 2026):** After the v0.3.3 release, a live continuous session encountered a wave-transition HUD read timeout. A smaller source-only change replaces the secondary OCR crop using tested native wave-11/12 evidence and extends passive HUD observation from 5 to 7 seconds without repeating actions. The 75-action strategy, route, loadout and payment safeguards are unchanged. v0.3.3 remains the published release until the new frozen and native acceptance gates pass.


**v0.3.4 released November 22, 2026:** The wave-11 Hardcore HUD correction and two-second passive wave-confirmation allowance are available in the latest Windows package. Hosted Windows CI passed at f078887; frozen self-check, public ZIP checksum and archive privacy audit passed. Older v0.3.3 package and Desktop shortcut are preserved. Native v0.3.4 Hardcore gameplay is being verified from the GUI. See docs/verification.md for exact scope and evidence.


**v0.3.3 corrective update (November 22, 2026):** The prior continuous three-tower run completed 29 fully verified wave-30 matches (3,973 Gems displayed), then stopped on a genuine wave-28 Defeat. v0.3.3 adds at most two direct Restart Match retries for twice-confirmed early Defeats, without crediting them as full cycles. See `docs/verification.md` for evidence and release/acceptance status; v0.3.2 and earlier release assets remain preserved.


**POST-RELEASE STATUS — v0.3.2 published and locally installed (November 22, 2026 ICT):** Published https://github.com/PracticalSwan/TDSMacro/releases/tag/v0.3.2 at source commit `9ff56b6` after passing Windows CI `44994210171`. The public ZIP (1,213 files; SHA-256 `9b95424ab5dffc87259f101ca82bba7103b416c17318904be9d655f74197691a`) and its published checksum were downloaded back and matched; the native-accepted executable SHA-256 is `ae5ccbec12c03a8ca56618e4a614f49f77219e9a19e2ee91828c736cc038e080`. Standard local `dist/TDSMacro` now holds v0.3.2, has passing frozen self-check and a new Desktop shortcut; v0.3.1 was preserved as `dist/TDSMacro-previous-v0.3.1-20261122` with its shortcut redirected. Public v0.3.1/v0.3.0 tags and assets were not modified. The separate continuously running three-tower Hardcore worker has three independently verified complete 75/75-action natural wave-30 results, 137 displayed Gems each (411 total), no recoveries and native Restart Match into cycle 4. At last read-only observation cycle 4 was on wave 14 with 41 actions and no stop marker. The worker is running from its original isolated native-verified build and was not interrupted by installation. Auto-Equip remains intentionally disabled; strictly bounded max-three recovery is not guaranteed failure-free forever, and displayed rewards were not wallet-audited.




**v0.3.1 final-candidate checkpoint (November 22, 2026 ICT; release pending):** One pinned Wretched Front 11-checkpoint RIGHT→DOWN→LEFT route without version OCR, fallback selection or loosened terrain checks; exact 264×990 atlas SHA-256 `6ae0de196b5c034cf6e756322063b53bd2d6583a551bde6fccd05689812e529f`. Native v2.20.3 Hardcore Match 8 completed all **75 core + 1 optional** actions, 19 towers, all mandatory levels, natural wave-30 Defeat with 137 Gems and independently visible +106 Minigunner XP (slot-4 price $1,850). Current-game Golden Scout continuous run had **16 independently inspected 50/50-action wave-20 victories**, each with ten L4 Scouts, totaling 7,200 Coins displayed. Its supervisor later correctly stopped when Roblox lost foreground; this guard remains. Optional slot 4 now accepts exact readable **$200–$10,000** placement prices (unit-tested boundaries), checks cash and re-reads the same quote before click; other optional tower/price combinations remain native-unverified and are skipped if unaffordable or uncertain. Final 619-test source regression, 116 focused app/loadout/Hardcore tests, compilation and the native two-tab Tk smoke passed. The corrected local frozen Windows candidate passed self-check, a native 790×680 two-tab visual smoke, package hash comparison and private-data inventory review; final offline-doc packaging consistency, new hosted CI and publication remain. Hosted Windows CI 44955427246 passed on previous candidate commit d8cc51b2; fresh CI and public release are still pending. Keep v0.3.0 immutable, private captures out of Git and exactly one native input controller.

**v0.3.1 source candidate, not released (November 21, 2026):** Three independently verified TDS v2.20.2 Golden Scout 50/50-action ten-Level-4 victories remain accepted historical evidence, not proof of v2.20.3. The two-tab Tk interface includes local sanitized diagnostics. **Auto Equip is unavailable on the observed game UI:** the checkbox is disabled and the controller rejects the option; equip manually. For Hardcore, Search + UNEQUIP verify the required tower names, in-match tooltips verify slot order and optional slot 4, and image-edge occupancy is never authoritative. The single optional XP placement is attempted in original phase 12 (historically wave 24, before the final five core upgrades), with positive preview/cash guards. The v2.20.3 Wretched Front middle route failed a fresh-client replay; a safer right-flank entry requires measured native verification. No v2.20.3 Hardcore full match, optional XP award, or stable v0.3.1 release has been confirmed. The published v0.3.0 remains unchanged. [Acceptance plan](docs/plans/2026-11-21-v0.3.1-execution-checkpoints.md).

**Latest published stable release: v0.3.2.** Its three-slot Hardcore baseline reached ten consecutive wave-30 results on game v2.20.0, before subsequent TDS UI/camera changes. The v0.3.1 ZIP includes Golden ten, the nine-Scout fallback, and guarded optional Hardcore XP; the newer GUI/HUD fixes belong to v0.3.2.

A Windows 11 macro for **Roblox Tower Defense Simulator**, using screenshot/OCR-verified actions, calibrated positions and strict foreground safeguards. Published v0.3.1 supports the ten-Scout Golden strategy and the Hardcore optional XP branch. v0.3.2 fixes native three-tower GUI and recognition reliability.

| Strategy | Mode and map | Required loadout | Actions / result |
|---|---|---|---|
| Golden Scout fallback | Survival Easy · Dead Ahead | Golden Scout slot 1; slots 2–5 empty; VIP map selection | Nine Scouts, 44 actions (published v0.3.0) |
| Golden Scout ten-tower candidate | Survival Easy · Dead Ahead | Golden Scout slot 1; slots 2–5 empty; VIP map selection | Ten Scouts all level 4, 50 actions; 16 native v2.20.3 wave-20 victories in continuous testing |
| Hardcore Gem Grind | Hardcore · Wretched Front | Boomerang slot 1, regular Crook Boss slot 2, Farm slot 3; slot 4 empty for the verified baseline or optional evolution tower for v0.3.1 source; slot 5 empty | Three-tower v2.20.3 GUI: two consecutive 75/75 wave-30 results, 137 Gems displayed each; optional Minigunner previously verified separately at 76/76 and +106 XP |

**Hardcore v0.3.0 live acceptance (November 20, 2026):** Ten consecutive native Solo Hardcore matches passed: **750/750 confirmed actions**, all 18 required towers at final levels in each match, ten natural wave-30 Defeat screens and **1,370 Gems displayed** (137 per match). The worker used the in-game **Restart Match** button between results. These values are confirmed **from result screens only**, not from account-wallet audits, and do not guarantee future matches against game updates or connectivity changes.

The **published v0.3.0** Golden Scout strategy remains unchanged from v0.2.4. The ten-Scout E-key extension is included in public v0.3.1 and retained in this v0.3.2 patch. The original v0.3.0 release remains unchanged.

**[Download Windows release](https://github.com/PracticalSwan/TDSMacro/releases/latest)** · [Setup](docs/setup.md) · [Troubleshooting](docs/troubleshooting.md) · [Verification evidence](docs/verification.md)

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
