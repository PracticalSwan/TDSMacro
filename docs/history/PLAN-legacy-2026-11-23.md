# Historical completion plan (archived November 23, 2026)

> **Not the current task list.** See [active PLAN](../PLAN.md), [current status](../STATUS.md), and [verification](../verification.md). Below are older, sometimes superseded implementation checkpoints.

# TDS app completion plan

**Next major milestone, v1.0.0 — PLANNING ONLY (2026-11-23):** Maintain [per-strategy requirements](../requirements/strategies/README.md), plan [verified loadout preset switching](../plans/2026-11-23-v1.0-loadout-switching.md) and [5-success Golden → 5-success Hardcore repeating rotation](../plans/2026-11-23-v1.0-successful-run-rotation.md). No implementation, new GUI control, runtime migration, build, or release in this documentation task. Preserve v0.5.1 and incremental v0.x maintenance/release numbering.

v0.5.0 released installed and user-requested central X1 placement completed. Two 137 Gem/+106 Juggernaut XP native matches, CI, full 672 tests, public download and installed selfcheck passed. Standard continuous four-tower XP worker now launched; next action inspect its live status and preserve exactly one controller. Keep private calibration PNG untouched.


v0.5.0 near-path X1 task: (976,580) instead of (1120,660), core coords unchanged. 672 unit tests, frozen candidate selfcheck, CI 45091424347 and one native full wave30 137 Gem +106 Juggernaut XP result verified. Current second match continuous. Next final documented build, CI, merge/main release, install standard with ONE Desktop shortcut and safe handover at verified match boundary; no damage output measurement.


2026-11-23 NEW REQUEST: shift optional XP X1 placement to path-side near player using point (976,580) from old far right (1120,660). Test native white footprint/Place before click; native complete 137 Gems and Juggernaut XP after relocation, plus CI/frozen package; release v0.5.0 only if all gates pass. Preserve old 18 towers/route/3-tower strategy, one stable Desktop shortcut; no workers currently, Roblox returned lobby.


2026-11-23 current next action: finish full suite for candidate6, native v0.5.0 XP trial with Juggernaut actual placement at first verified $10k cash, verify result and XP placement. Update CI/commit/push/merge/main/release/install one latest Desktop shortcut; leave single safe continuous XP worker running. Previous diagnostic: 18 cycles 2,466 Gems; 0 XP placements due OCR 10099 error; two green consensus crops fix verified on 92 native screenshots.


v0.5.0 UPD: XP priority after preserving ten Farms L3 + B1 L4/B2/B3 L3/C1/C2 L3/C3/C4/C5 L2, defer expensive final 5 only if buying verified Juggernaut. Need native result wave30/137 and positive Juggernaut XP.


v0.5.0 ACTIVE: User requests one latest TDS Macro Desktop shortcut and distinct GUI-selectable four-tower Hardcore Gem+XP path with Juggernaut already equipped in slot4. Shortcut cleanup completed (9 obsolete removed, one stable shortcut kept); source branch feat/hardcore-xp-slot4 adds distinct XP ID, strict hotbar verification, optional cash reserve, XP placement counts. Next: full regression + frozen candidate GUI/UI, native trial with Juggernaut name/$10,000 quote, place and inspect actual reward, optimize only if proven needed, CI, publish/install if accepted, leave one four-tower continuous worker running. Preserve original 3-tower strategy and private route/image captures.


**FINAL OWNER v0.3.1 DECISION (2026-11-21 17:44 ICT; supersedes earlier conditional OCR proposals):** **Remove automatic game-version OCR completely, now.** v0.3.1 must use **one fixed Wretched Front candidate route**, never select or retry routes from version text and never perform even one-time version detection. It is still **NOT an accepted route** until the native proof of **RIGHT onto rock tops → DOWN across the pale/white boulder beside the old gate → DOWN ends ON path → LEFT to original placement pose**, plus two fresh-spawn guarded repetitions and unchanged three-rock camera/drift checks. Terrain mismatch, lost foreground/client identity, unknown Ready/zero-tower state or failed placement checks must stop; non-version gameplay OCR stays. The candidate source has removed version-OCR route dispatch; **no live match, optional XP, final build, CI or release success is claimed**. This instruction now authorizes implementation and native calibration in separate guarded batches, not weakening safety or changing published v0.3.0.

