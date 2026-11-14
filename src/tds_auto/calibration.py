"""Provenance, viewport and camera checks for the supervised overhead trial."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
import cv2
import numpy as np

from .strategy import read_strategy
from .observer import ink

ROOT = Path(__file__).resolve().parents[2]


def load_profile(path):
    profile = json.loads(Path(path).read_text(encoding="utf-8"))
    # The executable strategy is mandatory. A private historical source is
    # optional provenance, never a dependency of the public calibrated profile.
    for key in (('source','strategy') if 'source' in profile else ('strategy',)):
        target = (ROOT / profile[key]).resolve()
        if not target.is_relative_to(ROOT / "strategies"):
            raise ValueError("Profile strategy path is outside the strategy directory.")
        if hashlib.sha256(target.read_bytes()).hexdigest() != profile[key + "_sha256"]:
            raise ValueError(f"{key} integrity changed; recalibration required.")
    strategy = read_strategy(ROOT / profile["strategy"])
    if (strategy.map_name, strategy.difficulty, strategy.source_width, strategy.source_height) != (
            profile["map"], profile["mode"], *profile["size"]):
        raise ValueError("Profile metadata and strategy disagree.")
    if profile["slot"] not in range(1, 6) or profile["tower"] != "Scout":
        raise ValueError("Only the observed Scout loadout is supported.")
    if any(step.args[2] != profile["slot"] for step in strategy.steps if step.operation == "SpawnTower"):
        raise ValueError("Strategy slot differs from calibrated slot.")
    return profile, strategy


class CameraGate:
    def __init__(self, profile_path):
        self.profile, strategy = load_profile(profile_path)
        scene_path = (Path(profile_path).parent / self.profile['scene']).resolve()
        if not scene_path.is_relative_to(Path(profile_path).parent.resolve()):
            raise ValueError('Scene path must remain inside calibration directory.')
        positions=np.float32([step.args[:2] for step in strategy.steps if step.operation=="SpawnTower"])
        low,high=positions.min(axis=0),positions.max(axis=0)
        self.extent=np.float32([[low[0],low[1]],[high[0],low[1]],[low[0],high[1]],[high[0],high[1]]])
        self.landmarks = []
        for landmark in self.profile["landmarks"]:
            path = (Path(profile_path).parent / landmark["file"]).resolve()
            if not path.is_relative_to(Path(profile_path).parent.resolve()):
                raise ValueError("Landmark path must remain inside calibration directory.")
            with Image.open(path) as image:
                self.landmarks.append((tuple(landmark["box"]), image.convert("RGB")))
        if len(self.landmarks) < 2:
            raise ValueError("At least two camera landmarks are required.")
        self.bound = None
        self.prepared_features = None
        with Image.open(scene_path) as scene:
            if scene.size != tuple(self.profile['size']):
                raise ValueError('Scene dimensions do not match the calibrated viewport.')
            self.reference = np.asarray(scene.convert("L"))
        self.mask = np.zeros(self.reference.shape, dtype=np.uint8)
        for left, top, right, bottom in self.profile["scene_rois"]:
            self.mask[top:bottom, left:right] = 255
        # Use identical ROI context for reference/live descriptors. Range fills
        # reduce terrain contrast, so retain more low-contrast features while
        # keeping the same inlier, both-sides and drift requirements.
        self.reference=np.where(self.mask!=0,self.reference,0).astype(np.uint8)
        self.detector = cv2.SIFT_create(nfeatures=4000, contrastThreshold=0.001)
        self.keypoints, self.descriptors = self.detector.detectAndCompute(self.reference, self.mask)

    def features(self, frame):
        current = np.where(self.mask != 0, np.asarray(frame.convert('L')), 0).astype(np.uint8)
        return self.detector.detectAndCompute(current, self.mask)

    def estimate(self, frame, reference=None):
        if frame.size != tuple(self.profile["size"]):
            return None
        reference_keys,reference_descriptors=reference if reference is not None else (self.keypoints,self.descriptors)
        keypoints, descriptors = self.features(frame)
        if descriptors is None or reference_descriptors is None:
            return None
        pairs = cv2.BFMatcher(cv2.NORM_L2).knnMatch(reference_descriptors, descriptors, k=2)
        good = [pair[0] for pair in pairs if len(pair) == 2 and pair[0].distance < 0.70 * pair[1].distance]
        if len(good) < 30:
            return None
        source = np.float32([reference_keys[m.queryIdx].pt for m in good])
        target = np.float32([keypoints[m.trainIdx].pt for m in good])
        cv2.setRNGSeed(0)
        matrix, inliers = cv2.estimateAffinePartial2D(source, target, method=cv2.RANSAC,
                                                    ransacReprojThreshold=2.0, maxIters=1000)
        if matrix is None or inliers is None:
            return None
        selected = inliers.ravel().astype(bool)
        if selected.sum() < 60 or selected.mean() < 0.50:
            return None
        # Require observations on both sides of the road, not one repeated prop.
        if (source[selected, 0] < 900).sum() < 10 or (source[selected, 0] > 1000).sum() < 10:
            return None
        return matrix

    def bind(self, frame):
        """Bind a small fresh-match variation once, before any placement."""
        matrix = self.estimate(frame)
        if matrix is None:
            return False
        scale = float(np.hypot(matrix[0, 0], matrix[1, 0]))
        angle = float(np.degrees(np.arctan2(matrix[1, 0], matrix[0, 0])))
        points = self.extent
        transformed = cv2.transform(points[None], matrix)[0]
        if not 0.975 <= scale <= 1.025 or abs(angle) > 1.0 or np.max(np.linalg.norm(transformed - points, axis=1)) > 10:
            return False
        self.bound = matrix
        # The original scene certifies setup; this verified frame is the fixed
        # reference for drift during this match. Never update it after placement.
        self.prepared_features = self.features(frame)
        return True

    def map_point(self, point):
        if self.bound is None:
            return tuple(point)
        mapped = cv2.transform(np.float32([[point]]), self.bound)[0, 0]
        return tuple(round(float(value)) for value in mapped)

    def check(self, frame):
        """True: matching pose; False: measured mismatch; None: insufficient evidence."""
        if frame.size != tuple(self.profile["size"]):
            return False
        if self.bound is not None:
            current = self.estimate(frame,self.prepared_features)
            if current is None:
                return None
            points = self.extent[None]
            prepared = cv2.transform(points,self.bound)
            drift = (cv2.transform(prepared,current)-prepared if self.prepared_features is not None
                     else cv2.transform(points,current)-prepared)
            return bool(np.max(np.linalg.norm(drift, axis=2)) <= 2.0)
        for box, template in self.landmarks:
            sample = frame.crop(box).convert("RGB")
            delta = ImageStat.Stat(ImageChops.difference(sample, template))
            if max(delta.mean) > 0.8:
                return False
        return True


def valid_preview(frame, x, y):
    if frame.size != (1920, 991) or not 40 <= x < 1880 or not 50 <= y < 940:
        return False
    pixels = list(frame.crop((x - 18, y - 18, x + 18, y + 18)).convert("RGB").get_flattened_data())
    red = sum(r > 180 and r > g * 1.7 and r > b * 1.7 for r, g, b in pixels)
    white = sum(r > 180 and g > 180 and b > 180 for r, g, b in pixels)
    if red >= 8 or white < 40:
        return False
    # A selected existing tower can also have a white outline. Require the
    # actual placement prompt as a second independent precondition.
    from .resources import LocalOCR
    crop=frame.crop((x + 15, y + 30, x + 150, y + 65))
    ocr=LocalOCR()
    return any('place' in ocr.read(sample).casefold().split() for sample in (crop,ink(crop)))
