"""Small, read-only, fail-closed UI observer. No input module is imported here."""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

DEFAULT_MANIFEST = Path(__file__).resolve().parents[2] / "assets/ui_2191/manifest.json"


def ink(image, colored=False):
    """Bright neutral UI lettering, independent of the moving scene underneath."""
    red, green, blue = image.convert("RGB").split()
    if colored:
        return ImageChops.lighter(ImageChops.lighter(red, green), blue).point(lambda v: 255 if v > 180 else 0)
    neutral = ImageChops.difference(red, green).point(lambda v: 255 if v < 35 else 0)
    neutral = ImageChops.multiply(neutral, ImageChops.difference(red, blue).point(lambda v: 255 if v < 35 else 0))
    return ImageChops.multiply(neutral, image.convert("L").point(lambda v: 255 if v > 205 else 0))


def overlap(a, b):
    count_a, count_b = ImageStat.Stat(a).sum[0], ImageStat.Stat(b).sum[0]
    if min(count_a, count_b) < 255 * 12:
        return 0.0
    intersection = ImageStat.Stat(ImageChops.multiply(a, b)).sum[0]
    return 2 * intersection / (count_a + count_b)


def label_overlap(a,b):
    """Ignore small caption padding changes, preserving the actual glyph pixels."""
    bounds_a,bounds_b=a.getbbox(),b.getbbox()
    if bounds_a is None or bounds_b is None:
        return 0.0
    a,b=a.crop(bounds_a),b.crop(bounds_b)
    size=(max(a.width,b.width),max(a.height,b.height))
    left,right=Image.new('L',size),Image.new('L',size)
    left.paste(a,(0,0));right.paste(b,(0,0))
    return overlap(left,right)


@dataclass(frozen=True)
class Observation:
    state: str
    confidence: float
    scores: dict[str, float]
    reason: str = ""


