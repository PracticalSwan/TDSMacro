"""Live-capture regressions requiring local English Windows OCR; no input."""
import sys
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from tds_auto.recovery import close_prompt,roblox_home


class ClosePromptTests(unittest.TestCase):
    def test_actual_close_prompt_requires_title_and_both_buttons(self):
        with Image.open(Path(__file__).parent/'fixtures/roblox_close_prompt.png') as frame:
            self.assertTrue(close_prompt(frame))
            frame.paste('black',(650,694,954,736))
            self.assertFalse(close_prompt(frame))
        self.assertFalse(close_prompt(Image.new('RGB',(1920,991))))


class RobloxHomeTests(unittest.TestCase):
    def test_current_sidebar_home_requires_all_four_exact_navigation_labels(self):
        path=Path(__file__).parent/'fixtures'/'roblox_home_current_nav.png'
        boxes=((10,16,95,84),(0,90,88,158),(0,170,88,240),(0,248,88,320))
        with Image.open(path) as source:
            frame=source.copy()
            self.assertTrue(roblox_home(frame))
            for box in boxes:
                changed=frame.copy()
                changed.paste('black',box)
                self.assertFalse(roblox_home(changed))
