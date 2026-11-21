# Changelog

**v0.3.1 acceptance checkpoint (2026-11-22 ICT; unreleased candidate):** The fixed Wretched Front RIGHT-over-rocks / DOWN-over-pale-boulder / LEFT-to-original-position route has 11 exact checkpoints and no game-version OCR, jumps, route-selection fallback or weakened safety gates. Single atlas 264x990 SHA-256 `6ae0de196b5c034cf6e756322063b53bd2d6583a551bde6fccd05689812e529f`; only checkpoints 4, 6, 8 and 9 have independently captured same-pose variants. The corrected slot-4 price reader avoids a native green-mask $1,850->$7,850 OCR error while retaining exact cash/price/click checks. **Native Match 8 accepted:** fresh TDS v2.20.3 Solo Hardcore Wretched Front, all 75 required actions plus one positively verified Minigunner X1 placement (76 actions; 19 towers), all exact required final levels, natural wave-30 Defeat, 137 Gems displayed and +106 Minigunner XP visible on the native result screen; controller exited 0. Rewards are result-screen evidence, not wallet audit. Full local 614-test suite, compilation, 18 installed-package compatibility and git diff checks pass. **Still required before public v0.3.1:** current-client Golden Scout 50/50 wins and replay, packaged frozen/GUI/privacy checks, hosted Windows CI, signed-off source review and verified published ZIP/checksum. Published v0.3.0 remains untouched.

**OWNER ROUTE CORRECTION — 2026-11-21 13:44 Bangkok:** The desired new Wretched Front route is **RIGHT FIRST at the original fresh-spawn position**, then travel DOWN along the outside/right-hand mountain boundary, and only after clearing the central obstacles go LEFT into the existing predefined placement pose. The previous experiments moving right *after entering the central path* do NOT test this proposal and must not be promoted to a route. Guarded reset used normal client close/relaunch; fresh lobby was verified on a new Roblox PID. A fresh zero-tower, no-purchase right-at-spawn probe is in progress. Keep the original final three-rock placement check and reject unknown intermediate positions; gather native terrain evidence before modifying the route atlas or production steps. Do not claim XP/full-match/release acceptance from movement-only evidence.

**ACTIVE v0.3.1 SIMPLIFICATION / RELEASE GATE — 2026-11-21 (supersedes earlier implementation suggestions):** The source-only candidate keeps the v0.3.0 release immutable. Auto Equip is **unavailable** on the observed TDS UI: the Tk checkbox is disabled, Controller rejects activation, and direct session preflights reject it before any input. Equip manually. Inventory edge/graphic occupancy is **diagnostic only** and cannot authorize Tower Verification; exact searched name plus UNEQUIP and the in-match ordered name tooltip are authoritative. Slots 4/5 use bounded tooltip and textual price absence checks; unknown priced slots stop, not guess. Optional X1 is one attempted placement in phase 12, after ~70 required purchases (historical wave 24) and before the final five expensive core upgrades; only a positive optional tooltip enables it, and the native X1 placement/result/XP award are not yet verified. Camera retains the three-landmark final gate and cross-frame drift constraints. The v2.20.3 12-step middle route reached the final bound pose in a guarded continuation but failed fresh-client replay at checkpoint 4; do not claim it supported. Prefer a **native-measured right-flank** entry rather than more masks, route alternates or OCR fallbacks. One measured version text ROI plus two fresh positive readings replaces the multi-crop fallback chain. Stop on unknown version, unknown terrain, wrong focus/geometry, uncertain purchase or changed state. Never weaken the camera/placement gates or publish stable v0.3.1 without an uninterrupted fresh-start Hardcore native 76-action/slot-4 result, independent XP evidence when meaningful, current-version Golden checks, frozen QA and hosted CI. The three v2.20.2 native Golden 50/50 victories remain valid historical evidence only; 69 focused tests passed after these simplifications, full regression/native acceptance still pending. No Codex CLI, external scripts/injection, concurrent game controllers, private captures in Git, or forced Roblox termination.

v0.3.1 Golden acceptance VERIFIED: Three native 50/50-action wave20 Easy Dead Ahead Victories, 10/10 Scouts Lv4 in each, 150 source-confirmed actions and 1,350 total displayed Coins, game v2.20.2 terrain calibrated and E-upgrade path, verified normal two-match Play Again loop. Additional v0.3.1 hardening after successful test: optional Hardcore XP placement is processed only after all 75 core required actions, preventing XP purchase from delaying critical final Crook Boss upgrades; explicit OCR 'EMPTY' slot labels no longer incorrectly count as occupied; ten-Scout native candidate becomes GUI default and nine-Scout remains explicit fallback. Source-focused tests pass, current Hardcore native/XP and frozen/CI/release remain pending.

v0.3.1 latest native evidence, Nov 21 morning: Golden Scout ten-tower v2.20.2 terrain-calibrated trial completed 50/50 individual actions (10 placements and 40 guarded E-key upgrades), all ten Lv4, Dead Ahead Easy wave20 Victory with 450 displayed Coins. A fresh-client two-match repeat run has passed end-to-end menu, Golden text-loadout and camera preparation; live worker still purchasing, so repeatability outcome is not yet known. Includes updated forthcoming Windows README and GUI/diagnostics documentation in build script. Hardcore optional slot4 XP camera acceptance and frozen Windows/CI/release remain blocked and must not be advertised as delivered.

v0.3.1 UNRELEASED Golden native milestone, November 21: On TDS v2.20.2 the separate camera/SIFT-calibrated ten-Scout candidate performed all 10 guarded placements and 40 one-time E-key upgrades, verified ALL 10 level4 and wave20 natural Victory, 459 seconds and 450 Coins displayed. Process exited 0; result/steps and final screenshot saved privately. Single-run result only; fresh-map startup, repeatability, optional Hardcore slot4 XP, packaged GUI, hosted CI and stable release still outstanding.


Unreleased v0.3.1 Golden v2.20.2 native trial: after current-map camera pose drift and preservation of strict original gate, produced separate sanitized terrain-reference calibration and reprojected 10 XY. Native trial reference independently passes original camera bind/drift checks. First Scout placement and two E-key upgrades confirmed 3/50, remainder active. Original 44-action nine-Scout and initial 50-action candidate untouched. These are partial experimental results, NOT a production-ready win or published binary.


Additional unreleased v0.3.1 v2.20.2 VIP override adaptation: retained three independent text anchors, added one tiny Normal-filter label alternative from native current modal because old template only matched 0.745 (other two still matched above .998); native menu now verifies .9976 and sanitized test/negative masking passes. Search for Maps field and Dead Ahead hovered title were independently and positively read twice during supervised mode; map-selection input not yet sent. The previous Golden test stopped safely before placement. Do not present v031 as released.


Unreleased v0.3.1 additional UI fixes (November 21): Skip a redundant card search when existing exact Search query and selected tower/action match twice; ignore subthreshold 0.82-0.90 second-state similarity when best state is accepted, while still rejecting two >=0.90 conflicting states; accept only <=3px OCR button-center jitter with exact Equip/Unequip text. Native sanitized Easy squad fixture/regression included. Golden ten-Scout retry3 underway without 50/50 result; v2.20.1 Wretched camera blocker remains open.


