"""Cash decisions use bottom HUD only; no player-list / K abbreviation parsing."""
import sys
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from tds_auto.resources import HudReader


class BottomOnlyCashTests(unittest.TestCase):
    def frame(self, name):
        path=ROOT/"tests"/"fixtures"/name
        with Image.open(path) as fragments:
            image=Image.new("RGB",(1920,991),"black")
            if fragments.size==(150,55):
                image.paste(fragments,(1260,885))
            else:
                image.paste(fragments.crop((0,0,135,45)),(1270,890))
            # Player list is intentionally NOT pasted or needed.
            return image

    def test_native_corrupted_bottom_reads_work_without_player_list(self):
        for name, expected in [
            ("hardcore_cash_braced_native_rois.png", 10085),
            ("hardcore_cash_semicolon_native_rois.png", 16487),
            ("hardcore_cash_wave7_wide_2220.png", 2220),
            ("hardcore_cash_wave24_wide_16487.png", 16487),
            ("hardcore_cash_player_dot_missing_1579.png", 1579),
        ]:
            with self.subTest(name=name):
                reader=HudReader(hardcore=True)
                native=reader.ocr

                class NoPlayerListOCR:
                    def read(self, crop):
                        if crop.size in ((105,40),(70,29),(69,27)):
                            raise AssertionError("Cash reader inspected player list")
                        return native.read(crop)

                reader.ocr=NoPlayerListOCR()
                self.assertEqual(reader.read(self.frame(name)).cash, expected)

    def test_native_opening_cash_350_without_player_list(self):
        with Image.open(ROOT/"tests/fixtures/hardcore_cash_opening_350.png") as fragment:
            frame=Image.new("RGB",(1920,991),"black")
            frame.paste(fragment,(1260,885))
        self.assertEqual(HudReader(hardcore=True).read(frame).cash,350)

    def test_native_successful_run_low_cash_at_early_and_late_waves(self):
        for name,expected in (("hardcore_cash_opening_f2_650.png",650),
                              ("hardcore_cash_early_b1_104.png",104),
                              ("hardcore_cash_opening_f3_350.png",350),
                              ("hardcore_cash_late_b3_97.png",97)):
            with self.subTest(name=name):
                with Image.open(ROOT/"tests/fixtures"/name) as fragment:
                    frame=Image.new("RGB",(1920,991),"black")
                    frame.paste(fragment,(1260,885))
                self.assertEqual(HudReader(hardcore=True).read(frame).cash,expected)

    def test_no_bottom_digits_remains_unreadable_even_if_player_list_is_present(self):
        with Image.open(ROOT/"tests"/"fixtures"/"hardcore_cash_empty_plain_masked_2220.png") as fragments:
            frame=Image.new("RGB",(1920,991),"black")
            frame.paste(fragments.crop((135,0,260,50)),(1790,135))
        self.assertIsNone(HudReader(hardcore=True).read(frame).cash)

    def test_different_bottom_regions_disagree_and_stop(self):
        frame=self.frame("hardcore_cash_empty_plain_masked_2220.png")
        reader=HudReader(hardcore=True)
        native=reader.ocr
        class WrongCropOCR:
            def read(self, crop):
                if crop.size==(127,42):
                    return "2,219"
                if crop.size==(150,55):
                    return "2,220" if crop.mode=="RGB" else ""
                return native.read(crop)
        reader.ocr=WrongCropOCR()
        self.assertIsNone(reader.read(frame).cash)

if __name__=="__main__":
    unittest.main()
