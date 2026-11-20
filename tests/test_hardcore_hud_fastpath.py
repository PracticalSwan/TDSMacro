"""Fast-path readable Hardcore HUD without weakening ambiguous-cash fallbacks."""
import sys, unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from tds_auto.resources import HudReader
class CountingOCR:
    def __init__(self, delegate):
        self.delegate=delegate
        self.sizes=[]
    def read(self, crop):
        self.sizes.append(crop.size)
        return self.delegate.read(crop)
class FastPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir=ROOT/"tests/fixtures"
    def test_clean_hud_reads_four_bottom_ocr_variants(self):
        reader=HudReader(hardcore=True)
        counting=CountingOCR(reader.ocr)
        reader.ocr=counting
        with Image.open(self.dir/"hardcore_fast_clean_hud.png") as source:
            result=reader.read(source)
        self.assertEqual((result.cash,result.wave,result.tower_count),(1463,24,18))
        self.assertEqual(counting.sizes.count((112,28)),0)
    def test_corrupted_separator_uses_same_bottom_regions(self):
        reader=HudReader(hardcore=True)
        counting=CountingOCR(reader.ocr)
        reader.ocr=counting
        with Image.open(self.dir/"hardcore_fast_ambiguous_hud.png") as source:
            result=reader.read(source)
        self.assertEqual((result.cash,result.wave,result.tower_count),(10085,25,18))
        self.assertEqual(counting.sizes.count((112,28)),0)
        self.assertGreaterEqual(counting.sizes.count((150,55)),1)
if __name__=="__main__":
    unittest.main()
