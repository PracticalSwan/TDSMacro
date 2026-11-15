"""Bound only diagnostic PNG work; every captured frame is still checked."""
from pathlib import Path
import time


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
