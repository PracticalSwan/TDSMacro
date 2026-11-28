"""Controller/hotkey contracts; never start or send input to Roblox."""
import ctypes
from ctypes import wintypes
import json
import queue
from pathlib import Path
import sys
import tempfile
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tds_auto.app import Controller, Hotkeys, STRATEGIES, preflight_roblox_start, status_text
from tds_auto.phase1 import RobloxWindowUnavailable, Window
from unittest.mock import patch


class Worker:
    def __init__(self): self.code=None
    def poll(self): return self.code


class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.commands=[]
        self.events=[]
        self.preflight_cancelled=None
        self.preflight_allow_recovery=None
        self.preflight_window=Window(101,202,0,29,1920,991,120,True)
        self.child=Worker()
        def launch(command,**kwargs):
            self.commands.append(command)
            self.events.append('launch')
            return self.child
        def preflight(cancelled=None,allow_recovery=False):
            self.events.append('preflight')
            self.preflight_cancelled=cancelled
            self.preflight_allow_recovery=allow_recovery
            if cancelled is not None and cancelled():
                raise RuntimeError('Roblox focus preflight cancelled.')
            return self.preflight_window
        self.controller=Controller(self.root,launch,preflight=preflight)

    def test_engine_enables_native_fault_logging_before_dispatch(self):
        from tds_auto.app import main
        calls=[]
        with patch('faulthandler.enable',side_effect=lambda **kw:calls.append(('fault_logging',kw))), \
             patch('tds_auto.session.main',side_effect=lambda args:calls.append(('engine',args)) or 0):
            self.assertEqual(main(['--engine','start','--output',str(self.root/'test-run')]),0)
        self.assertEqual([c[0] for c in calls],['fault_logging','engine'])
        self.assertIs(calls[0][1]['file'],sys.stderr)
        self.assertTrue(calls[0][1]['all_threads'])

    def test_refresh_button_hover_and_keyboard_focus_without_tk(self):
        from tds_auto.app import App
        class Button:
            def __init__(self):
                self.state='normal'
                self.events={}
                self.color=None
            def bind(self,tag,callback):self.events[tag]=callback
            def cget(self,key):return self.state
            def configure(self,**kwargs):self.color=kwargs.get('bg')
        button=Button()
        App._button_hover(button,'base','hover')
        button.events['<Enter>'](None)
        self.assertEqual(button.color,'hover')
        button.events['<Leave>'](None)
        self.assertEqual(button.color,'base')
        button.events['<FocusIn>'](None)
        self.assertEqual(button.color,'hover')
        button.state='disabled'
        button.events['<Leave>'](None)
        self.assertEqual(button.color,'hover')

    def test_update_install_never_starts_when_game_worker_running(self):
        from tds_auto.app import App
        from unittest.mock import Mock
        panel=App.__new__(App)
        panel.controller=Mock(running=True)
        panel.updater=Mock(staged=Path('verified'),busy=False)
        panel.update_message=Mock()
        panel.install_update()
        panel.updater.launch_installer.assert_not_called()
        panel.update_message.set.assert_called()

    def test_update_install_handover_starts_only_when_idle(self):
        from tds_auto.app import App
        from unittest.mock import Mock
        panel=App.__new__(App)
        panel.controller=Mock(running=False)
        panel.updater=Mock(staged=Path('verified'),busy=False)
        panel.updater.launch_installer.return_value=object()
        panel.update_message=Mock()
        panel.hotkeys=Mock()
        panel.root=Mock()
        panel.closing=False
        panel.update_handoff=False
        panel.install_update()
        self.assertTrue(panel.update_handoff)
        panel.updater.launch_installer.assert_called_once()
        panel.root.destroy.assert_called_once()
        panel.controller.stop.assert_not_called()

    def test_auto_update_poll_does_not_download_or_handover_while_running(self):
        from tds_auto.app import App
        from unittest.mock import Mock
        panel=App.__new__(App)
        panel.closing=False
        panel.updater=Mock(enabled=True,busy=False,staged=None,error=None,
                           release=object(),next_check=10**15,status='Waiting')
        panel.update_message=Mock()
        panel.check_update_button=Mock()
        panel.install_update_button=Mock()
        panel.install_update=Mock()
        panel.maintain_updates(True)
        panel.updater.prepare_now.assert_not_called()
        panel.install_update.assert_not_called()
        panel.maintain_updates(False)
        panel.updater.prepare_now.assert_called_once()

    def test_one_strategy_starts_one_explicit_continuous_guarded_worker(self):
        self.assertTrue(self.controller.start(next(iter(STRATEGIES))))
        self.assertFalse(self.controller.start(next(iter(STRATEGIES))))
        self.assertEqual(len(self.commands),1)
        command=self.commands[0]
        self.assertIn('--engine',command)
        self.assertIn('--confirm-start',command)
        self.assertIn('--continuous',command)
        self.assertIn('--auto-recover',command)
        self.assertEqual(command[command.index('--startup-delay')+1],'5')

    def test_auto_equip_unavailable_stops_before_new_worker(self):
        from tds_auto.hardcore_plan_v2 import PLAN_ID
        label=next(name for name,value in STRATEGIES.items() if value==PLAN_ID)
        self.controller.start(label,auto_recover=False)
        self.assertNotIn('--auto-equip',self.commands[0])
        self.child.code=0
        with self.assertRaisesRegex(RuntimeError,'Auto Equip is unavailable'):
            self.controller.start(label,auto_recover=False,auto_equip=True)
        self.assertEqual(len(self.commands),1)

    def test_auto_recovery_can_be_disabled_for_a_supervised_trial(self):
        self.controller.start(next(iter(STRATEGIES)),auto_recover=False)
        self.assertNotIn('--auto-recover',self.commands[0])

    def test_hardcore_selection_starts_one_v2_worker_with_the_native_anchor(self):
        from tds_auto.hardcore_plan_v2 import PLAN_ID
        strategy=next(label for label,value in STRATEGIES.items() if value==PLAN_ID)
        self.assertTrue(self.controller.start(strategy))
        self.assertFalse(self.controller.start(strategy))
        command=self.commands[0]
        self.assertEqual(command[command.index('--strategy')+1],PLAN_ID)
        self.assertIn('--expected-window',command)
        self.assertIn('--auto-recover',command)
        self.assertNotIn('--profile',command)

    def test_native_focus_preflight_precedes_worker_launch(self):
        self.controller.start(next(iter(STRATEGIES)))
        self.assertEqual(self.events,['preflight','launch'])
        self.assertIsNone(self.preflight_cancelled)
        self.assertTrue(self.preflight_allow_recovery)

    def test_worker_receives_the_exact_preflight_window_anchor(self):
        expected=Window(101,202,0,29,1920,991,120,True)
        self.controller.preflight=lambda cancelled=None,allow_recovery=False: expected
        self.controller.start(next(iter(STRATEGIES)))
        command=self.commands[0]
        anchor=json.loads(command[command.index('--expected-window')+1])
        self.assertEqual(anchor,{'hwnd':101,'pid':202,'x':0,'y':29,'width':1920,
                                'height':991,'dpi':120,'foreground':True})

    def test_missing_window_uses_guarded_native_recovery_without_anchor(self):
        self.controller.preflight=lambda cancelled=None,allow_recovery=False: None
        self.controller.start(next(iter(STRATEGIES)),auto_recover=True)
        command=self.commands[0]
        self.assertIn('--auto-recover',command)
        self.assertNotIn('--expected-window',command)
        self.assertIn('official Roblox launch',self.controller.startup_message)

    def test_missing_window_without_recovery_never_launches_worker(self):
        self.controller.preflight=lambda cancelled=None,allow_recovery=False: None
        with self.assertRaisesRegex(RuntimeError,'enable guarded recovery'):
            self.controller.start(next(iter(STRATEGIES)),auto_recover=False)
        self.assertEqual(self.commands,[])
        self.assertIsNone(self.controller.output)

    def test_preflight_allows_only_missing_window_to_defer_to_recovery(self):
        with patch('tds_auto.phase1.focus_roblox',side_effect=RobloxWindowUnavailable('missing')):
            self.assertIsNone(preflight_roblox_start(allow_recovery=True))
        with patch('tds_auto.phase1.focus_roblox',side_effect=RuntimeError('foreground denied')):
            with self.assertRaisesRegex(RuntimeError,'foreground denied'):
                preflight_roblox_start(allow_recovery=True)

    def test_failed_focus_preflight_never_launches_or_creates_run_folder(self):
        def fail(cancelled=None,allow_recovery=False):
            raise RuntimeError('Roblox did not reach the foreground.')
        self.controller.preflight=fail
        with self.assertRaisesRegex(RuntimeError,'foreground'):
            self.controller.start(next(iter(STRATEGIES)))
        self.assertEqual(self.commands,[])
        self.assertIsNone(self.controller.output)

    def test_f2_cancellation_during_preflight_never_launches_worker(self):
        with self.assertRaisesRegex(RuntimeError,'cancelled'):
            checks=iter((False,True))
            self.controller.start(next(iter(STRATEGIES)),cancelled=lambda: next(checks))
        self.assertEqual(self.commands,[])
        self.assertEqual(self.events,['preflight'])
        self.assertIsNone(self.controller.output)

    def test_queued_f1_then_f2_keeps_the_start_request_cancelled(self):
        keys=Hotkeys.__new__(Hotkeys)
        keys.events=queue.Queue()
        keys._generation_lock=threading.Lock()
        keys._stop_generation=0
        keys._queue_event('start')
        keys._queue_event('stop')
        action,generation=keys.events.get_nowait()
        self.assertEqual(action,'start')
        with self.assertRaisesRegex(RuntimeError,'cancelled'):
            self.controller.start(next(iter(STRATEGIES)),
                                  cancelled=lambda: keys.cancelled_since(generation))
        self.assertEqual(self.commands,[])
        self.assertEqual(self.events,[])

    def test_f2_during_worker_launch_writes_the_stop_marker_immediately(self):
        cancelled=threading.Event()
        def launch(command,**kwargs):
            self.commands.append(command)
            cancelled.set()
            return self.child
        self.controller.launch=launch
        self.controller.start(next(iter(STRATEGIES)),cancelled=cancelled.is_set)
        self.assertTrue((self.controller.output/'stop').exists())
        self.assertTrue(self.controller.stop_requested)

    def test_f2_stop_marker_works_even_before_worker_creates_its_folder(self):
        self.controller.start(next(iter(STRATEGIES)))
        self.assertTrue(self.controller.stop())
        self.assertTrue((self.controller.output/'stop').exists())
        self.assertTrue(self.controller.stop_requested)

    def test_idle_stop_or_invalid_strategy_never_launches_input(self):
        self.assertFalse(self.controller.stop())
        with self.assertRaises(ValueError):self.controller.start('Unknown strategy')
        self.assertEqual(self.commands,[])
        self.assertEqual(self.events,[])

    def test_restart_after_worker_exit_uses_new_evidence_folder(self):
        self.controller.start(next(iter(STRATEGIES)));before=self.controller.output
        self.child.code=2
        self.assertTrue(self.controller.start(next(iter(STRATEGIES))))
        self.assertNotEqual(before,self.controller.output)

    def test_worker_exit_before_first_status_shows_recorded_startup_failure(self):
        self.controller.start(next(iter(STRATEGIES)))
        self.controller.output.mkdir()
        reason = 'Roblox client identity changed during startup.'
        (self.controller.output/'result.json').write_text(
            json.dumps({'status': 'stopped', 'reason': reason}), encoding='utf-8')
        self.child.code = 2

        self.assertEqual(status_text(self.controller.status(), self.controller.running),
                         'Stopped: '+reason)

    def test_unexpected_worker_exit_replaces_ready_with_exit_details(self):
        self.controller.start(next(iter(STRATEGIES)))
        self.controller.output.mkdir()
        (self.controller.output/'status.json').write_text(
            json.dumps({'phase': 'hardcore_action', 'wave': 25}), encoding='utf-8')
        self.child.code = 1

        data = self.controller.status()
        self.assertEqual(data['wave'], 25)
        self.assertIn('exit code 1', status_text(data, self.controller.running))

    def test_status_reports_nested_stop_and_live_progress_without_raw_log_dump(self):
        self.assertIn('7 Scouts',status_text({'phase':'playing','match':2,'progress':{'count':7,'confirmed_step':21}},True))
        data={'result':{'matches':[{'status':'stopped','reason':'Map was not confirmed.'}]}}
        self.assertEqual(status_text(data,False),'Stopped: Map was not confirmed.')
        self.assertEqual(status_text({'phase':'stopped','matches':[{'reason':'Focus changed.'}]},False),'Stopped: Focus changed.')
        self.assertIn('Stopped.',status_text(data,False,True))
        self.assertEqual(status_text({},False,start_error='Roblox foreground was not verified.'),
                         'Start stopped: Roblox foreground was not verified.')

    def test_verified_early_defeat_gui_explains_bounded_direct_restart(self):
        text=status_text({'phase':'hardcore_early_result_retry','wave':28,
                          'consecutive_early_defeats':1},True)
        self.assertIn('wave-28',text)
        self.assertIn('1/2',text)
        self.assertIn('no full-cycle Gems counted',text)

    def test_passive_focus_wait_explains_natural_return_and_stop(self):
        text=status_text({'phase':'recovering','stage':'awaiting_foreground','recoveries':0,'seconds':30},True)
        self.assertIn('30 seconds',text)
        self.assertIn('naturally',text)
        self.assertIn('F2',text)
        self.assertNotIn('Recovery 1/',text)
        missing=status_text({'phase':'recovering','stage':'awaiting_foreground'},True)
        self.assertNotIn('seconds',missing)
        self.assertIn('naturally',missing)

    def test_native_f1_f2_queue_and_release_without_keyboard_input(self):
        keys=Hotkeys()
        try:
            user=ctypes.WinDLL('user32',use_last_error=True)
            user.PostThreadMessageW.argtypes=[wintypes.DWORD,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
            for ident,expected in ((0x5441,'start'),(0x5442,'stop')):
                self.assertTrue(user.PostThreadMessageW(keys.thread_id,0x0312,ident,0))
                action,generation=keys.events.get(timeout=1)
                self.assertEqual(action,expected)
                if expected=='stop':
                    self.assertEqual(generation,1)
                    self.assertTrue(keys.cancelled_since(0))
            with self.assertRaisesRegex(RuntimeError,'already in use'):Hotkeys()
        finally:keys.close()
        again=Hotkeys();again.close()
        self.assertFalse(again.thread.is_alive())
