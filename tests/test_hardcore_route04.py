"""Historical pre-v0.3.1 checkpoint tiles must not authorize the single new route."""
import sys
import unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from tds_auto.hardcore_vision import WretchedRoute

def frame_from_terrain(name):
    path=ROOT/"tests"/"fixtures"/name
    out=Image.new("RGB",(1920,991))
    with Image.open(path) as tiles:
        out.paste(tiles.crop((0,0,330,450)),(430,290))
        out.paste(tiles.crop((330,0,660,450)),(1180,290))
    return out

class WretchedRouteCheckpoint4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route=WretchedRoute("wretched_front_hardcore_v2")

    def test_old_occluded_checkpoint_four_rejected(self):
        frame=frame_from_terrain("hardcore_route04_occluded_terrain_only.png")
        self.assertEqual(self.route.matching_steps(frame,range(len(self.route.steps))),[])
        self.assertFalse(self.route.matches(frame,3))
        self.assertFalse(self.route.matches(frame,5))

    def test_old_unobstructed_checkpoint_four_rejected(self):
        frame=frame_from_terrain("hardcore_route04_baseline_terrain_only.png")
        self.assertEqual(self.route.matching_steps(frame,range(len(self.route.steps))),[])

    def test_old_checkpoint_three_rejected(self):
        frame=frame_from_terrain("hardcore_route03_terrain_only.png")
        self.assertEqual(self.route.matching_steps(frame,range(len(self.route.steps))),[])
        self.assertFalse(self.route.matches(frame,4))

    def test_blank_terrain_does_not_match(self):
        self.assertFalse(self.route.matches(Image.new("RGB",(1920,991)),4))

if __name__=="__main__":
    unittest.main()