Unreleased v0.3.1 source checkpoint, Nov 21: TDS2.20 Hardcore three-slot baseline verified with fresh native 10/10, 750 confirmed purchases, wave30 and 1370 displayed Gems. Optional Scout slot4 verified equipped via positive title/button text and 2x pre/post slot-state observations; one-match placement/XP acceptance still in progress. Golden ten-Scout candidate once-only E upgrades, dark two-tab Tk GUI, sanitized diagnostics and opt-in strict text-empty Auto Equip implemented only in source. Native Tk Overview and Diagnostics were screenshot-verified. Full source 587 tests green. Current game empty inventory tiles have no explicit EMPTY labels, so Auto Equip cannot yet be called generally usable; it stops safely. No v031 release, commit or installation performed, and published v0.3.0 remains authoritative.


v0.3.1 scope approved but NOT yet released: optional Hardcore user-equipped slot4 tower-XP placement (default three-tower strategy unchanged); ten Golden Scouts Lv4 with once-only E upgrades; two-tab Tk GUI and sanitized diagnostics, strictly opt-in text-only auto-equip; TDS 2.20.0 compatibility and safe latency/disconnect handling. Exact live, frozen and hosted CI verification pending.

## v0.3.1 — historical requirements snapshot (implementation underway; not released)

- Planned Golden Scout ten placements / forty upgrades, each confirmed; switch Golden upgrade purchases from mouse-button click to guarded E key while retaining selected tower/price/cash/post-level checks and the nine-Scout fallback.
- Planned small two-tab Tk Overview/Diagnostics GUI: clearer navigation/stats/failure instructions, readable bounded log console, explicit sanitized Copy/Export diagnostics (no arbitrary command execution or background upload), preserved F1/F2/F8/Escape.
- Planned **Auto-equip towers** checkbox default OFF with visible “requires all five hotbar slots empty” note. OFF emits no Equip input; ON uses exact inventory Search and text-only slot/identity checks, never skins/icons/models/borders/Golden color marker/fixed inventory-card points; refuse unknown/nonempty/partial slots.
- Integrate and fully verify existing TDS 2.20.0 UI corrections plus additional native screen/edge-case checks **as v0.3.1**, not a separately published v0.3.0 patch. See [integrated handoff](docs/plans/2026-11-21-v0.3.1-integrated-handoff.md). That planning entry preceded later authorized implementation; see the current unreleased source checkpoint at the top of this changelog.

Unpublished candidate checkpoint (November 21): isolated Windows folder-mode build succeeded with 20 observer states and passed bundled self-check/basic package audit. Three independently verified wave-30, 75-action, 137-displayed-Gem cycles have passed in the ongoing updated-game acceptance. No hotfix publication or completed 10/10 claim. Windows CI now runs test_observer.py.

## Unreleased — TDS 2.20.0 compatibility and desktop GUI refresh

- Recognize the new direct Survival menu after Play and retain the older multi-step route.
- Accept native current vote-one glyphs without accepting zero; inspect shifted inventory Equip text using an exact alternate crop.
- Redesign the existing Tk GUI with clear strategy/session panels, status indicator, keyboard focus and pointer hover on Start/Stop, retaining F1/F2/F8/Escape and a single guarded worker.
- The updated-game ten-match acceptance and frozen package/release gates remain pending; do not confuse the source patch with the published v0.3.0 archive. The ten-Golden-Scout proposal is excluded.


## v0.3.0 — Hardcore Wretched Front Gem Grind

Released November 21, 2026 (Bangkok), at commit f9fb225; successful Windows CI and independently checked published archive.

- Add a separate 14-phase Solo Hardcore Wretched Front strategy using 10 Farms level 3, 3 Boomerangs level 4 and 5 regular Crook Bosses level 3. The original nine-Golden-Scout strategy and its 44 actions remain unchanged; the tenth-Scout revamp is reserved for v0.3.1.
- Use real-time bottom-HUD-only digit-filtered cash OCR, verified tower identities/levels/quotes, protected camera registration, bounded selection-only retry, guarded setup and direct Restart Match after qualifying results. No per-cycle lobby wallet polling.
- Native acceptance on November 20: ten consecutive result-verified wave30 natural Defeat screens, 75/75 guarded purchase actions per match and 137 Gems displayed per match (1,370 total). Displayed rewards are not independent wallet-credit audits.
- Distinguish Roblox network disconnect 277 from camera changes. Prevent guessed clicks, unsafe refocus, duplicate upgrades, and unverified rewards. Keep F1/F2/F8/Escape and original foreground/geometry safety checks.

### Historical pre-release trials (superseded by the verified v0.3.0 release)

## v0.3.0 unreleased — bounded owned-tower reselection

- A new direct-restart batch verified one wave30/75-action 137-Gem result, then stopped in cycle2 at wave25 after failing to select an already-owned C3 Lv.2. The native capture showed correct hover ownership but no open upgrade panel. Permit exactly one *selection-only* retry after two fresh, matching owner-hover/empty-panel observations. Always reverify the selected tower and its level; never repeat placement or paid upgrade input. Wrong panel and second failure still stop safely. Strict 10/10 acceptance and updated build pending.

## v0.3.0 unreleased — correct Roblox disconnect diagnosis

- A restored-strategy run reached 1/10 verified 75-action wave30 137-displayed-Gem results before Roblox disconnected during the second match at wave27 (Error Code 277, 73 confirmed actions). Blurred terrain under the official disconnect dialog was misreported as unverified camera alignment. Now the camera-failure path checks the existing exact Disconnected/Leave/Reconnect evidence and reports a network disconnect without further gameplay input. Native fixture red→green regression, true camera drift regression and 569/569 Python tests passed. Ten consecutive matches and final release gates still pending.

## v0.3.0 unreleased — revert unproven late purchase priorities

- The C4-before-B3 attempt lost at wave29 (74/75, 133 Gems); the Crook-first C3/C4/C5-before-B2/B3 attempt lost at wave28 (73/75, 127 Gems). Restored the exact original SHA-pinned 14-phase purchase order, preserving the tested OCR/camera/direct-restart fixes. Both experiments remain recorded only as rejected trials. Fresh 10/10 acceptance still required; no release.

## v0.3.0 unreleased — guarded Farm level OCR retry

- Crook-first late-game trial stopped before wave5 because selected F2 Level 1 was unreadable in the original broad and first narrow OCR boxes. Added a second fixed labeled crop that only accepts a level if normal/inverted OCR agree exactly. Added up to 2-second read-only selected identity/level recheck before E, saving a screenshot and stopping on persistent mismatch. No blind input, quote/cash bypass or Golden Scout change. Sanitized native red→green fixture and positive/negative upgrade tests added. Late-game strategy effect still untested.

## v0.3.0 unreleased — Crook-first late-wave trial

- Previous attempt to move only C4 L3 before B3 L4 remained unaffordable until wave28 and failed naturally on wave29 (74/75, C5 L2, 133 Gems). Do not count it.
- For a new reversible trial, prioritize C3/C4/C5 L3 before B2/B3 L4. All 18 towers, 75 purchases and existing safety/restart protocols are retained. Focused tests passed, live outcome pending; no release.

## v0.3.0 unreleased — earlier fourth Crook Boss level 3

- Direct-restart run completed two consecutive wave30, 75-action 137-displayed-Gem results, then lost at wave29 with C5 L2 (74/75, 133 displayed Gems). The run fails the 10/10 gate.
- Re-pinned late purchase ordering for a new in-game trial: phase13 C3 L3 → B2 L4 → C4 L3, phase14 B3 L4 → C5 L3. Crook L3 supplies more boss-target damage and spawns Tommy Goons, so advancing C4 ahead of the final Boomerang is plausible; outcome remains unverified. Same 75 actions/18 towers, camera constraints, restart loop and Golden Scout v4.

