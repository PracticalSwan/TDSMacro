# Strategies and provenance

The release selects `GOLDIE SCOUTO.vertical-nine-slot1.strat`, bound to `dead_ahead_vertical_nine_v4.json`.

| Property | Value |
|---|---|
| Map / mode | Dead Ahead / Survival Easy / Solo |
| Loadout | Golden Scout slot 1; no other towers |
| Placement | Nine Scouts in vertical columns along the path |
| Actions | 9 placements + 35 upgrades = 44 |
| Final levels | First eight level 4, ninth level 3 |
| Viewport | 1920×991 physical pixels at 120 DPI |
| SHA-256 | `59548c3cf386f63eb0ae9f820ec165747c600706bbb59c7ce6acbd4da133eafb` |

The original user-supplied GOLDIE SCOUTO strategy credits **gall**. It had no redistribution license notice. That original and historical variants remain private and are absent from source and release. The public file is a separate calibrated 44-action nine-Scout variant based on the observed winning prefix. Attribution is retained; no ownership of the original is claimed. See NOTICE.md.

The original hash is provenance only; runtime does not require the private file. The public strategy's exact hash is checked before play. Edits require corresponding calibration and fresh validation.

Supported commands are `SpawnTower(x, y, slot, id)` and `UpgradeTower(id)` in the existing `.strat` text format. Unknown operations, invalid slots/IDs, malformed metadata and out-of-bounds coordinates are rejected. Data is not executable code. Other formats and the original 224-action tail are outside release scope.

New submissions belong in `strategies/community`, `calibrations/community` and `docs/strategies`, following CONTRIBUTING.md. They are unselectable until reviewed and verified. State geometry, loadout, UI version, skin, modifiers, camera setup and actual outcomes. A single-account win is not universal proof.