class Observer:
    def __init__(self, manifest=DEFAULT_MANIFEST):
        path = Path(manifest)
        data = json.loads(path.read_text(encoding="utf-8"))
        self.size = tuple(data["size"])
        self.anchors = {}
        self.result_ocr = None
        for state, anchors in data["states"].items():
            self.anchors[state] = []
            if len(anchors) < 2:
                raise ValueError("Every state requires at least two independent UI anchors.")
            for anchor in anchors:
                templates = []
                for file in [anchor["file"], *anchor.get("alternatives", [])]:
                    with Image.open(path.parent / file) as image:
                        templates.append(ink(image, anchor.get("colored", False)))
                margin=anchor.get('search_x',0)
                if type(margin) is not int or not 0<=margin<=24:
                    raise ValueError('Anchor horizontal search must be 0..24 pixels.')
                left,top,right,bottom=anchor['box']
                boxes=tuple((left+dx,top,right+dx,bottom) for dx in range(-margin,margin+1))
                self.anchors[state].append((boxes, templates, anchor.get("colored", False)))

    def result_location(self, frame):
        """Register the result panel's small reward-dependent vertical shift."""
        if frame.size!=self.size:
            return None
        states=[state for state in ('victory','defeat') if state in self.anchors]
        if not states:
            return None
        boxes=[box for state in states for box in self.anchors[state][0][0]]
        region=(min(b[0] for b in boxes),min(b[1] for b in boxes)-16,
                max(b[2] for b in boxes),max(b[3] for b in boxes)+16)
        minimum=min(ImageStat.Stat(t).sum[0] for state in states for t in self.anchors[state][0][1])
        # F1 >= .90 needs at least .818 of the template ink. This cheap necessary
        # condition avoids scanning offsets on ordinary dark gameplay frames.
        if ImageStat.Stat(ink(frame.crop(region),True)).sum[0]<minimum*.8:
            return None
        best=(0,None,0)
        for state in states:
            boxes,templates,colored=self.anchors[state][0]
            for dy in range(-16,17):
                score=max(overlap(ink(frame.crop((b[0],b[1]+dy,b[2],b[3]+dy)),colored),t)
                          for b in boxes for t in templates)
                if score>best[0]:
                    best=(score,state,dy)
        if best[0]>=.90:
            return best[1],best[2]
        # Current TDS result banner can render a smaller title font. Keep the
        # standard image threshold intact. A known clipped title can block
        # gameplay. observe() still requires an independent result control.
        if (best[1]=='victory' and best[0]>=.74) or (best[1]=='defeat' and best[0]>=.84):
            from .resources import LocalOCR
            if self.result_ocr is None:
                self.result_ocr=LocalOCR()
            title=self.result_ocr.read(frame.crop((800,343,1120,426))).strip().upper()
            if best[1]=='defeat':
                # A left-side tower tooltip can obscure YOU while leaving
                # LOST intact. Require the registered shape and both reads.
                if (title.split()==['R','TOWER','U','LOST']
                        and self.result_ocr.read(frame.crop((948,352,1110,414))).upper()=='LOST'):
                    return 'defeat',0
                return None
            if title=='TRIUMPH!':
                # OCR matches the canonical positions; a template offset here
                # can reflect font animation rather than a moved result panel.
                return 'victory',0
            if (title.lstrip('•').split()==['TRIUMP','YOUR']
                    and self.result_ocr.read(frame.crop((800,343,1050,426))).upper()=='TRIUMP'):
                return 'victory',0
        return None

    def align_result(self, frame, location=None):
        location=location or self.result_location(frame)
        if location is None or location[1]==0:
            return frame
        dy=location[1]
        aligned=frame.copy()
        aligned.paste(frame.crop((630,330+dy,1290,805+dy)),(630,330))
        return aligned

    def result_banner(self, frame):
        """One located banner blocks gameplay; controls/metadata still certify it."""
        location=self.result_location(frame)
        return location[0] if location else None

    def observe(self, frame: Image.Image) -> Observation:
        if frame.size != self.size:
            return Observation("unknown", 0.0, {}, "Uncalibrated client dimensions.")
        location=self.result_location(frame)
        if location:
            frame=self.align_result(frame,location)
        scores = {state: min(max((label_overlap if state in {'victory','defeat'} and index>0 else overlap)(ink(frame.crop(box), colored), template)
                                 for box in boxes for template in templates)
                             for index,(boxes, templates, colored) in enumerate(anchors))
                  for state, anchors in self.anchors.items()}
        banner=location[0] if location else None
        if banner and scores[banner]<.90:
            # The hover animation changes font size continuously. Confirm the
            # actual action text instead of adding templates for each size.
            # Lazy import keeps resources' ink/overlap dependency acyclic.
            from .resources import LocalOCR
            if self.result_ocr is None:
                self.result_ocr=LocalOCR()
            if banner == 'defeat':
                box, caption = (701, 745, 968, 790), ['Return', 'To', 'Lobby']
            else:
                box, caption = self.anchors['victory'][1][0][0], ['Play', 'Again']
            crop=frame.crop(box)
            samples=(crop,ink(crop,True)) if banner=='defeat' else (crop,)
            if any(self.result_ocr.read(sample).casefold().split()==[word.casefold() for word in caption]
                   for sample in samples):
                scores[banner]=.90
        if banner and scores[banner]<.90:
            return Observation('unknown',round(scores[banner],4),scores,
                               'Result banner is visible but its controls are not confirmed.')
        ranked = sorted(scores, key=scores.get, reverse=True)
        # This known overlay intentionally leaves the map-vote HUD visible.
        # Its modal controls must block every action on that underlying screen.
        if scores.get("vip_maps", 0) >= 0.90:
            ranked = [state for state in ranked if state != "map_vote"]
        if scores.get("match_ready", 0) >= 0.90:
            ranked = [state for state in ranked if state != "in_match"]
        if scores.get("defeat", 0) >= 0.90:
            ranked = [state for state in ranked if state not in {"in_match", "match_ready"}]
        if scores.get('victory',0)>=.90:
            ranked=[state for state in ranked if state not in {'in_match','match_ready'}]
        if scores.get('login_rewards',0)>=.90:
            ranked=[state for state in ranked if state!='lobby']
        if scores.get('inventory_scout',0)>=.90:
            ranked=[state for state in ranked if state not in {'inventory_list','inventory_list_2192','inventory_search_2192'}]
        elif scores.get('inventory_list_2192',0)>=.90:
            ranked=[state for state in ranked if state not in {'inventory_list','inventory_search_2192'}]
        elif scores.get('inventory_list',0)>=.90:
            ranked=[state for state in ranked if state!='inventory_search_2192']
        best = ranked[0]
        if scores[best] < 0.90:
            return Observation("unknown", round(scores[best], 4), scores, "Missing or low-confidence anchors.")
        # A second state is ambiguous only if it ALSO meets the positive
        # .90 acceptance threshold. Shared squad headers can score .83 on
        # the wrong mode while the true mode independently scores .99.
        if len(ranked) > 1 and scores[ranked[1]] >= 0.90:
            return Observation("unknown", round(scores[best], 4), scores, "Conflicting screen states.")
        return Observation(best, round(scores[best], 4), scores)


class StableState:
    def __init__(self, frames=2):
        if not 2 <= frames <= 10:
            raise ValueError("Require 2..10 consecutive confirmations.")
        self.required, self.last, self.count = frames, "unknown", 0

    def update(self, state):
        self.count = self.count + 1 if state == self.last else 1
        self.last = state
        return state if state != "unknown" and self.count >= self.required else "unknown"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, help="Offline image; sends no input")
    parser.add_argument("--frames", type=int, default=1, help="Bounded foreground observation count")
    parser.add_argument("--interval", type=float, default=0.5)
    args = parser.parse_args(argv)
    if not 1 <= args.frames <= 1200 or not 0.2 <= args.interval <= 5:
        parser.error("Use 1..1200 frames and 0.2..5 seconds interval.")
    observer = Observer()
    if args.image:
        with Image.open(args.image) as frame:
            print(json.dumps(asdict(observer.observe(frame)), indent=2))
        return 0
    from .phase1 import capture, locate_roblox
    stable = StableState()
    window = locate_roblox()
    try:
        for _ in range(args.frames):
            result = observer.observe(capture(window))
            print(json.dumps({**asdict(result), "stable": stable.update(result.state)}), flush=True)
            if args.frames > 1:
                time.sleep(args.interval)
    except (RuntimeError, OSError) as exc:
        print(f"OBSERVER_STOP: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