## v0.3.0 unreleased — static right-wall camera landmark

- A new initial checkpoint-8 stop had a 3px mismatch from a large right-wall landmark. Narrowed only that landmark to a measured, fixed subregion of the existing pinned scene. Tested against native failed/accepted frames and wave27/28 examples. Three-point consensus and camera-drift tolerance remain unchanged. New sanitized red-to-green camera regression added. Acceptance still pending.

## v0.3.0 unreleased — F2 level OCR precision

- A fresh unattended attempt placed Boomerang B1 at wave3 but stopped before a Farm F2 upgrade because the broad panel OCR read Level: 7 for a visible Level 1. The selected Farm, level and $600 quote remain mandatory guards. One Hardcore-only tight labeled level crop recovers 1 only on normal/inverted agreement. Added a native sanitized red-green regression. No in-game upgrade key was sent on the failed uncertain frame.

## v0.3.0 unreleased — bounded hotbar price recheck

- A five-result-verified direct-restart batch failed its sixth match at wave3 before B1 placement when price or cash changed. Do not count it toward the ten-consecutive acceptance gate. Pre-click placement guard now waits no more than two seconds for the same exact price and sufficient fresh cash; all input is withheld during uncertainty. Persistent mismatches save a diagnostic screenshot and stop. Positive transient-price and negative cash-change regressions added.

## v0.3.0 unreleased — native full-match direct restart observed

- First complete 75-action wave30 Wretched Front match under the result-screen-only loop displayed 137 Gems. Guarded Restart Match transition directly opened fresh zero-tower Ready and the second cycle ran without lobby, map vote, inventory or wallet OCR. F5 passed its previous failed hover and reached L3 on wave7. Current uninterrupted result-screen acceptance 1/10; not committed, pushed or released.

## v0.3.0 unreleased — Farm 5 hover OCR drift

- A true owned Farm 5 at level 1 produced an unreadable type label at its original hover crop. Verify the ownership caption first; retry the OCR crop only at +/-2 horizontal pixels. No cursor or click-point changes and no bypass of post-click tower/level checks. Sanitized native positive and negative regressions added to Windows CI.

## v0.3.0 unreleased — native Restart Match, no lobby-wallet cycle

- One-time Hardcore Solo loadout and Wretched Front vote; after 75 confirmed actions, wave-30 natural Defeat and exactly 137 Gems shown on the result screen, use the existing guarded Restart Match button for the next cycle. Require fresh zero-tower Ready and camera rebind before placements, without visiting lobby.
- Removed runtime wallet OCR and redundant lobby-credit checks, plus the obsolete wallet-only tests and CI entry. Gem totals now represent displayed rewards; do not describe them as account-verified credits.
- Native Restart Match transition verified on a real wave-13 Defeat to zero-tower Wretched Front Ready. Automated two-cycle unit test covers one preflight plus one guarded restart; early/incorrect rewards prohibit replay. Ten-cycle acceptance and release pending.

## v0.3.0 unreleased — complete labeled lobby wallet digits

- New ten-match retry stopped without entering gameplay after a truncated wide wallet OCR reading 710 conflicted with the displayed 4,710 Gem wallet. Strict labeled wallet validation now reads only three small digit crops, requires consistent full amounts and remains fail-closed on missing/colliding labels or unresolved values. Native 2,987, 4,426, 4,710 fixtures and two live lobby rereads pass. Updated acceptance streak remains 0/10 until independently credited runs complete.

## v0.3.0 unreleased — checkpoint-8 native parallax recognition

- An unattended first cycle completed all 75 actions and +137 independent Gem credit, but cycle 2 stopped before Ready at terrain checkpoint 8. Saved native screenshot and a new live no-input read identified 3–4px parallax at the first fixed-rock landmark; two independent other landmarks remained consistent at 2px. Narrowly allow up to 4px only at the first rock while keeping other landmarks and bound-camera drift strictly limited to 2px. New red-to-green fixture with negative camera-shift test. Ten consecutive unattended credits remain unverified.

## v0.3.0 unreleased — new first unattended cycle after cash simplification

- The latest bottom-only OCR candidate completed 75/75 actions, all required tower levels, natural wave30 defeat, 137 displayed and independently credited Gems (4573 to 4710). The bounded worker automatically began cycle 2 with wallet 4710; **acceptance currently 1/10 consecutive, not released**.

## v0.3.0 unreleased — simplified bottom-HUD-only Hardcore cash OCR

- Removed Hardcore player-list balance reads, K-abbreviation guessing, special-case punctuation branches and duplicated consensus logic. Read normal/inverted cash text from two bottom-HUD crops, drop nondigits and require one uniquely most-repeated value; use a contrast-enhanced tie-breaker only for ambiguity. Unresolved conflicts fail closed. Strict upgrade-price, tower count, wave and stop guards remain.
- Added native wave7/wave8 regression fixtures and bottom-only safety tests; earlier wave14/wave24 failures replay. The published Golden Scout v4 fallback is preserved, and its revamp remains v0.3.1.
- Unattended acceptance remains blocked. Prior batch credited one cycle then stopped on wave7 OCR; latest batch stopped on wave8 OCR with no credited cycles. Supervised 3/3 is already verified.

## v0.3.0 unreleased — unattended wave-7 cash consensus regression

- First bounded unattended cycle finished all 75 guarded actions, natural wave30 defeat, and independently +137 credited Gems; second stopped at wave7/17 actions, without a credit, on an empty plain cash OCR while inverted and ink crops both indicated $2,220. Preserved the private frame, sanitized account-free fixture, negative ambiguity tests and independently verified player-list bound.
- Added two-or-more agreement among three masked dollar-prefixed cash regions only when their independent K balance is consistent and no competing plausible or full-HUD amount conflicts. Existing strict price/reward parsers unchanged. 10/10 uninterrupted acceptance remains unsatisfied; no release.

## v0.3.0 unreleased — first credited unattended replay

- First cycle of one bounded 10-match unattended run passed 75 actions, natural wave30 result, exact final tower levels and independently credited +137 Gems (4426 to 4563). The worker automatically started the second cycle; acceptance currently **1/10**, not a completed ten-cycle streak. Do not publish yet.

## v0.3.0 unreleased — third supervised credit and native wallet OCR regression

- Supervised 3/3 passed: 75/75 verified actions, exact final 10F L3/3B L4/5C L3, natural wave30 defeat, 137 displayed and independently credited Gems (wallet 4289 → 4426).
- First ten-match unattended attempt stopped safely in lobby without starting a match because floor artwork appended a non-wallet OCR glyph to 4,426. A narrow, strictly labeled digits ROI fixed an account-free native fixture and preserves conflicting-read rejection. Ten-cycle unattended acceptance remains 0/10 and is not released.
- Golden Scout v0.3.1 remains isolated; v0.3.0 Golden fallback unchanged.

## v0.3.0 unreleased — wave23 repeated after early B1 priority

- The first Boomerang level-2 priority reached wave6 and kept 100/100 base HP through both C1 and C2 level-2 checks, but another full native session still lost at wave23 (68/75, 80 displayed, no credit). F5 L3 remained late at wave11 in both losses versus wave7 in the credited wave30 run.
- Narrowly moved C1/B1 L3 reservation from wave8 to wave9 to allow phase3 F5 L3 purchase when affordable; original deadline wave11 remains. Five focused policy and 30 v2 tests pass. Live acceptance, unattended streak, hosted CI and publication remain unverified.

