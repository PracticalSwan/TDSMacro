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


def bottom_hud_cash_digits(text):
    """Ignore nondigits in a bottom-HUD OCR sample; never use this for quotes."""
    digits = "".join(char for char in text if "0" <= char <= "9")
    return int(digits) if 1 <= len(digits) <= 7 else None


def parse_count(text):
    match = re.fullmatch(r"\s*([0-9]{1,2})\s*/\s*40\s*", text, flags=re.ASCII)
    return int(match.group(1)) if match and int(match.group(1)) <= 40 else None


def parse_level(text):
    match = re.fullmatch(r"\s*Level\s*:\s*([0-5])\s*", text, flags=re.ASCII)
    return int(match.group(1)) if match else None


def parse_wave(text, total=20):
    match = re.fullmatch(r"\s*([0-9]{1,2})\s*/\s*" + str(total) + r"\s*", text, flags=re.ASCII)
    return int(match.group(1)) if match and 1 <= int(match.group(1)) <= total else None


def read_hardcore_wave(frame, ocr):
    if frame.size != (1920, 991):
        return None
    # Capture both edges of the fraction while the wave-number animation settles.
    crop = frame.crop((547, 75, 689, 122))
    normal = (parse_wave(ocr.read(crop), 45) or parse_wave(ocr.read(ink(crop)), 45)
              or parse_wave(ocr.read(ImageOps.invert(crop.convert('RGB'))), 45))
    if normal is not None:
        return normal
    # A wave-14 native frame OCR'd as '114 / 45' in every original
    # polarity. Two differently bounded crops both read 14 / 45 exactly.
    # Require agreement, not a guessed digit correction, before using it.
    broad = parse_wave(ocr.read(frame.crop((542, 69, 700, 133))), 45)
    # Keep the full numerator and /45 suffix in this second, smaller region.
    # The old overly tight crop lost the native wave-11 fraction.
    tight = parse_wave(ocr.read(ink(frame.crop((542, 70, 696, 126)))), 45)
    if broad is not None and broad == tight:
        return broad
    # In another native wave-14 frame, the broad plain crop was empty while
    # broad and tight contrast-masked crops both read the exact 14 / 45.
    # Keep two independently bounded valid reads; do not repair digits.
    broad_ink = parse_wave(ocr.read(ink(frame.crop((542, 69, 700, 133)))), 45)
    return broad_ink if broad_ink is not None and broad_ink == tight else None


