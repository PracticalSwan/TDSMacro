"""Failure relaunch policy tests; injected adapters never touch Roblox."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
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

    def test_four_attempt_ledgers_preserve_63_wins_three_recoveries_and_one_user_stop(self):
        recovery=self.module();deltas=[35,5,15,8];attempt_deltas=[35,5,15,9]
        reasons=[
            'Post-vote title unreadable; Ready was not clicked.',
            'VIP prompt unconfirmed; no E was sent.',
            'Vote badge remained unknown; Ready was not clicked.',
            'F2 pressed after 44 confirmed actions; result not yet available.'
        ]
        calls=[]
        def attempt(path,control,totals):
            index=len(calls);calls.append(path)
            wins=deltas[index]
            totals['attempts']+=attempt_deltas[index]
            totals['matches_completed']+=wins
            totals['wins']+=wins
            totals['coins_total']+=wins*450
            kind='user_stop' if index==3 else 'failure'
            matches=[{'status':'victory','coins':450} for _ in range(wins)]
            if kind=='user_stop':
                matches.append({'status':'stopped','stop_kind':'user_stop','reason':reasons[index]})
            return {'status':'stopped','reason':reasons[index],'stop_kind':kind,'matches':matches}
        def restart(control,platform,report):
            platform.sleep(1)
            report(stage='lobby_ready')

        result=recovery.supervise(self.path,self.platform,None,attempt=attempt,
            restart=restart,locate=lambda:self.platform.window)

        sessions=[json.loads(line) for line in (self.path/'sessions.jsonl').read_text().splitlines()]
        events=[json.loads(line) for line in (self.path/'recovery.jsonl').read_text().splitlines()]
        self.assertEqual([row['attempt_folder'] for row in sessions],
                         ['attempt_001','attempt_002','attempt_003','attempt_004'])
        self.assertEqual([row['totals']['wins'] for row in sessions],[35,40,55,63])
        self.assertEqual([row['totals']['coins_total'] for row in sessions],[15750,18000,24750,28350])
        self.assertTrue(all(row['totals']['coins_total']==row['totals']['wins']*450 for row in sessions))
        self.assertEqual([row['recovery_attempt'] for row in events],[1,1,1],
                         'A win resets the consecutive-failure recovery counter.')
        self.assertEqual([row['recoveries'] for row in events],[1,2,3])
        self.assertEqual([row['elapsed_seconds'] for row in events],[1,2,3],
                         'Recovery elapsed time uses one app-run origin.')
        for row in events:
            self.assertTrue(row['event_time_utc'].endswith('Z'))
            datetime.fromisoformat(row['event_time_utc'].replace('Z','+00:00'))
        self.assertEqual([row['reason'] for row in events],reasons[:3])
        self.assertEqual((result['status'],result['stop_kind'],result['recoveries']),
                         ('stopped','user_stop',3))
        self.assertEqual((result['attempts'],result['matches_completed'],result['wins'],result['coins_total']),
                         (64,63,63,28350))
        self.assertEqual(result['coins_total'],sessions[-1]['totals']['coins_total'],
                         'Lifetime totals are cumulative, not the sum of cumulative ledger snapshots.')
        self.assertEqual(sessions[-1]['result']['reason'],reasons[-1])

    def test_protected_stops_never_relaunch(self):
        recovery=self.module()
        for kind in ('user_stop','focus_interrupted','window_changed','setup','storage'):
            with self.subTest(kind=kind):
                root=self.path/kind;root.mkdir()
                launches=[]
                result=recovery.supervise(root,self.platform,None,
                    attempt=lambda *args:{'status':'stopped','stop_kind':kind,'reason':'guard'},
                    restart=lambda *args:launches.append(1),locate=lambda:self.platform.window)
                self.assertEqual(result['status'],'stopped')
                self.assertEqual(launches,[])

    def test_natural_focus_return_requires_two_stable_reads_without_input(self):
        recovery=self.module();expected=self.platform.window;seen=[]
        states=iter([False,True,False,True,True])
        recovery.await_foreground(SessionControl(self.path),self.platform,expected,
            locate=lambda:replace(expected,foreground=next(states)),report=lambda **row:seen.append(row))
        self.assertAlmostEqual(self.platform.now(),.8)
        self.assertEqual([row['stage'] for row in seen],['awaiting_foreground','foreground_restored'])
        self.assertEqual(self.platform.events,[])

    def test_passive_focus_wait_cancels_for_stop_pause_and_emergency(self):
        recovery=self.module()
        for stop in ('stop','pause','emergency'):
            with self.subTest(stop=stop):
                root=self.path/stop;root.mkdir();platform=FakeOS();expected=platform.window
                def cancel(os):
                    if stop=='emergency':os.stopped=True
                    else:(root/stop).touch()
                platform.on_sleep=cancel
                with self.assertRaises(StopRun) as caught:
                    recovery.await_foreground(SessionControl(root),platform,expected,
                        locate=lambda:replace(expected,foreground=False))
                self.assertEqual(caught.exception.kind,'user_stop')
                self.assertLess(platform.now(),.2)
                self.assertEqual(platform.events,[])

    def test_focus_wait_rejects_changed_identity_or_geometry_even_in_background(self):
        recovery=self.module();expected=self.platform.window
        for changed in ({'hwnd':3},{'pid':4},{'x':2},{'y':30},{'width':1800},{'height':992},{'dpi':96}):
            with self.subTest(changed=changed),self.assertRaises(StopRun) as caught:
                recovery.await_foreground(SessionControl(self.path),self.platform,expected,
                    locate=lambda:replace(expected,foreground=False,**changed))
            self.assertEqual(caught.exception.kind,'window_changed')
        self.assertEqual(self.platform.events,[])

    def test_unverifiable_interrupted_client_stops_without_input(self):
        recovery=self.module()
        def missing():raise RuntimeError('No visible client')
        with self.assertRaises(StopRun) as caught:
            recovery.await_foreground(SessionControl(self.path),self.platform,self.platform.window,locate=missing)
        self.assertEqual(caught.exception.kind,'focus_interrupted')
        self.assertEqual(self.platform.events,[])

    def test_brief_focus_loss_restarts_once_in_a_fresh_attempt(self):
        recovery=self.module();calls=[];restarts=[];expected=self.platform.window
        def attempt(path,control,totals):
            calls.append(path)
            if len(calls)==1:
                self.platform.window=replace(expected,foreground=False)
                return {'status':'stopped','matches':[{'stop_kind':'focus_lost','reason':'Interrupted purchase'}]}
            return {'status':'victory'}
        def natural_return(os):
            if os.now()>=.3:os.window=expected
        self.platform.on_sleep=natural_return
        result=recovery.supervise(self.path,self.platform,None,attempt=attempt,
            restart=lambda *args:restarts.append(self.platform.window),locate=lambda:self.platform.window)
        self.assertEqual((result['status'],result['recoveries']),('victory',1))
        self.assertEqual(restarts,[expected])
        self.assertNotEqual(calls[0],calls[1])
        self.assertEqual(self.platform.events,[])
        rows=[json.loads(line) for line in (self.path/'recovery.jsonl').read_text().splitlines()]
        self.assertEqual(rows[0]['stop_kind'],'focus_interrupted')
        self.assertEqual(rows[0]['stage'],'awaiting_foreground')

    def test_persistent_focus_loss_stops_in_five_seconds_without_restart(self):
        recovery=self.module();restarts=[]
        def attempt(*args):
            self.platform.window=replace(self.platform.window,foreground=False)
            raise StopRun('Not foreground',kind='focus_lost')
        result=recovery.supervise(self.path,self.platform,None,attempt=attempt,
            restart=lambda *args:restarts.append(1),locate=lambda:self.platform.window)
        self.assertEqual((result['stop_kind'],result['recoveries']),('focus_interrupted',0))
        self.assertAlmostEqual(self.platform.now(),5)
        self.assertEqual(restarts,[])
        self.assertEqual(self.platform.events,[])

    def test_start_without_foreground_cannot_enter_passive_recovery(self):
        recovery=self.module();restarts=[]
        self.platform.window=replace(self.platform.window,foreground=False)
        result=recovery.supervise(self.path,self.platform,None,
            attempt=lambda *args:{'status':'stopped','stop_kind':'focus_lost'},
            restart=lambda *args:restarts.append(1),locate=lambda:self.platform.window)
        self.assertEqual(result['stop_kind'],'focus_lost')
        self.assertEqual(self.platform.now(),0)
        self.assertEqual(restarts,[])

    def test_focus_recovery_uses_the_existing_relaunch_budget(self):
        recovery=self.module();restarts=[];attempts=[]
        def attempt(*args):
            attempts.append(1)
            return {'status':'stopped','stop_kind':'focus_lost'}
        result=recovery.supervise(self.path,self.platform,None,attempt=attempt,
            restart=lambda *args:restarts.append(1),locate=lambda:self.platform.window)
        self.assertEqual((len(attempts),len(restarts),result['recoveries']),(4,3,3))
        self.assertIn('recovery limit',result['reason'].lower())

    def test_changed_client_during_cooldown_is_never_closed_or_relaunched(self):
        recovery=self.module();actions=[];expected=self.platform.window
        self.platform.on_sleep=lambda os:setattr(os,'window',replace(expected,pid=99))
        with self.assertRaises(StopRun) as caught:
            recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
                locate=lambda:self.platform.window,expected=expected,
                close=lambda w:actions.append('close'),launch=lambda:actions.append('launch'))
        self.assertEqual(caught.exception.kind,'window_changed')
        self.assertEqual(actions,[])

    def test_original_missing_then_replaced_during_cooldown_never_closes_replacement(self):
        recovery=self.module();expected=self.platform.window;replacement=replace(expected,pid=99,hwnd=100)
        seen=[];actions=[];original_restart=recovery.restart_client
        def locate():
            seen.append(1)
            if len(seen)==1:return expected
            if len(seen)==2:raise RuntimeError('Original client disappeared')
            return replacement
        def restart(control,platform,report,**kwargs):
            return original_restart(control,platform,report,**kwargs,
                close=lambda w:actions.append(('close',w.pid)),exists=lambda w:False,
                launch=lambda:actions.append(('launch',)),observe=lambda w:'lobby')
        with patch.object(recovery,'restart_client',side_effect=restart):
            result=recovery.supervise(self.path,self.platform,None,
                attempt=lambda *args:{'status':'stopped','reason':'Game failed'},locate=locate,max_recoveries=1)
        self.assertEqual(actions,[])
        self.assertEqual(result['stop_kind'],'window_changed')

    def test_anchored_client_crash_can_relaunch_when_it_stays_absent_until_launch(self):
        recovery=self.module();expected=self.platform.window;launched=[]
        def locate():
            if not launched:raise RuntimeError('Original client exited')
            return replace(expected,pid=99,hwnd=100)
        recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
            locate=locate,expected=expected,close=lambda w:self.fail('No client to close'),
            launch=lambda:launched.append(1),observe=lambda w:'lobby')
        self.assertEqual(launched,[1])

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

    def test_store_broker_settles_for_sixty_seconds_after_process_exit(self):
        recovery=self.module();closed=[];launched=[];stages=[]
        recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:stages.append(row['stage']),
            locate=lambda:self.platform.window,close=lambda w:closed.append(self.platform.now()),
            exists=lambda w:False,launch=lambda:launched.append(self.platform.now()),observe=lambda w:'lobby')
        self.assertEqual(len(launched),1)
        self.assertGreaterEqual(launched[0]-closed[0],60)
        self.assertIn('settling_launcher',stages)

    def test_an_already_absent_client_still_allows_the_launcher_to_settle(self):
        recovery=self.module();launched=[];seen=[]
        def missing():
            seen.append(1)
            if len(seen)==1:raise RuntimeError('No Roblox window')
            return self.platform.window
        recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
            locate=missing,close=lambda w:self.fail('No client to close'),
            launch=lambda:launched.append(self.platform.now()),observe=lambda w:'lobby',timeout=1)
        self.assertEqual(len(launched),1)
        self.assertGreaterEqual(launched[0],65)

    def test_stop_partway_through_broker_settle_prevents_launch(self):
        recovery=self.module();actions=[]
        def stop_later(platform):
            if platform.now()>=35:(self.path/'stop').touch()
        self.platform.on_sleep=stop_later
        with self.assertRaises(StopRun) as caught:
            recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
                locate=lambda:self.platform.window,close=lambda w:actions.append('close'),
                exists=lambda w:False,launch=lambda:actions.append('launch'),observe=lambda w:'lobby')
        self.assertEqual(caught.exception.kind,'user_stop')
        self.assertEqual(actions,['close'])

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

    def test_disconnect_prompt_requires_observed_dialog_and_exact_actions(self):
        recovery=self.module()
        path=Path(__file__).resolve().parent/'fixtures'/'disconnect_leave_prompt.png'
        with Image.open(path) as source:frame=source.copy()
        self.assertEqual(recovery.Observer().observe(frame).state,'disconnect')
        self.assertTrue(recovery.disconnect_prompt(frame))
        with patch.object(recovery,'LocalOCR') as ocr:
            ocr.return_value.read.side_effect=['Disconnected','Leave','Try Again']
            self.assertFalse(recovery.disconnect_prompt(frame))
        self.assertFalse(recovery.disconnect_prompt(Image.new('RGB',(100,100))))

    def test_roblox_home_transition_requires_all_four_exact_anchors(self):
        recovery=self.module()
        path=Path(__file__).resolve().parent/'fixtures'/'roblox_home_controls.png'
        with Image.open(path) as source:frame=source.copy()
        self.assertTrue(recovery.roblox_home(frame))
        self.assertFalse(recovery.roblox_home(Image.new('RGB',(100,100))))
        with patch.object(recovery,'LocalOCR') as ocr:
            ocr.return_value.read.side_effect=['Home','Search','For you','Discover']
            self.assertFalse(recovery.roblox_home(frame))

    def test_home_screen_is_not_a_confirmable_close_or_disconnect_dialog(self):
        recovery=self.module();control=SessionControl(self.path)
        path=Path(__file__).resolve().parent/'fixtures'/'roblox_home_controls.png'
        with Image.open(path) as source:frame=source.copy()
        with patch.object(recovery,'client_exists',return_value=True), \
             patch.object(recovery,'capture',return_value=frame):
            self.assertFalse(recovery.close_prompt(frame))
            self.assertFalse(recovery.disconnect_prompt(frame))
            self.assertFalse(recovery.confirm_close(self.platform.window,control,self.platform))
        self.assertFalse(any(event[0]=='left_down' for event in self.platform.events))

    def test_disconnect_leave_confirmation_is_guarded_and_rechecks_before_click(self):
        recovery=self.module();control=SessionControl(self.path)
        frame=Image.new('RGB',(1920,991))
        with patch.object(recovery,'client_exists',return_value=True), \
             patch.object(recovery,'capture',return_value=frame), \
             patch.object(recovery,'close_prompt',return_value=False), \
             patch.object(recovery,'disconnect_prompt',side_effect=[True,True]):
            self.assertEqual(recovery.confirm_close(self.platform.window,control,self.platform),'disconnect')
        self.assertIn(('move',845,634),self.platform.events)
        self.assertEqual(self.platform.events.count(('left_down',)),1)
        self.assertEqual(self.platform.events[-1],('left_up',))

        self.platform.events.clear()
        with patch.object(recovery,'client_exists',return_value=True), \
             patch.object(recovery,'capture',return_value=frame), \
             patch.object(recovery,'close_prompt',return_value=False), \
             patch.object(recovery,'disconnect_prompt',side_effect=[True,False]):
            with self.assertRaisesRegex(StopRun,'disconnect dialog changed'):
                recovery.confirm_close(self.platform.window,control,self.platform)
        self.assertNotIn(('left_down',),self.platform.events)

    def test_consumed_disconnect_dialog_cannot_click_leave_again(self):
        recovery=self.module();control=SessionControl(self.path);frame=Image.new('RGB',(1920,991))
        with patch.object(recovery,'client_exists',return_value=True), \
             patch.object(recovery,'capture',return_value=frame), \
             patch.object(recovery,'close_prompt',return_value=False), \
             patch.object(recovery,'disconnect_prompt') as disconnect:
            self.assertFalse(recovery.confirm_close(self.platform.window,control,self.platform,allow_disconnect=False))
        disconnect.assert_not_called()
        self.assertFalse(any(event[0]=='left_down' for event in self.platform.events))

    def test_leave_home_reposts_one_close_then_confirms_close_dialog(self):
        recovery=self.module();control=SessionControl(self.path);posts=[];confirms=[];launched=[];running=[True]
        home=Image.new('RGB',(1920,991))
        with patch.object(recovery,'capture',return_value=home), \
             patch.object(recovery,'roblox_home',side_effect=[True,True],create=True) as home_check:
            def close(window):posts.append(window)
            def confirm(window,control,platform,allow_disconnect=True):
                confirms.append(allow_disconnect)
                if len(confirms)==1:return 'disconnect'
                running[0]=False
                return 'close'
            recovery.restart_client(control,self.platform,lambda **row:None,
                locate=lambda:self.platform.window,close=close,exists=lambda window:running[0],
                launch=lambda:launched.append(self.platform.now()),observe=lambda window:'lobby',confirm=confirm)
        self.assertEqual(len(posts),2)
        self.assertEqual(confirms,[True,False])
        self.assertEqual(home_check.call_count,2)
        self.assertEqual(len(launched),1)
        self.assertGreaterEqual(launched[0],recovery.LAUNCHER_SETTLE_SECONDS+5)

    def test_leave_that_exits_client_does_not_repost_close(self):
        recovery=self.module();posts=[];launched=[];checks=iter([True,False])
        recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
            locate=lambda:self.platform.window,close=lambda window:posts.append(window),
            exists=lambda window:next(checks,False),launch=lambda:launched.append(True),observe=lambda window:'lobby',
            confirm=lambda *args:'disconnect')
        self.assertEqual(len(posts),1)
        self.assertEqual(launched,[True])

    def test_leave_requires_two_home_reads_before_reposting_close(self):
        recovery=self.module();posts=[];launched=[];running=[True]
        with patch.object(recovery,'capture',return_value=Image.new('RGB',(1920,991))), \
             patch.object(recovery,'roblox_home',return_value=False,create=True), \
             patch.object(recovery,'close_prompt',return_value=False):
            with self.assertRaisesRegex(StopRun,'verified Home') as caught:
                recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
                    locate=lambda:self.platform.window,close=lambda window:posts.append(window),
                    exists=lambda window:running[0],launch=lambda:launched.append(True),
                    observe=lambda window:'lobby',confirm=lambda *args:'disconnect')
        self.assertEqual(caught.exception.kind,'setup')
        self.assertEqual(len(posts),1)
        self.assertEqual(launched,[])

    def test_one_transient_home_read_does_not_repost_close(self):
        recovery=self.module();posts=[];launched=[];reads=iter([True,False])
        def home(frame):return next(reads,False)
        with patch.object(recovery,'capture',return_value=Image.new('RGB',(1920,991))), \
             patch.object(recovery,'roblox_home',side_effect=home,create=True), \
             patch.object(recovery,'close_prompt',return_value=False):
            with self.assertRaisesRegex(StopRun,'verified Home'):
                recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
                    locate=lambda:self.platform.window,close=lambda window:posts.append(window),
                    exists=lambda window:True,launch=lambda:launched.append(True),observe=lambda window:'lobby',
                    confirm=lambda *args:'disconnect')
        self.assertEqual(len(posts),1)
        self.assertEqual(launched,[])

    def test_exact_close_prompt_after_leave_uses_close_only_confirmation(self):
        recovery=self.module();posts=[];confirms=[];launched=[];running=[True]
        with patch.object(recovery,'capture',return_value=Image.new('RGB',(1920,991))), \
             patch.object(recovery,'roblox_home',return_value=False,create=True), \
             patch.object(recovery,'close_prompt',return_value=True):
            def confirm(window,control,platform,allow_disconnect=True):
                confirms.append(allow_disconnect)
                if len(confirms)==1:return 'disconnect'
                running[0]=False
                return 'close'
            recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
                locate=lambda:self.platform.window,close=lambda window:posts.append(window),
                exists=lambda window:running[0],launch=lambda:launched.append(True),observe=lambda window:'lobby',confirm=confirm)
        self.assertEqual(len(posts),1)
        self.assertEqual(confirms,[True,False])
        self.assertEqual(launched,[True])

    def test_process_exit_between_home_gate_and_second_close_is_expected(self):
        recovery=self.module();posts=[];launched=[];running=[True]
        def close(window):
            posts.append(window)
            if len(posts)==2:
                running[0]=False
                raise RuntimeError('Window closed during WM_CLOSE')
        with patch.object(recovery,'capture',return_value=Image.new('RGB',(1920,991))), \
             patch.object(recovery,'roblox_home',side_effect=[True,True],create=True):
            recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
                locate=lambda:self.platform.window,close=close,exists=lambda window:running[0],
                launch=lambda:launched.append(True),observe=lambda window:'lobby',confirm=lambda *args:'disconnect')
        self.assertEqual(len(posts),2)
        self.assertEqual(launched,[True])

    def test_f2_during_second_home_sample_prevents_reposted_close(self):
        recovery=self.module();posts=[];launched=[];reads=[0]
        def home(frame):
            reads[0]+=1
            if reads[0]==1:(self.path/'stop').write_text('F2')
            return True
        with patch.object(recovery,'capture',return_value=Image.new('RGB',(1920,991))), \
             patch.object(recovery,'roblox_home',side_effect=home,create=True):
            with self.assertRaises(StopRun) as caught:
                recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
                    locate=lambda:self.platform.window,close=lambda window:posts.append(window),
                    exists=lambda window:True,launch=lambda:launched.append(True),observe=lambda window:'lobby',
                    confirm=lambda *args:'disconnect')
        self.assertEqual(caught.exception.kind,'user_stop')
        self.assertEqual(reads[0],1)
        self.assertEqual(len(posts),1)
        self.assertEqual(launched,[])

    def test_stop_after_leave_cancels_before_second_close(self):
        recovery=self.module();posts=[];launched=[];control=SessionControl(self.path)
        def confirm(*args):
            (self.path/'stop').write_text('F2')
            return 'disconnect'
        with self.assertRaises(StopRun) as caught:
            recovery.restart_client(control,self.platform,lambda **row:None,
                locate=lambda:self.platform.window,close=lambda window:posts.append(window),
                exists=lambda window:True,launch=lambda:launched.append(True),observe=lambda window:'lobby',confirm=confirm)
        self.assertEqual(caught.exception.kind,'user_stop')
        self.assertEqual(len(posts),1)
        self.assertEqual(launched,[])

    def test_changed_client_after_leave_is_not_closed_or_relaunched(self):
        recovery=self.module();posts=[];launched=[];locations=iter([self.platform.window,replace(self.platform.window,pid=99)])
        with self.assertRaises(StopRun) as caught:
            recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
                locate=lambda:next(locations),close=lambda window:posts.append(window),
                exists=lambda window:True,launch=lambda:launched.append(True),observe=lambda window:'lobby',
                confirm=lambda *args:'disconnect')
        self.assertEqual(caught.exception.kind,'window_changed')
        self.assertEqual(len(posts),1)
        self.assertEqual(launched,[])

    def test_lost_foreground_after_leave_is_not_closed_or_relaunched(self):
        recovery=self.module();posts=[];launched=[]
        locations=iter([self.platform.window,replace(self.platform.window,foreground=False)])
        with self.assertRaises(StopRun) as caught:
            recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
                locate=lambda:next(locations),close=lambda window:posts.append(window),
                exists=lambda window:True,launch=lambda:launched.append(True),observe=lambda window:'lobby',
                confirm=lambda *args:'disconnect')
        self.assertEqual(caught.exception.kind,'focus_lost')
        self.assertEqual(len(posts),1)
        self.assertEqual(launched,[])

    def test_missing_window_after_leave_stops_while_original_process_lives(self):
        recovery=self.module();posts=[];launched=[];locations=iter([self.platform.window,None])
        with self.assertRaisesRegex(StopRun,'verified Home') as caught:
            recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
                locate=lambda:next(locations,None),close=lambda window:posts.append(window),
                exists=lambda window:True,launch=lambda:launched.append(True),observe=lambda window:'lobby',
                confirm=lambda *args:'disconnect')
        self.assertEqual(caught.exception.kind,'setup')
        self.assertEqual(len(posts),1)
        self.assertEqual(launched,[])

    def test_reappearing_disconnect_after_home_never_reposts_or_repeats_leave(self):
        recovery=self.module();posts=[];allowed=[];launched=[]
        with patch.object(recovery,'capture',return_value=Image.new('RGB',(1920,991))), \
             patch.object(recovery,'roblox_home',side_effect=[True,True],create=True):
            def confirm(window,control,platform,allow_disconnect=True):
                if len(allowed)<2:allowed.append(allow_disconnect)
                return 'disconnect'
            with self.assertRaisesRegex(StopRun,'did not close') as caught:
                recovery.restart_client(SessionControl(self.path),self.platform,lambda **row:None,
                    locate=lambda:self.platform.window,close=lambda window:posts.append(window),
                    exists=lambda window:True,launch=lambda:launched.append(True),observe=lambda window:'lobby',confirm=confirm)
        self.assertEqual(caught.exception.kind,'setup')
        self.assertEqual(allowed,[True,False])
        self.assertEqual(len(posts),2)
        self.assertEqual(launched,[])

    def test_recovery_ledger_append_failure_is_a_protected_storage_stop(self):
        recovery=self.module();original_open=Path.open
        def deny_recovery_ledger(path,*args,**kwargs):
            if path.name=='recovery.jsonl':raise PermissionError('recovery ledger is unavailable')
            return original_open(path,*args,**kwargs)
        def restart(control,platform,report):report(stage='closing')
        with patch.object(Path,'open',deny_recovery_ledger):
            result=recovery.supervise(self.path,self.platform,{},
                attempt=lambda path,control,totals:{'status':'stopped','reason':'recoverable failure','stop_kind':'failure'},
                restart=restart,locate=lambda:self.platform.window)
        self.assertEqual(result['status'],'stopped')
        self.assertEqual(result['stop_kind'],'storage')
        self.assertIn('recovery.jsonl',result['reason'])

    def test_known_close_confirmation_is_attempted_once_before_relaunch(self):
        recovery=self.module();actions=[];checks=iter([True,True,False])
        recovery.restart_client(SessionControl(self.path),self.platform,lambda **data:None,
            locate=lambda:self.platform.window,close=lambda w:actions.append('close'),
            exists=lambda w:next(checks,False),launch=lambda:actions.append('launch'),observe=lambda w:'lobby',
            confirm=lambda *args:actions.append('confirm') or 'close')
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

    def test_close_click_keeps_its_caption_clear_for_the_last_recheck(self):
        recovery=self.module();control=SessionControl(self.path)
        def readable(frame):
            moves=[e for e in self.platform.events if e[0]=='move']
            if not moves:return True
            x,y=moves[-1][1],moves[-1][2]-self.platform.window.y
            return not (740<=x<=860 and 694<=y<=736)
        with patch.object(recovery,'client_exists',return_value=True), \
             patch.object(recovery,'capture',return_value=Image.new('RGB',(1920,991))), \
             patch.object(recovery,'close_prompt',side_effect=readable):
            self.assertEqual(recovery.confirm_close(self.platform.window,control,self.platform),'close')
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_expected_client_disappearance_after_close_click_allows_relaunch(self):
        recovery=self.module();control=SessionControl(self.path)
        for error,expected in ((RuntimeError('Window closed'),True),(StopRun('F2',kind='user_stop'),False)):
            with patch.object(recovery,'GuardedInput') as driver,patch.object(recovery,'capture'), \
                 patch.object(recovery,'close_prompt',return_value=True),patch.object(recovery,'client_exists',side_effect=[True,False]):
                driver.return_value.click.side_effect=error
                if expected:self.assertEqual(recovery.confirm_close(self.platform.window,control,self.platform),'close')
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
