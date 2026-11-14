import unittest,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
try:
    from tds_auto.maps import read_boards,find_target,Board
except ImportError:
    read_boards=None

class MapTests(unittest.TestCase):
    def test_read_distance_keeps_four_physical_headers_visible(self):
        with Image.open(ROOT/'tests/fixtures/boards_close_clipped.png') as frame:
            self.assertEqual(read_boards(frame),())
        with Image.open(ROOT/'tests/fixtures/boards_read_distance.png') as frame:
            boards=read_boards(frame)
            self.assertEqual(len(boards),4)
            self.assertEqual(find_target(boards).index,1)

    def test_distant_board_row_requires_four_aligned_banners(self):
        from tds_auto.maps import spawn_board_row
        with Image.open(ROOT/'tests/fixtures/vote_spawn_row.png') as frame:
            center=spawn_board_row(frame)
            self.assertIsNotNone(center)
            self.assertTrue(980<center[0]<1020)
            self.assertTrue(295<center[1]<320)
            frame.paste('black',(895,290,990,325))
            self.assertIsNone(spawn_board_row(frame))
        with Image.open(ROOT/'tests/fixtures/vote_spawn_water.png') as frame:
            self.assertIsNone(spawn_board_row(frame))

    def test_real_spawn_connected_red_header_still_detects_four_boards(self):
        from tds_auto.maps import spawn_board_row
        with Image.open(ROOT/'tests/fixtures/vote_spawn_connected_header.png') as source:
            frame=source.copy()
        row=spawn_board_row(frame)
        self.assertIsNotNone(row,'Four physical headers were visible despite one connected thumbnail.')
        self.assertTrue(905<row[0]<930, row)
        self.assertTrue(300<row[1]<312, row)
        frame.paste('black',(932,285,1015,318))
        self.assertIsNone(spawn_board_row(frame),'Three remaining headers must not pass.')

    def test_target_replaced_first_board_and_already_present_second_board(self):
        self.assertIsNotNone(read_boards,'read-only map board identification is missing')
        for name,index in [('boards_target1',1),('boards_target2',2),('boards_target4',4)]:
            with Image.open(ROOT/'tests/fixtures'/f'{name}.png') as frame:
                boards=read_boards(frame)
                self.assertEqual(len(boards),4)
                self.assertEqual(find_target(boards).index,index)

    def test_no_target_or_ambiguous_target_never_defaults_to_first(self):
        self.assertIsNotNone(read_boards)
        self.assertIsNone(find_target([Board(i,(0,0,200,40),'Unknown') for i in range(1,5)]))
        self.assertIsNone(find_target([Board(i,(0,0,200,40),'Dead Ahead') for i in range(1,5)]))
        self.assertIsNone(find_target([Board(1,(0,0,200,40),'Dead Ahead')]))

    def test_blank_and_wrong_geometry_have_no_boards(self):
        self.assertIsNotNone(read_boards)
        for frame in (Image.new('RGB',(1920,991)),Image.new('RGB',(1000,750))):
            self.assertEqual(read_boards(frame),())

    def test_visible_tracking_does_not_invent_physical_board_indices(self):
        from tds_auto.maps import visible_target
        with Image.open(ROOT/'tests/fixtures/boards_target2.png') as source:
            boards=read_boards(source)
            target=find_target(boards)
            frame=Image.new('RGB',source.size)
            x1,y1,x2,y2=target.box
            whole_header=(x1,y1,x2,y1+round((y2-y1)/.66)+3)
            frame.paste(source.crop(whole_header),whole_header[:2])
            self.assertEqual(read_boards(frame),())
            self.assertEqual(visible_target(frame).title,'Dead Ahead')

    def test_vip_requires_actual_target_card_not_query_rendering(self):
        from tds_auto.maps import vip_target_matches
        with Image.open(ROOT/'tests/fixtures/vip_search_target.png') as frame:
            self.assertTrue(vip_target_matches(frame))
            frame.paste('black',(660,217,796,252))
            self.assertTrue(vip_target_matches(frame))
            frame.paste('black',(635,350,752,398))
            self.assertFalse(vip_target_matches(frame))

    def test_search_caret_does_not_become_a_trailing_letter(self):
        from tds_auto.maps import vip_target_matches
        with Image.open(ROOT/'tests/fixtures/vip_search_caret.png') as frame:
            self.assertTrue(vip_target_matches(frame))

    def test_exact_vote_prompt_is_read_from_local_neutral_text(self):
        from tds_auto.maps import vote_prompt
        with Image.open(ROOT/'tests/fixtures/vote_prompt.png') as frame:
            self.assertTrue(vote_prompt(frame))
        self.assertFalse(vote_prompt(Image.new('RGB',(1920,991))))

    def test_vote_digit_template_distinguishes_one_from_real_zero_badges(self):
        from tds_auto.maps import badge_is_one
        with Image.open(ROOT/'tests/fixtures/vote_badges.png') as frame:
            self.assertTrue(badge_is_one(frame,(974,397,1023,446)))
            self.assertFalse(badge_is_one(frame,(1262,390,1313,437)))
            self.assertFalse(badge_is_one(frame,(1549,391,1611,439)))

    def test_board4_perspective_digit_is_one_and_its_neighbour_badges_are_zero(self):
        from tds_auto.maps import badge_is_one
        with Image.open(ROOT/'tests/fixtures/vote_board4_badges.png') as frame:
            self.assertTrue(badge_is_one(frame,(1052,391,1103,441)))
            for box in [(210,388,272,433),(526,382,572,425),(784,383,827,427)]:
                self.assertFalse(badge_is_one(frame,box))
            frame.paste('black',(1052,391,1103,441))
            self.assertFalse(badge_is_one(frame,(1052,391,1103,441)))

    def test_solo_player_count_is_read_without_names(self):
        from tds_auto.maps import solo_vote
        from unittest.mock import patch
        with Image.open(ROOT/'tests/fixtures/solo_vote_count.png') as frame:
            self.assertTrue(solo_vote(frame))
        with patch('tds_auto.maps.LocalOCR') as ocr:
            ocr.return_value.read.return_value='PLAYERS (2/6)'
            self.assertFalse(solo_vote(Image.new('RGB',(1920,991))))

    def test_vote_prompt_follows_keycap_when_camera_distance_changes(self):
        from tds_auto.maps import vote_prompt
        with Image.open(ROOT/'tests/fixtures/vote_prompt_lower.png') as frame:
            self.assertTrue(vote_prompt(frame))

    def test_vote_prompt_must_belong_to_the_target_header(self):
        from tds_auto.maps import vote_prompt,visible_target,Board
        with Image.open(ROOT/'tests/fixtures/vote_approach_ready.png') as frame:
            target=visible_target(frame)
            self.assertIsNotNone(target)
            self.assertTrue(vote_prompt(frame,target))
            wrong=Board(3,(target.box[0]+700,target.box[1],target.box[2]+700,target.box[3]),'Dead Ahead')
            self.assertFalse(vote_prompt(frame,wrong))

    def test_caret_inside_the_search_crop_does_not_break_exact_query_verification(self):
        from tds_auto.maps import vip_target_matches
        with Image.open(ROOT/'tests/fixtures/vip_search_caret_edge.png') as frame:
            self.assertTrue(vip_target_matches(frame))

    def test_red_map_thumbnail_is_not_a_fifth_board_header(self):
        with Image.open(ROOT/'tests/fixtures/boards_red_thumbnail.png') as frame:
            boards=read_boards(frame)
            self.assertEqual(len(boards),4)
            self.assertEqual([b.index for b in boards],[1,2,3,4])
            self.assertIsNone(find_target(boards))

    def test_scene_edge_beneath_query_is_not_an_extra_letter(self):
        from tds_auto.maps import vip_target_matches
        with Image.open(ROOT/'tests/fixtures/vip_query_scene_noise.png') as frame:
            self.assertTrue(vip_target_matches(frame))

    def test_title_phrase_tolerates_small_ocr_noise_but_not_another_map(self):
        from tds_auto.maps import title_matches
        for text in ('Dead Ahead','DeadAhead','Dead Ahead i','l Dead Ahead!','Dead Aheadi'):
            self.assertTrue(title_matches(text),text)
        for text in ('Undead Ahead','Dead Aheadish','Dead End','unknown'):
            self.assertFalse(title_matches(text),text)
        boards=[Board(i,(0,0,200,40),'Other') for i in range(1,5)]
        boards[2]=Board(3,(0,0,200,40),'l Dead Ahead!')
        self.assertEqual(find_target(boards).index,3)
        boards[3]=Board(4,(0,0,200,40),'Dead Aheadi')
        self.assertIsNone(find_target(boards))
