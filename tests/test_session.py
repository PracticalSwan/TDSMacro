"""Controller boundary tests: fake OS and state frames, no live game input."""
import sys,unittest,tempfile,contextlib,io,json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tds_auto.control import GuardedInput,StopRun
from tds_auto.session import Session,SessionControl
from tds_auto.run import Playback,MatchFinished
from tds_auto.results import GameResult
from test_control import FakeOS

def vip_evidence(confirmed,score=None):
    return {'confirmed':confirmed,'keycap_score':score,'literal_caption':confirmed}

class SessionTests(unittest.TestCase):
    def test_normal_lobby_skips_the_login_rewards_click(self):
        self.state='lobby'
        readings=[]
        self.session.ocr=SimpleNamespace(read=lambda frame:readings.append(frame.size) or '')
        self.session.lobby()
        self.assertEqual(self.platform.events,[])
        self.assertEqual(readings,[])

    def test_login_claim_is_clicked_once_then_close_and_lobby_are_confirmed(self):
        self.state='login_rewards'
        readings=iter(['CLAIM','Claim','claim','Close','Close','Close',''])
        self.session.ocr=SimpleNamespace(read=lambda frame:next(readings,''))
        original=self.platform.emit
        def emit(kind,*args):
            original(kind,*args)
            if kind=='left_up':
                if self.platform.events.count(('left_down',))==2: self.state='lobby'
        self.platform.emit=emit
        self.session.lobby()
        self.assertEqual(self.platform.events.count(('left_down',)),2)
        self.assertEqual([e[1:] for e in self.platform.events if e[0]=='move'],[(1045,816),(1718,71)])
        self.assertEqual(self.state,'lobby')
        self.assertEqual(self.session.driver.before_click,self.session.click_gate)

    def test_already_claimed_login_overlay_dismisses_without_claiming(self):
        self.state='login_rewards'
        readings=iter(['Close','Close','Close'])
        self.session.ocr=SimpleNamespace(read=lambda frame:next(readings,''))
        original=self.platform.emit
        def emit(kind,*args):
            original(kind,*args)
            if kind=='left_up': self.state='lobby'
        self.platform.emit=emit
        self.session.lobby()
        self.assertEqual([e[1:] for e in self.platform.events if e[0]=='move'],[(1718,71)])
        self.assertEqual(self.platform.events.count(('left_down',)),1)
        self.assertEqual(self.state,'lobby')

    def test_claim_can_close_the_popup_directly_without_a_dismiss_click(self):
        self.state='login_rewards'
        self.session.ocr=SimpleNamespace(read=lambda frame:'CLAIM')
        original=self.platform.emit
        def emit(kind,*args):
            original(kind,*args)
            if kind=='left_up':self.state='lobby'
        self.platform.emit=emit
        self.session.lobby()
        self.assertEqual(self.platform.events.count(('left_down',)),1)
        self.assertEqual(self.state,'lobby')

    def test_changed_claim_label_before_click_is_refused(self):
        self.state='login_rewards'
        readings=iter(['Claim','Claim','close'])
        self.session.ocr=SimpleNamespace(read=lambda frame:next(readings,''))
        def refuse_transition(name):
            raise AssertionError('An uncertain claim must not dismiss the overlay.')
        self.session.transition=refuse_transition
        gate=self.session.driver.before_click
        with self.assertRaisesRegex(StopRun,'Claim label changed'):
            self.session.lobby()
        self.assertNotIn(('left_down',),self.platform.events)
        self.assertEqual(self.session.driver.before_click,gate)

    def test_delayed_claim_observation_never_sends_a_second_claim(self):
        self.state='login_rewards'
        readings=iter(['Claim','Claim'])
        self.session.ocr=SimpleNamespace(read=lambda frame:next(readings,'Claim'))
        original=self.platform.emit
        def emit(kind,*args):
            original(kind,*args)
            if kind=='left_up': self.state='login_rewards'
        self.platform.emit=emit
        def refuse_transition(name):
            raise AssertionError('A delayed claim must not be clicked or dismissed again.')
        self.session.transition=refuse_transition
        with self.assertRaisesRegex(StopRun,'login reward action did not settle'):
            self.session.lobby()
        self.assertEqual(self.platform.events.count(('left_down',)),1)
        self.assertEqual([e[1:] for e in self.platform.events if e[0]=='move'],[(1045,816)])
        self.assertGreaterEqual(self.platform.clock,8)

    def test_uncertain_login_caption_waits_bounded_and_never_clicks(self):
        self.state='login_rewards'
        self.session.ocr=SimpleNamespace(read=lambda frame:'')
        def refuse_transition(name):
            raise AssertionError('An unreadable caption must not dismiss the overlay.')
        self.session.transition=refuse_transition
        with self.assertRaisesRegex(StopRun,'unreadable'):
            self.session.lobby()
        self.assertEqual(self.platform.events,[])
        self.assertGreaterEqual(self.platform.clock,8)

    def test_claim_requires_green_button_and_exact_real_caption(self):
        for name,expected in (('login_rewards.png','claim'),('login_rewards_current.png','close')):
            with Image.open(ROOT/'tests/fixtures'/name) as frame:
                self.assertEqual(self.session._login_caption(frame),expected)
                if expected=='claim':
                    self.assertIsNone(self.session._login_caption(frame.convert('L').convert('RGB')))

    def test_unreadable_caption_breaks_the_claim_confirmation_sequence(self):
        self.state='login_rewards';readings=iter(['Claim','','Claim',''])
        self.session.ocr=SimpleNamespace(read=lambda frame:next(readings,''))
        with self.assertRaises(StopRun):self.session.lobby()
        self.assertEqual(self.platform.events,[])

    def test_a_brief_reward_overlay_restarts_the_lobby_stability_wait(self):
        def capture():
            frame=Image.new('RGB',(1920,991))
            reward=1.59<=self.platform.now()<1.79
            frame.info['state']='login_rewards' if reward else 'lobby'
            if reward:frame.paste((100,220,120),Session.LOGIN_CAPTION_BOX)
            return frame
        self.session.capture=capture
        self.session.ocr=SimpleNamespace(read=lambda frame:'Claim')
        self.session.lobby()
        self.assertGreaterEqual(self.platform.now(),3.79)
        self.assertEqual(self.platform.events,[])

    def test_recovery_attempt_uses_root_controls_and_shared_totals(self):
        child=self.path/'attempt_001';child.mkdir()
        control=SessionControl(self.path,context={'attempt_folder':'attempt_001'})
        totals={'attempts':2,'matches_completed':2,'wins':2,'coins_total':900}
        session=Session(self.driver,child,control=control,totals=totals,read_frame=lambda:Image.new('RGB',(1920,991)),now=self.platform.now)
        self.assertIs(session.totals,totals)
        session.status('starting')
        import json
        self.assertEqual(json.loads((self.path/'status.json').read_text())['attempt_folder'],'attempt_001')
        (self.path/'stop').touch()
        with self.assertRaises(StopRun):self.driver.key('W')
        self.assertEqual(self.platform.events,[])
    def test_transient_missing_title_is_reobserved_without_any_movement(self):
        from tds_auto.maps import Board
        self.state='map_vote'
        target=Board(1,(750,220,1100,270),'Dead Ahead')
        with patch('tds_auto.session.visible_target',side_effect=[None,target]), \
             patch('tds_auto.session.vote_prompt',side_effect=[False,True]), \
             patch('tds_auto.session.voting_floor',return_value=True):
            self.session.approach_target()
        self.assertEqual(self.platform.events,[])

    def test_curved_floor_margin_moves_forward_before_the_next_strafe(self):
        from tds_auto.maps import Board
        self.state='map_vote'
        images=[]
        for name in ['vote_floor_margin_edge.png','vote_floor_margin_safe.png','vote_floor_margin_safe.png']:
            with Image.open(ROOT/'tests/fixtures'/name) as f:images.append(f.copy())
        for f in images:f.info['state']='map_vote'
        frames=iter(images);self.session.capture=lambda:next(frames,images[-1])
        far=Board(1,(710,249,950,283),'Dead Ahead')
        near=Board(1,(840,249,1080,283),'Dead Ahead')
        with patch('tds_auto.session.visible_target',side_effect=[far,far,near]), \
             patch('tds_auto.session.vote_prompt',side_effect=[False,False,True]):
            self.session.approach_target()
        self.assertEqual([e for e in self.platform.events if e[0]=='key_down'],[('key_down','W'),('key_down','A')])

    def test_vote_validation_keeps_the_lower_post_vote_header_and_physical_index(self):
        from tds_auto.maps import Board
        self.state='map_vote';self.session.allowed={'map_vote'}
        with Image.open(ROOT/'tests/fixtures/boards_post_vote_low_4.png') as image:frame=image.copy()
        frame.info['state']='map_vote';self.session.capture=lambda:frame
        original=Board(4,(780,237,1042,277),'Dead Ahead')
        with patch.object(self.session,'approach_target',return_value=(frame,original)), \
             patch.object(self.session,'vote_count',return_value=1),patch.object(self.session,'wait_state'), \
             patch.object(self.session.driver,'key',wraps=self.session.driver.key) as key_press:
            self.session.vote_target(original)
        self.assertEqual(self.session.board_index,4)
        self.assertEqual(self.platform.events.count(('key_down','E')),1)
        self.assertEqual([entry.args for entry in key_press.call_args_list],[('E',.8),('S',.15)])
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_recorded_a_and_c_badges_stay_distinct_from_recovered_titles(self):
        from tds_auto.maps import visible_target
        for name,expected in (('post_vote_header_a_roi.png',None),('post_vote_header_c_roi.png',1)):
            with self.subTest(name=name),Image.open(ROOT/'tests/fixtures'/name) as source:
                frame=source.copy()
                target=visible_target(frame,after_vote=True)
                self.assertIsNotNone(target)
                self.assertEqual(self.session.vote_count(frame,target),expected)

    def test_recorded_a_unknown_badge_stops_without_ready_after_one_safe_view_clear(self):
        from tds_auto.maps import Board,visible_target
        self.state='map_vote';self.session.allowed={'map_vote'}
        with Image.open(ROOT/'tests/fixtures/post_vote_header_a_roi.png') as source:
            frame=source.copy();frame.info['state']='map_vote'
        visible=visible_target(frame,after_vote=True)
        original=Board(4,visible.box,visible.title)
        self.session.capture=lambda:frame.copy()
        with patch.object(self.session,'approach_target',return_value=(frame,original)), \
             patch('tds_auto.session.voting_floor',return_value=True):
            with self.assertRaisesRegex(StopRun,'does not show one solo vote') as caught:
                self.session.vote_target(original)
        self.assertEqual(self.session.board_index,4)
        self.assertEqual(self.platform.events.count(('key_down','E')),1)
        self.assertEqual(self.platform.events.count(('key_down','D')),1)
        self.assertNotIn(('left_down',),self.platform.events)
        self.assertIn('title_tokens=dead,ahead',str(caught.exception))
        status=json.loads((self.path/'status.json').read_text())
        self.assertEqual(status['title_header_count'],1)
        self.assertEqual(status['title_tokens'],['dead','ahead'])

    def test_recorded_c_exact_badge_one_allows_ready_for_original_board(self):
        from tds_auto.maps import Board,visible_target
        self.state='map_vote';self.session.allowed={'map_vote'}
        with Image.open(ROOT/'tests/fixtures/post_vote_header_c_roi.png') as source:
            frame=source.copy();frame.info['state']='map_vote'
        visible=visible_target(frame,after_vote=True)
        original=Board(3,visible.box,visible.title)
        self.session.capture=lambda:frame.copy()
        with patch.object(self.session,'approach_target',return_value=(frame,original)), \
             patch.object(self.session,'wait_state'):
            self.session.vote_target(original)
        self.assertEqual(self.session.board_index,3)
        self.assertEqual(self.platform.events.count(('key_down','E')),1)
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_post_vote_stationary_reread_recovers_title_without_repeating_vote(self):
        from tds_auto.maps import Board
        self.state='map_vote';self.session.allowed={'map_vote'}
        frame=Image.new('RGB',(1920,991));frame.info['state']='map_vote'
        original=Board(4,(780,237,1042,277),'Dead Ahead')
        current=Board(1,(780,237,1042,277),'Dead Ahead')
        saved=[];save_frame=self.session.save_frame
        def save(image,name):
            saved.append(name);save_frame(image,name)
        self.session.save_frame=save
        with patch.object(self.session,'approach_target',return_value=(frame,original)), \
             patch('tds_auto.session.visible_target',side_effect=[None,None,None,current]), \
             patch.object(self.session,'vote_count',return_value=1),patch.object(self.session,'wait_state'):
            self.session.vote_target(original)
        self.assertEqual(self.session.board_index,4,'Post-vote view-relative numbering cannot replace the original physical board.')
        self.assertEqual(self.platform.events.count(('key_down','E')),1)
        self.assertEqual(self.platform.events.count(('key_down','S')),1)
        self.assertEqual(self.platform.events.count(('left_down',)),1)
        self.assertEqual(saved.count('latest.png'),4,'Repeated reads coalesce to one final latest-frame write.')

    def test_post_vote_title_timeout_never_repeats_vote_or_clicks_ready(self):
        from tds_auto.maps import Board
        self.state='map_vote';self.session.allowed={'map_vote'}
        frame=Image.new('RGB',(1920,991));frame.info['state']='map_vote'
        original=Board(2,(780,237,1042,277),'Dead Ahead')
        self.session.frame=lambda **kwargs:frame.copy()
        with patch.object(self.session,'approach_target',return_value=(frame,original)), \
             patch('tds_auto.session.visible_target',return_value=None):
            with self.assertRaisesRegex(StopRun,'Target identity was lost after voting'):
                self.session.vote_target(original)
        self.assertEqual(self.platform.events.count(('key_down','E')),1)
        self.assertNotIn(('left_down',),self.platform.events)
        self.assertGreaterEqual(self.platform.clock,3.2)
        self.assertLessEqual(self.platform.clock,3.5)
        status=json.loads((self.path/'status.json').read_text())
        self.assertEqual(status['phase'],'post_vote_title_unconfirmed')
        self.assertEqual(status['physical_board'],2)
        self.assertIs(status['target_recognized'],False)
        self.assertIs(status['badge_read'],False)
        self.assertGreater(status['title_observations'],1)
        self.assertNotIn('ocr_text',status)

    def test_f2_interrupts_post_vote_stationary_reread_before_ready(self):
        from tds_auto.maps import Board
        self.state='map_vote';self.session.allowed={'map_vote'}
        frame=Image.new('RGB',(1920,991));frame.info['state']='map_vote'
        original=Board(3,(780,237,1042,277),'Dead Ahead')
        self.platform.on_sleep=lambda os:(self.path/'stop').touch() if os.clock>1.7 else None
        with patch.object(self.session,'approach_target',return_value=(frame,original)), \
             patch('tds_auto.session.visible_target',return_value=None):
            with self.assertRaises(StopRun) as caught:self.session.vote_target(original)
        self.assertEqual(caught.exception.kind,'user_stop')
        self.assertEqual(self.platform.events.count(('key_down','E')),1)
        self.assertNotIn(('left_down',),self.platform.events)

    def test_post_vote_unknown_badge_needs_safe_floor_for_its_single_view_clear(self):
        from tds_auto.maps import Board
        self.state='map_vote';self.session.allowed={'map_vote'}
        frame=Image.new('RGB',(1920,991));frame.info['state']='map_vote'
        target=Board(2,(780,237,1042,277),'Dead Ahead')
        with patch.object(self.session,'approach_target',return_value=(frame,target)), \
             patch('tds_auto.session.visible_target',return_value=target), \
             patch.object(self.session,'vote_count',return_value=None), \
             patch('tds_auto.session.voting_floor',return_value=False):
            with self.assertRaisesRegex(StopRun,'floor margin'):
                self.session.vote_target(target)
        self.assertEqual(self.platform.events.count(('key_down','E')),1)
        self.assertEqual([event for event in self.platform.events if event[0]=='key_down' and event[1]=='D'],[])
        self.assertNotIn(('left_down',),self.platform.events)

    def test_unknown_vote_badge_uses_at_most_one_clear_step_then_stops(self):
        from tds_auto.maps import Board
        self.state='map_vote';self.session.allowed={'map_vote'}
        frame=Image.new('RGB',(1920,991));frame.info['state']='map_vote'
        target=Board(1,(780,237,1042,277),'Dead Ahead')
        with patch.object(self.session,'approach_target',return_value=(frame,target)), \
             patch('tds_auto.session.visible_target',return_value=target), \
             patch.object(self.session,'vote_count',side_effect=[None,None]), \
             patch('tds_auto.session.voting_floor',return_value=True):
            with self.assertRaisesRegex(StopRun,'does not show one solo vote'):
                self.session.vote_target(target)
        self.assertEqual(self.platform.events.count(('key_down','E')),1)
        self.assertEqual(self.platform.events.count(('key_down','D')),1)
        self.assertNotIn(('left_down',),self.platform.events)
        status=json.loads((self.path/'status.json').read_text())
        self.assertEqual(status['phase'],'post_vote_badge_unconfirmed')
        self.assertEqual(status['physical_board'],1)
        self.assertIs(status['target_recognized'],True)
        self.assertIs(status['badge_read'],False,'Unknown is not a recognized numeric badge value.')
        self.assertIsNone(status['badge_count'])
        self.assertEqual(status['view_clear_steps'],1)

    def test_post_vote_state_change_during_stationary_read_stops_before_ready(self):
        from tds_auto.maps import Board
        self.state='map_vote';self.session.allowed={'map_vote'}
        frames=[]
        for state in ('map_vote','map_vote','in_match'):
            frame=Image.new('RGB',(1920,991));frame.info['state']=state;frames.append(frame)
        target=Board(3,(780,237,1042,277),'Dead Ahead')
        self.session.frame=lambda **kwargs:frames.pop(0)
        with patch.object(self.session,'approach_target',return_value=(frames[0],target)), \
             patch('tds_auto.session.visible_target',return_value=None):
            with self.assertRaisesRegex(StopRun,'Map-vote state changed after voting'):
                self.session.vote_target(target)
        self.assertEqual(self.platform.events.count(('key_down','E')),1)
        self.assertNotIn(('left_down',),self.platform.events)

    def test_zero_vote_badge_stops_without_view_clear_or_ready(self):
        from tds_auto.maps import Board
        self.state='map_vote';self.session.allowed={'map_vote'}
        frame=Image.new('RGB',(1920,991));frame.info['state']='map_vote'
        target=Board(1,(780,237,1042,277),'Dead Ahead')
        with patch.object(self.session,'approach_target',return_value=(frame,target)), \
             patch('tds_auto.session.visible_target',return_value=target), \
             patch.object(self.session,'vote_count',return_value=0), \
             patch('tds_auto.session.voting_floor',side_effect=AssertionError('A zero badge must not cause movement')):
            with self.assertRaisesRegex(StopRun,'does not show one solo vote'):
                self.session.vote_target(target)
        self.assertEqual(self.platform.events.count(('key_down','E')),1)
        self.assertNotIn(('key_down','D'),self.platform.events)
        self.assertNotIn(('left_down',),self.platform.events)
        status=json.loads((self.path/'status.json').read_text())
        self.assertIs(status['badge_read'],True)
        self.assertEqual(status['badge_count'],0)

    def test_persistent_missing_title_remains_a_bounded_no_movement_stop(self):
        self.state='map_vote'
        with patch('tds_auto.session.visible_target',return_value=None), \
             patch('tds_auto.session.vote_prompt',return_value=False):
            with self.assertRaises(StopRun):self.session.approach_target()
        self.assertEqual(self.platform.events,[])
        self.assertLessEqual(self.platform.clock,6)

    def test_vip_walk_stops_on_confirmed_prompt_and_measures_the_return(self):
        self.state='map_vote'
        self.assertTrue(callable(getattr(self.session,'approach_vip',None)))
        with patch('tds_auto.session._vip_prompt_evidence',side_effect=[vip_evidence(False,.12),vip_evidence(False,.13),vip_evidence(True,.996),vip_evidence(True,.995)]):
            duration=self.session.approach_vip()
        self.assertAlmostEqual(duration,.30)
        self.assertEqual([e for e in self.platform.events if e[0]=='key_down'],[('key_down','D')]*2)

    def test_missing_vip_prompt_never_sends_e_or_walks_past_the_budget(self):
        self.state='map_vote'
        self.assertTrue(callable(getattr(self.session,'approach_vip',None)))
        with patch('tds_auto.session._vip_prompt_evidence',return_value=vip_evidence(False,0.0)):
            with self.assertRaisesRegex(StopRun,'VIP proximity'):
                self.session.approach_vip()
        self.assertEqual([e for e in self.platform.events if e[0]=='key_down'],[('key_down','D')]*12)
        status=json.loads((self.path/'status.json').read_text())
        self.assertEqual(status['phase'],'vip_prompt_unconfirmed')
        self.assertEqual(status['steps'],12)
        self.assertEqual(status['observation_count'],13)
        self.assertEqual(status['keycap_score'],0.0)
        self.assertIs(status['literal_caption'],False)
        self.assertNotIn('ocr_text',status)

    def test_recorded_vip_failure_frame_confirms_only_after_two_stationary_reads(self):
        self.state='map_vote'
        frames=[]
        for _ in range(12):
            frame=Image.new('RGB',(1920,991));frame.info['state']='map_vote';frames.append(frame)
        with Image.open(ROOT/'tests/fixtures/vip_override_b_roi.png') as source:
            for _ in range(2):
                frame=source.copy();frame.info['state']='map_vote';frames.append(frame)
        self.session.capture=lambda:frames.pop(0)
        self.assertAlmostEqual(self.session.approach_vip(),1.8)
        self.assertEqual(self.platform.events.count(('key_down','D')),12)
        self.assertNotIn(('key_down','E'),self.platform.events)
        self.assertEqual(len(list(self.path.glob('vip_step_*.png'))),14)

    def test_vip_prompt_at_final_position_confirms_without_a_thirteenth_step(self):
        self.state='map_vote'
        prompts=[vip_evidence(False,0.0)]*12+[vip_evidence(True,.996),vip_evidence(True,.995)]
        with patch('tds_auto.session._vip_prompt_evidence',side_effect=prompts):
            self.assertAlmostEqual(self.session.approach_vip(),1.8)
        self.assertEqual([e for e in self.platform.events if e[0]=='key_down'],[('key_down','D')]*12)

    def test_f2_during_last_vip_approach_hold_never_sends_an_extra_step(self):
        self.state='map_vote'
        self.platform.on_sleep=lambda os:(self.path/'stop').touch() if os.events.count(('key_down','D'))>=12 else None
        with patch('tds_auto.session._vip_prompt_evidence',return_value=vip_evidence(False,0.0)):
            with self.assertRaises(StopRun) as caught:self.session.approach_vip()
        self.assertEqual(caught.exception.kind,'user_stop')
        self.assertEqual(self.platform.events.count(('key_down','D')),12)
        self.assertNotIn(('key_down','E'),self.platform.events)

    def test_approach_reaches_voting_floor_before_strafing_toward_outer_board(self):
        from tds_auto.maps import Board
        self.state='map_vote'
        far=Board(1,(450,255,790,290),'Dead Ahead')
        near=Board(1,(750,220,1100,270),'Dead Ahead')
        with patch('tds_auto.session.voting_floor',side_effect=[False,True],create=True), \
             patch('tds_auto.session.visible_target',side_effect=[far,near]), \
             patch('tds_auto.session.vote_prompt',side_effect=[False,True]):
            self.session.approach_target()
        self.assertEqual([e for e in self.platform.events if e[0]=='key_down'],[('key_down','W')])

    def test_losing_the_verified_floor_stops_before_more_strafing(self):
        from tds_auto.maps import Board
        self.state='map_vote'
        target=Board(1,(450,230,790,280),'Dead Ahead')
        with patch('tds_auto.session.voting_floor',side_effect=[True,True,False,False],create=True), \
             patch('tds_auto.session.visible_target',return_value=target), \
             patch('tds_auto.session.vote_prompt',return_value=False):
            with self.assertRaisesRegex(StopRun,'voting floor'):
                self.session.approach_target()
        self.assertEqual([e for e in self.platform.events if e[0]=='key_down'],[('key_down','A')])

    def test_walkway_edge_advances_inward_before_resuming_alignment(self):
        from tds_auto.maps import Board
        self.state='map_vote'
        far=Board(1,(450,230,790,280),'Dead Ahead')
        near=Board(1,(750,220,1100,270),'Dead Ahead')
        with patch('tds_auto.session.voting_floor',side_effect=[True,True,False,True,True]), \
             patch('tds_auto.session.visible_target',side_effect=[far,far,near]), \
             patch('tds_auto.session.vote_prompt',side_effect=[False,False,True]):
            self.session.approach_target()
        self.assertEqual([e for e in self.platform.events if e[0]=='key_down'],[('key_down','A'),('key_down','W')])

    def test_board_read_walk_and_vip_return_use_the_verified_distance(self):
        from tds_auto.maps import Board
        self.state='map_vote'
        unknown=tuple(Board(i,(0,0,200,40),'Other') for i in range(1,5))
        target=tuple(Board(i,(0,0,200,40),'Dead Ahead' if i==1 else 'Other') for i in range(1,5))
        self.session.face_boards=lambda:None
        self.session.boards=lambda:next(boards)
        boards=iter((unknown,target))
        self.session.wait_state=lambda *args:None
        self.session.approach_vip=lambda:.6
        self.session.vote_target=lambda target:None
        self.driver.before_click=None
        original_key=self.driver.key
        movements=[]
        def key(name,seconds=.1):
            movements.append((name,seconds))
            original_key(name,seconds)
        self.driver.key=key
        def card_matches(frame):
            moves=[e for e in self.platform.events if e[0]=='move']
            x,y=moves[-1][1],moves[-1][2]-self.driver.expected.y
            self.assertFalse(635<=x<752 and 350<=y<398,
                             'VIP hover must leave the complete map title clear for OCR.')
            return True
        with patch('tds_auto.session.vip_target_matches',side_effect=card_matches):
            self.session.choose_map()
        # Matching forward/back duration preserves the existing VIP spawn route.
        self.assertEqual(movements[:2],[('W',2.8),('S',2.8)])
        self.assertEqual(movements[-1],('W',.9))
        self.assertIn(('A',.6),movements)

    def setUp(self):
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)
        self.platform=FakeOS()
        self.driver=GuardedInput(self.platform.window,self.platform)
        self.state='lobby'
        def frame():
            image=Image.new('RGB',(1920,991))
            if self.state=='login_rewards':
                image.paste((100,220,120),Session.LOGIN_CAPTION_BOX)
            image.info['state']=self.state
            return image
        self.session=Session(self.driver,self.path,read_frame=frame,now=self.platform.now)
        self.session.observer=SimpleNamespace(observe=lambda frame:SimpleNamespace(state=frame.info['state']))
        self.session.navigator.observer=self.session.observer

    def test_login_overlay_is_dismissed_once_then_lobby_is_confirmed(self):
        self.state='login_rewards'
        self.session.ocr=SimpleNamespace(read=lambda frame:'Close')
        original=self.platform.emit
        def emit(kind,*args):
            original(kind,*args)
            if kind=='left_up': self.state='lobby'
        self.platform.emit=emit
        self.session.lobby()
        self.assertEqual(self.platform.events.count(('left_down',)),1)
        self.assertIn(('move',1718,71),self.platform.events)
        self.assertEqual(self.state,'lobby')

    def test_delayed_login_overlay_blocks_the_play_click(self):
        self.session.allowed={'lobby'}
        self.state='login_rewards'
        with self.assertRaises(StopRun):self.driver.click(960,785)
        self.assertNotIn(('left_down',),self.platform.events)

    def test_stop_file_interrupts_a_hold_and_releases_the_key(self):
        self.platform.on_sleep=lambda os:(self.path/'stop').touch()
        with self.assertRaises(StopRun):self.driver.key('W',.95)
        self.assertEqual(self.platform.events,[('key_down','W'),('key_up','W')])

    def test_navigation_diagnostic_write_failure_is_a_storage_stop(self):
        with patch.object(Image.Image,'save',side_effect=PermissionError('Evidence is not writable')):
            with self.assertRaises(StopRun) as caught:self.session.frame()
        self.assertEqual(caught.exception.kind,'storage')
        self.assertEqual(self.platform.events,[])

    def test_unverified_loadout_is_a_setup_stop_after_bounded_observation(self):
        self.session.lobby=lambda:None
        self.session.transition=lambda name:'inventory_scout'
        with patch('tds_auto.session.verify_inventory',return_value='Golden Scout is not equipped'):
            with self.assertRaises(StopRun) as caught:self.session.preflight()
        self.assertEqual(caught.exception.kind,'setup')
        self.assertGreaterEqual(self.platform.now(),5)
        self.assertEqual(self.platform.events,[])

    def test_pause_sends_no_input_and_focus_loss_stops_it(self):
        from dataclasses import replace
        (self.path/'pause').touch()
        self.platform.on_sleep=lambda os:setattr(os,'window',replace(os.window,foreground=False))
        with self.assertRaises(StopRun):self.session.pause()
        self.assertEqual(self.platform.events,[])

    def test_clean_restart_accepts_different_cash_and_never_repeats_movement(self):
        self.state='match_ready'
        with patch('tds_auto.session.HudReader') as hud,patch('tds_auto.session.CameraGate') as gate,patch('tds_auto.session.read_hotbar',return_value=SimpleNamespace(valid=True,price=175)):
            hud.return_value.read.return_value=SimpleNamespace(tower_count=0,cash=250)
            gate.return_value.bind.return_value=True
            self.session.prepare_camera(retained=True)
        self.assertEqual(self.platform.events,[])

    def test_fresh_camera_can_correct_zoom_only_before_any_tower_exists(self):
        self.state='match_ready'
        from unittest.mock import Mock
        gate=Mock();gate.bind.side_effect=[False,True];gate.zoom_step.return_value=-10
        with patch('tds_auto.session.HudReader') as hud:
            hud.return_value.read.return_value=SimpleNamespace(tower_count=0)
            self.session.align_fresh_camera(gate)
        self.assertEqual([e for e in self.platform.events if e[0]=='wheel'],[('wheel',-10)])
        self.assertFalse(any(e[0] in {'key_down','left_down','right_down'} for e in self.platform.events))
        self.platform.events.clear();gate.reset_mock();gate.bind.side_effect=None;gate.bind.return_value=False
        with patch('tds_auto.session.HudReader') as hud:
            hud.return_value.read.return_value=SimpleNamespace(tower_count=1)
            with self.assertRaises(StopRun):self.session.align_fresh_camera(gate)
        self.assertEqual(self.platform.events,[])
        gate.zoom_step.assert_not_called()

    def test_fresh_camera_adjustments_are_bounded_and_retained_restarts_never_adjust(self):
        self.state='match_ready'
        from unittest.mock import Mock
        gate=Mock();gate.bind.return_value=False;gate.zoom_step.return_value=-10
        with patch('tds_auto.session.HudReader') as hud:
            hud.return_value.read.return_value=SimpleNamespace(tower_count=0)
            with self.assertRaises(StopRun):self.session.align_fresh_camera(gate)
        self.assertEqual([e for e in self.platform.events if e[0]=='wheel'],[('wheel',-10)]*6)
        self.platform.events.clear()
        with patch('tds_auto.session.HudReader') as hud,patch('tds_auto.session.CameraGate',return_value=gate):
            hud.return_value.read.return_value=SimpleNamespace(tower_count=0)
            with self.assertRaises(StopRun):self.session.prepare_camera(retained=True)
        self.assertEqual(self.platform.events,[])

    def test_result_banner_interrupts_playback_before_any_click(self):
        playback=object.__new__(Playback)
        playback.full_evidence=True
        playback.driver=self.driver
        playback.output=self.path
        playback.frame=self.session.frame
        playback.observer=SimpleNamespace(observe=lambda frame:SimpleNamespace(state='victory'))
        expected=GameResult('victory','Dead Ahead','Easy',20,484,450)
        playback.results=SimpleNamespace(read=lambda frame:expected)
        self.driver.before_click=playback.click_gate
        with self.assertRaises(MatchFinished) as caught:self.driver.click(220,578)
        self.assertEqual(caught.exception.result,expected)
        self.assertNotIn(('left_down',),self.platform.events)

    def test_vote_badge_belongs_to_the_verified_target(self):
        from tds_auto.maps import Board
        with Image.open(ROOT/'tests/fixtures/vote_badges.png') as frame:
            self.assertEqual(self.session.vote_count(frame,Board(1,(787,245,1029,282),'Dead Ahead')),1)
            self.assertIsNone(self.session.vote_count(frame,Board(2,(1110,245,1350,282),'Other')))
        with Image.open(ROOT/'tests/fixtures/vote_board4_badges.png') as frame:
            self.assertEqual(self.session.vote_count(frame,Board(4,(901,253,1126,286),'Dead Ahead')),1)

    def test_view_clear_badge_one_survives_bounded_registration_without_accepting_neighbor_zeros(self):
        from tds_auto.maps import visible_target,badge_is_one
        with Image.open(ROOT/'tests/fixtures/post_vote_badge_view_clear_d.png') as frame:
            target=visible_target(frame,after_vote=True)
            self.assertIsNotNone(target,'The sanitized view-clear frame has one complete Dead Ahead header.')
            self.assertEqual(self.session.vote_count(frame,target),1)
            self.assertTrue(badge_is_one(frame,(809,408,860,457)))
            self.assertFalse(badge_is_one(frame,(1115,404,1167,452)))
            self.assertFalse(badge_is_one(frame,(1422,408,1487,459)))

    def test_replay_vote_one_is_read_at_the_cleared_camera_angle(self):
        from tds_auto.maps import visible_target,badge_is_one
        with Image.open(ROOT/'tests/fixtures/vote_badge_clear_replay.png') as frame:
            target=visible_target(frame)
            self.assertEqual(self.session.vote_count(frame,target),1)
            for box in ((1110,387,1157,432),(1387,390,1444,437),(1760,403,1850,462)):
                self.assertFalse(badge_is_one(frame,box))
            frame.paste('black',(834,391,880,435))
            self.assertIsNone(self.session.vote_count(frame,target))

    def test_already_selected_solo_does_not_require_player_list_overlay(self):
        self.state='map_vote'
        with Image.open(ROOT/'tests/fixtures/vote_spawn_row.png') as image:frame=image.copy()
        frame.info['state']='map_vote'
        self.session.capture=lambda:frame
        with patch.object(self.session,'boards',side_effect=StopRun('reached board reader')):
            with self.assertRaisesRegex(StopRun,'reached board reader'):
                self.session.choose_map()
        self.assertNotIn(('key_down','TAB'),self.platform.events)
        self.assertIn(('key_down','W'),self.platform.events)

    def test_continuous_grind_records_wins_and_stops_on_the_first_non_victory(self):
        outcomes=iter([
            {'status':'victory','coins':450,'full_strategy_verified':True},
            {'status':'victory','coins':450,'full_strategy_verified':True},
            {'status':'defeat','coins':250,'full_strategy_verified':False}])
        class Engine:
            def __init__(engine,*args,**kwargs):engine.profile=self.session.profile
            def play(self,**kwargs):return next(outcomes)
        # The live GUI is external to this loop test; its independent navigation
        # and match tests cover the adapters. Exercise the real session policy.
        self.session.preflight=lambda:None
        self.session.choose_map=lambda:None
        self.session.prepare_camera=lambda retained=False:None
        self.session.transition=lambda name:None
        with patch('tds_auto.session.Playback',Engine):
            try:result=self.session.run(continuous=True)
            except TypeError as exc:self.fail(f'Continuous session is unavailable: {exc}')
        self.assertEqual(result['status'],'defeat')
        self.assertEqual(result['wins'],2)
        self.assertEqual(result['matches_completed'],3)
        import json
        ledger=[json.loads(line) for line in (self.path/'matches.jsonl').read_text().splitlines()]
        self.assertEqual([row['result']['status'] for row in ledger],['victory','victory','defeat'])

    def test_compact_grind_evidence_keeps_latest_and_result_without_step_images(self):
        frame=Image.new('RGB',(1920,991),'navy')
        try:
            playback=Playback(ROOT/'calibrations/dead_ahead_vertical_nine_v4.json',self.driver,self.path/'compact',full_evidence=False,latest_path=self.path/'latest.png')
        except TypeError as exc:self.fail(f'Compact evidence is unavailable: {exc}')
        with patch('tds_auto.run.capture',return_value=frame):
            playback.frame()
        playback.save_evidence(frame,'initial.png')
        playback.save_evidence(frame,'step_001.png')
        playback.save_evidence(frame,'final.png')
        self.assertTrue((self.path/'latest.png').is_file())
        self.assertFalse((self.path/'compact/initial.png').exists())
        self.assertFalse((self.path/'compact/step_001.png').exists())
        with Image.open(self.path/'compact/final.png') as result:
            self.assertLess(result.width*result.height,frame.width*frame.height//2)

    def test_approach_backs_off_a_close_occluded_header_then_uses_visible_vote(self):
        images=[]
        for path in ['vote_approach_close.png','vote_approach_ready.png']:
            with Image.open(ROOT/'tests/fixtures'/path) as frame:images.append(frame.copy())
        for frame in images:frame.info['state']='map_vote'
        frames=iter(images)
        self.session.capture=lambda:next(frames,images[-1])
        with patch('tds_auto.session.voting_floor',return_value=True,create=True):
            try:frame,target=self.session.approach_target()
            except AttributeError as exc:self.fail(f'Feedback approach is unavailable: {exc}')
        self.assertEqual(target.title,'Dead Ahead')
        self.assertIn(('key_down','S'),self.platform.events)
        self.assertNotIn(('key_down','W'),self.platform.events)
        self.assertNotIn(('key_down','E'),self.platform.events)

    def test_camera_change_during_pointer_motion_prevents_the_click(self):
        playback=object.__new__(Playback)
        playback.driver=self.driver
        playback.frame=self.session.frame
        playback.observer=SimpleNamespace(observe=lambda frame:SimpleNamespace(state='in_match'))
        playback.camera=SimpleNamespace(check=lambda frame:False)
        self.driver.before_click=playback.click_gate
        with self.assertRaises(StopRun):self.driver.click(220,578)
        self.assertNotIn(('left_down',),self.platform.events)

    def test_transient_unknown_before_a_click_is_reobserved_without_a_retry(self):
        playback=object.__new__(Playback)
        playback.driver=self.driver
        playback.observer=SimpleNamespace(observe=lambda frame:SimpleNamespace(state=frame.info['state']))
        playback.camera=SimpleNamespace(check=lambda frame:True)
        images=[]
        for state in ['unknown','in_match']:
            frame=Image.new('RGB',(1920,991));frame.info['state']=state;images.append(frame)
        sequence=iter(images)
        playback.frame=lambda:next(sequence,images[-1])
        self.driver.before_click=playback.click_gate
        with patch('tds_auto.run.time.monotonic',side_effect=self.platform.now):
            self.driver.click(220,578)
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_stopped_playback_is_an_attempt_and_not_a_completed_match(self):
        outcome={'status':'stopped','reason':'Unconfirmed action','full_strategy_verified':False}
        class Engine:
            def __init__(engine,*args,**kwargs):engine.profile=self.session.profile
            def play(engine,**kwargs):return outcome
        self.session.preflight=lambda:None
        self.session.choose_map=lambda:None
        self.session.prepare_camera=lambda retained=False:None
        with patch('tds_auto.session.Playback',Engine):result=self.session.run()
        self.assertEqual(result['status'],'stopped')
        self.assertEqual(result['matches_completed'],0)
        self.assertEqual(result['attempts'],1)

    def test_a_win_with_unreadable_reward_is_recorded_without_starting_another_match(self):
        outcome={'status':'victory','coins':None,'full_strategy_verified':True}
        class Engine:
            def __init__(engine,*args,**kwargs):engine.profile=self.session.profile
            def play(engine,**kwargs):return outcome
        self.session.preflight=lambda:None
        self.session.choose_map=lambda:None
        self.session.prepare_camera=lambda retained=False:None
        self.session.transition=lambda name:self.fail('Another match was started without a verified reward')
        with patch('tds_auto.session.Playback',Engine):result=self.session.run(continuous=True)
        self.assertEqual(result['status'],'stopped')
        self.assertIn('coin reward',result['reason'])
        self.assertEqual((result['wins'],result['matches_completed']),(1,1))
        self.assertEqual(result['matches'][0]['status'],'victory')

    def test_low_disk_space_stops_before_lobby_input(self):
        self.session.preflight=lambda:self.fail('Input flow began on a full evidence disk')
        with patch('shutil.disk_usage',return_value=SimpleNamespace(free=0)):
            with self.assertRaisesRegex(StopRun,'GiB'):self.session.run(continuous=True)
        self.assertEqual(self.platform.events,[])

    def test_rejected_second_start_preserves_active_control_pointer(self):
        from tds_auto.session import main
        pointer=self.path/'captures/last_session.txt'
        pointer.parent.mkdir()
        pointer.write_text('active-session',encoding='utf-8')
        output=self.path/'rejected'
        with patch('tds_auto.session.ROOT',self.path), \
             patch('tds_auto.session.WindowsOS',side_effect=StopRun('F8 already owned')), \
             patch('tds_auto.session.locate_roblox') as locate:
            self.assertEqual(main(['start','--confirm-start','--output',str(output)]),2)
        locate.assert_not_called()
        self.assertFalse(output.exists())
        self.assertEqual(pointer.read_text(encoding='utf-8'),'active-session')

    def test_startup_failure_releases_native_stop_registration(self):
        from tds_auto.session import main
        platform=SimpleNamespace(stop_requested=lambda:False,current=lambda:self.platform.window,
                                 close=lambda:None)
        with patch('tds_auto.session.WindowsOS',return_value=platform), \
             patch.object(platform,'close') as close, \
             patch('tds_auto.session.locate_roblox',side_effect=StopRun('No client')):
            self.assertEqual(main(['start','--confirm-start','--output',str(self.path/'failed')]),2)
        close.assert_called_once()

    def test_ready_loading_can_observe_a_blank_but_other_waits_reject_it(self):
        from tds_auto.phase1 import BlankCapture
        self.state='match_ready'
        original=self.session.capture
        blank=[True]
        def capture():
            if blank and blank.pop():raise BlankCapture('Loading')
            return original()
        self.session.capture=capture
        self.session.wait_state('match_ready',allowed={'loading'})
        blank.append(True)
        with self.assertRaises(BlankCapture):self.session.wait_state('match_ready')
        self.assertEqual(self.platform.events,[])

    def test_vote_view_search_rotates_without_walking_until_row_is_verified(self):
        self.state='map_vote'
        frames=[]
        for name in ['vote_spawn_water','vote_spawn_row','vote_spawn_row']:
            with Image.open(ROOT/'tests/fixtures'/f'{name}.png') as image:frame=image.copy()
            frame.info['state']='map_vote';frames.append(frame)
        sequence=iter(frames)
        self.session.capture=lambda:next(sequence,frames[-1])
        self.session.face_boards()
        self.assertEqual(self.platform.events.count(('right_down',)),1)
        self.assertFalse(any(e[0]=='key_down' for e in self.platform.events))
        self.assertNotIn(('left_down',),self.platform.events)

    def test_missing_board_row_stops_without_any_walk_or_vote(self):
        self.state='map_vote'
        with self.assertRaisesRegex(StopRun,'board row'):self.session.face_boards()
        self.assertEqual(self.platform.events.count(('right_down',)),24)
        self.assertFalse(any(e[0]=='key_down' for e in self.platform.events))
        self.assertNotIn(('left_down',),self.platform.events)

    def test_connected_header_uses_alignment_not_unbounded_camera_search(self):
        frames=[]
        for name in ['vote_spawn_connected_header','vote_spawn_row','vote_spawn_row']:
            with Image.open(ROOT/'tests/fixtures'/f'{name}.png') as image:frame=image.copy()
            frame.info['state']='map_vote';frames.append(frame)
        sequence=iter(frames);self.session.capture=lambda:next(sequence,frames[-1])
        self.session.face_boards()
        self.assertEqual(self.platform.events.count(('right_down',)),1)
        movement=sum(event[1] for event in self.platform.events if event[0]=='relative')
        self.assertLess(movement,0,'Visible off-centre banners require an aligning orbit, not a blind coarse search.')
        self.assertFalse(any(event[0]=='key_down' for event in self.platform.events))

    def test_late_board_row_detection_reserves_time_for_alignment_and_two_confirmations(self):
        frames=[]
        for name in ['vote_spawn_water']*22+['vote_spawn_offset','vote_spawn_row','vote_spawn_row']:
            with Image.open(ROOT/'tests/fixtures'/f'{name}.png') as image:frame=image.copy()
            frame.info['state']='map_vote';frames.append(frame)
        sequence=iter(frames);self.session.capture=lambda:next(sequence,frames[-1])
        self.session.face_boards()
        self.assertEqual(self.platform.events.count(('right_down',)),23)
        self.assertFalse(any(e[0]=='key_down' for e in self.platform.events))

    def test_vote_row_is_centred_before_walking_so_the_last_board_stays_visible(self):
        frames=[]
        for name in ['vote_spawn_edge','vote_spawn_row','vote_spawn_row']:
            with Image.open(ROOT/'tests/fixtures'/f'{name}.png') as image:frame=image.copy()
            frame.info['state']='map_vote';frames.append(frame)
        sequence=iter(frames);self.session.capture=lambda:next(sequence,frames[-1])
        self.session.face_boards()
        self.assertEqual(self.platform.events.count(('right_down',)),1)
        self.assertFalse(any(e[0]=='key_down' for e in self.platform.events))

    def test_camera_confidence_can_recover_before_one_click_without_repeating_it(self):
        playback=object.__new__(Playback);playback.driver=self.driver;playback.frame=self.session.frame
        playback.observer=SimpleNamespace(observe=lambda frame:SimpleNamespace(state='in_match'))
        readings=iter([None,True]);playback.camera=SimpleNamespace(check=lambda frame:next(readings,True))
        self.driver.before_click=playback.click_gate
        with patch('tds_auto.run.time.monotonic',side_effect=self.platform.now):self.driver.click(220,578)
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_play_again_vote_room_reselects_map_and_uses_fresh_camera_setup(self):
        calls=[]
        class Engine:
            def __init__(engine,*args,**kwargs):engine.profile=self.session.profile
            def play(engine,**kwargs):return {'status':'victory','coins':450,'full_strategy_verified':True}
        self.session.preflight=lambda:calls.append('preflight')
        self.session.choose_map=lambda:calls.append('choose_map')
        self.session.prepare_camera=lambda retained=False:calls.append(('camera',retained))
        def transition(name):
            calls.append(name)
            return 'map_vote'
        self.session.transition=transition
        with patch('tds_auto.session.Playback',Engine):result=self.session.run(matches=2)
        self.assertTrue(result['all_requested_matches_won'])
        self.assertEqual(calls,['preflight','choose_map',('camera',False),'play_again','choose_map',('camera',False)])

    def test_diagnostic_storage_failure_preserves_win_but_stops_before_replay(self):
        calls=[]
        class Engine:
            def __init__(engine,*args,**kwargs):engine.profile=self.session.profile
            def play(engine,**kwargs):return {'status':'victory','coins':450,'full_strategy_verified':True,'diagnostic_error':'PNG locked'}
        self.session.preflight=lambda:None
        self.session.choose_map=lambda:None
        self.session.prepare_camera=lambda retained=False:None
        self.session.transition=lambda name:calls.append(name) or 'map_vote'
        with patch('tds_auto.session.Playback',Engine):result=self.session.run(matches=2)
        self.assertEqual(result['status'],'stopped')
        self.assertEqual(result['stop_kind'],'storage')
        self.assertEqual((result['wins'],result['coins_total']),(1,450))
        self.assertEqual(result['matches'][0]['status'],'victory')
        self.assertEqual(calls,[])

    def test_partial_result_banner_waits_for_controls_without_gameplay_input(self):
        from tds_auto.observer import Observer
        from tds_auto.results import ResultReader
        playback=object.__new__(Playback)
        playback.driver=self.driver;playback.output=self.path;playback.full_evidence=True
        playback.observer=Observer();playback.results=ResultReader(playback.observer)
        with Image.open(ROOT/'tests/fixtures/victory_normal_small.png') as source:pending=source.copy()
        pending.paste('black',(1008,752,1188,790))
        with Image.open(ROOT/'tests/fixtures/result_victory.png') as source:complete=source.copy()
        playback.frame=lambda:complete
        with self.assertRaises(MatchFinished) as caught:playback.finish_if_result(pending)
        self.assertEqual(caught.exception.result.status,'victory')
        self.assertEqual(caught.exception.result.coins,450)
        self.assertEqual(self.platform.events,[])

    def test_persistent_partial_result_banner_times_out_without_gameplay_input(self):
        from tds_auto.observer import Observer
        from tds_auto.results import ResultReader
        playback=object.__new__(Playback)
        playback.driver=self.driver;playback.output=self.path;playback.full_evidence=True
        playback.observer=Observer();playback.results=ResultReader(playback.observer)
        with Image.open(ROOT/'tests/fixtures/victory_normal_small.png') as source:pending=source.copy()
        pending.paste('black',(1008,752,1188,790));playback.frame=lambda:pending
        with patch('tds_auto.run.time.monotonic',side_effect=self.platform.now):
            with self.assertRaisesRegex(StopRun,'Result banner'):playback.finish_if_result(pending)
        self.assertEqual(self.platform.events,[])

    def test_obscured_vote_is_reobserved_from_one_clearer_position_without_revoting(self):
        from tds_auto.maps import Board
        target=Board(1,(750,250,990,282),'Dead Ahead')
        self.state='map_vote';self.session.allowed={'map_vote'}
        for final_count in (1,0):
            with self.subTest(final_count=final_count):
                self.platform.events.clear()
                frame=self.session.frame()
                with patch.object(self.session,'approach_target',return_value=(frame,target)), \
                     patch('tds_auto.session.visible_target',return_value=target), \
                     patch.object(self.session,'vote_count',side_effect=[None,final_count]), \
                     patch('tds_auto.session.voting_floor',return_value=True), \
                     patch.object(self.session,'wait_state'):
                    if final_count==1:self.session.vote_target(target)
                    else:
                        with self.assertRaisesRegex(StopRun,'one solo vote'):self.session.vote_target(target)
                self.assertEqual(self.platform.events.count(('key_down','E')),1)
                self.assertEqual(self.platform.events.count(('key_down','D')),1)
                self.assertEqual(self.platform.events.count(('left_down',)),int(final_count==1))

    def test_file_stop_during_startup_countdown_sends_no_game_input(self):
        from tds_auto.session import main
        output=self.path/'cancelled_start'
        def stop_requested():
            (output/'stop').touch()
            return False
        platform=SimpleNamespace(stop_requested=stop_requested,close=lambda:None)
        with patch('tds_auto.session.WindowsOS',return_value=platform), \
             patch('tds_auto.session.locate_roblox') as locate:
            self.assertEqual(main(['start','--confirm-start','--startup-delay','1','--output',str(output)]),2)
        locate.assert_not_called()

    def test_ready_can_take_thirty_seconds_to_start_without_another_click(self):
        from tds_auto.recording import LatestFrame
        from tds_auto.resources import Hud
        from tds_auto.match import Snapshot
        from tds_auto.run import Progress
        from tds_auto.strategy import Step
        playback=object.__new__(Playback)
        playback.driver=self.driver;playback.window=self.driver.expected
        playback.profile={'slot':1,'dpi':120,'strategy_sha256':'test'}
        playback.strategy=SimpleNamespace(steps=())
        playback.output=self.path;playback.full_evidence=False
        playback.recording=LatestFrame(self.path/'latest.png')
        playback.camera=SimpleNamespace(bind=lambda f:True,check=lambda f:True,map_point=lambda p:p)
        playback.finish_if_result=lambda frame:playback.observer.observe(frame).state
        playback.frame=lambda:None
        playback.save_evidence=lambda *args:None
        playback.notify=lambda *args:None;playback.pause=lambda *args:None
        playback.observer=SimpleNamespace(observe=lambda f:SimpleNamespace(state='in_match' if self.platform.clock>=30 else 'match_ready'))
        playback.hud=SimpleNamespace(read=lambda f:Hud(1000,0,'Scout',0,150,1 if self.platform.clock>=30 else None))
        playback.read=lambda:Snapshot('match_ready',Hud(1000,0,'Scout',0,150,None),True)
        self.driver.before_click=None
        def sequence(strategy,runner,progress,mapper,operations,before,checkpoint):
            before(Step('UpgradeTower',(1,)),Progress(2,0,{}))
        with patch('tds_auto.run.run_sequence',side_effect=sequence), \
             patch('tds_auto.run.time.monotonic',side_effect=self.platform.now):
            result=playback.play(start_waves=True)
        self.assertEqual(result['status'],'operation_limit_reached')
        self.assertGreaterEqual(self.platform.clock,30)
        self.assertEqual(self.platform.events.count(('left_down',)),1)

if __name__=='__main__':unittest.main()
