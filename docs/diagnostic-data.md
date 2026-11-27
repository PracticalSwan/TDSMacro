# Local diagnostic data map

This inventory is derived from the current writer code and documented paths. It uses field names and synthetic examples only; no private run records or screenshots were read to produce it.

## Purpose and boundary

The app stores local progress and failure evidence so the operator can see whether a guarded step completed, diagnose a stopped run, and verify a result. It uses local Windows OCR. The app does not upload these diagnostics or send them to a cloud OCR or analytics service. Opening Roblox through its official URI is a separate recovery action; it does not transmit the diagnostic files.

Run data is written below `captures/runs/app_<timestamp>/`. Recovery attempts use child `attempt_<number>/` folders. The worker log is the sibling `app_<timestamp>.log`; `captures/last_session.txt` stores the current run path. These paths are local workspace metadata. The `captures/` tree is ignored by Git.

## Field and store inventory

| Fields or content | Purpose | Store | Retention and deletion path |
|---|---|---|---|
| `phase`, `runner_pid`, `elapsed_seconds`, `attempts`, `matches_completed`, `wins`, `coins_total` | Show current stage, local process, timing, and cumulative progress | `status.json`; `Session.status()` also emits its event to worker stdout and the sibling log, without context fields merged by `SessionControl.write()` | `status.json` is atomically replaced. The log is kept with the run until manually removed. |
| `progress.confirmed_step`, `progress.count`, `progress.levels`; navigation fields such as `physical_board`, `target_recognized`, `badge_read`, `badge_count`, `title_observations`, `view_clear_steps`, `forward_correction_steps`, `keycap_score`, `literal_caption`, `header_count`, `observation_count`, `steps`, `stable_reads`, `coarse_turns`, `alignment_turns`, `row_center`, `wheel_delta`, `retained`, and `placement_price`; one-time idle fields such as `idle_requested_seconds`, `idle_observed_seconds`, `idle_elapsed_seconds`, `idle_remaining_seconds`, `capture_interval_seconds`, `no_game_input`, `disconnect_observed`, `stable_lobby_reads`, `stable_disconnect_reads`, and recognized `state`; the `title` value | Confirm bounded navigation, no-input idle monitoring and tower progress | `status.json`; `Session.status()` events are captured in the worker log. Recovery report events are stored separately in `recovery.jsonl` and are not emitted to worker stdout | The `title` value comes from OCR on a board-header crop. It can include recognized text around the expected Dead Ahead phrase, so review it before sharing status or logs. Idle fields are scalar observations; snapshots replace earlier status. |
| `stage`, `event_time_utc`, `elapsed_seconds`, `runner_pid`, `client_pid`, `client_hwnd`, `lobby_state`, `close_reason`, `seconds`, `recoveries`, `max_recoveries`, `recovery_attempt`, `reason`, and `stop_kind` | Explain a recovery transition and distinguish its local process/window from a relaunched client | `status.json` and `recovery.jsonl` | `recovery.jsonl` is append-only and has no automatic expiry. `client_pid` and `client_hwnd` are transient local OS identifiers. Candidate recovery events also include foreground activation outcome, final observed lobby state/geometry or error type, and ordinary-close timeout flags. Recovery ledger records are not separately emitted to the worker log. |
| `status`, `reason`, `stop_kind`, `map_name`, `difficulty`, `wave`, `duration_seconds`, `coins`, per-run counters, and the recent `matches` list | Summarize a stop or a measured match result | `result.json`; attempt result files; nested in `sessions.jsonl`; per-match rows in `matches.jsonl`; some fields are repeated in `status.json` and the worker log | `result.json` is rewritten and retains a last-20 match window. JSONL histories append and remain with the run. Error text stored in `reason` can include OS-specific path details; redact before sharing. |
| `attempt_folder`, attempt `result`, and cumulative `totals` | Relate each fresh recovery attempt to its result while retaining shared totals | `sessions.jsonl` | Append-only; no automatic expiry. |
| `uncredited_cycles`, `uncredited_reason`, `observed_early_results`, `early_results`, `direct_replay` | Distinguish observed outcomes, verified early receipts, and same-strategy replay from credited totals | v0.5.2 status, per-match receipts, and the existing attempt and recovery ledgers | Per-match and recovery histories remain with the local run. |
| `event`, `tower_id`, `selection_clicks`, `upgrade_keys` | Measure Golden 10 selection reuse and successful input calls | Local per-match `selection.jsonl` and result summary | Selection events hold the event name and strategy tower ID; the candidate also records placement target, expected/observed count and price, cash, preview/hotbar booleans, and rejected hover target/count when relevant. No raw OCR text is added. |
| `strategy_sha256`, local `pid`, and `progress.next_step`, `progress.count`, `progress.levels` | Validate the exact strategy prefix before resuming a local operation sequence | `progress.json` within a match folder | Rewritten at confirmed checkpoints; removed only with its selected run folder. |
| Full-window or cropped PNG contents, including `latest.png`, `final.png`, navigation checkpoints, confirmed-step images, and `idle_disconnect_confirmed.png`, `idle_disconnect_unverified.png`, `idle_lobby_state_unverified.png` or `idle_lobby_interrupted.png` when needed | Diagnose visual recognition and preserve the final observed game state | Run or attempt folders | `latest.png` is overwritten during observation; named evidence remains. A screenshot can show Roblox account UI, so treat every PNG as private even when its filename is generic. |
| Worker stdout/stderr, including emitted status events, errors, and exception text | Local troubleshooting | Sibling `app_<timestamp>.log` | Kept until manually removed. Status events may omit context fields present in `status.json`; recovery ledger records are stored separately. OS exception text can contain a local path, and title OCR can include surrounding header text; review before sharing. |
| Absolute run path | Let local tooling find the most recent session | `captures/last_session.txt` | Replaced when a run starts. If deleting the exact completed run it names, remove the pointer only when it still points to that same folder. |
| `pause` and `stop` marker files | Request a local pause or safe stop | Run root | `pause` is removed on resume; `stop` remains with the run until manual cleanup. |

