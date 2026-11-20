"""The native back-path camera and placement checks for Wretched Front."""
from __future__ import annotations

import hashlib
import json
import re
from statistics import median_low

import cv2
import numpy as np
from PIL import Image, ImageOps

from .hardcore_plan import PROFILE_ID, ROOT
from .hotbar import green_ink
from .observer import ink
from .resources import parse_cash


PRICE_BOXES = {
    1: (733, 947, 798, 973),
    2: (822, 943, 905, 974),
    3: (925, 948, 1005, 973),
    4: (1025, 948, 1105, 973),
}

ROUTE_SIDES = ((430, 290, 760, 740), (1180, 290, 1510, 740))
ROUTE_TILE_SIZE = (66, 90)
WRETCHED_TRAVEL_PITCH = -350
ROUND_PREVIEW_RADIUS = 26
_ROUND_Y, _ROUND_X = np.ogrid[-ROUND_PREVIEW_RADIUS:ROUND_PREVIEW_RADIUS+1,
                             -ROUND_PREVIEW_RADIUS:ROUND_PREVIEW_RADIUS+1]
ROUND_PREVIEW_MASK = _ROUND_X ** 2 + _ROUND_Y ** 2 <= ROUND_PREVIEW_RADIUS ** 2
ROUTE_STEPS = (
    (('zoom', -8), ('orbit', 0, 650), ('orbit', 0, 650)),
    (('key', 'S', .65),),
    (('key', 'D', .30),),
    (('orbit', 0, -350),),
    (('key', 'A', .30),),
    (('key', 'S', .55),),
    (('key', 'S', .52),),
    (('key', 'D', .62),),
    (('key', 'S', .70),),
    (('key', 'S', .94),),
    (('orbit', 0, 650),),
)
ROUTE_STEPS_V2 = (
    (('orbit', 0, 650), ('orbit', 0, 650), ('zoom', -8)),
    (('key', 'S', .65),),
    (('key', 'A', .30), ('orbit', 0, WRETCHED_TRAVEL_PITCH)),
    (('key', 'S', .55),),
    (('key', 'D', .62),),
    (('key', 'S', .70),),
    (('key', 'S', .55),),
    (('orbit', 0, 650),),
)


def wretched_route_tiles(frame):
    return tuple(frame.crop(box).convert('L').resize(ROUTE_TILE_SIZE, Image.Resampling.BOX)
                 for box in ROUTE_SIDES)


