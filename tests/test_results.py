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
