"""Hardcore cash: two matching bottom-HUD crops, no player-list dependency."""
import sys
import unittest
from pathlib import Path

from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from tds_auto.resources import HudReader,parse_cash,bottom_hud_cash_digits


class BottomHudCashTests(unittest.TestCase):
    @staticmethod
    def frame(filename):
        with Image.open(ROOT/"tests"/"fixtures"/filename) as fragment:
            frame=Image.new("RGB",(1920,991),"black")
            if fragment.size==(150,55):
                frame.paste(fragment,(1260,885))
            else:
                frame.paste(fragment.crop((0,0,135,45)),(1270,890))
            return frame

    def test_native_cash_punctuation_and_empty_plain_ocr(self):
        cases=(
            ("hardcore_cash_braced_native_rois.png",10085),
            ("hardcore_cash_semicolon_native_rois.png",16487),
            ("hardcore_cash_wave7_wide_2220.png",2220),
            ("hardcore_cash_player_dot_missing_1579.png",1579),
        )
        for file,expected in cases:
            with self.subTest(file=file):
                self.assertEqual(HudReader(hardcore=True).read(self.frame(file)).cash,expected)

    def test_non_digits_are_removed_only_from_bottom_cash(self):
        for text in ("16!487","16;487","16a487","16,487"):
            with self.subTest(text=text):
                self.assertEqual(bottom_hud_cash_digits(text),16487)
        self.assertIsNone(parse_cash("16!487"))  # Prices remain strict.
        self.assertIsNone(bottom_hud_cash_digits("unreadable"))

    def test_conflicting_masked_crops_reject_spending(self):
        frame=self.frame("hardcore_cash_empty_plain_masked_2220.png")
        reader=HudReader(hardcore=True)
        original=reader.ocr
        class ConflictingOCR:
            def read(self,crop):
                if crop.size==(127,42):
                    return "2,219"
                if crop.size==(150,55):
                    return "2,220" if crop.mode=="RGB" else ""
                return original.read(crop)
        reader.ocr=ConflictingOCR()
        self.assertIsNone(reader.read(frame).cash)

    def test_one_readable_crop_is_insufficient(self):
        frame=self.frame("hardcore_cash_empty_plain_masked_2220.png")
        reader=HudReader(hardcore=True)
        original=reader.ocr
        class OneCropOCR:
            reads=0
            def read(self,crop):
                if crop.size in ((127,42),(150,55)):
                    self.reads+=1
                    return "2,220" if self.reads==1 else ""
                return original.read(crop)
        reader.ocr=OneCropOCR()
        self.assertIsNone(reader.read(frame).cash)

    def test_no_bottom_cash_is_never_guessed(self):
        self.assertIsNone(HudReader(hardcore=True).read(Image.new("RGB",(1920,991))).cash)


if __name__=="__main__":
    unittest.main()