## v0.3.0 unreleased — wave23 defense priority after native regression

- The latest supervised trial reached wave23 without the prior cash/wave OCR stops, but its base was at 87/100 by Crook Boss 1 level2 and it lost with only 68/75 actions and 80 displayed Gems. The prior independently +137-credited wave30 run had 100/100 health and completed Boomerang 1 level2 at wave5; the new loss deferred this upgrade until wave9.
- Added an early first-Boomerang level2 reserve from wave5 until completed, before wave8 Crook urgency. Four new red→green tests and existing 30 v2 tests passed. Native outcome and extended streak still unverified; do not publish. Golden v0.3.1 remains out of scope.

## v0.3.0 unreleased: Hardcore-only OCR live regression (2026-11-20)

- Fixed cash punctuation OCR with guarded digit extraction and independent player-list verification. A subsequent native wave14 failure was actually fraction OCR: cash 4,979 and ten towers were visible. Sanitized second wave14 fixture and broad/tight ink agreement fixed the offline reproduction without guessing. No third credited cycle yet.
- Golden ten-tower/50-action revamp is deferred to separate v0.3.1; existing nine-Scout/44-action Golden v4 untouched in v0.3.0. No release yet.



## v0.3.0 unreleased — November 20 wave-14 native OCR correction

- Fixed false unreadable wave14 HUD from one native trial (40 actions, $1893 and 11 towers verified), whose old Windows OCR read a visible 14/45 fraction as 114/45. The fallback requires exact matching parsed wave from broad plain and tight ink crops, only after existing reads reject. It never guesses a digit. Four native-wave tests red→green, all 90 Hardcore tests pass; new module in Windows CI.
- No new full match or credited Gems, no published release, no Codex CLI.

## v0.3.0 unreleased — November 20, phase11 aligned to only credited run

- Compared the only complete 75-action/+137 credited wave30 ledger against the two Crook-first incomplete wave30 ledgers: the successful run bought B1 L4 at wave21 before C1/C2 L3, whereas the later trials deferred B1 to wave24 and failed to max C5. Updated the bundled 14-phase plan's phase11 to **B1 L4 → C1 L3 → C2 L3**, preserving the no-urgency-override implementation. Re-pinned SHA256 `3bc8761073a85cab3e14d68a547cc8777085c5910459400bd91d85432ef1e1ef`; 30/30 v2 and 86/86 focused Hardcore tests pass. Native evidence is correlational; further supervised gameplay still needed.
- The wave28 animated first-landmark false stop is separately reproduced and fixed using a stationary 30×19 crop, retaining independent consensus and negative camera-shift tests. Official guarded defeat recovery reached a verified foreground lobby.
- The previous frozen private Windows candidate contains the old v2 plan digest. It is retained as historical private evidence, **not release-ready**. No hosted CI, commit, push or v0.3.0 release claimed.

## v0.3.0 unreleased — November 20: verified foreground startup and native wave-28 camera false alarm

- User-authorized official Roblox launch and foreground/maximize safely verified a 1920×991 120-DPI TDS client; new current-source E-key supervised trial placed all 18 towers, maxed 10 Farms and all 3 Boomerangs, confirmed 73/75 actions, and retained **100/100 base HP at waves22 and28**. The worker stopped safely on a moving-range-ring camera false alarm before results; no Gems credited or new supervised qualification.
- Exact saved wave28 frame revealed that the two independent stationary landmarks still agreed at (-15,-8), while both prior first-landmark variants incorrectly matched (-23,-15). Narrowed the first fixed rock region to (531,782,561,801) based on five native screenshots, retaining the full three-rock +/-2px consensus. Added account-free 92KB terrain regression; red→green and 5/5 related positive/negative tests pass. No movement threshold relaxed.
- Full regression, new native trial, packaging/hosted CI/privacy and v0.3.0 publication remain unverified/pending; prior successful +137 credited wave30 run is still the only accepted supervised cycle.

## v0.3.0 unreleased — native E upgrades, redundant-read removal and compact evidence (Nov 19, 23:29 Bangkok)

- Keyboard `E` now replaces the costly pointer travel to the Hardcore Upgrade button, but retains a fresh selected tower/level/cost/cash test immediately before guarded keypress and a positively confirmed level afterwards. Negative tests caught the previous mouse-click path, then passed.
- Removed the duplicate full-HUD cash/slot read before arming a placement. A separate regression verifies that a cash change after arming the hotbar still blocks placement before any mouse-down.
- Successful Hardcore action proofs now use JPEG quality90 without chroma subsampling (2.48 MB PNG → 0.56 MB JPEG in one audited C4 example, same CROOK L3, HUD cash, wave, count) while failure/result captures remain PNG; historical evidence untouched.
- Full local regression after these changes: **537/537 tests pass**. A new private 140.6MB current-source Windows package passed its frozen `--self-check` and exact strategy/calibration SHA audit; no suspicious private-evidence filenames bundled. Removed only the older, redundant 140.6MB private candidate after verifying the replacement. Hosted CI, game trials and public release remain pending.
- One previous verified wave30/137 credited run remains the only accepted supervised cycle. Latest supervised run stopped at wave29 (74/75, 133 displayed, no independently checked wallet), so no new accepted cycle; optional Scout X1 remains uncalibrated. No release/commit/push or final Golden Scout run.

## Unreleased v0.3.0 — verified Windows candidate and privacy checks, November 19 evening

- Passed **530/530 local unit tests**, compileall, 18 installed packages checked by `uv pip check`, and `git diff --check`. All 13 named Hardcore Windows CI test modules exist; hosted CI has **not** run.
- Built a fresh private optimized v0.3.0 Windows executable candidate (140.6 MB/1,257 files) and verified frozen `--self-check`: original Golden Scout 44 operations/hash, Hardcore v2 14 phases/hash, game UI observer/OCR/Tk checks. Removing only the unused OpenCV video I/O FFmpeg DLL saved **27.2 MB** versus the previous 167.8 MB package; no source references to OpenCV video capture/write APIs, and the no-DLL smoke build passed first.
- Removed only two temporary comparison packages generated during this task (~308.4 MB), not the published v0.2.4 application, user-controlled game files or private run history. The packaged inventory had no private-evidence or credential filenames, and a 396-file Git-visible scan found no literal secrets/token prefixes/private Messenger links.
- Live supervised acceptance remains **1/3**, unattended **0/10**. Official Roblox Store activation did not verify a supported lobby; subsequently the client was background and input was correctly withheld. No v0.3.0 commit/push/release, GUI redesign or continuous Golden Scout launch.

## Unreleased v0.3.0 — November 19 evening: targeted route/HUD latency repair

