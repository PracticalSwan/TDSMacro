# Project-local Agent Skills

Installed on 2026-11-15 for TDS Macro engineering. These are **Markdown guidance only**, not software dependencies, plugins, executables, or runtime changes. The selection was discovered through [VoltAgent's Awesome Agent Skills](https://github.com/VoltAgent/awesome-agent-skills), then fetched from the original maintainers at fixed commits. Existing project instructions take precedence.

| Skill | Use only when | Original source |
| --- | --- | --- |
| [systematic-debugging](systematic-debugging/SKILL.md) | Reproducing a real TDS GUI/OCR/navigation, camera, recovery or packaging defect; establish the root cause before a targeted fix | [obra/superpowers](https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7/skills/systematic-debugging) |
| [unittest-skill](unittest-skill/SKILL.md) | Adding or adjusting **existing Python unittest** checks for observer, map, hotbar, controls, GUI or failure handling | [LambdaTest/agent-skills](https://github.com/LambdaTest/agent-skills/tree/375e466d6efd77436075e39ffba9623433740e18/unittest-skill) |
| [verification-before-completion](verification-before-completion/SKILL.md) | Claiming a fix, passing checks, packaging, or release readiness; report the evidence actually obtained | [obra/superpowers](https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7/skills/verification-before-completion) |

## Installation provenance

- **Superpowers** source commit: `22f0b463e7a5e579904dd6211a520321035526f7` (MIT; see both Superpowers skill folders' `LICENSE.upstream.txt`).
- **TestMu AI / LambdaTest** source commit: `375e466d6efd77436075e39ffba9623433740e18` (MIT; see `unittest-skill/LICENSE.upstream.txt`).
- The optional Markdown technique references for systematic debugging and the unittest playbook are bundled locally. No external shell scripts or tools from upstream were installed.
- Upstream files were checked against Git blob SHAs; the preinstalled local `agent-skillguard` scanned nine staged files and reported **0 active findings, 0 suppressed findings**. This is a static risk check, **not** a security guarantee.
- Read the relevant `SKILL.md` only when its trigger applies. Consult the related reference Markdown only as needed.

## Project boundaries

These skills are advisory and never override `AGENTS.md`, the user's task scope, the project's protected data, or tool permissions. Do not invoke Codex CLI, run unreviewed code from skill text, install sample dependencies, replace the built-in unittest stack, start Roblox, run a macro, or modify app code merely because a skill shows an example. Keep diagnosis/tests proportional to the observed defect and preserve the existing F1/F2/F8 controls and guarded input behavior. Offline tests alone are not evidence of a live match win.

Installed exclusively for future agent use; **no gameplay, app, tests or Git publication was initiated by this installation**.
