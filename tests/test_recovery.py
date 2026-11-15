"""Failure relaunch policy tests; injected adapters never touch Roblox."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from dataclasses import replace
from unittest.mock import patch
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from test_control import FakeOS
from tds_auto.control import StopRun
from tds_auto.session import SessionControl


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)
        self.platform=FakeOS()

    def module(self):
        from tds_auto import recovery
        return recovery

    def test_failure_relaunches_into_a_fresh_attempt_and_preserves_totals_and_evidence(self):
        recovery=self.module();calls=[]
        def attempt(path,control,totals):
            calls.append(path)
            totals['wins']+=1;totals['coins_total']+=450
            return {'status':'stopped','reason':'map unreadable'} if len(calls)==1 else {'status':'victory'}
        launches=[]
        result=recovery.supervise(self.path,self.platform,None,attempt=attempt,
            restart=lambda *args:launches.append(1),locate=lambda:self.platform.window)
        self.assertEqual((result['status'],result['wins'],result['coins_total']),('victory',2,900))
        self.assertEqual(len(launches),1)
        self.assertNotEqual(calls[0],calls[1])
        self.assertEqual(json.loads((calls[0]/'result.json').read_text())['status'],'stopped')
        self.assertEqual(json.loads((calls[1]/'result.json').read_text())['status'],'victory')

    def test_manual_stop_or_focus_loss_never_relaunches(self):
        recovery=self.module()
        for kind in ('user_stop','focus_lost','window_changed','setup','storage'):
            with self.subTest(kind=kind):
                root=self.path/kind;root.mkdir()
                launches=[]
                result=recovery.supervise(root,self.platform,None,
                    attempt=lambda *args:{'status':'stopped','stop_kind':kind,'reason':'guard'},
                    restart=lambda *args:launches.append(1),locate=lambda:self.platform.window)
                self.assertEqual(result['status'],'stopped')
                self.assertEqual(launches,[])

    def test_relaunch_budget_is_bounded_without_a_confirmed_win(self):
        recovery=self.module();launches=[];attempts=[]
        def attempt(*args):attempts.append(1);return {'status':'stopped','reason':'UI changed'}
        result=recovery.supervise(self.path,self.platform,None,attempt=attempt,
            restart=lambda *args:launches.append(1),locate=lambda:self.platform.window)
        self.assertEqual(len(attempts),4)
        self.assertEqual(len(launches),3)
        self.assertIn('recovery limit',result['reason'].lower())

    def test_a_confirmed_win_resets_the_consecutive_recovery_budget(self):
        recovery=self.module();number=[0];launches=[]
        def attempt(path,control,totals):
            number[0]+=1
            if number[0] in (2,4):totals['wins']+=1
            return {'status':'victory' if number[0]==4 else 'stopped','reason':'failure'}
        result=recovery.supervise(self.path,self.platform,None,attempt=attempt,
            restart=lambda *args:launches.append(1),locate=lambda:self.platform.window,max_recoveries=2)
        self.assertEqual(result['status'],'victory')
        self.assertEqual(len(launches),3)

    def test_focus_race_after_a_generic_failure_cancels_recovery(self):
        recovery=self.module();launches=[]
        result=recovery.supervise(self.path,self.platform,None,
            attempt=lambda *args:{'status':'stopped','reason':'capture failure'},
            restart=lambda *args:launches.append(1),locate=lambda:replace(self.platform.window,foreground=False))
        self.assertEqual(result['stop_kind'],'focus_lost')
        self.assertEqual(launches,[])

    def test_an_inactive_or_unverifiable_existing_window_is_not_treated_as_a_crash(self):
        recovery=self.module();launches=[]
        def inactive():raise StopRun('Window minimized',kind='window_changed')
        result=recovery.supervise(self.path,self.platform,None,
            attempt=lambda *args:{'status':'stopped','reason':'capture unavailable'},
            restart=lambda *args:launches.append(1),locate=inactive)
        self.assertEqual(result['stop_kind'],'window_changed')
        self.assertEqual(launches,[])

    def test_a_missing_client_can_be_reopened(self):
        recovery=self.module();launches=[];calls=[]
        def missing():raise RuntimeError('No Roblox window')
        def attempt(*args):
            calls.append(1)
            return {'status':'stopped','reason':'client disappeared'} if len(calls)==1 else {'status':'victory'}
        result=recovery.supervise(self.path,self.platform,None,attempt=attempt,
            restart=lambda *args:launches.append(1),locate=missing)
        self.assertEqual(result['status'],'victory')
        self.assertEqual(launches,[1])

    def test_close_rechecks_identity_and_foreground_before_posting(self):
        recovery=self.module()
        for current in (replace(self.platform.window,pid=99),replace(self.platform.window,foreground=False)):
            with self.subTest(current=current),patch.object(recovery,'locate_client',return_value=current), \
                 patch.object(recovery.ctypes,'WinDLL') as native:
                with self.assertRaises(StopRun):recovery.close_client(self.platform.window)
                native.assert_not_called()

    def test_stop_marker_during_failure_cancels_before_relaunch(self):
        recovery=self.module();launches=[]
        def attempt(path,control,totals):
            (self.path/'stop').touch()
            return {'status':'stopped','reason':'failure'}
        result=recovery.supervise(self.path,self.platform,None,attempt=attempt,
            restart=lambda *args:launches.append(1),locate=lambda:self.platform.window)
        self.assertEqual(result['stop_kind'],'user_stop')
        self.assertEqual(launches,[])

    def test_lobby_and_login_reward_arrivals_are_accepted_without_input(self):
        recovery=self.module()
        for target in ('lobby','login_rewards'):
            with self.subTest(target=target):
                root=self.path/target;root.mkdir();control=SessionControl(root)
                states=iter(['loading',target,target]);actions=[]
                recovery.restart_client(control,self.platform,lambda **data:None,
                    locate=lambda:self.platform.window,close=lambda w:actions.append('close'),
                    exists=lambda w:False,launch=lambda:actions.append('launch'),
                    observe=lambda w:next(states,target))
                self.assertEqual(actions,['close','launch'])
                self.assertEqual(self.platform.events,[])

    def test_f2_during_cooldown_prevents_close_and_launch(self):
        recovery=self.module();control=SessionControl(self.path);actions=[]
        self.platform.on_sleep=lambda platform:(self.path/'stop').touch()
        with self.assertRaises(StopRun) as caught:
            recovery.restart_client(control,self.platform,lambda **data:None,
                locate=lambda:self.platform.window,close=lambda w:actions.append('close'),
                exists=lambda w:False,launch=lambda:actions.append('launch'),observe=lambda w:'lobby')
        self.assertEqual(caught.exception.kind,'user_stop')
        self.assertEqual(actions,[])

    def test_emergency_stop_also_cancels_recovery_before_close(self):
        recovery=self.module();actions=[];self.platform.stopped=True
        with self.assertRaises(StopRun) as caught:
            recovery.restart_client(SessionControl(self.path),self.platform,lambda **data:None,
                locate=lambda:self.platform.window,close=lambda w:actions.append('close'),
                exists=lambda w:False,launch=lambda:actions.append('launch'),observe=lambda w:'lobby')
        self.assertEqual(caught.exception.kind,'user_stop')
        self.assertEqual(actions,[])

    def test_wait_never_passes_a_negative_duration_when_clock_advances_between_reads(self):
        recovery=self.module();clock=[0.0];sleeps=[]
        def now():clock[0]+=.03;return clock[0]
        def sleep(seconds):
            self.assertGreaterEqual(seconds,0)
            sleeps.append(seconds)
        self.platform.now=now;self.platform.sleep=sleep
        recovery.wait(SessionControl(self.path),self.platform,.1)
        self.assertTrue(sleeps)

    def test_failed_client_close_never_launches_another_client(self):
        recovery=self.module();control=SessionControl(self.path);actions=[]
        with self.assertRaisesRegex(StopRun,'did not close'):
            recovery.restart_client(control,self.platform,lambda **data:None,
                locate=lambda:self.platform.window,close=lambda w:actions.append('close'),
                exists=lambda w:True,launch=lambda:actions.append('launch'),observe=lambda w:'lobby',confirm=lambda *args:False)
        self.assertEqual(actions,['close'])

    def test_close_prompt_requires_its_title_and_both_button_labels(self):
        recovery=self.module()
        frame=Image.new('RGB',(1920,991))
        for captions,expected in ((['New to the Roblox App','Close Roblox','Back to Home'],True),
                                  (['New to the Roblox App','Other','Back to Home'],False),
                                  (['Other'],False)):
            with patch.object(recovery,'LocalOCR') as ocr:
                ocr.return_value.read.side_effect=captions
                self.assertEqual(recovery.close_prompt(frame),expected)

    def test_known_close_confirmation_is_attempted_once_before_relaunch(self):
        recovery=self.module();actions=[];checks=iter([True,True,False])
        recovery.restart_client(SessionControl(self.path),self.platform,lambda **data:None,
            locate=lambda:self.platform.window,close=lambda w:actions.append('close'),
            exists=lambda w:next(checks,False),launch=lambda:actions.append('launch'),observe=lambda w:'lobby',
            confirm=lambda *args:actions.append('confirm') or True)
        self.assertEqual(actions,['close','confirm','launch'])
        self.assertGreaterEqual(self.platform.now(),8)

    def test_process_lifetime_check_is_independent_of_a_window_handle(self):
        recovery=self.module()
        self.assertTrue(recovery.client_running(replace(self.platform.window,pid=os.getpid(),hwnd=0)))
        self.assertFalse(recovery.client_running(replace(self.platform.window,pid=0,hwnd=0)))

    def test_close_confirmation_uses_guarded_input_and_stops_if_caption_changes(self):
        recovery=self.module();control=SessionControl(self.path)
        with patch.object(recovery,'client_exists',return_value=True), \
             patch.object(recovery,'capture',return_value=Image.new('RGB',(1920,991))), \
             patch.object(recovery,'close_prompt',side_effect=[True,False]):
            with self.assertRaisesRegex(StopRun,'confirmation changed'):
                recovery.confirm_close(self.platform.window,control,self.platform)
        self.assertFalse(any(event[0]=='left_down' for event in self.platform.events))

    def test_expected_client_disappearance_after_close_click_allows_relaunch(self):
        recovery=self.module();control=SessionControl(self.path)
        for error,expected in ((RuntimeError('Window closed'),True),(StopRun('F2',kind='user_stop'),False)):
            with patch.object(recovery,'GuardedInput') as driver,patch.object(recovery,'capture'), \
                 patch.object(recovery,'close_prompt',return_value=True),patch.object(recovery,'client_exists',side_effect=[True,False]):
                driver.return_value.click.side_effect=error
                if expected:self.assertTrue(recovery.confirm_close(self.platform.window,control,self.platform))
                else:
                    with self.assertRaises(StopRun):recovery.confirm_close(self.platform.window,control,self.platform)

    def test_unreadable_reopened_lobby_has_a_deadline_and_sends_no_input(self):
        recovery=self.module();control=SessionControl(self.path);actions=[]
        with self.assertRaisesRegex(StopRun,'did not reach'):
            recovery.restart_client(control,self.platform,lambda **data:None,
                locate=lambda:self.platform.window,close=lambda w:actions.append('close'),
                exists=lambda w:False,launch=lambda:actions.append('launch'),observe=lambda w:'unknown',timeout=1)
        self.assertEqual(actions,['close','launch'])
        self.assertEqual(self.platform.events,[])