class WretchedRoute:
    """Terrain-only checkpoints for the guarded walk from spawn past the gate."""
    def __init__(self, profile_id=PROFILE_ID):
        self.legacy = profile_id == PROFILE_ID
        self.steps = ROUTE_STEPS if self.legacy else ROUTE_STEPS_V2
        path = ROOT / 'calibrations' / f'{profile_id}.route.png'
        width, height = ROUTE_TILE_SIZE
        pair_width = width * len(ROUTE_SIDES)
        with Image.open(path) as atlas:
            variants, remainder = divmod(atlas.width, pair_width)
            if remainder or variants < 1 or atlas.height != height * len(self.steps):
                raise ValueError('Wretched route has the wrong number of landmarks.')
            self.gray_views = [
                [tuple(np.asarray(atlas.crop(
                    (x, step*height, x+width, (step+1)*height)).convert('L'))
                       for x in range(left, left+pair_width, width))
                 for left in range(0, atlas.width, pair_width)]
                for step in range(len(self.steps))
            ]
        self.views = [[tuple(cv2.Canny(tile, 18, 38) for tile in landmarks) for landmarks in variants]
                      for variants in self.gray_views]

    @staticmethod
    def _matching_pair(tiles, landmarks, margin, threshold):
        fits = [cv2.minMaxLoc(cv2.matchTemplate(actual, planned[margin:-margin, margin:-margin],
                                              cv2.TM_CCOEFF_NORMED))
                for actual, planned in zip(tiles, landmarks)]
        return all(score >= threshold for _, score, _, _ in fits) and all(
            abs(a-b) <= 1 for a,b in zip(fits[0][3], fits[1][3]))

    def matching_steps(self, frame, checkpoints):
        if frame.size != (1920, 991):
            return []
        gray = [np.asarray(tile) for tile in wretched_route_tiles(frame)]
        edges = [cv2.Canny(tile, 18, 38) for tile in gray]
        matches = []
        for index in checkpoints:
            if self.legacy and index in (6, 7):
                # These adjacent views flank a pillar and must remain distinct.
                if all(cv2.matchTemplate(actual, planned, cv2.TM_CCOEFF_NORMED)[0, 0] >= .84
                       for actual, planned in zip(edges, self.views[index][0])):
                    matches.append(index)
            elif any(self._matching_pair(edges, landmarks, 4, .65) for landmarks in self.views[index]):
                matches.append(index)
            elif not self.legacy:
                # Animated scenery can obscure broad tiles at steps 2-5.
                # Use only measured fixed rock/wall sections at each step,
                # preserving two independent matching landmarks and the
                # original .90 agreement threshold.
                stable_left = {2: np.s_[50:78,10:48],
                               5: np.s_[25:63,35:63]}
                stable_right = {2: np.s_[35:70,30:61],
                                3: np.s_[21:70,19:65],
                                4: np.s_[30:66,32:62],
                                5: np.s_[30:68,10:38]}
                right = stable_right.get(index, np.s_[:,:])
                left = stable_left.get(index, np.s_[:,:])
                if any(self._matching_pair((gray[0][left], gray[1][right]),
                                           (landmarks[0][left], landmarks[1][right]), 7, .90)
                       for landmarks in self.gray_views[index]):
                    matches.append(index)
        return matches

    def matches(self, frame, index):
        return bool(self.matching_steps(frame, (index,)))