- Replayed the latest stopped checkpoint-2 trial; the saved final image positively matches the existing two-landmark route classifier, so exploratory alternative ROI patches were **not** retained. Extended the existing passive checkpoint reread deadline from 5 to 8 seconds, retaining two consecutive matching terrain observations, no blind movement, and stop-on-unknown behavior. Two new red→green tests cover late success and bounded failure.
- Profiled native Hardcore HUD recognition and added a tightly bounded clean-cash fast path: skip two digit OCR calls only when both exact dollar-prefixed full-HUD reads agree **and** a separate player-list value confirms/bounds them. Ambiguous input retains the original full OCR fallback. Sanitized cropped HUD fixtures and two tests; representative clean frame changed from 9 OCR calls/~0.154s to 6 calls/~0.072s in separate diagnostic samples (not a controlled benchmark); ambiguous `$10}085` still resolves with its independent bound. 81 focused Hardcore and 17 resource tests pass; Windows CI lists all 13 Hardcore test modules.
- Removed only temporary checkpoint-2 exploratory fixtures and debug scripts created during this work; preserved private full frames, user work, earlier evidence and the published Golden Scout app. No second credited supervised cycle, unattended streak, packaging or release claimed.

## v0.3.0 unreleased — first completely credited Hardcore v2 cycle, CI regression coverage (Nov 19)

- First verified single-cycle acceptance: 75/75 action confirmations, 18/18 final tower levels, Solo Wretched Front Hardcore natural wave-30 defeat, 137 result Gems and 137 **independently credited** lobby-wallet Gems. No selling or time-scale tickets. Two more supervised and ten consecutive unattended credited cycles are still required.
- A later supervised route attempt stopped before purchases at checkpoint 4 because two rock/terrain matches disagreed about pose. The stricter two-landmark rejection was preserved; a fresh two-cycle series was started after an official guarded client rejoin.
- Updated `.github/workflows/checks.yml` to include eight previously omitted focused Hardcore regression modules. No release/commit/push; keep all preexisting user work and evidence.

## Unreleased v0.3.0 — first fully credited Hardcore strategy cycle (2026-11-19)

- First verified Solo Wretched Front v2 complete cycle: **75 actions, 18/18 required instances and all final levels**, 10 Farms L3, 3 Boomerangs L4, 5 Crook Bosses L3, natural wave-30 defeat, **137 Gem displayed reward and matching wallet delta +137** (3124→3261). C4 and C5 completed L3 on wave29; no selling/speed manipulation. `match_seconds=452` receipt. Missed experimental defense milestones 18/19 were nonfatal.
- Minimal camera dual-landmark median correction, bounded guarded Ready verification and strict two-view $1,250 spawn-cash OCR have now passed a complete native run. Targeted Hardcore tests **75/75** and resource **17/17** passed before run.
- Further **2 supervised** and **10 consecutive unattended** credited cycles, recovery/focus/safety, Golden regression, full tests, Windows packaging/CI/privacy and actual v0.3.0 release remain gated. Source worktree and old v0.2.4 published build untouched; no commit/push/publish at this milestone.

## Unreleased v0.3.0 — bounded Ready-button pre-click revalidation (2026-11-19)

- A live retest proved the dual-landmark camera route fix and all four L0 pre-Ready Farms, but a single-frame pre-click Ready check stopped without input despite later valid native UI observations. Updated the guarded check to reuse a single captured frame for readiness and evidence, with at most two short read-only retries on failure and an explicit unverified screenshot; no blind click. Two targeted tests and 72/72 focused Hardcore tests pass. Fresh Roblox guarded rejoin was initiated; wave30/credited gems/replay still unverified.

## Unreleased v0.3.0 — camera first-landmark alternate consensus (2026-11-19)

- Preserved original 18/18 placement wave-28 native evidence; 10 L3 Farms, 3 L4 Boomerangs and C1–C3 L3 were verified, but C4/C5 L3 and natural wave-30 gem credit/replay remain pending.
- A wave-28 range circle shifted the first broad camera template; the earlier cropped-rock fix handled that frame but caused a checkpoint-8 false stop at the end of the next Wretched Front route. A localized reader now considers broad and cropped first-landmark offsets and accepts only a **three-landmark median consensus within 2px**, retaining original correlation and stop gates. New privacy-sanitized route fixture, old wave-28 and initial camera tests plus **70/70 focused Hardcore regressions** passed. A new supervised native cycle was started; acceptance is not yet claimed.
- No release, commit or push. Preserve current published Golden Scout v0.2.4 and all earlier native evidence.

## Unreleased v0.3.0 — measured full 18-tower formation and wave28 camera fix (2026-11-19)

- First native supervised Wretched run with **all 18 required towers placed** confirmed by 73-action ledger: ten Farms L3, three Boomerangs L4, three Crook Bosses L3; C4/C5 still L2 at wave28. Base 100/100 on last frame; safety guard stopped on camera recognition before final-result/credit/replay, not a completed cycle. Observed 14,000 game-cash price for Crook Boss L3.
- Fixed the specific first camera landmark misregistration from a late-wave attack-range line by matching the lower stationary rock edge instead of the broad region. Still requires all three independent landmark matches and unchanged drift checks. Native wave27/28 regression 4/4, focused Hardcore 67/67 and complete archived camera/placement frame replay 20/20. v0.3.0 remains unreleased; published Golden Scout and dirty worktree preserved.

## Unreleased v0.3.0 — inventory notification resilience (2026-11-19)

- Added an eight-second bounded read-only confirmation for transient OS notifications covering the inventory's final slots. Requires two consecutive correct Farm-name/five-slot checks, never clicks another app, retains stop on persistent/real wrong occupancy. Three targeted tests and 29 loadout/63 Hardcore tests pass. Private notification frame is not shipped. A new single-controller supervised v2 trial is underway; no public release yet.

## Unreleased v0.3.0 — Wretched route index-5 follow-up (2026-11-19)

- Corrected another narrow animated-landmark false rejection at route index 5 after confirming index 4 worked in live Roblox. New fixed left-rock and right-wall terrain regions remain a two-point 0.90 threshold guard. Added sanitized native checkpoint-5 fixtures and four tests. Archive replay matched **31/31** correct route stages with no cross-step false positives. Still no completed wave-30 credited cycle or published v0.3.0.

## v0.3.0 Hardcore v2: checkpoint-4 route occlusion safety (2026-11-19, unreleased)

- First native retry after wallet OCR correction read Gems, verified loadout/Solo, but stopped at Wretched route checkpoint 4 before placing any towers. A moving/occluded right-side landmark did not match although stable left terrain matched earlier native evidence.
- Added one checkpoint-4-specific right rock/wall crop fallback requiring unchanged full left terrain agreement at the existing strict threshold, and limited initial camera reset to checkpoint zero. Sanitized three cropped terrain fixtures and four focused route regressions; 55/55 focused Hardcore tests pass. Full renewed walkthrough and any completed gem cycle remain unverified.

## v0.3.0 Hardcore v2: targeted wallet/OCR continuation — 2026-11-19 (unreleased)

- Corrected the observed false negative when lobby `Gems 2,987` was legible on the RGB capture but not on the pink-mask OCR. Retains exact lobby/Gems constraints, unique valid numeric reading, and two independent pre/post-game wallet observations; no claimed award/credit or replay. Added sanitized fixture and focused wallet tests (3/3) and confirmed existing results tests (6/6).
- Added sanitized F10 placement screenshot and focused preview tests (3/3). The previously rejected F10 frame now passes the current safe white-footprint and exact `Place` reader; preserve red/missing-caption rejection and confirm behavior in the next native occupied match before assuming fixed.
- Executed guarded official TDS disconnect recovery into a verified fresh lobby; started one native v2 test in `captures/runs/live_v2_wallet_f10_retry_20261119_1125/`. The 14-phase strategy and uncommitted codebase remain intact. No release/commit/push or completed wave-30 credited cycle yet.