No scheduled retention job or automatic run-folder deletion is implemented. To remove data, first ensure the GUI and worker have stopped, select one completed `captures/runs/app_<timestamp>/` folder, and remove only that folder and its matching sibling `.log`. Remove `captures/last_session.txt` only if its contents name the folder being removed. Preserve active runs, unrelated histories, named evidence needed for diagnosis, the shared `captures/` root, and release/source data.

## Synthetic examples

These fabricated records illustrate the field shapes only; values do not come from a live run:

```json
{
  "phase": "post_vote_badge_unconfirmed",
  "runner_pid": 1234,
  "elapsed_seconds": 12.3,
  "wins": 0,
  "coins_total": 0,
  "physical_board": 2,
  "target_recognized": true,
  "badge_read": false,
  "badge_count": null,
  "title_observations": 3,
  "view_clear_steps": 1
}
```

```json
{
  "phase": "recovering",
  "event_time_utc": "2026-01-01T00:00:00.000Z",
  "elapsed_seconds": 20.0,
  "runner_pid": 1234,
  "client_pid": 5678,
  "client_hwnd": 65536,
  "stage": "waiting_lobby",
  "recoveries": 1,
  "max_recoveries": 3,
  "stop_kind": "failure"
}
```

The data map describes local operational diagnostics, not anonymized data or a consent, access, or deletion-request service. Do not publish raw run folders or logs; share only a reviewed, redacted summary or sanitized UI fixture.

## Maintenance evidence archive (November 25)

Ignored captures/maintenance/20261125 holds cleanup.jsonl, cleanup-summary.json, preserved worktree patches and historical non-runtime distribution evidence. Historical dist/<old-directory>/ paths may now resolve under its dist/<old-directory>/ subtree; consult ledger. Active captures and latest rollback were not moved. Never publish archive or use old captures as live state.
