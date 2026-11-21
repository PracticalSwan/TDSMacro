"""Retired route-5 terrain must fail closed against the pinned v0.3.1 atlas."""
import sys,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from tds_auto.hardcore_vision import WretchedRoute

def frame(name):
    output=Image.new("RGB",(1920,991))
    with Image.open(ROOT/"tests/fixtures"/name) as img:
        output.paste(img.crop((0,0,330,450)),(430,290))
        output.paste(img.crop((330,0,660,450)),(1180,290))
    return output

class Route5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route=WretchedRoute("wretched_front_hardcore_v2")

    def test_old_occluded_checkpoint_five_rejected(self):
        x=frame("hardcore_route05_occluded_terrain_only.png")
        self.assertEqual(self.route.matching_steps(x,range(len(self.route.steps))),[])
        for j in (3,4,6):
            self.assertFalse(self.route.matches(x,j))

    def test_old_route_five_baseline_rejected(self):
        self.assertEqual(self.route.matching_steps(frame("hardcore_route05_baseline_terrain_only.png"),range(len(self.route.steps))),[])

    def test_old_previous_checkpoint_four_rejected(self):
        x=frame("hardcore_route04_new_terrain_only.png")
        self.assertEqual(self.route.matching_steps(x,range(len(self.route.steps))),[])
        self.assertFalse(self.route.matches(x,5))

    def test_blank_terrain_not_five(self):
        self.assertFalse(self.route.matches(Image.new("RGB",(1920,991)),5))

if __name__=="__main__":
    unittest.main()