class WretchedCamera:
    def __init__(self, plan, *, require_positions=True):
        directory = ROOT / 'calibrations'
        if plan.profile_id not in {PROFILE_ID, 'wretched_front_hardcore_v2'}:
            raise ValueError('Unknown Wretched Front profile.')
        profile = json.loads((directory / f'{plan.profile_id}.json').read_text(encoding='utf-8'))
        if plan.profile_id == PROFILE_ID:
            coordinates = profile['points']
        else:
            if profile['source_profile'] != PROFILE_ID:
                raise ValueError('Wretched v2 requires the verified back-path scene.')
            coordinates = profile['coordinates']
        self.size = (1920, 991)
        if (profile['profile_id'], profile['map'], profile['mode'], tuple(profile['size']), profile['dpi']) != (
                plan.profile_id, plan.map_name, plan.mode, self.size, 120):
            raise ValueError('Wretched camera profile metadata does not match the fixed strategy.')

        self.points = {name: tuple(point) for name, point in coordinates.items() if point is not None}
        required = {tower.tower_id for tower in plan.towers if not tower.optional}
        known = {tower.tower_id for tower in plan.towers}
        if (require_positions and not required.issubset(self.points)) or not set(self.points) <= known or any(
                len(point) != 2 or any(type(value) is not int for value in point)
                or not (80 <= point[0] < 1750 and 80 <= point[1] < 880)
                for point in self.points.values()) or len(set(self.points.values())) != len(self.points):
            raise ValueError('Wretched placement points must cover all required towers in the calibrated view.')

        scene_path = directory / f'{plan.profile_id}.scene.png'
        if hashlib.sha256(scene_path.read_bytes()).hexdigest() != profile['scene_sha256']:
            raise ValueError('Wretched camera landmarks changed. Recalibration is required.')
        with Image.open(scene_path) as scene:
            if scene.size != self.size or len(profile['landmarks']) < 3:
                raise ValueError('Wretched camera requires multiple landmarks in the supported viewport.')
            boxes = [tuple(box) for box in profile['landmarks']]
            self.first_alternate = None
            if plan.profile_id == 'wretched_front_hardcore_v2':
                original = boxes[0]
                self.first_alternate = (original, np.asarray(scene.crop(original).convert('L')))
                # Late-wave moving range rings can shift the match within both
                # the broad tile and its former tall rock crop. The small lower
                # fixed rock edge matches all observed wave-22/27/28 frames.
                # Keep three independent landmarks and the same consensus gate.
                x0, y0, _, _ = boxes[0]
                boxes[0] = (x0 + 10, y0 + 45, x0 + 40, y0 + 64)
                # A large right-wall crop sometimes registers 3px away from
                # the other two fixed rocks. This observed static subregion
                # agrees across failed checkpoint-8 and late-wave views.
                boxes[1] = (1468, 602, 1513, 662)
            self.landmarks = [(box, np.asarray(scene.crop(box).convert('L')))
                              for box in boxes]
        self.offset = None

    def estimate(self, frame, radius=40):
        if frame.size != self.size:
            return None
        def locate(landmark):
            (x0, y0, x1, y1), template = landmark
            search = np.asarray(frame.crop((x0-radius, y0-radius, x1+radius, y1+radius)).convert('L'))
            scores = cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED)
            _, score, _, (x, y) = cv2.minMaxLoc(scores)
            return (x-radius, y-radius) if score >= .88 else None

        offsets = [locate(landmark) for landmark in self.landmarks]
        if self.first_alternate is not None:
            # The wave-28 range ring affects the broad first landmark; a
            # moving effect at spawn can instead affect its short rock crop.
            # Use either view ONLY when it agrees with both independent rocks.
            other = offsets[1:]
            if any(item is None for item in other):
                return None
            candidates = [offsets[0], locate(self.first_alternate)]
            def consensus(candidate):
                if candidate is None:
                    return False
                triple = [candidate, *other]
                center = [median_low(axis) for axis in zip(*triple)]
                # The left fixed rock has measured 3px parallax in a
                # second native checkpoint-8 pose. Preserve the 2px bounds
                # on both independent right-side landmarks and subsequent
                # cross-frame camera drift; only the first rock may differ
                # by up to 4px from their median.
                return all(abs(item[axis]-center[axis]) <= (4 if i == 0 else 2)
                           for i,item in enumerate(triple) for axis in (0, 1))
            offsets[0] = next((candidate for candidate in candidates if consensus(candidate)), None)
        if any(item is None for item in offsets):
            return None
        dx, dy = (median_low(axis) for axis in zip(*offsets))
        if any(abs(item[axis]-(dx,dy)[axis]) > (
                4 if self.first_alternate is not None and i==0 else 2)
                for i,item in enumerate(offsets) for axis in (0,1)):
            return None
        return dx, dy

    def bind(self, frame):
        self.offset = self.estimate(frame)
        return self.offset is not None

    def check(self, frame):
        actual = self.estimate(frame)
        return self.offset is not None and actual is not None and all(
            abs(observed-expected) <= 2 for observed, expected in zip(actual, self.offset))

    def point(self, tower_id):
        if self.offset is None:
            raise ValueError('Bind the Wretched camera before mapping tower points.')
        x, y = self.points[tower_id]
        return x+self.offset[0], y+self.offset[1]


def wretched_preview(frame, point, ocr, *, round_footprint=False):
    """Require the prompt and a white footprint without an invalid red outline."""
    x, y = point
    if frame.size != (1920, 991) or not (40 <= x < 1763 and 50 <= y < 917):
        return False
    if round_footprint:
        # Ignore adjacent tower outlines outside the ghost's round footprint.
        r = ROUND_PREVIEW_RADIUS
        pixels = np.asarray(frame.crop((x-r, y-r, x+r+1, y+r+1)).convert('RGB'))[ROUND_PREVIEW_MASK]
    else:
        # Keep the square Farm footprint and omit path units below the prompt.
        pixels = np.asarray(frame.crop((x-39, y-40, x+35, y+27)).convert('RGB'))
    red, green, blue = np.moveaxis(pixels, -1, 0)
    invalid = (red > 195) & (green < 85) & (blue < 115)
    white = (red > 219) & (green > 219) & (blue > 219)
    if invalid.sum() > 40 or white.sum() < 110:
        return False
    caption = frame.crop((x+24, y+25, x+157, y+74))
    label = frame.crop((x+55, y+37, x+107, y+57))
    if ('place' in ocr.read(caption).casefold().split()
            or 'place' in ocr.read(ink(caption)).casefold().split()
            or ocr.read(label).casefold() == 'place'
            or ocr.read(ink(label)).casefold() == 'place'):
        return True
    if round_footprint:
        return False
    # In the live ten-Farm row the footprint remains white, but a one-pixel
    # camera/template registration changes the caption OCR from Place to blank.
    # Shift *only* the caption read, never the verified footprint or click point.
    shifted=frame.crop((x+23,y+24,x+156,y+73))
    return ('place' in ocr.read(shifted).casefold().split()
            or 'place' in ocr.read(ink(shifted)).casefold().split())


