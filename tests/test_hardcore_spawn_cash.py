"""Strict two-view Hardcore cash OCR fallback on a privacy-sanitized HUD sample."""
import sys
import unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from tds_auto.resources import HudReader

class HardcoreSpawnCashTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with Image.open(ROOT/"tests/fixtures/hardcore_spawn_cash_1250.png") as im:
            cls.frame=im.copy()

    def test_spawn_cash_1250_not_lost_to_comma_as_brace_ocr(self):
        hud=HudReader(hardcore=True).read(self.frame)
        self.assertEqual((hud.cash,hud.tower_count),(1250,0))

    def test_blank_cash_never_licenses_spending(self):
        frame=self.frame.copy()
        frame.paste((0,0,0),(1260,878,1415,935))
        self.assertIsNone(HudReader(hardcore=True).read(frame).cash)

if __name__=="__main__":
    unittest.main()
