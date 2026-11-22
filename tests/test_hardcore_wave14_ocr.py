"""Strict fallback for real wave-14 HUD OCR overlay ambiguity."""
import sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tds_auto.resources import LocalOCR,read_hardcore_wave

class HardcoreWave14OCRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Image.open(ROOT/'tests/fixtures/hardcore_wave14_ocr_crops.png').convert('RGB')
        cls.ocr=LocalOCR()
    def frame(self):
        im=Image.new('RGB',(1920,991),'black')
        im.paste(self.source,(518,50))
        return im
    def test_actual_hardcore_wave14_wrong_leading_one_is_recovered(self):
        self.assertEqual(read_hardcore_wave(self.frame(),self.ocr),14)
    def test_second_native_wave14_overlay_uses_two_ink_crops(self):
        with Image.open(ROOT/'tests/fixtures/hardcore_wave14_ocr_variant_20261120.png') as fragment:
            frame=Image.new('RGB',(1920,991),'black')
            frame.paste(fragment,(542,69))
        self.assertEqual(read_hardcore_wave(frame,self.ocr),14)

    def test_native_wave12_fraction_remains_exact(self):
        with Image.open(ROOT/'tests/fixtures/hardcore_wave12_fraction_native_20261122.png') as fragment:
            frame=Image.new('RGB',(1920,991),'black')
            frame.paste(fragment,(542,69))
        self.assertEqual(read_hardcore_wave(frame,self.ocr),12)

    def test_second_native_wave14_missing_total_is_rejected(self):
        with Image.open(ROOT/'tests/fixtures/hardcore_wave14_ocr_variant_20261120.png') as fragment:
            frame=Image.new('RGB',(1920,991),'black')
            frame.paste(fragment,(542,69))
        ImageDraw.Draw(frame).rectangle((605,76,699,129),fill='black')
        self.assertIsNone(read_hardcore_wave(frame,self.ocr))

    def test_missing_total_45_stays_unverified(self):
        frame=self.frame()
        ImageDraw.Draw(frame).rectangle((610,70,707,130),fill='black')
        self.assertIsNone(read_hardcore_wave(frame,self.ocr))
    def test_blank_frame_stays_unverified(self):
        self.assertIsNone(read_hardcore_wave(Image.new('RGB',(1920,991)),self.ocr))
    def test_incorrect_size_stays_unverified(self):
        self.assertIsNone(read_hardcore_wave(Image.new('RGB',(1920,900)),self.ocr))
if __name__=='__main__':
    unittest.main()
