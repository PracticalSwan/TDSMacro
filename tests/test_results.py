import unittest,sys
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
try:
    from tds_auto.results import ResultReader,parse_duration
except ImportError:
    ResultReader=None

class ResultTests(unittest.TestCase):
    def v052_panel(self,name):
        frame=Image.new('RGB',(1920,991))
        with Image.open(ROOT/'tests/fixtures'/name) as panel:
            frame.paste(panel,(625,330))
        return frame

    def test_native_obscured_triumph_requires_control_and_receipt_metadata(self):
        from tds_auto.results import GameResult

        frame=self.v052_panel('v052_golden_overlay.png')
        reader=ResultReader()
        self.assertEqual(reader.read(frame),GameResult('victory','Dead Ahead','Easy',20,456,450))
        for box in ((1150,473,1265,499),(1200,585,1265,612),(1160,548,1265,574),
                    (1225,510,1265,536),(969,733,1240,802)):
            with self.subTest(box=box):
                obscured=frame.copy()
                obscured.paste('black',box)
                self.assertEqual(reader.observer.result_banner(obscured),'victory')
                self.assertIsNone(reader.read(obscured))

    def test_native_victory_with_coin_caption_clipped_keeps_reward_unverified(self):
        from tds_auto.results import GameResult

        frame=self.v052_panel('v052_golden_clipped_coin.png')
        self.assertEqual(ResultReader().read(frame),GameResult('victory','Dead Ahead','Easy',20,454,None))

    def test_native_reversed_hardcore_wave_requires_label_and_value_in_place(self):
        from tds_auto.observer import Observer
        from tds_auto.resources import LocalOCR
        from tds_auto.results import HardcoreResult,read_hardcore_result

        frame=self.v052_panel('v052_hardcore_wave29.png')
        observer,ocr=Observer(),LocalOCR()
        self.assertEqual(read_hardcore_result(frame,observer,ocr),HardcoreResult('defeat',29,417,133))
        frame.paste('black',(1020,509,1135,541))
        self.assertIsNone(read_hardcore_result(frame,observer,ocr))

    def test_native_hardcore_defeat_with_farm_hover_blocks_input_and_reads_receipt(self):
        from tds_auto.observer import Observer
        from tds_auto.resources import LocalOCR
        from tds_auto.results import HardcoreResult,read_hardcore_result

        observer,ocr=Observer(),LocalOCR()
        for name in ('v052_hardcore_hover_defeat.png','v052_hardcore_tall_hover_defeat.png'):
            with self.subTest(name=name):
                frame=self.v052_panel(name)
                self.assertEqual(observer.result_banner(frame),'defeat')
                self.assertEqual(read_hardcore_result(frame,observer,ocr),HardcoreResult('defeat',10,107,1))
                frame.paste('black',(700,735,968,802))
                self.assertEqual(observer.result_banner(frame),'defeat')
                self.assertIsNone(read_hardcore_result(frame,observer,ocr))

    def test_real_victory_and_loss_have_verified_metadata(self):
        self.assertIsNotNone(ResultReader)
        reader=ResultReader()
        for name,status,seconds,coins in [('result_victory','victory',484,450),('result_defeat','defeat',524,250),('result_victory_7m42s','victory',462,450),('result_victory_7m44s','victory',464,450)]:
            with Image.open(ROOT/'tests/fixtures'/f'{name}.png') as frame:
                result=reader.read(frame)
                self.assertIsNotNone(result)
                self.assertEqual((result.status,result.map_name,result.difficulty,result.wave,result.duration_seconds,result.coins),(status,'Dead Ahead','Easy',20,seconds,coins))

    def test_banner_without_correct_map_metadata_is_insufficient(self):
        self.assertIsNotNone(ResultReader)
        with Image.open(ROOT/'tests/fixtures/result_victory.png') as source:frame=source.copy()
        ImageDraw.Draw(frame).rectangle((1150,473,1265,499),fill='black')
        self.assertIsNone(ResultReader().read(frame))
        self.assertIsNone(ResultReader().read(Image.new('RGB',(1920,991))))

    def test_duration_parser_requires_game_format_and_valid_seconds(self):
        self.assertIsNotNone(ResultReader)
        self.assertEqual(parse_duration('8m 4s'),484)
        self.assertEqual(parse_duration('45s'),45)
        for text in ('8:04','8m 99s','-1s','unknown'):
            self.assertIsNone(parse_duration(text))

    def test_current_victory_panel_requires_map_mode_wave_and_duration(self):
        with Image.open(ROOT/'tests/fixtures/result_victory_current_panel.png') as source:
            frame=source.copy()
        result=ResultReader().read(frame)
        self.assertIsNotNone(result)
        self.assertEqual((result.status,result.map_name,result.difficulty,result.wave,result.duration_seconds),
                         ('victory','Dead Ahead','Easy',20,464))
        frame.paste('black',(1150,473,1265,499))
        self.assertIsNone(ResultReader().read(frame))

    def test_reward_layout_can_shift_the_whole_result_panel(self):
        from tds_auto.observer import Observer
        with Image.open(ROOT/'tests/fixtures/result_victory_shifted.png') as frame:
            self.assertEqual(Observer().observe(frame).state,'victory')
            result=ResultReader().read(frame)
            self.assertIsNotNone(result)
            self.assertEqual((result.map_name,result.difficulty,result.wave,result.duration_seconds,result.coins),('Dead Ahead','Easy',20,464,450))

    def test_native_wave30_result_with_two_exact_ocr_confusions(self):
        # Native wave-30 result panel from long-run attempt 40. Outside the
        # result card is blacked out to exclude player/account information.
        from tds_auto.observer import Observer
        from tds_auto.resources import LocalOCR
        from tds_auto.results import HardcoreResult, read_hardcore_result
        with Image.open(ROOT/'tests/fixtures/hardcore_result_wave30_native_sanitized.png') as source:
            frame=source.convert('RGB')
        self.assertEqual(Observer().observe(frame).state,'defeat')
        self.assertEqual(read_hardcore_result(frame,Observer(),LocalOCR()),
                         HardcoreResult('defeat',30,463,137))
        frame.paste('black',(1090,473,1281,501))
        self.assertIsNone(read_hardcore_result(frame,Observer(),LocalOCR()))

    def test_current_hardcore_defeat_reads_the_wave_and_displayed_gems(self):
        from tds_auto.observer import Observer
        from tds_auto.resources import LocalOCR
        from tds_auto.results import HardcoreResult, read_hardcore_result

        for wave, duration, gems in ((12,134,4),(19,252,37)):
            with self.subTest(wave=wave):
                with Image.open(ROOT/'tests/fixtures'/f'hardcore_result_wave{wave}.png') as frame:
                    self.assertEqual(read_hardcore_result(frame, Observer(), LocalOCR()),
                                     HardcoreResult('defeat',wave,duration,gems))
                    self.assertIsNone(ResultReader().read(frame))

    def test_native_xp_result_reads_exact_clipped_wretched_fron(self):
        from tds_auto.observer import Observer
        from tds_auto.resources import LocalOCR
        from tds_auto.results import HardcoreResult, read_hardcore_result

        observer, ocr = Observer(), LocalOCR()
        with Image.open(ROOT/'tests/fixtures/hardcore_result_map_fron_native.png') as source:
            frame = source.convert('RGB')
        self.assertEqual(read_hardcore_result(frame, observer, ocr),
                         HardcoreResult('defeat', 30, 451, 137))
        frame.paste('black', (1090, 473, 1281, 501))
        self.assertIsNone(read_hardcore_result(frame, observer, ocr))

    def test_native_shifted_hardcore_receipt_with_broken_first_map_glyph(self):
        from tds_auto.observer import Observer
        from tds_auto.resources import LocalOCR
        from tds_auto.results import HardcoreResult, read_hardcore_result

        frame=self.v052_panel('v053_hardcore_cycle_024.png')
        observer,ocr=Observer(),LocalOCR()
        self.assertEqual(read_hardcore_result(frame,observer,ocr),HardcoreResult('defeat',30,463,137))
        for box in ((1138,473,1281,508),(1150,548,1282,576),(1150,584,1282,614),
                    (1020,510,1135,540),(700,735,968,803)):
            with self.subTest(box=box):
                obscured=frame.copy()
                obscured.paste('black',box)
                self.assertIsNone(read_hardcore_result(obscured,observer,ocr))
        wrong_map=frame.copy()
        with Image.open(ROOT/'tests/fixtures/result_victory.png') as golden:
            wrong_map.paste('black',(1138,473,1281,508))
            wrong_map.paste(golden.crop((1150,473,1265,499)),(1150,474))
        self.assertIsNone(read_hardcore_result(wrong_map,observer,ocr))
        frame.paste('black',(646,505,1010,717))
        self.assertEqual(read_hardcore_result(frame,observer,ocr),HardcoreResult('defeat',30,463,None))
