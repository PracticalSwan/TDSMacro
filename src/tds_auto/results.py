"""Read-only result validation; a banner alone is not a supported-map win."""
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from PIL import Image,ImageOps
from .observer import Observer,ink,overlap
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
        if not matches:
            rewards=self.ocr.read(ink(frame.crop((650,520,1010,710))))
            matches=re.findall(r'(?<![0-9])([0-9][0-9,]{0,7})\s*Coins\b',rewards,re.IGNORECASE)
        coins=parse_cash(matches[0]) if len(matches)==1 else None
        return GameResult(state,map_name,difficulty,wave,duration,coins)


@dataclass(frozen=True)
class HardcoreResult:
    status: str
    wave: int
    duration_seconds: int
    displayed_gems: int | None


HARDCORE_MAP_BOX = (1138, 472, 1262, 507)
# Observed on native wave-30 results: high-contrast purple scenery changes
# only the W/M/N first glyph and the terminal t/d/i. These exact variants
# are independently bounded to the verified Wretched Front result panel.
HARDCORE_MAP_LABELS_OCR = frozenset({
    'Wretched Front', 'Wretched Fror', 'Wretched Fron',
    'Mretched Froni', 'Mretched Frond', 'Nretched Frond',
})


@lru_cache(maxsize=1)
def hardcore_map_labels():
    directory = Path(__file__).resolve().parents[2] / 'assets/ui_2191'
    labels = []
    for name in ('hardcore_result_wretched_label.png','hardcore_result_wretched_label_19.png'):
        with Image.open(directory / name) as label:
            labels.append(ink(label))
    return tuple(labels)


def read_hardcore_result(frame, observer, ocr):
    """Read the result for the verified Wretched Front match."""
    frame = observer.align_result(frame)
    state = observer.observe(frame).state
    if state not in {'defeat', 'victory'}:
        return None
    text = lambda box: ocr.read(frame.crop(box))
    map_name = text((1090, 473, 1281, 501))
    # The current result panel clips the last letters of Wretched Front.
    # On the observed shifted panel the broken W reads as a quote in the
    # wide crop and as N in the independently bounded contrast mask.
    if (map_name not in HARDCORE_MAP_LABELS_OCR
            and not (map_name == '"retched Fron'
                     and ocr.read(ink(frame.crop(HARDCORE_MAP_BOX))) == 'Nretched Fron')
            and max(overlap(ink(frame.crop(HARDCORE_MAP_BOX)), label)
                    for label in hardcore_map_labels()) < .94):
        return None
    if (text((1150, 548, 1282, 575)), text((1150, 584, 1282, 613))) != ('Hardcore', 'Hardcore'):
        return None
    wave_row = frame.crop((1020, 510, 1280, 538))
    waves = set()
    for sample in (wave_row, ink(wave_row), ImageOps.invert(wave_row.convert('RGB'))):
        row = ocr.read(sample)
        if match := re.fullmatch(r'Wave:\s*([0-9]{1,2})', row):
            waves.add(int(match[1]))
        elif match := re.fullmatch(r'([0-9]{1,2}) Wave:', row):
            # The OCR engine can order the right value before the left label.
            # Require both to independently read in their expected locations.
            if text((1020, 510, 1135, 538)) == 'Wave:' and text((1200, 510, 1280, 538)) == match[1]:
                waves.add(int(match[1]))
    duration = read_duration(frame, ocr)
    if len(waves) != 1 or duration is None:
        return None
    wave = waves.pop()
    if not 1 <= wave <= 45:
        return None
    rewards = frame.crop((650, 505, 1010, 710))
    values = set()
    for crop in (rewards, ink(rewards)):
        for line, _ in ocr.read_lines(crop):
            amount = re.fullmatch(r'([0-9][0-9,]{0,7})\s+Gems?', line, re.IGNORECASE)
            if amount and (value := parse_cash(amount[1])) is not None:
                values.add(value)
    # XP rewards can reorder the tiles. Read the full label in each tile.
    for left, right in ((658, 775), (776, 895), (896, 1005)):
        caption = frame.crop((left, 602, right, 634))
        for crop in (caption, ink(caption), ImageOps.invert(caption.convert('RGB'))):
            amount = re.fullmatch(r'([0-9][0-9,]{0,7})\s+Gems?', ocr.read(crop), re.IGNORECASE)
            if amount and (value := parse_cash(amount[1])) is not None:
                values.add(value)
    gems = values.pop() if len(values) == 1 else None
    return HardcoreResult(state, wave, duration, gems)
