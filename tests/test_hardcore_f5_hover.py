"""Native two-pixel OCR crop drift must not reject an owned Farm."""
import sys
import unittest
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tds_auto.hardcore_vision import wretched_hover
from tds_auto.resources import LocalOCR


class FarmHoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with Image.open(ROOT/'tests/fixtures/hardcore_f5_hover_two_pixel_20261120.png') as im:
            cls.frame=im.copy()

    def test_native_owned_f5_label_with_two_pixel_read_drift(self):
        self.assertTrue(wretched_hover(self.frame,(639,521),'Farm',LocalOCR()))

    def test_other_tower_name_never_authorizes_farm_hover(self):
        self.assertFalse(wretched_hover(self.frame,(639,521),'Crook Boss',LocalOCR()))

    def test_missing_owner_caption_cannot_authorize_hover(self):
        frame=self.frame.copy()
        ImageDraw.Draw(frame).rectangle((645,455,835,482),fill='black')
        self.assertFalse(wretched_hover(frame,(639,521),'Farm',LocalOCR()))

if __name__=='__main__':
    unittest.main()