## Unreleased v0.3.0 — November 19 continued scheduling and evidence fix

- Recovered the newest Codex owner steering: late Farms F6–F10 prefer their most expensive affordable next upgrade, every Crook reaches L2 immediately, C4/C5 remain compact with right-lane coverage, loadout verification reads names twice instead of skin-dependent borders, and defense/Farm spending is reevaluated after each action.
- Analyzed the 57-action wave-23/100-HP trial and measured the actual purchase prices. The run left F8 at L0/F9–F10 absent and stopped on unverified camera despite three landmarks in its saved frame matching (-28,-1). Added explicit bound-vs-observed offset recording; kept the camera stop guard.
- Modified the bounded Farm scheduler to honor reached phases and accept ROI-positive Farm buys using available deadline slack without delaying protection beyond deadline. Added red-green-focused tests and evidence capture for an unreadable lobby gem wallet. No claimed wave-30 gem credit/replay or release.
- Separate Golden Scout recovery candidate's completed log contains 18 verified wins and 8,100 coins before an explicit stop; no current continuous worker.



## Golden Scout recovery candidate — November 19, 2026 (not a public release)

- Diagnosed a live continuous v0.2.4 run: after a verified 44/44 wave-20 Golden Scout victory and a later confirmation failure, a new client reached TDS lobby but then remained on the orange TDS loading screen; the solo/map-vote transition timed out and ordinary Roblox WM_CLOSE later failed. Native GDK logs included a game-server NoResponse error.
- Added the smallest bounded recovery fallback for a stalled loading client: one `WM_SYSCOMMAND/SC_CLOSE` only after two current loading observations, same foreground HWND/PID/geometry, five seconds after original WM_CLOSE. No kill, unknown-screen click, duplicate controller or unlimited relaunch.
- Added two regressions; isolated published-v0.2.4 recovery/visual checks passed 58/58 and a separate Windows EXE passed its 44-action/self-check. The dirty v0.3.0 tree, previous published executable and all captures were preserved. A new continuous Golden Scout candidate was started through GUI F1; actual recurrence/recovery and future extended reliability require fresh native evidence.

## Unreleased v0.3.0 — documentation sync after Codex usage limit (2026-11-19)

- Preserved the 14-phase v2 contract, pinned source executor and all uncommitted work. Current blocker is a **red B2 preview beside rock** on the revised fresh-spawn camera at wave 15; older B2 placements in a different pose do not prove new-point validity. Last 10-Farm/17-tower wave-19 run displayed 37 gems, not verified wallet credit; a defense-priority retry had 100 HP through C3 at wave 17.
- Reconciled owner requirements: **shorter tower placement/upgrade latency without weakening positive guards**, direct one-click commitment from armed valid previews, Crook Bosses packed left (especially C2 next to C1), defense-wave upper deadlines and cash protection, optional owned slot-4 testing, measured performance and cautious temporary cleanup.
- Recorded the full remaining objective: wave-30 natural defeat/credit/replay and v0.3.0 release gates, **then** a complete UI redesign with hover/focus behavior and verified continuous Golden Scout operation. v0.2.4 remains the published release; no new live acceptance or publication in this documentation pass.

## 0.3.0 (in progress)

- Reserve the next purchases for each newly placed Crook Boss until its level 2 is verified. Apply that order when a defense target pulls a placement into an earlier phase.

- Verify exact Hardcore slot names through native match-ready hover tooltips. Keep independent inventory occupancy checks for empty slots and auto-equip. Restore the overhead pitch before zooming out during camera entry.

- Prefer the most expensive affordable eligible upgrade for F6–F10. Record an overdue defense target and continue prioritizing it until completion or the wave-30 cutoff. Move C4 beside C1 toward the right-hand bend based on a confirmed placement in the occupied cluster.

- Calibrate Hardcore entry from either verified gate approach and allow one camera-only correction before walking. Route an exact disconnect during that setup into the existing bounded transport recovery. Match native HUD counts through 17 and preserve the exact `Place` caption when terrain colors obscure it.

- Load and execute the pinned 14-phase Wretched Front v2 plan with **10 Farms L3 / 3 Boomerangs L4 / 5 Crook Bosses L3**. Buy four Farms before Ready and favor the cheapest eligible Farm actions during the match. Add native v2 placement previews, recognition for the updated Hardcore result panel, and independent lobby-balance verification before replay. The full wave-30 cycle is pending live acceptance.
- Reserve cash for Crook Boss and Boomerang milestones as their wave deadlines approach. Commit an already verified preview with one placement click. Keep path units out of the footprint color check and recognize the exact `14 / 40` counter on the current HUD.
- Reuse the positively identified upgrade panel for the first price read, with a fresh guard before every upgrade. Store the lossless HUD evidence for ordinary Farm upgrades and retain full-frame placement, combat, error and result checkpoints.
- Defer a changed upgrade quote before mouse-down. Match the exact hovered Return To Lobby caption on a verified defeat panel and mask the Crook Boss title against a bright inventory background.

- **Historical v1 continuation (2026-11-19):** The prototype used normal speed and left towers in place after wave 29.
- Adjust Wretched Front placement to match the user-supplied overhead reference: rear-strip Farms, compact staggered Crook Boss-left/Boomerang-right rows and a Boomerang B1 with observed right-hand-turn range. The combined occupied-tower formation still needs trial proof. Four pre-Ready Farms, early income upgrades, and a partial wave-14 run with C1 L2/F8 placed were observed, not a gem success. No v0.3.0 commit, package or release has been made.

- Use available cash for another eligible Farm placement or upgrade while the selected Farm's next upgrade is unaffordable. Verify the live price before clicking and keep combat priorities.
- Place F1–F4 on the Wretched Front back-path strip before Ready. The remaining economy and defense actions use verified wave windows. After wave 28, leave the towers in place and wait for the natural result.
- Add the calibrated straight-down Wretched Front back-path view, 18 checked terrain points and a guarded Hardcore action runner. Keep the existing Scout profile separate.
- Allow the resident Swift helper's hidden overlay during native startup. The guard still detects visible Computer Use overlays and the legacy controller process. A native window regression covers both visibility states.
- Adjust the selected-tower name crop and mask the blinking inventory search caret in the OCR crop. Live name reads confirmed Boomerang, Crook Boss and Farm in slots 1–3 with slots 4–5 empty and zero equip actions.
- Check the Hardcore Solo player count after entering the voting room. The squad menu confirms the mode and Solo choice before selection.

- **Post-restart source/hand-off audit (2026-11-18):** preserved the uncommitted Hardcore candidate and independently passed all **451/451** local unittests (64.671 s), syntax parsing of **42** Python files, `uv pip check` for **18** packages, and `git diff --check` (exit 0, existing CRLF warnings). Aligned `AGENTS.md`, setup/development guidance and live plans to a **native-only TDS controller** to eliminate contradictory CUA-launch/passive-viewing directions. The ChatGPT desktop app auto-recreated a hidden Swift Computer Use overlay after reboot and again after stopping its exact helper; the native guard still blocks LIVE-00 until the actual session is ended through supported UI. No new gameplay, commit, push or release is claimed.

