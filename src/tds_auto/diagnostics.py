"""Read-only, bounded and sanitized diagnostic summary for the Tk panel."""
from __future__ import annotations
from pathlib import Path
import json
import re

FIELDS=('phase','strategy_id','wave','step','tower_id','level','attempts',
        'matches_completed','gem_cycles','gems_total','confirmed_actions',
        'recovery_attempt','status','reason')
EVENT_FIELDS=('phase','action','tower_id','level','wave','status','reason')


def sanitized(value):
    text=str(value).replace('\n',' ').replace('\r',' ')
    text=re.sub(r'(?i)(?<!\w)(?:[a-z]:[\\/]|\\\\[^\\/\s]+[\\/][^\\/\s]+[\\/]|/(?:users|home|mnt)/)[^;|]*?(?=\s+(?:phase|reason|status|wave|step|action|tower_id|level)\s*[=:]|[;|]|$)', '[private path]', text)
    text=re.sub(r"(?i)\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b",'[email]',text)
    text=re.sub(r"(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|token|cookie|password|authorization|bearer|secret)\b\s*[:=]\s*(?:\"[^\"]*\"|'[^']*'|[^\s,;|&]+)|\bBearer\s+[^\s,;|&]+",
                '[credential]',text)
    text=re.sub(r"\b\d{6,}\b",'[account id]',text)
    return text[:320]


def collect_diagnostics(status,output=None):
    """Only known event fields, limited tail; no commands or screenshot bytes."""
    lines=['TDS Macro diagnostic summary (read only)']
    lines.extend(f'{key}={sanitized(status[key])}' for key in FIELDS
                 if status.get(key) is not None)
    if output is None:
        return '\n'.join(lines)
    root=Path(output)
    paths=[root/'recovery.jsonl',root/'hardcore_actions.jsonl']
    cycles=sorted(root.glob('hardcore_cycle_*/hardcore_actions.jsonl'))
    if cycles:
        paths.append(cycles[-1])
    for path in paths:
        if not path.is_file():
            continue
        try:
            with path.open('rb') as stream:
                stream.seek(0,2)
                end=stream.tell()
                stream.seek(max(0,end-32768))
                if end>32768:
                    stream.readline()
                recent=stream.read(32768).decode('utf-8','replace').splitlines()[-12:]
            for line in recent:
                try:
                    event=json.loads(line)
                    if not isinstance(event,dict):
                        continue
                    safe=' '.join(f'{key}={sanitized(event[key])}'
                                  for key in EVENT_FIELDS if key in event)
                    if safe:
                        lines.append(safe)
                except (ValueError,TypeError):
                    continue
        except OSError:
            continue
    return '\n'.join(lines[-44:])
