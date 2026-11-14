"""Read-only result validation; a banner alone is not a supported-map win."""
import re
from dataclasses import dataclass
from .observer import Observer,ink
from .resources import LocalOCR,parse_cash


def parse_duration(text):
    match=re.fullmatch(r'\s*(?:([0-9]{1,2})m\s*)?([0-9]{1,2})s\s*',text)
    if not match or int(match[2])>=60:
        return None
    return int(match[1] or 0)*60+int(match[2])


def read_duration(frame,ocr):
    # Right-aligned values change width. The wider crop can include the tail
    # of "Completed:"; tighter crops can lose glyph context. Require agreement
    # across explicit observed crops; retain strict parsing with no substitutions.
    values=[parse_duration(ocr.read(frame.crop(box))) for box in (
        (1150,430,1270,470),(1178,430,1270,470),
        (1180,430,1265,467),(1190,430,1270,470))]
    valid=[value for value in values if value is not None]
    return valid[0] if len(valid)>=2 and len(set(valid))==1 else None


@dataclass(frozen=True)
class GameResult:
    status: str
    map_name: str
    difficulty: str
    wave: int
    duration_seconds: int
    coins: int | None


class ResultReader:
    def __init__(self,observer=None):
        self.observer=observer or Observer()
        self.ocr=LocalOCR()

    def read(self,frame):
        frame=self.observer.align_result(frame)
        state=self.observer.observe(frame).state
        if state not in {'victory','defeat'}:
            return None
        text=lambda box:self.ocr.read(frame.crop(box))
        map_name=text((1150,473,1265,499))
        difficulty=text((1200,585,1265,612))
        mode=text((1160,548,1265,574))
        wave_text=text((1225,510,1265,536))
        duration=read_duration(frame,self.ocr)
        if map_name!='Dead Ahead' or difficulty!='Easy' or mode.casefold()!='survival' or duration is None or not wave_text.isascii() or not wave_text.isdecimal():
            return None
        wave=int(wave_text)
        if not 1<=wave<=20 or (state=='victory' and wave!=20):
            return None
        rewards=text((650,520,1010,710))
        matches=re.findall(r'(?<![0-9])([0-9][0-9,]{0,7})\s*Coins\b',rewards,re.IGNORECASE)
        if len(matches)!=1:
            rewards=self.ocr.read(ink(frame.crop((650,520,1010,710))))
            matches=re.findall(r'(?<![0-9])([0-9][0-9,]{0,7})\s*Coins\b',rewards,re.IGNORECASE)
        coins=parse_cash(matches[0]) if len(matches)==1 else None
        return GameResult(state,map_name,difficulty,wave,duration,coins)
