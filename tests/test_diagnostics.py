import json
from pathlib import Path
import tempfile
import unittest

from tds_auto.diagnostics import collect_diagnostics


class DiagnosticsTests(unittest.TestCase):
    def test_redacts_and_limits_private_data_and_recent_events(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with (root/'hardcore_actions.jsonl').open('w',encoding='utf-8') as f:
                for i in range(50):
                    f.write(json.dumps({'phase':'hardcore_action','wave':i,
                        'secret':'do_not_copy','reason':'password: test123',
                        'tower_id':'F1'})+'\n')
            text=collect_diagnostics({'phase':'running','reason':
                         r'C:\Users\Private\Documents\run; user@site.com 123456789'},root)
            for secret in ('test123','user@site.com','Private','do_not_copy'):
                self.assertNotIn(secret,text)
            self.assertIn('wave=49',text)
            self.assertNotIn('wave=1 ',text)
            self.assertLess(len(text),6500)

    def test_redacts_private_windows_paths_with_spaces(self):
        from tds_auto.diagnostics import sanitized
        msg='Save failed D:/Side Projects/Private User/run.log; phase=stopped'
        output=sanitized(msg)
        self.assertNotIn('Private User',output)
        self.assertNotIn('Projects',output)
        self.assertIn('phase=stopped',output)
        self.assertIn('[private path]',output)

    def test_no_file_or_command_execution(self):
        self.assertIn('phase=ready',collect_diagnostics({'phase':'ready'},None))