def wretched_price(frame, slot, ocr):
    if frame.size != (1920, 991) or slot not in PRICE_BOXES:
        return None
    text = ocr.read(green_ink(frame.crop(PRICE_BOXES[slot])))
    return parse_cash(text) if text.startswith('$') else None


def wretched_ready(frame, ocr):
    if frame.size != (1920, 991):
        return False
    title = frame.crop((825, 160, 933, 196))
    wide_title = frame.crop((819, 156, 945, 196))
    caption = any(ocr.read(sample).casefold() == 'ready?' for sample in (
        title, wide_title, ImageOps.invert(title.convert('RGB')), ImageOps.invert(wide_title.convert('RGB')),
        ink(frame.crop((830, 158, 935, 193)))))
    count = frame.crop((820, 195, 951, 220))
    button = frame.crop((984, 194, 1081, 218))
    return (caption and any(ocr.read(sample).casefold().split() == ['0/1', 'required']
                            for sample in (count, ink(count)))
            and any(ocr.read(sample).casefold() == 'ready' for sample in (button, ink(button))))


def wretched_match_ready(frame, observer, ocr):
    state = observer.observe(frame).state
    return state == 'match_ready' or (state == 'unknown' and wretched_ready(frame, ocr))


def wretched_hover(frame, point, tower, ocr):
    x, y = point
    if frame.size != (1920, 991) or not (10 <= x < 1730 and 88 <= y < 946):
        return False
    # Ignore common OCR glyphs in the detached blue level suffix. The exact
    # numeric level is required in the selected panel after the click.
    name = re.escape(tower)
    labeled = name + r'(?:\s*[|I](?:\s*Lv[. /]*[0-5lIoO])?)?'
    # Income popups can run through the ownership caption. Read the cyan text
    # separately so it still needs to spell out the full ownership label.
    region = frame.crop((x+10, y-66, x+178, y-39)).convert('RGB')
    red, green, blue = np.moveaxis(np.asarray(region).astype(np.int16), -1, 0)
    cyan = (green > 150) & (blue > 180) & (green > red + 25)
    owner = ocr.read(Image.fromarray(cyan.astype(np.uint8) * 255))
    if owner.casefold() == 'your tower':
        # A native F5 hover shifted the white Farm glyph boundary by two
        # pixels. Shift only the OCR read window; never the owned-tower
        # point, selection click, or subsequent tower/level verification.
        for dx in (0,-2,2):
            title=frame.crop((x+11+dx,y-32,x+190+dx,y+5)).convert('RGB')
            pixels=np.asarray(title)
            white=(pixels.min(axis=2)>169)&(pixels.max(axis=2)-pixels.min(axis=2)<32)
            identity=ocr.read(Image.fromarray(white.astype(np.uint8)*255))
            if re.fullmatch(name+r'(?:\s*[|I])?',identity,re.IGNORECASE):
                return True
            if re.fullmatch(labeled,ocr.read(title),re.IGNORECASE):
                return True
    caption = ocr.read(frame.crop((x+7, y-88, x+190, y+45)))
    return re.fullmatch(r'Your Tower\s+' + labeled, caption, re.IGNORECASE) is not None
