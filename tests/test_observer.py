"""Sanitized real UI frames and adversarial variants; observer never imports input."""
import sys
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
try:
    from tds_auto.observer import Observer, StableState
except ImportError:
    Observer = StableState = None


class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Observer, "visual observer is not implemented")
        self.observer = Observer(ROOT / "assets" / "ui_2191" / "manifest.json")

    def test_encountered_states_on_independent_sanitized_frames(self):
        for name in ("lobby", "play_menu", "survival_menu", "squad_easy", "map_vote", "settings", "inventory_scout", "loading", "vip_maps", "match_ready", "in_match", "defeat", "disconnect", "victory", "login_rewards"):
            with self.subTest(name=name):
                with Image.open(ROOT / "tests" / "fixtures" / f"{name}.png") as frame:
                    self.assertEqual(self.observer.observe(frame).state, name)

    def test_blank_unfamiliar_and_resized_images_are_unknown(self):
        for frame in (Image.new("RGB", (1920, 991)), Image.new("RGB", (1920, 991), "white"),
                      Image.new("RGB", (1002, 750), "green")):
            self.assertEqual(self.observer.observe(frame).state, "unknown")

    def test_lobby_normal_button_and_hover_button_are_both_supported(self):
        for name in ("lobby", "lobby_normal"):
            with Image.open(ROOT / "tests/fixtures" / f"{name}.png") as frame:
                self.assertEqual(self.observer.observe(frame).state,"lobby")

    def test_current_inventory_scout_title_variant(self):
        with Image.open(ROOT/'tests/fixtures/inventory_scout_slot1.png') as frame:
            self.assertEqual(self.observer.observe(frame).state,'inventory_scout')

    def test_inventory_list_and_scout_details_are_distinct(self):
        with Image.open(ROOT/'tests/fixtures/inventory_list.png') as frame:
            self.assertEqual(self.observer.observe(frame).state,'inventory_list')
        from PIL import ImageChops
        with Image.open(ROOT/'tests/fixtures/inventory_list.png') as a, Image.open(ROOT/'tests/fixtures/inventory_scout_slot1.png') as b:
            frame=a.copy()
            for boxes,_,_ in self.observer.anchors['inventory_scout']:
                for box in boxes:
                    frame.paste(b.crop(box),box[:2])
            self.assertEqual(self.observer.observe(frame).state,'inventory_scout')

    def test_one_anchor_is_insufficient(self):
        with Image.open(ROOT / "tests" / "fixtures" / "lobby.png") as source:
            frame = source.copy()
        ImageDraw.Draw(frame).rectangle((100, 400, 250, 480), fill="black")
        self.assertEqual(self.observer.observe(frame).state, "unknown")

    def test_wrong_mode_does_not_pass_easy_precondition(self):
        with Image.open(ROOT / "tests" / "fixtures" / "squad_easy.png") as source:
            frame = source.copy()
        ImageDraw.Draw(frame).rectangle((752, 190, 970, 220), fill="black")
        self.assertEqual(self.observer.observe(frame).state, "unknown")

    def test_conflicting_states_are_unknown(self):
        from PIL import ImageChops
        with Image.open(ROOT / "tests" / "fixtures" / "lobby.png") as a:
            with Image.open(ROOT / "tests" / "fixtures" / "squad_easy.png") as b:
                frame = ImageChops.lighter(a, b)
        self.assertEqual(self.observer.observe(frame).state, "unknown")

    def test_state_must_repeat_and_unknown_resets_confirmation(self):
        stable = StableState(2)
        self.assertEqual(stable.update("lobby"), "unknown")
        self.assertEqual(stable.update("lobby"), "lobby")
        self.assertEqual(stable.update("unknown"), "unknown")
        self.assertEqual(stable.update("lobby"), "unknown")

    def test_vip_overlay_blocks_underlying_map_vote_state(self):
        from PIL import ImageChops
        with Image.open(ROOT / "tests/fixtures/map_vote.png") as a:
            with Image.open(ROOT / "tests/fixtures/vip_maps.png") as b:
                frame = ImageChops.lighter(a, b)
        self.assertEqual(self.observer.observe(frame).state, "vip_maps")

    def test_defeat_blocks_underlying_active_match_hud(self):
        from PIL import ImageChops
        with Image.open(ROOT / "tests/fixtures/in_match.png") as a:
            with Image.open(ROOT / "tests/fixtures/defeat.png") as b:
                self.assertEqual(self.observer.observe(ImageChops.lighter(a,b)).state, "defeat")

    def test_victory_blocks_underlying_active_match_hud(self):
        from PIL import ImageChops
        with Image.open(ROOT/'tests/fixtures/in_match.png') as a, Image.open(ROOT/'tests/fixtures/victory.png') as b:
            self.assertEqual(self.observer.observe(ImageChops.lighter(a,b)).state,'victory')

    def test_login_rewards_blocks_underlying_lobby(self):
        from PIL import ImageChops
        with Image.open(ROOT/'tests/fixtures/lobby.png') as a, Image.open(ROOT/'tests/fixtures/login_rewards.png') as b:
            frame=a.copy()
            # Modal controls replace the underlying Play lettering; adding the
            # two text images would create an impossible ghosted Claim/Play UI.
            for boxes,_,_ in self.observer.anchors['login_rewards']:
                for box in boxes:
                    frame.paste(b.crop(box),box[:2])
            self.assertEqual(self.observer.observe(frame).state,'login_rewards')

    def test_login_rewards_accepts_claim_and_close_but_requires_both_anchors(self):
        for name in ('login_rewards.png','login_rewards_current.png'):
            with self.subTest(name=name),Image.open(ROOT/'tests/fixtures'/name) as frame:
                self.assertEqual(self.observer.observe(frame).state,'login_rewards')
                for missing in ((667,338,955,381),(910,773,1010,806)):
                    incomplete=frame.copy();incomplete.paste('black',missing)
                    self.assertNotEqual(self.observer.observe(incomplete).state,'login_rewards')



    def test_live_items_hover_uses_explicit_font_variant(self):
        with Image.open(ROOT/'tests/fixtures/lobby_items_hover.png') as frame:
            self.assertEqual(Observer().observe(frame).state,'lobby')


    def test_profile_tooltip_obscuring_play_is_rejected_and_upper_padding_is_clear(self):
        for name,expected in [('lobby_tooltip_obscured','unknown'),('lobby_tooltip_clear','lobby')]:
            with Image.open(ROOT/'tests/fixtures'/f'{name}.png') as frame:
                self.assertEqual(Observer().observe(frame).state,expected)


    def test_map_vote_buttons_survive_white_world_background_behind_the_title(self):
        with Image.open(ROOT/'tests/fixtures/map_vote_bright_background.png') as frame:
            self.assertEqual(Observer().observe(frame).state,'map_vote')


    def test_ready_hover_can_shift_the_neighbour_inventory_caption(self):
        with Image.open(ROOT/'tests/fixtures/map_vote_ready_hover_layout.png') as frame:
            self.assertEqual(Observer().observe(frame).state,'map_vote')


    def test_map_vote_still_requires_both_buttons_within_the_small_search_band(self):
        with Image.open(ROOT/'tests/fixtures/map_vote.png') as image:frame=image.copy()
        frame.paste('black',(650,760,835,805))
        self.assertEqual(Observer().observe(frame).state,'unknown')
        with Image.open(ROOT/'assets/ui_2191/map_vote_1.png') as label:
            frame.paste(label,(650,765))
        self.assertEqual(Observer().observe(frame).state,'unknown')


    def test_wave_counter_pulse_does_not_cover_the_static_wave_label(self):
        with Image.open(ROOT/'tests/fixtures/in_match_wave_pulse.png') as frame:
            self.assertEqual(Observer().observe(frame).state,'in_match')

    def test_normal_play_again_font_recognizes_victory_over_the_active_hud(self):
        for name in ['victory_normal_small','victory_hover_small']:
            with Image.open(ROOT/'tests/fixtures'/f'{name}.png') as image:frame=image.copy()
            self.assertEqual(Observer().observe(frame).state,'victory')
            frame.paste('black',(1008,752,1188,790))
            self.assertEqual(Observer().observe(frame).state,'unknown')


    def test_current_victory_panel_blocks_match_hud_when_title_font_changes(self):
        with Image.open(ROOT/'tests/fixtures/result_victory_current_panel.png') as source:
            frame=source.copy()
        self.assertEqual(self.observer.result_banner(frame),'victory')
        self.assertEqual(self.observer.observe(frame).state,'victory')
        frame.paste('black',(997,733,1213,799))
        self.assertIsNone(self.observer.result_banner(frame))
        self.assertNotEqual(self.observer.observe(frame).state,'victory')

    def test_actual_replay_hover_keeps_result_recognized_without_font_variants(self):
        with Image.open(ROOT/'tests/fixtures/victory_hover_animated.png') as source:
            frame=source.copy()
        self.assertEqual(self.observer.observe(frame).state,'victory')
        # A known banner cannot replace the missing action control.
        frame.paste('black',(1008,744,1188,798))
        self.assertEqual(self.observer.observe(frame).state,'unknown')

if __name__ == "__main__":
    unittest.main()
