"""Read-only OCR integration checks on small account-free HUD fixtures."""
import sys
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
try:
    from tds_auto.resources import HudReader, parse_cash, parse_count, parse_level, parse_wave
except ImportError:
    HudReader = None


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(HudReader, "cash/count/level reader has not been implemented")

    def test_real_hud_cash_and_count_before_and_after_placement(self):
        reader = HudReader()
        for file, cash, count in (("hud_750", 750, 0), ("hud_500", 500, 1), ("hud_350", 350, 1)):
            with self.subTest(file=file), Image.open(ROOT / "tests/fixtures" / f"{file}.png") as frame:
                result = reader.read(frame)
                self.assertEqual((result.cash, result.tower_count), (cash, count))

    def test_selected_level_and_next_cost_change_after_upgrade(self):
        reader = HudReader()
        for file, level, cost in (("hud_500", 0, 150), ("hud_350", 1, 600)):
            with self.subTest(file=file), Image.open(ROOT / "tests/fixtures" / f"{file}.png") as frame:
                result = reader.read(frame)
                self.assertEqual((result.tower_name, result.level, result.upgrade_cost), ("Scout", level, cost))

    def test_unambiguous_higher_level_text_is_supported(self):
        for level in (2,3,4):
            with Image.open(ROOT/'tests/fixtures'/f'hud_level{level}_synthetic.png') as frame:
                self.assertEqual(HudReader().read(frame).level,level)

    def test_live_level2_cash_517_survives_ocr_polarity_error(self):
        with Image.open(ROOT/'tests/fixtures/hud_517_level2.png') as frame:
            result=HudReader().read(frame)
            self.assertEqual((result.cash,result.level,result.upgrade_cost),(517,2,1800))

    def test_hardcore_native_farm_level1_in_tight_labeled_crop(self):
        with Image.open(ROOT/'tests/fixtures/hardcore_f2_level1_narrow_crop_20261120.png') as frame:
            result=HudReader(hardcore=True).read(frame)
        self.assertEqual((result.tower_name,result.level),('Farm',1))

    def test_hardcore_selected_farm_uses_mask_when_native_title_ocr_is_empty(self):
        reader = HudReader(hardcore=True)
        frame = Image.new('RGB', (1920, 991))
        with Image.open(ROOT/'tests/fixtures/hardcore_farm_title_native_blank_ocr.png') as title:
            frame.paste(title, reader.title_box[:2])
        self.assertEqual(reader.read(frame).tower_name, 'Farm')
        frame.paste('black', reader.title_box)
        self.assertIsNone(reader.read(frame).tower_name)

    def test_hardcore_second_native_farm_level1_uses_bounded_variant(self):
        with Image.open(ROOT/'tests/fixtures/hardcore_f2_level1_offset_20261120.png') as frame:
            result=HudReader(hardcore=True).read(frame)
        self.assertEqual((result.tower_name,result.level),('Farm',1))

    def test_preview_count_ocr_uses_alternate_polarity_without_guessing(self):
        with Image.open(ROOT/'tests/fixtures/hud_preview_count1.png') as frame:
            self.assertEqual(HudReader().read(frame).tower_count,1)

    def test_cash_digits_are_read_when_dollar_sign_confuses_ocr(self):
        with Image.open(ROOT/'tests/fixtures/hud_cash355.png') as frame:
            self.assertEqual(HudReader().read(frame).cash,355)

    def test_cash_uses_conservative_lower_amount_when_displays_differ(self):
        with Image.open(ROOT/'tests/fixtures/hud_cash626_agreement.png') as frame:
            self.assertEqual(HudReader().read(frame).cash,626)
        with Image.open(ROOT/'tests/fixtures/hud_cash_disagreement.png') as frame:
            self.assertEqual(HudReader().read(frame).cash,626)
        with Image.open(ROOT/'tests/fixtures/hud_dollar_as5_379.png') as frame:
            self.assertEqual(HudReader().read(frame).cash,379)
        with Image.open(ROOT/'tests/fixtures/hud_cash_animation43_45.png') as frame:
            self.assertEqual(HudReader().read(frame).cash,43)

    def test_green_upgrade_cost_1800_uses_color_mask_and_enabled_background(self):
        with Image.open(ROOT/'tests/fixtures/hud_green1800.png') as frame:
            h=HudReader().read(frame)
            self.assertEqual((h.level,h.upgrade_cost,h.upgrade_affordable),(2,1800,True))

    def test_live_maxed_scout_requires_full_upgrade_label(self):
        with Image.open(ROOT/'tests/fixtures/hud_max4.png') as frame:
            h=HudReader().read(frame)
            self.assertEqual(h.level,4)
            self.assertTrue(h.maxed)
            self.assertFalse(h.upgrade_affordable)

    def test_level_glyph_tolerates_observed_single_pixel_horizontal_layout_shift(self):
        for name in ('hud_shifted_level0','hud_xy_shift_level0'):
            with Image.open(ROOT/'tests/fixtures'/f'{name}.png') as frame:
                self.assertEqual(HudReader().read(frame).level,0)

    def test_hovered_scout_tooltip_proves_only_a_selection_target(self):
        from tds_auto import resources
        self.assertTrue(hasattr(resources,'hovered_scout_at'))
        with Image.open(ROOT/'tests/fixtures/scout_hover_no_selection.png') as frame:
            self.assertTrue(resources.hovered_scout_at(frame,(1020,328)))
            frame=frame.copy()
        frame.paste('black',(1030,254,1180,335))
        self.assertFalse(resources.hovered_scout_at(frame,(1020,328)))
        self.assertFalse(resources.hovered_scout_at(frame,(1800,300)))

    def test_unreadable_hud_does_not_invent_resources(self):
        result = HudReader().read(Image.new("RGB", (1920, 991)))
        self.assertIsNone(result.cash)
        self.assertIsNone(result.tower_count)
        self.assertIsNone(result.level)

    def test_cash_parser_rejects_guessing_and_ambiguous_values(self):
        for text in ("$I50", "$1.2K", "$-2", "$1,20", "150 600", "", "$10000000"):
            self.assertIsNone(parse_cash(text))
        self.assertEqual(parse_cash("$1,250"), 1250)
        self.assertEqual(parse_cash("$0"), 0)

    def test_tower_count_rejects_other_limits_or_overflow(self):
        self.assertEqual(parse_count("1 / 40"), 1)
        for text in ("41/40", "1/6", "I/40", "40", ""):
            self.assertIsNone(parse_count(text))

    def test_level_parser_requires_explicit_label(self):
        self.assertEqual(parse_level("Level: 1"), 1)
        for text in ("Cost: 150", "Level: I", "Level: 99", ""):
            self.assertIsNone(parse_level(text))

    def test_hardcore_wave11_requires_two_independently_valid_crops(self):
        from tds_auto.resources import read_hardcore_wave
        with Image.open(ROOT/'tests/fixtures/hardcore_wave11_native_ui_crop.png') as crop:
            frame=Image.new('RGB',(1920,991))
            frame.paste(crop,(542,69))
        ocr=HudReader(hardcore=True).ocr
        self.assertEqual(read_hardcore_wave(frame,ocr),11)
        frame.paste('black',(595,83,669,117))
        self.assertIsNone(read_hardcore_wave(frame,ocr))

    def test_live_easy_wave_fraction_is_read_without_confusing_total(self):
        with Image.open(ROOT / "tests/fixtures/hud_wave4.png") as frame:
            self.assertEqual(HudReader().read(frame).wave, 4)
        with Image.open(ROOT/'tests/fixtures/hud_wave12.png') as frame:
            self.assertEqual(HudReader().read(frame).wave,12)
        with Image.open(ROOT/'tests/fixtures/hud_wave9.png') as frame:
            self.assertEqual(HudReader().read(frame).wave,9)
        self.assertEqual(parse_wave("4 / 20"), 4)
        for text in ("4 / 40", "21 / 20", "--", "I / 20", "20"):
            self.assertIsNone(parse_wave(text))

    def test_seventh_tower_counter_is_confirmed_from_its_ui_glyphs(self):
        with Image.open(ROOT/'tests/fixtures/hud_count_seven.png') as frame:
            hud=HudReader().read(frame)
            self.assertEqual((hud.cash,hud.tower_count),(3293,7))
            frame.paste('black',(1294,940,1370,974))
            self.assertIsNone(HudReader().read(frame).tower_count)
