"""Local Windows OCR on small HUD regions. Unreadable values stay None."""
from __future__ import annotations

import argparse
import asyncio
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageOps

from .observer import ink, overlap


def parse_cash(text):
    match = re.fullmatch(r"\s*\$?\s*([0-9]{1,7}|[0-9]{1,3}(?:,[0-9]{3}){1,2})\s*", text, flags=re.ASCII)
    if not match:
        return None
    value = int(match.group(1).replace(",", ""))
    return value if value <= 9999999 else None


def parse_count(text):
    match = re.fullmatch(r"\s*([0-9]{1,2})\s*/\s*40\s*", text, flags=re.ASCII)
    return int(match.group(1)) if match and int(match.group(1)) <= 40 else None


def parse_level(text):
    match = re.fullmatch(r"\s*Level\s*:\s*([0-5])\s*", text, flags=re.ASCII)
    return int(match.group(1)) if match else None


def parse_wave(text):
    match = re.fullmatch(r"\s*([0-9]{1,2})\s*/\s*20\s*", text, flags=re.ASCII)
    return int(match.group(1)) if match and 1 <= int(match.group(1)) <= 20 else None


class LocalOCR:
    def __init__(self):
        from winrt.windows.media.ocr import OcrEngine
        from winrt.windows.globalization import Language
        self.engine = OcrEngine.try_create_from_language(Language("en-US"))
        if self.engine is None:
            raise RuntimeError("Windows English OCR is unavailable; no input may be sent.")

    async def _read(self, image):
        from winrt.windows.graphics.imaging import SoftwareBitmap, BitmapPixelFormat, BitmapAlphaMode
        from winrt.windows.storage.streams import DataWriter
        image = ImageOps.expand(image.convert("RGB").resize((image.width * 4, image.height * 4)), border=20, fill="black")
        bitmap = SoftwareBitmap(BitmapPixelFormat.BGRA8, image.width, image.height, BitmapAlphaMode.IGNORE)
        writer = DataWriter()
        writer.write_bytes(image.tobytes("raw", "BGRX"))
        bitmap.copy_from_buffer(writer.detach_buffer())
        try:
            result = await self.engine.recognize_async(bitmap)
            return result.text.strip()
        finally:
            bitmap.close()
            writer.close()

    def read(self, image):
        return asyncio.run(self._read(image))


def hovered_scout_at(frame, point, ocr=None):
    """Recognize the local tower-hover tooltip, never an upgrade confirmation."""
    if frame.size != (1920, 991) or len(point) != 2:
        return False
    x, y = point
    if not (isinstance(x, int) and isinstance(y, int) and 0 <= x < 1920 and 0 <= y < 991):
        return False
    box = (max(0, x + 10), max(0, y - 85), min(1920, x + 225), min(991, y + 35))
    if box[0] >= box[2] or box[1] >= box[3]:
        return False
    text = (ocr or LocalOCR()).read(frame.crop(box)).casefold()
    return bool(re.search(r'\byour\s+tower\s+scout\b', text))


@dataclass(frozen=True)
class Hud:
    cash: int | None = None
    tower_count: int | None = None
    tower_name: str | None = None
    level: int | None = None
    upgrade_cost: int | None = None
    wave: int | None = None
    upgrade_affordable: bool = False
    maxed: bool = False


