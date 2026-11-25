# Contributing

Public contributions are limited to **suggestions and new strategies**.

- Use a Suggestion issue for a behavior defect, improvement or setup observation, with reproducible steps and expected behavior.
- Use a Strategy proposal before a strategy PR. Submit only material you created or have permission to redistribute; state attribution and license/permission.
- Strategy PRs may add data under `strategies/community/`, calibration PNG/JSON under `calibrations/community/`, and evidence Markdown under `docs/strategies/`. No source code, executables, dependencies, engine edits or workflow changes in community PRs.
- Core implementation and existing release calibration changes are owner-maintained. Suggest changes through issues; core-code PRs are outside scope.

New strategies are not auto-loaded. Acceptance requires strict parsing, compatible geometry, reproducible camera/loadout, actual-price behavior, stop/failure checks and supervised live results. State UI version, skin, modifiers, matches, time/rewards and distinguish simulated from live evidence.

Every proposed strategy must supply the conditions listed in [the strategy requirements template](docs/requirements/strategies/_TEMPLATE.md), including required cash, perk/skill constraints, ordered slots, stop conditions, and a verifiable success predicate. Community submissions should put those details in their allowed `docs/strategies/` evidence; maintainers publish a reviewed sheet in `docs/requirements/strategies/` before shipping or including a strategy in future automatic rotation. A single successful owner-account run does not prove universal account compatibility.

Remove usernames, balances, chat, personal paths and account identifiers before sharing. Do not upload raw captures, credentials, Roblox logs/session files, private imports or injection code. Security issues use SECURITY.md.

A passing CI check is not acceptance or proof of a win. The maintainer may decline submissions outside scope.