- Added readable-name inventory search and fail-closed selected-tower/slot verification for the Hardcore loadout. On a saved native TDS 2.19.2 Farm frame, the tight label crop reads `Farm` where the older wide crop read `Fanm`; the wide crop remains a compatibility fallback. No icon, model or skin is used for identity, and no equip click is sent for the already nonempty loadout.
- Fixed the Hardcore preflight's stale inventory click allowance after opening Inventory. The search click now requires the verified inventory state set; a focused regression confirms the guard accepts the current screen state without bypassing it.
- Extended the native startup guard to recognize active ChatGPT Computer Use overlay windows used by the current client. During this checkpoint, the guard correctly refused a new run while the hidden active overlay remained. The saved native Farm/Items regressions and focused suite passed **58/58**; actual Wretched Front gameplay, wave rewards, gem credit, replay and release acceptance remain unverified.
- Recorded the verified readable-name Boomerang/Crook Boss/Farm inventory slots and the prepare-only Farm-slot recognition failure, which stopped before game start or tower input. A later native capture shows Error 278; one targeted Win32 Escape to the advertised overlay cancel window did not clear the controller guard. A preparatory app/window inventory showed no dedicated controller-cancel control; a later native check still detected two controller PIDs. Guarded recovery remains stopped, with no Leave action or post-fix live retry claimed. Fresh saved-frame recognition, active-controller refusal, unknown-hover click blocking, and transient-unknown no-retry regressions each passed 1/1; no OCR or game input was attempted during the active overlay check.
- Reuse one `HudReader` across the bounded Hardcore match-ready zero-tower observations. The focused regression failed before the change and passed afterward; the session module passed **96/96**. This is offline verification only; the live prepare-only retry remains blocked by the active Computer Use overlay.
- Removed the unused `_slot_read` helper and its helper-only test. Slot uncertainty remains covered through the production `_slot_occupied` path and `read_equipped_slots` fail-closed regression.

## 0.2.4

- Post-release maintainer audit (2026-11-18): aligned the current release instructions and private project state with the published v0.2.4 evidence and documented the separate Error 277 foreground limitation. Promoted the release-matching 1,277-file local install, preserved the old v0.2.3 installation and captures, and corrected the versioned desktop shortcuts. This local installation change does not modify the distributed executable or prove another live match.
- For a post-vote unknown badge, permit one guarded 0.10-second forward correction only when the non-strafe floor check still finds support; reread map-vote state, unique title and badge. Keep D view clearing behind the stricter strafe margin. A focused regression confirms no second E, no unsafe D and no Ready before badge 1.
- Add a one-time 20–30 minute, no-input TDS-lobby AFK monitor for explicitly started continuous auto-recovery trials. It stays pending across startup recovery, requires two stable lobby reads and exact disconnect labels, and sends no input while monitoring. The fresh r4 build naturally reached Error 278 after 1,193.7 seconds of active monitoring (1,196.9 seconds from the stable-lobby event, 3.1 seconds below 1,200); guarded Leave → Roblox Home → close → process exit → 60-second cooldown → official URI → stable lobby then led to a 44/44 win. That live recovery passed. A later Error 277 was also a genuine Roblox network disconnect; its guarded recovery reached URI launch but did not verify a foreground lobby within 180 seconds. The post-stop client was background. Because per-poll state was not retained, that later activation/session condition is unresolved rather than attributed to a code defect; the worker stopped safely. See verification for precise boundaries.
- Follow-up review (2026-11-17): benchmarked `Session.vote_count` against the saved vote-one/zero and A/C frames and replaced its full 1920×991 float32 color-mask allocation with a bounded 320–649-row, target-centered uint16 ROI (strictly equivalent integer red/green comparison). Reject contours clipped at horizontal ROI edges. All seven existing saved badge outcomes were unchanged; the mask/contour stage measured approximately 28.28 ms full-frame versus 1.15 ms cropped on one real sanitized capture (a narrow processing benchmark, **not** a faster game-wave claim). The 72-test session suite and the full 341-test suite, compilation and 18-package compatibility check passed after this code change. The fresh r4 package later exercised the vote ROI in a board-1 vote and completed a 44/44 win after natural Error 278 recovery; a later Error 277 recovery stopped safely at the foreground-lobby check (see verification).
- Clarify operational priorities in `AGENTS.md`: prompt real Roblox trial-and-error after narrowly scoped regression checks, preserve one controlled input owner, automatically clean only task-owned, provably redundant generated scratch/build artifacts, and retain all original strategies, release fallbacks, run histories, PNG evidence and user-owned files. Avoid redundant full-test cycles and speculative CPU/storage optimizations.

- Recover the exact Dead Ahead title from both recorded post-vote OCR failures with a final thresholded, 2× local header read. Complete-title and unique-target checks stay unchanged.
- Fix the recorded VIP false negative: the late E keycap was clipped by the y=700 search edge, and whole-caption OCR mixed with the adjacent prompt. Extend only the search edge to y=720 and accept two exact, keycap-anchored words as a fallback; retain the 0.93 keycap threshold and literal Override Map requirement.
- After one E, allow at most two seconds of stationary title rereads with stop, foreground and map-vote checks. An unreadable badge permits one floor-checked D view-clear only. Ready still requires the same unique target and vote badge 1.
- The supervised live trial showed that the previous 0.5-second post-vote S retreat removed the required two-sided floor support (from 100%/100% to under 8%/0%) while the title remained readable and the badge stayed unknown. Shorten that retreat to 0.15 seconds; keep the safe-floor check, one-D limit, and no-Ready-on-unknown rule.
- A later trial preserved the floor and safely used its one D view-clear, but still failed to read a visible badge 1: OCR was blank and the normalized digit overlap was 0.87694 against the 0.90 cutoff. Allow at most a two-pixel template registration shift without lowering the cutoff; the same frame then scores 0.92323 and its two visible zero badges stay below 0.77. A sanitized positive-plus-neighbor-negative regression covers that view, and the subsequent packaged replay evidence is recorded in `docs/verification.md`.
- Recognize the calibrated Roblox disconnect modal during explicitly started recovery only with exact `Disconnected`, `Leave`, and `Reconnect` labels. After one rechecked Leave click, require two exact Roblox Home-navigation reads on the same foreground client before one additional ordinary WM_CLOSE; an exact Roblox close confirmation uses its existing guarded click. Never repeat Leave, and require process exit before the official URI. Unknown screens, cancellation, identity/geometry changes and unclosed clients stop without force termination.
- Classify status, match, recovery-ledger, progress and image write failures as protected storage stops. Preserve an already confirmed result when its final diagnostic image cannot be written, and stop before replay.
- Coalesce repeated `latest.png` writes during that bounded reread, preserving the final frame while avoiding up to nine redundant encodes/writes. No retained run history or user captures were removed.
- Add privacy-bounded navigation failure fields, including an allowlist of the map-title tokens, and clearer recovery ledger timing: UTC event time, app-run-relative elapsed seconds and cumulative recovery count. Keep detailed screenshots and append-only records local for future troubleshooting; never persist arbitrary OCR streams.
- Add sanitized A/B/C, disconnect-dialog and Roblox Home regressions plus no-second-vote, no-Ready, F2, floor-margin, final-step VIP, 12-D-cap, changed-dialog and protected storage-failure checks. Acceptance and release status are recorded in docs/verification.md.
- Earlier packaged trial 5 completed the owner-approved ten-match gate: 10 consecutive 44/44 Dead Ahead/Easy wave-20 wins, 4,500 coins and zero navigation recoveries. The registered F2 hotkey then stopped match 11 safely. Those results apply to that earlier candidate; the fresh r4 recovery, vote-path and later Error 277 evidence are recorded above and in `docs/verification.md`.

