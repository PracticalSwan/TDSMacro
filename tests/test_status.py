"""Atomic status-file sharing regressions; no OCR, hotkeys or game input."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from tds_auto.session import SessionControl


class StatusTests(unittest.TestCase):
    def setUp(self):
        directory=tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path=Path(directory.name)
        self.control=SessionControl(self.path)

    @unittest.skipUnless(sys.platform=='win32','Windows delete-sharing reproduction')
    def test_actual_windows_read_handle_collision_recovers_after_reader_closes(self):
        old=self.path/'status.json';old.write_text('{"phase":"old"}')
        original=Path.replace;calls=[]
        with old.open('r') as held:
            def replace(path,target):
                calls.append(1)
                try:return original(path,target)
                except PermissionError:
                    held.close()
                    raise
            with patch.object(Path,'replace',replace):self.control.write({'phase':'new'})
        self.assertEqual(len(calls),2)
        self.assertEqual(json.loads(old.read_text()),{'phase':'new'})

    def test_transient_reader_retry_keeps_the_same_completed_data(self):
        original=Path.replace;calls=[]
        def replace(path,target):
            calls.append(path.read_text())
            if len(calls)<3:
                error=PermissionError('Reader temporarily denies delete sharing');error.winerror=5
                raise error
            return original(path,target)
        with patch.object(Path,'replace',replace):self.control.write({'phase':'playing','step':1})
        self.assertEqual(json.loads((self.path/'status.json').read_text()),{'phase':'playing','step':1})
        self.assertEqual(len(calls),3)
        self.assertEqual(len(set(calls)),1)
        self.assertFalse((self.path/'status.tmp').exists())

    def test_permanent_denial_is_bounded_and_preserves_previous_status(self):
        old=self.path/'status.json';old.write_text('{"phase":"old"}')
        error=PermissionError('Persistent write denial');error.winerror=5
        with patch.object(Path,'replace',side_effect=error) as replace:
            with self.assertRaises(PermissionError):self.control.write({'phase':'new'})
        self.assertEqual(replace.call_count,5)
        self.assertEqual(old.read_text(),'{"phase":"old"}')
