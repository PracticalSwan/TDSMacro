"""Offline update checks, signed-by-release digest verification, and atomic rollback.

These tests never contact GitHub, restart Roblox, or replace the real application.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tds_auto import updates


def release(version='0.4.1', *, prerelease=False, digest=None):
    archive=f'TDSMacro-{version}-windows-x64.zip'
    checksum=f'TDSMacro-v{version}-SHA256SUMS.txt'
    base=f'https://github.com/PracticalSwan/TDSMacro/releases/download/v{version}/'
    return {'tag_name':f'v{version}','draft':False,'prerelease':prerelease,
            'assets':[{'name':archive,'browser_download_url':base+archive,
                       'digest':'sha256:'+(digest or 'a'*64),'size':12500},
                      {'name':checksum,'browser_download_url':base+checksum,
                       'digest':'sha256:'+'b'*64,'size':100}]}


def package(version='0.4.1', extra=None, ending=None):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('TDSMacro/TDSMacro.exe',b'not-real-exe')
        z.writestr('TDSMacro/README.txt',f'TDS Macro - Windows v{version}'+(ending or chr(10)))
        z.writestr('TDSMacro/_internal/required.dll',b'fake-dll')
        z.writestr('TDSMacro/strategies/hardcore_wretched_front_boomerang_crook_farm_v2.json','{}')
        for name,data in (extra or {}).items():z.writestr(name,data)
    return out.getvalue()


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def test_version_order_rejects_prereleases_and_downgrades(self):
        self.assertTrue(updates.is_newer('0.4.1','0.4.0'))
        self.assertTrue(updates.is_newer('1.0.0','0.4.99'))
        self.assertFalse(updates.is_newer('0.4.0','0.4.0'))
        self.assertFalse(updates.is_newer('0.3.9','0.4.0'))
        for unsafe in ('v0.4.1-beta','0.4.1rc1','../../2.0','0.4','1.2.3.4','0.04.1'):
            with self.subTest(value=unsafe):
                with self.assertRaises(updates.UpdateError):updates.parse_version(unsafe)

    def test_release_requires_official_stable_assets_and_digests(self):
        r=updates.parse_release(release(),current='0.4.0')
        self.assertEqual(r.version,'0.4.1')
        self.assertIn('github.com/PracticalSwan/TDSMacro/',r.archive_url)
        for bad in [
            dict(release(),prerelease=True),
            dict(release(),draft=True),
            dict(release(),tag_name='v0.4.0'),
            dict(release(),tag_name='v0.4.2'),
        ]:
            with self.subTest(bad=bad.get('tag_name')):
                with self.assertRaises(updates.UpdateError):updates.parse_release(bad,current='0.4.0')
        broken=release();broken['assets'][0]['browser_download_url']='https://evil.example/installer.zip'
        with self.assertRaises(updates.UpdateError):updates.parse_release(broken,current='0.4.0')
        broken=release();broken['assets'][0]['digest']=None
        with self.assertRaises(updates.UpdateError):updates.parse_release(broken,current='0.4.0')

    def test_preference_defaults_disabled_and_survives_restart(self):
        config=self.root/'prefs.json'
        self.assertFalse(updates.load_auto_update(config))
        updates.save_auto_update(config,True)
        self.assertTrue(updates.load_auto_update(config))
        updates.save_auto_update(config,False)
        self.assertFalse(updates.load_auto_update(config))
        config.write_text('{bad',encoding='utf-8')
        self.assertFalse(updates.load_auto_update(config))

    def test_checksum_requires_exact_filename_and_hash(self):
        data=package()
        digest=hashlib.sha256(data).hexdigest()
        self.assertEqual(updates.parse_checksum(f'{digest}  TDSMacro-0.4.1-windows-x64.zip\n'.encode(), 'TDSMacro-0.4.1-windows-x64.zip'),digest)
        for bad in (f'{digest}  ../TDSMacro-0.4.1-windows-x64.zip\n',
                    f'{digest}  TDSMacro-0.4.1-windows-x64.zip\nabc',
                    f'{"0"*64}  TDSMacro-other.zip\n'):
            with self.assertRaises(updates.UpdateError):
                updates.parse_checksum(bad.encode(),'TDSMacro-0.4.1-windows-x64.zip')

    def test_windows_crlf_readme_is_valid_and_same_version_is_rejected(self):
        raw=package(ending=chr(13)+chr(10))
        archive=self.root/'crlf.zip';archive.write_bytes(raw)
        staged=updates.stage_archive(archive,self.root/'updates','0.4.1',
                                     hashlib.sha256(raw).hexdigest())
        self.assertTrue((staged/'TDSMacro.exe').exists())
        old=self.root/'app'/'TDSMacro';old.mkdir(parents=True)
        (old/'TDSMacro.exe').write_bytes(b'old')
        (old/'README.txt').write_bytes(b'TDS Macro - Windows v0.4.1'+bytes((13,10)))
        with self.assertRaises(updates.UpdateError):
            updates.apply_staged(staged,old,expected_version='0.4.1')
        self.assertEqual((old/'TDSMacro.exe').read_bytes(),b'old')

    def test_untrusted_archive_paths_and_links_are_rejected_without_files_outside(self):
        unsafe_names=['TDSMacro/../pwned.txt','TDSMacro/../../pwned.txt',
                      'TDSMacro/CON','TDSMacro/name:stream','TDSMacro/'+chr(92)+'evil.txt',
                      'elsewhere/evil.txt']
        for index,name in enumerate(unsafe_names):
            with self.subTest(name=name):
                p=self.root/f'bad{index}.zip';p.write_bytes(package(extra={name:b'bad'}))
                target=self.root/f'extracted{index}'
                with self.assertRaises(updates.UpdateError):updates.extract_archive(p,target,'0.4.1')
        p=self.root/'symlink.zip'
        with zipfile.ZipFile(io.BytesIO(package()),'r') as z, zipfile.ZipFile(p,'w') as out:
            for item in z.infolist():out.writestr(item,z.read(item.filename))
            link=zipfile.ZipInfo('TDSMacro/fake-link')
            link.create_system=3;link.external_attr=(0o120777 << 16)
            out.writestr(link,'/etc/passwd')
        with self.assertRaises(updates.UpdateError):updates.extract_archive(p,self.root/'links','0.4.1')
        self.assertFalse((self.root/'pwned.txt').exists())

    def test_stage_rejects_digest_mismatch_and_keeps_install_untouched(self):
        raw=package(); path=self.root/'release.zip';path.write_bytes(raw)
        target=self.root/'updates'
        with self.assertRaises(updates.UpdateError):
            updates.stage_archive(path,target,'0.4.1','0'*64)
        self.assertFalse((target/'v0.4.1').exists())

    def test_modified_staged_strategy_is_rejected_before_install(self):
        raw=package();archive=self.root/'release.zip';archive.write_bytes(raw)
        staged=updates.stage_archive(archive,self.root/'updates','0.4.1',
                                      hashlib.sha256(raw).hexdigest())
        strategy=staged/'strategies/hardcore_wretched_front_boomerang_crook_farm_v2.json'
        strategy.write_text('modified after verification',encoding='utf-8')
        old=self.root/'app'/'TDSMacro';old.mkdir(parents=True)
        (old/'TDSMacro.exe').write_bytes(b'preserve')
        with self.assertRaises(updates.UpdateError):
            updates.apply_staged(staged,old,expected_version='0.4.1')
        self.assertEqual((old/'TDSMacro.exe').read_bytes(),b'preserve')

    def test_installer_preserves_old_tree_and_rollback_on_failed_swap(self):
        raw=package();archive=self.root/'release.zip';archive.write_bytes(raw)
        digest=hashlib.sha256(raw).hexdigest()
        staged=updates.stage_archive(archive,self.root/'updates','0.4.1',digest)
        install=self.root/'app'/'TDSMacro';install.mkdir(parents=True)
        (install/'TDSMacro.exe').write_bytes(b'old-program')
        (install/'captures').mkdir();(install/'captures'/'private.txt').write_text('never delete')
        backup=updates.apply_staged(staged,install,expected_version='0.4.1')
        self.assertEqual((install/'TDSMacro.exe').read_bytes(),b'not-real-exe')
        self.assertEqual((backup/'TDSMacro.exe').read_bytes(),b'old-program')
        self.assertEqual((backup/'captures/private.txt').read_text(),'never delete')
        self.assertFalse((install/'captures').exists())

    def test_backup_rollback_when_second_directory_rename_fails(self):
        raw=package();archive=self.root/'release.zip';archive.write_bytes(raw)
        staged=updates.stage_archive(archive,self.root/'updates','0.4.1',
                                     hashlib.sha256(raw).hexdigest())
        install=self.root/'program'/'TDSMacro';install.mkdir(parents=True)
        (install/'TDSMacro.exe').write_bytes(b'original')
        (install/'captures').mkdir()
        (install/'captures'/'private.txt').write_text('preserve')
        def fail_second(src,dst):
            if '.TDSMacro-incoming-' in str(src):
                raise PermissionError('simulated locked destination')
            os.rename(src,dst)
        with self.assertRaises(PermissionError):
            updates.apply_staged(staged,install,expected_version='0.4.1',rename=fail_second)
        self.assertEqual((install/'TDSMacro.exe').read_bytes(),b'original')
        self.assertEqual((install/'captures/private.txt').read_text(),'preserve')
        self.assertFalse(list(install.parent.glob('.TDSMacro-incoming-*')))

    def test_failed_version_never_auto_retries_after_gui_restart(self):
        state=self.root/'prefs'
        state.mkdir()
        (state/'failed-update.json').write_text(
            json.dumps({'version':'0.4.1','error':'directory locked'}),encoding='utf-8')
        service=updates.UpdateService(install_root=self.root/'TDSMacro',
                                      state_dir=state)
        service.messages.put(('check',updates.parse_release(release(),current='0.4.0'),None))
        service.poll()
        self.assertIsNotNone(service.error)
        self.assertIn('manual',service.status.lower())
        service.clear_failed()
        self.assertFalse((state/'failed-update.json').exists())
        self.assertIsNone(service.error)

    def test_service_default_off_and_no_network_without_explicit_check(self):
        calls=[]
        service=updates.UpdateService(install_root=self.root/'TDSMacro',
                 state_dir=self.root/'prefs',check=lambda current:calls.append(current))
        self.assertFalse(service.enabled)
        self.assertEqual(calls,[])
        service.set_enabled(True)
        self.assertTrue(updates.UpdateService(
            install_root=self.root/'TDSMacro',state_dir=self.root/'prefs').enabled)
        service.set_enabled(False)
        self.assertFalse(updates.load_auto_update(service.preference))

    def test_background_check_reports_failure_without_retry_loop(self):
        import time
        def fail(current):
            raise updates.UpdateError('offline')
        service=updates.UpdateService(install_root=self.root/'TDSMacro',
                                      state_dir=self.root/'preferences',check=fail)
        self.assertTrue(service.check_now())
        for _ in range(100):
            if not service.messages.empty():break
            time.sleep(.01)
        self.assertEqual(service.poll(),['check'])
        self.assertIn('offline',service.status)
        self.assertEqual(service.error,'offline')
        self.assertGreater(service.next_check,time.monotonic())

    def test_frozen_candidate_selfcheck_requires_matching_version(self):
        staged=self.root/'TDSMacro';staged.mkdir()
        (staged/'TDSMacro.exe').write_bytes(b'fake executable')
        def successful(cmd,**kwargs):
            self.assertEqual(cmd[1],'--self-check')
            self.assertTrue(Path(cmd[0]).is_absolute())
            self.assertTrue(Path(cmd[2]).is_absolute())
            self.assertTrue(Path(kwargs['cwd']).is_absolute())
            Path(cmd[2]).write_text(json.dumps({
                'version':'0.4.1','frozen':True,'hardcore_phases':14}),encoding='utf-8')
        updates.validate_frozen_candidate(staged,'0.4.1',run=successful)
        def wrong(cmd,**kwargs):
            Path(cmd[2]).write_text(json.dumps({
                'version':'0.4.2','frozen':True,'hardcore_phases':14}),encoding='utf-8')
        with self.assertRaises(updates.UpdateError):
            updates.validate_frozen_candidate(staged,'0.4.1',run=wrong)
        self.assertFalse((staged.parent/'self-check.json').exists())

    def test_published_archive_rejects_duplicate_casefold_names(self):
        archive=self.root/'case.zip'
        archive.write_bytes(package(extra={
            'TDSMacro/DATA.txt':b'a','TDSMacro/data.txt':b'b'}))
        with self.assertRaises(updates.UpdateError):
            updates.extract_archive(archive,self.root/'case-out','0.4.1')

    def test_new_gui_launch_failure_restores_previous_executable(self):
        from types import SimpleNamespace
        raw=package();archive=self.root/'release.zip';archive.write_bytes(raw)
        staged=updates.stage_archive(archive,self.root/'updates','0.4.1',
                                     hashlib.sha256(raw).hexdigest())
        install=self.root/'installed'/'TDSMacro';install.mkdir(parents=True)
        (install/'TDSMacro.exe').write_bytes(b'old')
        (install/'captures').mkdir()
        (install/'captures'/'private.txt').write_text('preserve')
        with patch('tds_auto.updates.sys',SimpleNamespace(frozen=True,
                        executable=str(staged/'TDSMacro.exe'))),patch(
                        'tds_auto.updates.wait_process_exit'),patch(
                        'tds_auto.updates.subprocess.Popen',
                        side_effect=OSError('new GUI cannot start')):
            with self.assertRaises(OSError):
                updates.apply_from_helper(install,123,'0.4.1')
        self.assertEqual((install/'TDSMacro.exe').read_bytes(),b'old')
        self.assertEqual((install/'captures/private.txt').read_text(),'preserve')

    def test_cannot_install_over_same_version_or_from_unverified_stage(self):
        root=self.root/'app'/'TDSMacro';root.mkdir(parents=True)
        (root/'TDSMacro.exe').write_bytes(b'old')
        fake=self.root/'updates'/'v0.4.1'/'TDSMacro';fake.mkdir(parents=True)
        (fake/'TDSMacro.exe').write_bytes(b'fake')
        with self.assertRaises(updates.UpdateError):
            updates.apply_staged(fake,root,expected_version='0.4.1')
        self.assertEqual((root/'TDSMacro.exe').read_bytes(),b'old')


if __name__=='__main__':unittest.main()
