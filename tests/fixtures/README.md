# Sanitized navigation and recovery regression images

These fixtures preserve only the visual regions required to reproduce the 2026-11-17 navigation and recovery failures. Each file keeps the production reader's 1920×991 frame geometry; pixels outside the relevant UI are blanked, and PNG metadata is absent. The full native captures remain in the owner's ignored local run data and are not part of the repository.

| Fixture | Recorded case | Expected check | SHA-256 |
|---|---|---|---|
| `post_vote_header_a_roi.png` | A: complete Dead Ahead title; vote badge cannot be read from the saved view | Unique title is recovered; badge remains unknown and cannot authorize Ready | `0285015c8de913c691398467fbc8f0e79e3c217e52c066b0ac29f2c1225c44dc` |
| `post_vote_header_c_roi.png` | C: complete Dead Ahead title and exact vote badge 1 | Unique title and one-vote badge are both read | `88d008a7325eed8024fe62037a39dae152eedefe8382299a18e9a336d0fd8edf` |
| `post_vote_badge_view_clear_d.png` | D: live view-clear frame has one visible vote, but the digit falls below the strict template score after crop/scale registration | Unique title and badge 1 remain associated; bounded two-pixel template alignment recovers it while two neighboring zero badges remain rejected | `950e233a5481987cb5dc073a933a99386e95fae63c5648c70cf2f1fff2225d6e` |
| `vip_override_b_roi.png` | B: E keycap and literal Override Map prompt at the last safe approach position | Keycap score ≥0.93 and both exact caption words are required | `9a3d1070c439abd7a63e38d81b0fa3be02648bce9edb823d5bb73cde6c95a829` |
| `disconnect_leave_prompt.png` | Roblox error 278 disconnect modal observed during supervised recovery | Calibrated disconnect state plus exact Disconnected, Leave and Reconnect labels | `af7efec1ddd72abd713546fbc818614749cfa28b67e269c0342dc2347cd467a` |
| `roblox_home_controls.png` | Same-client Roblox Home view after the guarded Leave action | Four exact Home-navigation labels identify an intermediate state only; it cannot authorize a lobby, click, or relaunch | `99d6a7415a9feeb0883ba5fb49b07b4d2f77ebc683e8d13e8bbca91f82ae87cf` |

The blanked background is intentional. These image-only fixtures do not prove client identity, foreground, or movement safety; controller tests provide those states separately, and live gameplay remains a distinct verification gate. Keep the paired negative fixtures for incomplete title, zero/neighbor badge, generic E prompts, missing captions, clipped keycaps, changed disconnect labels, and non-Home/partial Home screens. Do not replace the original private captures with these sanitized copies.