## 2026-11-16 — Post-release local launcher correction (v0.2.3 unchanged)

- Resolved a confusing local launch setup: the generic `dist/TDSMacro` executable was still a v0.2.2-era copy even though a correct v0.2.3 build existed separately. Verified that the release's executable SHA-256 is `ddf76edbb7b440c83fc61b48635d18a24574cff86c7d1e3de826dd49416f4624` and that the bundled OCR, Tcl/Tk, 44 operations, 16 observer states and strategy hash pass its frozen self-check.
- Promoted the verified **existing** v0.2.3 release build to the local standard `dist/TDSMacro/` folder, retaining the previous folder as `dist/TDSMacro-previous-20261116/`. Created and tested a local desktop shortcut with the correct executable and working directory. Verified a responsive, visible Tk GUI from that shortcut with no Roblox game input.
- The GUI initially opened behind another window; a visible window is not necessarily the foreground one. No app source, strategy, Windows scaling or published ZIP was changed. The installed binary and desktop shortcut are local, ignored files, not repository/release assets.
- Version the existing optional project-local debugging, unittest and verification skill guidance under `.agents/skills/` with its original source references and MIT license notices. These are documentation only and do not change dependencies or runtime behavior.

## 0.2.3 — Passive foreground recovery and protected stops

- Add passive recovery after foreground interruption: immediately release input, wait up to five seconds for the same verified client to return naturally, then restart from a fresh session. Preserve manual stop/pause, geometry/identity, setup/storage and three-relaunch limits. No automatic refocus or interrupted purchase resumption.
- Keep the original client identity through disappearance and the recovery cooldown; reject a replacement before closing. Require two stable observations of the same reopened lobby window.
- Stop for unverified loadout/hotbar setup and failed navigation evidence writes instead of treating them as recoverable game failures.
- Require clean native captures for verification and prohibit computer-control sessions whose pointer/blue effects can contaminate recognition. Preserve the existing Items references; a clean hover still matches at 1.0.
- Defer modifier configuration and four-modifier win/reward validation pending challenge unlocks. Retain the existing nine-Scout, 44-action strategy and v4 profile.
- Verify a clean 7m39s / 450-coin, 44-action win and normal Play Again. A manual foreground interruption returned to the same client in 1.51 seconds, then recovered through a new verified lobby, full setup and 19 confirmed actions before native F2 stopped the trial. Native F2 and app close also cancel startup without game input. Full local suite: 301 passing tests.

## 0.2.2 — Voting walkway margin and post-vote title

- Verify the packaged candidate's 7m43s / 450-coin win, all 44 actions and zero recoveries; leave its continuous Play Again run active.
- Require an additional ten-pixel stone margin before sideways voting-room movement. Near the curved grass edge, take a bounded forward correction first; retain the original two-sided/one-sided support checks and lost-floor stop.
- Use a taller header band only after the vote backstep, preserving the full lowered Dead Ahead title. Keep normal board detection, the physical board index, exact title and one solo vote checks unchanged.
- Add sanitized real-frame regressions for all six observed map-setup stops, including erased-word negatives and physical-index preservation. No vote or purchase action is repeated.
- Extended 0.2.1 soak: 31 confirmed wins / 13,950 coins, all 44 actions in every match. Six natural map-setup stops recovered successfully; these fixes address their two demonstrated causes.

## 0.2.1 — Camera alignment and performance

- Verify a packaged recovery-to-win cycle (7m41s / 450 coins, all 44 actions), followed by normal Play Again through map voting, fresh overhead setup and the first confirmed placement/upgrade in match 2.
- Claim an available Login Reward once after two exact green-button readings and a final guarded check. Accept automatic popup closure or dismiss confirmed Close; skip absent rewards and never repeat an uncertain claim. Recognize the normal Claim hover font and avoid its profile tooltip.
- Wait 60 cancellable seconds after the verified Roblox process exits before one relaunch. This avoids the observed Store activation race and 0x800705b4 error; no force termination is added to the macro.
- Process only the existing 80/135-row map-header bands, restoring screen coordinates and preserving the four-board/title/vote checks.
- Remove the 200 ms unobserved wait after the second menu source confirmation; retain both spaced observations, normal polling and the final click guard.
- Limit camera feature extraction to padded map regions at native resolution, preserving client coordinates, matching requirements and drift limits.
- Remove repeated classification of the same gameplay frame and an extra discarded result-wait read; each measured failure still reaches the guarded action check.
- Use lossless fast PNG compression and bound gameplay latest-frame writes to once per second. Preserve critical evidence and flush the actual final frame.
- Preserve confirmed wins if the final diagnostic PNG write fails, then stop for the storage error before replay or recovery.
- Allow at most six fine zoom adjustments during verified fresh zero-tower setup, followed by the unchanged strict placement pose check. Keep retained restarts check-only and leave avatar settings unchanged.
- Keep lobby, VIP-card and client-close clicks in button/card padding so the pointer leaves verification labels clear.
- Remove verified duplicate local binary payloads while preserving captures, originals, release archives and the current fallback app.

## 0.2.0 — Failure recovery and replay voting-room navigation

- Verified three consecutive 450-coin wins (7m43s/7m44s/7m44s), all 44 actions in each, followed by normal Play Again entry into match 4 with zero recoveries.
- Add default-on, cancellable failure recovery: close the failed client, recognize its Close Roblox confirmation, wait for process exit and reopen TDS into a verified lobby/Login Rewards screen. Preserve attempt evidence and session totals.
- Retain manual stop, focus/geometry, setup/storage and bounded consecutive-failure stops. Native F2 cancelled a real recovery before close/launch; separate recovery trials reopened the client and resumed a winning match.
- Recognize both Claim and Close Login Rewards controls alongside the title. Normal lobby checks send no dismissal input; the macro does not claim rewards.
- Stop the VIP approach on two actual Override Map prompt observations, using short bounded steps and their duration for the return.
- Reach the stone walkway before sideways board alignment; follow its curved edge forward and stop on lost support.
- Recover full Dead Ahead text from tight original word crops; partial titles never authorize walking.
- Add an exact vote-one reference for the observed replay perspective, retaining the existing threshold and zero/erased negatives.
- Retry only transient Windows atomic status-file replacement conflicts without replaying a game action; persistent denial still fails.
- Add sanitized real failure fixtures, bounded private diagnostics and a refreshed app image. Full local suite: 256 passing tests; clean public export: 50 passing checks without the private original.

## 0.1.0 — 2026-11-15

- First public Windows app: one Golden Scout strategy, F1 start/F2 stop, progress and continuous Solo replay.
- Lobby/Login Rewards/loadout checks, four-board/VIP voting, overhead setup and nine vertical Scouts.
- Actual cash/prices, skin-independent identity, prepared-frame drift and result-before-spending checks.
- Fixes for decorated board headers, noisy/animated captions, obscured vote badges and one evidence-gated panel re-selection. No purchase retries.
- Shorter board-reading approach and bounded slow-loading/action-confirmation waits with regressions.
- Public setup/troubleshooting/verification docs, suggestion/strategy-only contributions, Windows core CI/build.
- Original import/history private; public profile independent of private source; confined scene paths and sanitized references.
- Verified a 7m39s/450-coin full win with the owner's Large UI/vertical-upgrade settings. Ignore dim terrain through empty hotbar slots while retaining extra bright-price rejection.