class LocalOCR:
    def __init__(self):
        from winrt.windows.media.ocr import OcrEngine
        from winrt.windows.globalization import Language
        self.engine = OcrEngine.try_create_from_language(Language("en-US"))
        if self.engine is None:
            raise RuntimeError("Windows English OCR is unavailable; no input may be sent.")

    async def _recognize(self, image):
        from winrt.windows.graphics.imaging import SoftwareBitmap, BitmapPixelFormat, BitmapAlphaMode
        from winrt.windows.storage.streams import DataWriter
        scale,border=4,20
        source=image.convert("RGB")
        prepared=ImageOps.expand(source.resize((source.width*scale,source.height*scale)),border=border,fill="black")
        bitmap = SoftwareBitmap(BitmapPixelFormat.BGRA8, prepared.width, prepared.height, BitmapAlphaMode.IGNORE)
        writer = DataWriter()
        writer.write_bytes(prepared.tobytes("raw", "BGRX"))
        bitmap.copy_from_buffer(writer.detach_buffer())
        try:
            result = await self.engine.recognize_async(bitmap)
            lines=[]
            for line in result.lines:
                boxes=[]
                for word in line.words:
                    rect=word.bounding_rect
                    boxes.append(((rect.x-border)/scale,(rect.y-border)/scale,
                                  (rect.x+rect.width-border)/scale,(rect.y+rect.height-border)/scale))
                if boxes:
                    x0=max(0,round(min(box[0] for box in boxes)))
                    y0=max(0,round(min(box[1] for box in boxes)))
                    x1=min(source.width,round(max(box[2] for box in boxes)))
                    y1=min(source.height,round(max(box[3] for box in boxes)))
                    if x0<x1 and y0<y1:
                        lines.append((line.text.strip(),(x0,y0,x1,y1)))
            return result.text.strip(),lines
        finally:
            bitmap.close()
            writer.close()

    async def _read(self,image):
        text,_=await self._recognize(image)
        return text

    async def _read_lines(self,image):
        _,lines=await self._recognize(image)
        return lines

    def read(self, image):
        return asyncio.run(self._read(image))

    def read_lines(self,image):
        """Return OCR line text and image-relative boxes for observed UI targets."""
        return asyncio.run(self._read_lines(image))


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
    def __init__(self, *, hardcore=False):
        self.ocr = LocalOCR()
        self.tower_names = {'Boomerang', 'Crook Boss', 'Farm'} if hardcore else {'Scout'}
        self.title_box = (85, 198, 296, 247) if hardcore else (130, 205, 240, 242)
        self.wave_total = 45 if hardcore else 20
        self.pixel_count_limit = 18 if hardcore else 10
        self.level_templates = {}
        for path in (Path(__file__).resolve().parents[2] / "assets/ui_2191").glob("level_*.png"):
            with Image.open(path) as image:
                self.level_templates[int(path.stem.split("_")[-1])] = ink(image)
        self.count_templates={}
        for path in (Path(__file__).resolve().parents[2]/'assets/ui_2191').glob('count_*.png'):
            count = int(path.stem.split('_')[-1])
            with Image.open(path) as image:
                self.count_templates[count] = ink(image)

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
        # the fallback for values outside the known glyph samples.
        glyphs=[ink(frame.crop((1274+dx,940+dy,1370+dx,974+dy)))
                for dx in (-1,0,1) for dy in (-1,0,1)]
        scores=sorted(((max(overlap(glyph,template) for glyph in glyphs),count)
                       for count,template in self.count_templates.items()),reverse=True)
        # Keep larger counts in the comparison so they cannot masquerade as 10.
        if (len(scores)>=2 and scores[0][1]<=self.pixel_count_limit
                and scores[0][0]>=.97 and scores[0][0]-scores[1][0]>=.03):
            return scores[0][1]
        return None

    def read(self, frame):
        if frame.size != (1920, 991):
            return Hud()
        cash_crop=frame.crop((1273,890,1400,932))
        if self.wave_total == 45:
            # Read the bottom cash counter only, not the rounded player list.
            # Both normal and inverted text may differ, so check the regular
            # and wider HUD crops and require an unambiguous repeated amount.
            wide=frame.crop((1260,885,1410,940))
            samples=(cash_crop,ImageOps.invert(cash_crop.convert('RGB')),
                     wide,ImageOps.invert(wide.convert('RGB')))
            amounts=[bottom_hud_cash_digits(self.ocr.read(sample)) for sample in samples]
            agreed={amount for amount in amounts
                    if amount is not None and amounts.count(amount)>=2}
            if len(agreed)!=1:
                # Recheck only ties or unreadable values with a contrast mask.
                amounts.append(bottom_hud_cash_digits(self.ocr.read(ink(wide))))
                agreed={amount for amount in amounts
                        if amount is not None and amounts.count(amount)>=2}
                if agreed:
                    leading=max(amounts.count(amount) for amount in agreed)
                    agreed={amount for amount in agreed
                            if amounts.count(amount)==leading}
            value=next(iter(agreed)) if len(agreed)==1 else None
        else:
            # Preserve the existing Golden v4 cash policy for v0.3.0.
            full=[self.ocr.read(cash_crop),
                  self.ocr.read(ImageOps.invert(cash_crop.convert('RGB')))]
            digits=frame.crop((1288,899,1400,927))
            readings=[parse_cash(text) if text.startswith(chr(36)) else None
                      for text in full]
            readings.extend(parse_cash(self.ocr.read(sample))
                            for sample in (digits,ImageOps.invert(digits.convert('RGB'))))
            player_cash=parse_cash(self.ocr.read(frame.crop((1800,140,1905,180))))
            if player_cash is not None:
                readings.append(player_cash)
            agreed={amount for amount in readings
                    if amount is not None and readings.count(amount)>=2}
            value=next(iter(agreed)) if len(agreed)==1 else None
            if value is not None and player_cash is not None:
                value=min(value,player_cash)
        cash=str(value) if value is not None else ''
        count=self.count_from_pixels(frame)
        if count is None:
            text=self.ocr.read(frame.crop((1274,940,1370,974)))
            count=parse_count(text)
            if count is None:
                count=parse_count(self.ocr.read(ImageOps.invert(frame.crop((1274,940,1370,974)).convert('RGB'))))
            if count is None and self.wave_total == 45:
                # The wider crop can read the outlined slash as a 1 after ten towers.
                count = parse_count(self.ocr.read(frame.crop((1274, 944, 1344, 969))))
            if count is None and self.wave_total == 45:
                # Extra vertical padding resolves the compact 0/40 at spawn.
                count = parse_count(self.ocr.read(frame.crop((1270, 934, 1354, 977))))
        title_crop = frame.crop(self.title_box)
        title = self.ocr.read(title_crop)
        if self.wave_total == 45 and title not in self.tower_names:
            title = self.ocr.read(ink(title_crop))
        tower = title if title in self.tower_names else None
        if self.wave_total == 45:
            wave = read_hardcore_wave(frame, self.ocr)
        else:
            text = self.ocr.read(frame.crop((550, 77, 674, 120)))
            if parse_wave(text) is None:
                text = self.ocr.read(ink(frame.crop((550,77,674,120))))
            if parse_wave(text) is None:
                text = self.ocr.read(frame.crop((550,77,595,120)))+' '+self.ocr.read(frame.crop((595,77,674,120)))
            wave = parse_wave(text)
        level = self.level_from_pixels(frame) if tower else None
        if tower and level is None:
            level = parse_level(self.ocr.read(frame.crop((35, 448, 160, 475))))
            if level is None and self.wave_total == 45:
                # The broad panel read can misidentify the Farm's numeric 1
                # as 7. Use a tightly bounded labeled text region, with
                # normal and inverted OCR agreeing on an exact level.
                for box in ((33,452,118,473),(30,440,144,480)):
                    tight=frame.crop(box)
                    normal=parse_level(self.ocr.read(tight))
                    inverse=parse_level(self.ocr.read(ImageOps.invert(tight.convert('RGB'))))
                    if normal is not None and normal == inverse:
                        level=normal
                        break
        background=list(frame.crop((120,542,320,610)).convert('RGB').get_flattened_data())
        affordable=sum(g>70 and g>r*1.5 and g>b*1.25 for r,g,b in background)>5000
        if self.wave_total == 45 and not tower:
            upgrade = None
        elif self.wave_total == 45 and affordable:
            from .hotbar import green_ink
            quotes = (self.ocr.read(green_ink(frame.crop(box)))
                      for box in ((125,586,241,608), (121,578,230,614)))
            prices = {value for text in quotes if text.startswith('$')
                      and (value := parse_cash(text)) is not None}
            upgrade = prices.pop() if len(prices)==1 else None
        else:
            price_crop=frame.crop((121,578,230,614))
            upgrade=parse_cash(self.ocr.read(price_crop))
            if upgrade is None:
                upgrade=parse_cash(self.ocr.read(ink(price_crop,True)))
        maxed=level==4 and self.ocr.read(frame.crop((50,548,320,600))).casefold()=='fully upgraded!'
        return Hud(parse_cash(cash), count, tower,
                   level, upgrade, wave,affordable and not maxed,maxed)


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
