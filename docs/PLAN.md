# Current TDS Macro roadmap — November 25, 2026

**Installed stable release: v0.5.1.** The v0.5.2 corrective candidate has passed its local and hosted Windows checks and completed native gameplay trials in both modes. See [project status](STATUS.md), the [defect register](../BUGS_FOUND.md), and [verification](verification.md) for the exact coverage and open release checks. Older development history is in the [archived plan](history/PLAN-legacy-2026-11-23.md).

## Current accepted baseline

- Four selectable strategies: Golden Scout 10 Max, Golden Scout 9 fallback, Hardcore Solo Wretched Front Gem-only 3 towers, and Gem + optional XP 4 towers.
- 50-action Golden 10/44-action Golden 9 and 75 mandatory + optional Hardcore action profiles remain pinned. v0.5.1 was previously released and tested; those release claims do **not** show that all observed v0.5.1 failures have been fixed.
- Latest native candidate: three-tower Hardcore retry at 08:13 ICT on November 25, 75/75 actions, wave30, 137 displayed Gems. Installed v0.5.1 session ended with 30 Golden wins and four recoveries. No macro worker at 08:26. **Check live state before doing anything invasive.**

## v0.5.2 acceptance

1. Verify native same-strategy continuation after an uncredited result, preserved totals and later exact-once credit. Verify both Hardcore profiles and the late-defense cash reserve in Gem + XP. [Recovery and receipt plan](plans/2026-11-24-v0.5.2-uncredited-cycle-recovery.md)
2. Verify repeated full Golden 10 matches, the exact number of selection clicks and E upgrades, and Play Again. Recheck fresh camera alignment, exact Solo vote and obscured results. [Golden selection and result plan](plans/2026-11-24-v0.5.2-golden-upgrade-selection-revamp.md)
3. Use one bounded representative native pass and exact historical saved-frame regressions; do not keep rerunning rare random board/tooltip/pose scenarios. Document any unverified native combination as residual risk and preserve all safety thresholds. Independent current regression: 694/694; hosted candidate CI passed. Complete the updated package and link check, frozen self-check, privacy review and release/idle installation evidence as authorized. [Verification record](verification.md)

## Separate major milestone — v1.0.0 remains planning-only

- [Guarded preset-based loadout switching](plans/2026-11-23-v1.0-loadout-switching.md) requires exact ordered five-slot readback including empty slots and Golden perk; if unsafe, stop at lobby for manual change.
- [Successful-run strategy rotation](plans/2026-11-23-v1.0-successful-run-rotation.md) aims at verified five Golden victories → five Hardcore 137-Gem wave-30 cycles → repeat, with exact-once counters, bounded recovery and no parallel workers.
- Future fixes can ship as **v0.5.2, v0.6.0, v0.7.0**, etc. No version bump or v1.0 implementation is implied by this documentation.

[AGENTS](../AGENTS.md) · [Requirements](requirements/strategies/README.md) · [Verification](verification.md) · [Open bugs](../BUGS_FOUND.md)
