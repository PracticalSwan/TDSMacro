"""Controller/hotkey contracts; never start or send input to Roblox."""
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tds_auto.app import Controller, Hotkeys, STRATEGIES, status_text


class Worker:
    def __init__(self): self.code=None
    def poll(self): return self.code


class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.commands=[]
        self.child=Worker()
        def launch(command,**kwargs):
            self.commands.append(command)
            return self.child
        self.controller=Controller(self.root,launch)

    def test_one_strategy_starts_one_explicit_continuous_guarded_worker(self):
        self.assertTrue(self.controller.start(next(iter(STRATEGIES))))
        self.assertFalse(self.controller.start(next(iter(STRATEGIES))))
        self.assertEqual(len(self.commands),1)
        command=self.commands[0]
        self.assertIn('--engine',command)
        self.assertIn('--confirm-start',command)
        self.assertIn('--continuous',command)
        self.assertEqual(command[command.index('--startup-delay')+1],'5')

    def test_f2_stop_marker_works_even_before_worker_creates_its_folder(self):
        self.controller.start(next(iter(STRATEGIES)))
        self.assertTrue(self.controller.stop())
        self.assertTrue((self.controller.output/'stop').exists())
        self.assertTrue(self.controller.stop_requested)

    def test_idle_stop_or_invalid_strategy_never_launches_input(self):
        self.assertFalse(self.controller.stop())
        with self.assertRaises(ValueError):self.controller.start('Unknown strategy')
        self.assertEqual(self.commands,[])

    def test_restart_after_worker_exit_uses_new_evidence_folder(self):
        self.controller.start(next(iter(STRATEGIES)));before=self.controller.output
        self.child.code=2
        self.assertTrue(self.controller.start(next(iter(STRATEGIES))))
        self.assertNotEqual(before,self.controller.output)

    def test_status_reports_nested_stop_and_live_progress_without_raw_log_dump(self):
        self.assertIn('7 Scouts',status_text({'phase':'playing','match':2,'progress':{'count':7,'confirmed_step':21}},True))
        data={'result':{'matches':[{'status':'stopped','reason':'Map was not confirmed.'}]}}
        self.assertEqual(status_text(data,False),'Stopped: Map was not confirmed.')
        self.assertIn('Stopped.',status_text(data,False,True))

    def test_native_f1_f2_queue_and_release_without_keyboard_input(self):
        keys=Hotkeys()
        try:
            user=ctypes.WinDLL('user32',use_last_error=True)
            user.PostThreadMessageW.argtypes=[wintypes.DWORD,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
            for ident,expected in ((0x5441,'start'),(0x5442,'stop')):
                self.assertTrue(user.PostThreadMessageW(keys.thread_id,0x0312,ident,0))
                self.assertEqual(keys.events.get(timeout=1),expected)
            with self.assertRaisesRegex(RuntimeError,'already in use'):Hotkeys()
        finally:keys.close()
        again=Hotkeys();again.close()
        self.assertFalse(again.thread.is_alive())
