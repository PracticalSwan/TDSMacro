"""Replay the observed F10 footprint/caption without archiving private full frames."""
import sys
import unittest
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from tds_auto.hardcore_vision import wretched_preview
from tds_auto.resources import LocalOCR

class F10PlacementPreviewTests(unittest.TestCase):
    def setUp(self):
        self.frame=Image.new("RGB",(1920,991))
        with Image.open(ROOT/"tests/fixtures/hardcore_f10_armed_preview.png") as crop:
            self.frame.paste(crop.convert("RGB"),(650,590))
        self.ocr=LocalOCR()

    def test_saved_armed_footprint_and_place_caption_are_readable(self):
        self.assertTrue(wretched_preview(self.frame,(724,640),self.ocr))

    def test_real_red_footprint_is_not_accepted(self):
        frame=self.frame.copy()
        ImageDraw.Draw(frame).rectangle((695,615,710,633),fill=(255,0,0))
        self.assertFalse(wretched_preview(frame,(724,640),self.ocr))

    def test_unnamed_or_unreadable_caption_is_rejected(self):
        frame=self.frame.copy()
        ImageDraw.Draw(frame).rectangle((747,663,900,720),fill="black")
        self.assertFalse(wretched_preview(frame,(724,640),self.ocr))

if __name__=="__main__":
    unittest.main()