**Active v0.3.1 roadmap override (2026-11-21 15:49 ICT)**: See the [current execution plan](../plans/2026-11-21-v0.3.1-execution-checkpoints.md#active-route-and-version-detection-decision-2026-11-21-1549-ict-docs-only). Native route goal is **spawn → RIGHT ON rock tops → DOWN ON light boulder beside old gate → DOWN ends ON path → LEFT to original placement pose**. Once *one* route passes native fresh-spawn acceptance, drop automatic route-version OCR and require its terrain/camera gates; otherwise allow only one-time-per-client version identification if necessary. Existing v0.3.1 implementation is **not** being changed in this docs-only pass. Earlier roadmap text is archival.

**OWNER'S CURRENT v0.3.1 HANDOFF (Nov 21, 2026; docs-only):** [Integrated plan for Golden Scout E upgrades, Tk Overview/Diagnostics, opt-in empty-hotbar auto-equip, text-only search/slot identity, and TDS 2.20.0](../plans/2026-11-21-v0.3.1-integrated-handoff.md). Earlier v0.3.0 “unreleased” checkpoints below are archived and were superseded by the verified public v0.3.0 tag. Existing uncommitted UI compatibility work is now designated for v0.3.1; no code/game/test/release action occurred in this planning pass.

**LATEST v0.3.0 HARDCORE DEFENSE FINDING (Nov 20 ~07:26 Bangkok):** Supervised native run `captures/runs/live_v030_wave14_dualink_supervised_20261120_0713` crossed wave14 without OCR failure but **lost naturally at wave23**, with **68/75 actions**, **80 Gems displayed, zero wallet-credit evidence**. The same saved-native OCR health crop from `hardcore_C1_level_2.jpg` shows **87/100** base HP, versus **100/100** in the previous 75/75-action, wave30, independently +137-credited run. First Boomerang level2 was **wave9 versus wave5** in the credited run; the earlier native loss reached C1 urgency before completing B1 L2. Introduced a narrow deadline **(7, lead 2, B1 L2)** ahead of the existing wave11 Crook/B1 urgency in `src/tds_auto/hardcore_match.py`; the new `tests/test_hardcore_early_boomerang.py` is red→green 4/4 and existing v2 30/30 passes. **Not yet verified in-game**; next run requires full regressions and a fresh guarded trial. Keep credited 2/3 supervised, 0/10 unattended, Golden revamp v0.3.1 deferred, and v0.3.0 unreleased.

ACTIVE VERSION SPLIT: v0.3.0 is Hardcore Wretched Front Gem farming ONLY. Legacy Golden v4 44-step regression is unchanged. The proposed ten-Scout, 50-step all-max strategy, including right-side (1020,465), is a separate v0.3.1 candidate (docs/plans/2026-11-20-v0.3.1-golden-scout-ten-max.md), not in this release.


> **Current 2026-11-19 scope override:** This file is an **archived v0.2.4 completion plan**, not the live v0.3.0 roadmap. v0.2.4 Golden Scout was subsequently published. For the current 10-Farm v2 Hardcore source, the stopped Codex thread, red B2 preview, 14 purchase phases, wave-30/credited gems, guarded replay, 3 supervised/10 unattended release gates, GUI redesign after release and continuous Golden Scout operation, use the [authoritative v0.3.0 handoff](../plans/2026-11-19-v0.3.0-hardcore-10-farm-revision.md). Keep dated historical data below as evidence, not current truth.

## 2026-11-17 — Latest final live acceptance and release handoff

**Source/doc patch pushed:** `b9162bd8c177cfdc7b7887432f8fcf6617a32a10` on `main` (six tracked files). Focused 72/72, full 341/341, all 18 dependencies, compilation, saved-frame behavior and Git privacy checks passed. Rebuild a fresh app and prioritize real Roblox vote/recovery trials; older v0.2.4 builds do not contain the optimization. No v0.2.4 release has been published.

**Active handoff plan:** v0.2.4 final live recovery, integration and publication (historical reference: `plans/2026-11-17-v0.2.4-final-live-acceptance.md`). The primary task is **real Roblox trial-and-error for the already-implemented disconnect-to-Home recovery** and fresh validation of the post-handoff bounded vote-badge ROI improvement, not expanding offline test counts. A previous candidate passed **10 real wins, 4,500 coins, 44/44 each, zero recoveries** and registered F2 stop; the revised owner acceptance gate is 10, not 20 wins. The changed recovery still lacks live Home→exit→reopen proof, so v0.2.3 stays the published release until a rebuilt v0.2.4 candidate passes it.

Instructions and project memory now require proactive **safe temporary/build cleanup** and measured speed/storage optimization while retaining all private recordings, log/JSONL evidence, original strategies, last-good release and current candidate. The independent source change touches `Session.vote_count`, a localized image-processing optimization with 72/72 session-focused checks, 341/341 full-suite tests, compilation/dependency validation and seven saved-frame outcomes; this edit requires a **new** built executable, post-integration full-suite pass, and live trial. No live gameplay or release publication was performed by the independent reviewer.

---



## v0.2.4 implementation handoff — 2026-11-17 (PLAN ONLY)

**Authoritative implementation, troubleshooting, verification and release plan:** v0.2.4 map-vote and VIP reliability (historical reference: `plans/2026-11-17-v0.2.4-map-vote-vip-reliability.md`).

The 2026-11-16/17 overnight run (`dist/TDSMacro/captures/runs/app_20261116_154247_263948/`) recorded **63 wins / 28,350 coins**, **zero recorded defeats**, and **three successful recoveries** following two post-vote Dead Ahead recognition stops and one VIP Override Map prompt recognition stop. F2 ended match 64; the last match had 44 confirmed actions but no recorded victory. The private failure images visually show Dead Ahead and the VIP prompt, but these images do **not** by themselves prove that the map vote registered or that OCR/template checks passed. The detailed plan requires exact read-only reproduction, minimal code changes, negative guard tests, supervised live acceptance including an extended streak, GLM-5.3-Flash narrow parallel read-only investigations, and full package/CI checks before a possible **v0.2.4** commit/push/release. Modifier automation remains deferred.

**Status:** This turn only creates local ignored plan documents. No gameplay, source changes, tests, builds, Git actions, or release performed. Do not confuse this section with the historic v0.2.3 plan below.

---

## Latest status — 2026-11-16 (supersedes historical plans below)

- **Documentation completed:** Reviewed/pushed 19 tracked source-of-truth docs and optional project-local agent Markdown skills (with MIT license notices) as commit `ca9957a19cb5b07aef5053c00608f7c8a2e3f0f5` on `main`. Private memory, plans, captures and original strategy remain ignored and local. v0.2.3 release assets/code were not rebuilt or republished.

- **Published v0.2.3:** `fdfd250715159c8c55a7fbd96c1215c98e780f2f` on `main`, hosted Windows CI successful. Its revised non-modifier recovery scope was implemented and verified with 301 tests, one match win/replay and passive same-client focus recovery. See tracked `docs/verification.md` and `CHANGELOG.md`.
- **Deferred features:** modifier selection, four-modifier combined win/rewards and gems. Intended future Golden Scout modifier set: Committed + Limitation + Hidden Enemies + Glass, after Challenge Trial unlocks and separate authorization. Not implemented in v0.2.3.
- **Local launcher repair:** `dist/TDSMacro/` now contains the v0.2.3 release-matching build; the earlier local build is archived in `dist/TDSMacro-previous-20261116/`. A correct desktop shortcut launched a responsive GUI. No new code/build/release or Roblox gameplay resulted from that repair; the public setup and troubleshooting docs cover it.
- **Next pending development:** none required for v0.2.3; revisit modifiers after unlocking and live compatibility checks. Historic active-PID and 'latest release' statements below are archival.

---



## Approved v0.2.3 plan — 2026-11-16 (PLANNING ONLY)

**Authoritative implementation plan:** Golden Scout modifiers and passive foreground recovery (historical reference: `plans/2026-11-16-v0.2.3-golden-scout-modifiers-and-focus-recovery.md`).

The owner approved M1, M2, M3, M4 exclusions, natural-focus recovery (F1 approval decision), and bounded local resilience/nonrecoverable protections (R1/R2). **Required initial Golden Scout modifier target: Committed + Limitation + Hidden Enemies + Glass.** All other selectable gameplay modifiers are excluded. Automatic foreground reclamation (F2 approval decision) was rejected; the app's actual F2 Stop hotkey remains unchanged. On loss of foreground, release controls immediately and recover from a fresh lobby only if Roblox regains foreground naturally within a bounded time. Do not resume unverified spending or weaken critical guards.

These are **future implementation requirements**, not current v0.2.2 behavior. The plan requires modifier UI/eligibility verification, full-four-modifier victories and measured rewards, focused/full tests, one supervised focus-loss recovery, packaged app checks, and verification before a v0.2.3 commit/push/release. The owner requested documentation changes only in this turn: no code, runtime, build, process, settings, Git or publication actions.

---

Updated2026-11-15 for the latest user scope: a runnable Windows strategy selector, F1start/F2stop, practical recovery from minor recognition noise, and an active GoldenScout grind at handoff. Reuse the existing engine; no new services or broad redesign.

Completed implementation and checks:

- Standard `dist/TDSMacro/TDSMacro.exe` contains the combined current source, including the victory, decorated board-row and closed-selection-panel repairs. Prior package and private execution evidence are preserved.
- Native selector UI is rendered and inspected. RealF1 creates the guarded worker; realF2 cancels its startup before match input. Global hotkeys have queue/ownership/cleanup coverage, and duplicate starts are refused.
-206automated tests pass after resolving an overlapping controller. Packaged strategy/assets/OCR/Tcl checks pass. Original strategy integrity remains unchanged.
- Actual cash/prices, skin-independent labels, LoginRewards checks, Solo menu path, all four physical board routes, fixed overhead/vertical placements and multiple prior wins have evidence.

Final acceptance completed:

- Actual packaged-appF1 launch completed a full464second/450coin/44action win.
- The same process automatically replayed, selected/voted the map, set the fresh overhead pose and advanced match2.
- Final source/exe/original-strategy hashes and live heartbeat passed. GUI39980 and worker44176 are left active; F2 stops.
- No extended cosmetic soak or additional strategy scope was added. See the verification record for finite evidence and unverified boundaries.

Boundaries: current English1920×991/120DPI configuration and account only. Other-skin live play, no-modifier wins, original224-call tail, claimed hourly income and a gem strategy remain outside verified GoldenScout acceptance. Preserve the original import, all earlier outcomes/stops and unrelated work. No injection, credentials, anti-idle/refocus, OS/security change or publication.

## Public release completion - 2026-11-15
The later publication goal is complete: public PracticalSwan/tds-macro v0.1.0, 214 local tests, successful hosted CI/build, checksum-verified release, Large UI full win and automatic replay. Earlier no-publication/pending-loop statements above are historical. Detailed current acceptance is in public docs/verification.md; private final audit and active run are under ignored captures. Continuous app worker remains active; F2 stops.

## 2026-11-15 - Recovery and replay acceptance for 0.2.0
- Final clean app run: D:\Side Projects\tower-defense-simulator-automation-script\dist\candidate-v0.2.0-r6\TDSMacro\captures\runs\app_20261115_175506_939357; GUI44656/worker30076, client44168. Three wins463/464/464seconds,450coins each,44confirmed actions each; normal Play Again entered match4 with zero recoveries. Four route checkpoints preserve source/floor evidence; match4 skipped VIP because Dead Ahead already existed.
- Separate recovery trials closed/reopened real Settings and map-vote failures; one recovered game won464seconds/450coins. Native F2 cancelled a live cooldown before close/launch, preserving client PID44168.
- Current grey Close Login Rewards dismissed live and from final packaged F1 start. Manifest also retains green Claim; normal lobby skips dismissal. No claim click.
- Final full suite256 passed47.886s; public export50 checks passed without original; frozen OCR/Tcl/44-action self-check passed; fresh focused recovery/status24 tests and compile/dependencies passed.
- Final candidate dist/candidate-v0.2.0-r6/TDSMacro; source and72runtime data files match. Original private gall strategy hash unchanged.
- Publication complete: main dc73535e8dcb3cd37c423e18153e859252f10758; hosted Windows CI43709060751 passed; public latest v0.2.0 release and both server asset SHA256 digests verified. Standard dist/TDSMacro was extracted from that ZIP and passed its self-check. Previous standard preserved at build/previous-standard-v010-before-v020-20261115.
- Final audit: captures/release_prep/final_verification_v020.json and final_live_v020.json. GUI44656/worker30076 remain active, match4 at the final check, three wins/1350coins and zero recoveries. F2 stops; do not start a second controller. All required acceptance checks passed; documented modifier/skin/viewport limits remain.
