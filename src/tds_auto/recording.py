"""Bound only diagnostic PNG work; every captured frame is still checked."""
from pathlib import Path
import json
import time

from .control import StopRun


def write_json(path,data):
    path=Path(path)
    try:path.write_text(json.dumps(data,indent=2),encoding='utf-8')
    except OSError as exc:
        raise StopRun(f'Cannot write {path.name} ({type(exc).__name__}).',kind='storage') from exc


def append_jsonl(path,data):
    path=Path(path)
    try:
        with path.open('a',encoding='utf-8') as ledger:
            ledger.write(json.dumps(data)+'\n')
    except OSError as exc:
        raise StopRun(f'Cannot append {path.name} ({type(exc).__name__}).',kind='storage') from exc


class LatestFrame:
    def __init__(self,path,now=time.monotonic):
        self.path=Path(path)
        self.now=now
        self.saved_at=None
        self.latest=None

    def write(self,image,force=False):
        self.latest=image
        stamp=self.now()
        if force or self.saved_at is None or stamp-self.saved_at>=1:
            image.save(self.path,compress_level=1)
            self.saved_at=stamp

    def flush(self):
        if self.latest is not None:
            self.write(self.latest,force=True)
