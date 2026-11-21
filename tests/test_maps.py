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
    def test_v2200_vote_one_at_two_angles_does_not_match_zero(self):
        from tds_auto.maps import badge_is_one
        for name,expected in (
            ('clear',True),('close',True),
            ('zero_left',False),('zero_right',False),
        ):
            with self.subTest(name=name):
                with Image.open(ROOT/'tests/fixtures'/f'vote_badge_2200_{name}.png') as image:
                    self.assertEqual(
                        badge_is_one(image,(0,0,image.width,image.height)),expected)

    def test_board_detection_only_processes_its_header_bands_and_keeps_screen_coordinates(self):
        from tds_auto import maps
        from unittest.mock import patch
        import numpy as np
        convert=np.asarray
        for name,read in (('vote_spawn_row.png',maps.spawn_board_row),('boards_read_distance.png',maps.read_boards)):
            with self.subTest(name=name),Image.open(ROOT/'tests/fixtures'/name) as frame:
                areas=[]
                def measured(image,*args,**kwargs):
                    if isinstance(image,Image.Image):areas.append(image.width*image.height)
                    return convert(image,*args,**kwargs)
                with patch('tds_auto.maps.np.asarray',side_effect=measured):result=read(frame)
                if read is maps.spawn_board_row:
                    self.assertTrue(980<result[0]<1020 and 295<result[1]<320)
                else:
                    self.assertEqual(len(result),4)
                    self.assertEqual(find_target(result).index,1)
                    self.assertTrue(all(180<=board.box[1]<315 for board in result))
                self.assertLessEqual(max(areas),1920*135,'Unused world/HUD pixels must not enter header color analysis.')

    def test_tight_header_read_recovers_complete_phrase_but_never_guesses_partial(self):
        from tds_auto.maps import visible_target
        with Image.open(ROOT/'tests/fixtures/boards_title_raw_partial.png') as frame:
            target=visible_target(frame)
            self.assertIsNotNone(target,'The complete Dead Ahead phrase is visible in this real frame.')
            self.assertEqual(target.index,1)
            frame.paste('black',(554,254,642,283))
            self.assertIsNone(visible_target(frame),'Dead alone cannot authorize more walking.')

    def test_word_crops_recover_second_actual_partial_header_view(self):
        from tds_auto.maps import visible_target
        with Image.open(ROOT/'tests/fixtures/boards_title_raw_partial_2.png') as frame:
            target=visible_target(frame)
            self.assertIsNotNone(target)
            self.assertEqual(target.index,1)
            frame.paste('black',(560,254,650,285))
            self.assertIsNone(visible_target(frame))

    def test_vip_override_prompt_requires_keycap_and_literal_caption(self):
        from tds_auto import maps
        self.assertTrue(callable(getattr(maps,'vip_prompt',None)),'VIP approach has no proximity checkpoint.')
        with Image.open(ROOT/'tests/fixtures/vip_override_prompt.png') as frame:
            self.assertTrue(maps.vip_prompt(frame))
            frame.paste('black',(1030,550,1280,605))
            self.assertFalse(maps.vip_prompt(frame))
        with Image.open(ROOT/'tests/fixtures/vote_prompt.png') as frame:
            self.assertFalse(maps.vip_prompt(frame))

    def test_recorded_vip_failure_roi_keeps_both_exact_prompt_cues_required(self):
        from tds_auto.maps import vip_prompt
        with Image.open(ROOT/'tests/fixtures/vip_override_b_roi.png') as source:
            frame=source.copy()
        self.assertTrue(vip_prompt(frame),'The recorded final approach frame contains a complete E keycap and Override Map label.')
        frame.paste('black',(1117,717,1290,752))
        self.assertFalse(vip_prompt(frame),'A detected E keycap without its literal caption cannot authorize VIP interaction.')
        with Image.open(ROOT/'tests/fixtures/vip_override_b_roi.png') as source:
            clipped=source.copy()
        clipped.paste('black',(1182,700,1237,713))
        self.assertFalse(vip_prompt(clipped),'A clipped E keycap is not a proximity confirmation.')
        with Image.open(ROOT/'tests/fixtures/vote_prompt.png') as frame:
            self.assertFalse(vip_prompt(frame),'A generic Vote E prompt is not Override Map.')
        self.assertFalse(vip_prompt(Image.new('RGB',(1000,750))))

    def test_recorded_post_vote_a_and_c_rois_recover_only_the_complete_title(self):
        from tds_auto.maps import read_headers,visible_target
        for name in ('post_vote_header_a_roi.png','post_vote_header_c_roi.png'):
            with self.subTest(name=name),Image.open(ROOT/'tests/fixtures'/name) as source:
                frame=source.copy()
                headers=read_headers(frame,after_vote=True)
                self.assertEqual(len(headers),1)
                self.assertEqual(headers[0].title,'Dead Ahead')
                target=visible_target(frame,after_vote=True)
                self.assertIsNotNone(target)
                self.assertEqual(target.title,'Dead Ahead')
                frame.paste('black',target.box)
                self.assertIsNone(visible_target(frame,after_vote=True),'A partial or removed title must remain unreadable.')

    def test_post_vote_diagnostics_keep_only_whitelisted_title_tokens(self):
        from tds_auto.maps import visible_target
        with Image.open(ROOT/'tests/fixtures/post_vote_header_a_roi.png') as source:
            frame=source.copy()
        diagnostics={}
        target=visible_target(frame,after_vote=True,diagnostics=diagnostics)
        self.assertEqual(target.title,'Dead Ahead')
        self.assertEqual(diagnostics,{'header_count':1,'title_tokens':['dead','ahead']})

    def test_voting_floor_requires_stone_on_both_sides_of_the_avatar(self):
        from tds_auto import maps
        self.assertTrue(callable(getattr(maps,'voting_floor',None)),'Voting approach has no floor checkpoint.')
        for name,expected in [('stone',True),('grass',False),('decoration',False)]:
            with Image.open(ROOT/'tests/fixtures'/f'vote_floor_{name}.png') as frame:
                self.assertEqual(maps.voting_floor(frame),expected,name)
                if expected:
                    frame.paste('black',(835,680,875,725))
                    self.assertFalse(maps.voting_floor(frame),'One stone patch is insufficient.')
        self.assertFalse(maps.voting_floor(Image.new('RGB',(1000,750))))

    def test_walkway_edge_retains_one_stone_support_but_decoration_does_not(self):
        from tds_auto.maps import voting_floor
        with Image.open(ROOT/'tests/fixtures/vote_floor_edge.png') as frame:
            self.assertFalse(voting_floor(frame))
            self.assertTrue(voting_floor(frame,require_both=False))
        with Image.open(ROOT/'tests/fixtures/vote_floor_decoration.png') as frame:
            self.assertFalse(voting_floor(frame,require_both=False))

    def test_strafe_requires_margin_before_the_curved_grass_edge(self):
        from tds_auto.maps import voting_floor
        for name,expected in [('vote_floor_margin_safe.png',True),('vote_floor_margin_edge.png',False)]:
            with self.subTest(name=name),Image.open(ROOT/'tests/fixtures'/name) as frame:
                self.assertTrue(voting_floor(frame))
                self.assertEqual(voting_floor(frame,for_strafe=True),expected)

    def test_wretched_front_dark_stone_uses_its_live_calibrated_threshold(self):
        from tds_auto.maps import voting_floor
        with Image.open(ROOT/'tests/fixtures/hardcore_wretched_floor.png') as source:
            frame=source.copy()
        self.assertFalse(voting_floor(frame),'Golden Scout threshold must stay unchanged.')
        self.assertTrue(voting_floor(frame,map_name='Wretched Front'))
        self.assertTrue(voting_floor(frame,require_both=False,map_name='Wretched Front'))
        frame.paste('black',(1045,680,1085,725))
        self.assertFalse(voting_floor(frame,map_name='Wretched Front'))
        self.assertTrue(voting_floor(frame,require_both=False,map_name='Wretched Front'))

    def test_wretched_front_shadowed_stone_retains_bilateral_and_strafe_support(self):
        from tds_auto.maps import voting_floor
        with Image.open(ROOT/'tests/fixtures/hardcore_wretched_floor_shadow.png') as frame:
            self.assertTrue(voting_floor(frame,map_name='Wretched Front'))
            self.assertTrue(voting_floor(frame,require_both=False,map_name='Wretched Front'))
            self.assertTrue(voting_floor(frame,for_strafe=True,map_name='Wretched Front'))
        with Image.open(ROOT/'tests/fixtures/hardcore_wretched_floor_deep_shadow.png') as frame:
            self.assertFalse(voting_floor(frame),'Golden Scout keeps its original threshold.')
            self.assertTrue(voting_floor(frame,map_name='Wretched Front'))
            self.assertTrue(voting_floor(frame,for_strafe=True,map_name='Wretched Front'))
        with Image.open(ROOT/'tests/fixtures/vote_floor_edge.png') as frame:
            self.assertFalse(voting_floor(frame,map_name='Wretched Front'))
            self.assertTrue(voting_floor(frame,require_both=False,map_name='Wretched Front'))
        with Image.open(ROOT/'tests/fixtures/vote_floor_decoration.png') as frame:
            self.assertFalse(voting_floor(frame,require_both=False,map_name='Wretched Front'))

    def test_wretched_front_near_board_purple_stone_keeps_bilateral_floor_support(self):
        from tds_auto.maps import voting_floor
        with Image.open(ROOT/'tests/fixtures/hardcore_wretched_near_floor.png') as frame:
            self.assertFalse(voting_floor(frame),'Golden Scout must keep its neutral-stone threshold.')
            self.assertTrue(voting_floor(frame,map_name='Wretched Front'))
            self.assertTrue(voting_floor(frame,for_strafe=True,map_name='Wretched Front'))
        for name in ('vote_floor_edge.png','vote_floor_decoration.png'):
            with self.subTest(name=name),Image.open(ROOT/'tests/fixtures'/name) as frame:
                self.assertFalse(voting_floor(frame,map_name='Wretched Front'))
                self.assertEqual(voting_floor(frame,require_both=False,map_name='Wretched Front'),name=='vote_floor_edge.png')

    def test_post_vote_backstep_keeps_the_entire_lower_header(self):
        from tds_auto.maps import visible_target
        for name in ['boards_post_vote_low_3.png','boards_post_vote_low_4.png']:
            with self.subTest(name=name),Image.open(ROOT/'tests/fixtures'/name) as frame:
                self.assertIsNone(visible_target(frame))
                target=visible_target(frame,after_vote=True)
                self.assertIsNotNone(target)
                self.assertEqual(target.title,'Dead Ahead')
                # The second word must remain independently present.
                frame.paste('black',(target.box[0]+(target.box[2]-target.box[0])//2,target.box[1],target.box[2],target.box[3]))
                self.assertIsNone(visible_target(frame,after_vote=True))

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

    def test_narrow_wretched_ribbons_preserve_the_four_physical_board_indices(self):
        from tds_auto.maps import read_boards,find_target,spawn_board_row
        with Image.open(ROOT/'tests/fixtures/hardcore_wretched_board_row.png') as frame:
            self.assertIsNotNone(spawn_board_row(frame),'The four-banner row must be present.')
            boards=read_boards(frame)
            self.assertEqual(len(boards),4,[(board.index,board.title) for board in boards])
            target=find_target(boards,'Wretched Front')
            self.assertIsNotNone(target,[(board.index,board.title) for board in boards])
            self.assertEqual(target.index,4)

    def test_wretched_front_title_recovers_from_the_live_low_contrast_banner(self):
        from tds_auto.maps import read_boards,find_target
        with Image.open(ROOT/'tests/fixtures/hardcore_wretched_board_row_ocr_fallback.png') as frame:
            boards=read_boards(frame)
            self.assertEqual(len(boards),4,[(board.index,board.title) for board in boards])
            target=find_target(boards,'Wretched Front')
            self.assertIsNotNone(target,[(board.index,board.title) for board in boards])
            self.assertEqual(target.index,4)

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

    def test_current_hardcore_solo_header_uses_wide_fallback_when_narrow_ocr_is_ambiguous(self):
        from tds_auto.maps import vote_players
        with Image.open(ROOT/'tests/fixtures/hardcore_solo_player_count.png') as frame:
            self.assertEqual(vote_players(frame),1)

    def test_solo_count_accepts_exact_token_with_ocr_noise_and_rejects_conflicting_reads(self):
        from tds_auto.maps import vote_players
        from unittest.mock import patch
        frame=Image.new('RGB',(1920,991))
        with patch('tds_auto.maps.LocalOCR') as ocr:
            ocr.return_value.read.side_effect=['PLAYERS (V6)','PLAYERS (1/6) IIP']
            self.assertEqual(vote_players(frame),1)
        with patch('tds_auto.maps.LocalOCR') as ocr:
            ocr.return_value.read.side_effect=['PLAYERS (1/6)','PLAYERS (2/6)']
            self.assertIsNone(vote_players(frame))

    def test_solo_count_uses_bounded_grayscale_fallback_after_raw_reads_fail(self):
        from tds_auto.maps import vote_players
        from unittest.mock import patch
        frame=Image.new('RGB',(1920,991))
        with patch('tds_auto.maps.LocalOCR') as ocr:
            ocr.return_value.read.side_effect=[
                'PLAYEYSN6)','', 'PLAYERS (1/6)', 'PLAYERS (116)', 'PLAYERS (1/6)'
            ]
            self.assertEqual(vote_players(frame),1)

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

    def test_wretched_front_close_vote_prompt_uses_target_anchored_low_contrast_read(self):
        from tds_auto.maps import Board,read_headers,title_matches,vote_prompt,visible_target
        with Image.open(ROOT/'tests/fixtures/hardcore_wretched_close_vote_prompt.png') as frame:
            target=visible_target(frame,'Wretched Front')
            self.assertIsNotNone(target)
            self.assertEqual(target.index,4)
            self.assertTrue(vote_prompt(frame,target))
            self.assertFalse(vote_prompt(frame),'Wretched-specific sensitivity requires an identified target.')
            wrong=Board(3,(634,253,879,293),'Wretched Front')
            self.assertFalse(vote_prompt(frame,wrong))

    def test_wretched_front_close_title_uses_the_lower_header_band(self):
        from tds_auto.maps import read_headers,visible_target
        with Image.open(ROOT/'tests/fixtures/hardcore_wretched_header_below_normal_band.png') as frame:
            self.assertFalse(any(board.title=='Wretched Front' for board in read_headers(frame)))
            target=visible_target(frame,'Wretched Front')
            self.assertIsNotNone(target)
            self.assertEqual(target.index,4)

    def test_wretched_front_close_target_remains_identifiable_when_board_one_is_clipped(self):
        from tds_auto.maps import read_headers,visible_target
        with Image.open(ROOT/'tests/fixtures/hardcore_wretched_vote_prompt_clipped_board1.png') as frame:
            headers=read_headers(frame,after_vote=True)
            self.assertEqual(len(headers),3)
            target=visible_target(frame,'Wretched Front')
            self.assertIsNotNone(target)
            self.assertEqual(target.title,'Wretched Front')
            self.assertEqual(target.index,3,'This index is view-relative and must be replaced by the stored physical index.')

    def test_map_vote_hover_fallback_requires_the_independent_vote_room_labels(self):
        from tds_auto.maps import map_vote_screen
        with Image.open(ROOT/'tests/fixtures/map_vote_hover_inventory.png') as frame:
            self.assertTrue(map_vote_screen(frame))
            frame=frame.copy()
        with Image.open(ROOT/'tests/fixtures/map_vote_red_instruction.png') as instruction:
            frame.paste(instruction,(560,170))
        self.assertTrue(map_vote_screen(frame),'Red live instruction text must remain readable.')
        frame.paste((0,0,0),(560,170,1370,225))
        self.assertFalse(map_vote_screen(frame),'The title alone cannot establish map-vote state.')
        self.assertFalse(map_vote_screen(Image.new('RGB',(1920,991))))
        self.assertFalse(map_vote_screen(Image.new('RGB',(1000,750))))

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