class HudReader:
    def __init__(self):
        self.ocr = LocalOCR()
        self.level_templates = {}
        for path in (Path(__file__).resolve().parents[2] / "assets/ui_2191").glob("level_*.png"):
            with Image.open(path) as image:
                self.level_templates[int(path.stem.split("_")[-1])] = ink(image)
        self.count_templates={}
        for path in (Path(__file__).resolve().parents[2]/'assets/ui_2191').glob('count_*.png'):
            with Image.open(path) as image:
                self.count_templates[int(path.stem.split('_')[-1])]=ink(image)

    def level_from_pixels(self, frame):
        glyphs = [ink(frame.crop((92+dx, 451+dy, 111+dx, 473+dy)))
                  for dx in (-1,0,1) for dy in (-1,0,1)]
        scores = sorted(((max(overlap(glyph,template) for glyph in glyphs), level) for level, template in self.level_templates.items()), reverse=True)
        if scores and scores[0][0] >= 0.97 and (len(scores) == 1 or scores[0][0] - scores[1][0] >= 0.1):
            return scores[0][1]
        return None

    def count_from_pixels(self,frame):
        # Fixed HUD text, independent of portraits/skins. Matching the complete
        # fraction verifies its /40 suffix as well as the numerator. OCR remains
        # the fallback for values outside the calibrated nine-Scout range.
        glyphs=[ink(frame.crop((1274+dx,940+dy,1370+dx,974+dy)))
                for dx in (-1,0,1) for dy in (-1,0,1)]
        scores=sorted(((max(overlap(glyph,template) for glyph in glyphs),count)
                       for count,template in self.count_templates.items()),reverse=True)
        if len(scores)>=2 and scores[0][0]>=.97 and scores[0][0]-scores[1][0]>=.03:
            return scores[0][1]
        return None

    def read(self, frame):
        if frame.size != (1920, 991):
            return Hud()
        cash_crop=frame.crop((1273,890,1400,932))
        full=[self.ocr.read(cash_crop),self.ocr.read(ImageOps.invert(cash_crop.convert('RGB')))]
        # A dollar sign can be recognized as the digit 5. Full-field OCR must
        # include its literal dollar; the separate digits crop excludes it.
        choices=[parse_cash(value) for value in full if value.startswith('$')]
        digits=frame.crop((1288,899,1400,927))
        choices.extend(parse_cash(self.ocr.read(sample)) for sample in (digits,ImageOps.invert(digits.convert('RGB'))))
        exact_player_cash=parse_cash(self.ocr.read(frame.crop((1800,140,1905,180))))
        if exact_player_cash is not None:
            choices.append(exact_player_cash)
        agreed={value for value in choices if value is not None and choices.count(value)>=2}
        value=next(iter(agreed)) if len(agreed)==1 else None
        # The bottom counter animates toward the player-list value while money
        # arrives. Use the lower validated amount; disagreement cannot increase
        # a spending allowance. Missing/ambiguous OCR still yields None.
        cash=str(min(value,exact_player_cash) if exact_player_cash is not None else value) if value is not None else ''
        count=self.count_from_pixels(frame)
        if count is None:
            text=self.ocr.read(frame.crop((1274,940,1370,974)))
            count=parse_count(text)
            if count is None:
                count=parse_count(self.ocr.read(ImageOps.invert(frame.crop((1274,940,1370,974)).convert('RGB'))))
        title = self.ocr.read(frame.crop((130, 205, 240, 242)))
        cost = self.ocr.read(frame.crop((121, 578, 230, 614)))
        if parse_cash(cost) is None:
            cost=self.ocr.read(ink(frame.crop((121,578,230,614)),True))
        wave = self.ocr.read(frame.crop((550, 77, 674, 120)))
        if parse_wave(wave) is None:
            wave=self.ocr.read(ink(frame.crop((550,77,674,120))))
        if parse_wave(wave) is None:
            wave = self.ocr.read(frame.crop((550,77,595,120)))+' '+self.ocr.read(frame.crop((595,77,674,120)))
        level = self.level_from_pixels(frame) if title == "Scout" else None
        if title == "Scout" and level is None:
            level = parse_level(self.ocr.read(frame.crop((35, 448, 160, 475))))
        background=list(frame.crop((120,542,320,610)).convert('RGB').get_flattened_data())
        affordable=sum(g>70 and g>r*1.5 and g>b*1.25 for r,g,b in background)>5000
        maxed=level==4 and self.ocr.read(frame.crop((50,548,320,600))).casefold()=='fully upgraded!'
        return Hud(parse_cash(cash), count, "Scout" if title == "Scout" else None,
                   level, parse_cash(cost), parse_wave(wave),affordable and not maxed,maxed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path)
    args = parser.parse_args(argv)
    if args.image:
        with Image.open(args.image) as frame:
            print(json.dumps(asdict(HudReader().read(frame)), indent=2))
    else:
        from .phase1 import capture, locate_roblox
        print(json.dumps(asdict(HudReader().read(capture(locate_roblox()))), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
