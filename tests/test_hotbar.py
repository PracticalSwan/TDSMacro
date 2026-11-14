import sys
import unittest
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
try:
    from tds_auto.hotbar import tower_hotbar
except ImportError:
    tower_hotbar=None


class HotbarTests(unittest.TestCase):
    def test_large_ui_empty_slots_ignore_dim_green_terrain_but_reject_a_second_price(self):
        with Image.open(ROOT/'tests/fixtures/hotbar_settings_large.png') as source:
            frame=source.copy()
        self.assertTrue(tower_hotbar(frame))
        with Image.open(ROOT/'assets/ui_2191/hotbar_price_1.png') as price:
            frame.paste(price,(833,947))
        self.assertFalse(tower_hotbar(frame))

    def test_towers_and_consumables_are_distinguished_before_slot_keys(self):
        self.assertIsNotNone(tower_hotbar,"hotbar mode gate has not been implemented")
        for name, expected in (("hotbar_towers",True),("hotbar_items",False)):
            with Image.open(ROOT/'tests/fixtures'/f'{name}.png') as frame:
                self.assertEqual(tower_hotbar(frame,slot=2),expected)
        self.assertFalse(tower_hotbar(Image.new('RGB',(1920,991))))

    def test_new_baseline_accepts_only_scout_slot1_with_other_slots_empty(self):
        frame=Image.new('RGB',(1920,991))
        with Image.open(ROOT/'assets/ui_2191/hotbar_price_1.png') as price:
            frame.paste(price,(733,947))
            self.assertTrue(tower_hotbar(frame))
            frame.paste(price,(833,947))
            self.assertFalse(tower_hotbar(frame))
        with Image.open(ROOT/'tests/fixtures/hotbar_towers.png') as old:
            self.assertFalse(tower_hotbar(old))

    def test_actual_price_changes_are_read_without_tower_icons(self):
        from tds_auto.hotbar import read_hotbar
        for cost in (175,250,300):
            frame=Image.new('RGB',(1920,991))
            draw=ImageDraw.Draw(frame)
            draw.text((734,947),f'${cost}',font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',20),fill=(0,255,0))
            draw.rectangle((720,890,805,940),fill='magenta')
            result=read_hotbar(frame)
            self.assertTrue(result.valid)
            self.assertEqual(result.price,cost)
