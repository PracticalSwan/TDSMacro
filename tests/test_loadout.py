import sys
import unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
try:
    from tds_auto.loadout import verify_inventory
except ImportError:
    verify_inventory=None

class LoadoutTests(unittest.TestCase):
    def frame(self):
        with Image.open(ROOT/'tests/fixtures/inventory_scout_slot1.png') as frame:
            return frame.copy()

    def test_live_golden_scout_only_slot1_is_accepted(self):
        self.assertIsNotNone(verify_inventory,'read-only Golden Scout baseline check is missing')
        self.assertIsNone(verify_inventory(self.frame()))

    def test_portrait_and_skin_changes_do_not_affect_identity(self):
        self.assertIsNotNone(verify_inventory)
        frame=self.frame()
        for x in (1155,1240,1325,1410,1495):
            ImageDraw.Draw(frame).rectangle((x-25,750,x+25,805),fill='magenta')
        self.assertIsNone(verify_inventory(frame))

    def test_missing_golden_marker_is_rejected(self):
        self.assertIsNotNone(verify_inventory)
        frame=self.frame();ImageDraw.Draw(frame).rectangle((1180,720,1208,754),fill='black')
        self.assertIn('Golden',verify_inventory(frame))

    def test_blank_or_wrong_state_is_rejected(self):
        self.assertIsNotNone(verify_inventory)
        self.assertIsNotNone(verify_inventory(Image.new('RGB',(1920,991))))
