"""Live-capture regressions requiring local English Windows OCR; no input."""
import sys
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from tds_auto.recovery import close_prompt


class ClosePromptTests(unittest.TestCase):
    def test_actual_close_prompt_requires_title_and_both_buttons(self):
        with Image.open(Path(__file__).parent/'fixtures/roblox_close_prompt.png') as frame:
            self.assertTrue(close_prompt(frame))
            frame.paste('black',(650,694,954,736))
            self.assertFalse(close_prompt(frame))
        self.assertFalse(close_prompt(Image.new('RGB',(1920,991))))
