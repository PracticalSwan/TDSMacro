"""Opt-in, verified GitHub release updates; never touches gameplay inputs.

A fresh release is staged outside the install, verified, and only swapped by
the *new* executable after the current GUI and all owned workers have exited.
No update operation stops an active match.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import io
import json
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import zipfile

CURRENT_VERSION = '0.4.0'
RELEASE_API = 'https://api.github.com/repos/PracticalSwan/TDSMacro/releases/latest'
MAX_ZIP_SIZE = 150 * 1024 * 1024
MAX_EXTRACT_SIZE = 800 * 1024 * 1024
MAX_FILES = 2500
CHECK_INTERVAL_SECONDS = 6 * 3600
_VERSION = re.compile(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)\Z')
_SHA = re.compile(r'[a-f0-9]{64}\Z')
_SAFE_HOSTS = frozenset(('api.github.com','github.com',
                         'release-assets.githubusercontent.com',
                         'objects.githubusercontent.com'))
_RESERVED = re.compile(r'(?i)^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?$')


class UpdateError(RuntimeError):
    pass


def parse_version(value: str):
    match = _VERSION.fullmatch(value) if isinstance(value,str) else None
    if not match:
        raise UpdateError('Invalid stable version; expected numeric major.minor.patch.')
    parts = tuple(int(part) for part in match.groups())
    if any(part > 999999 for part in parts):
        raise UpdateError('Version number is out of range.')
    return parts


def is_newer(candidate: str, current: str):
    return parse_version(candidate) > parse_version(current)


def settings_dir():
    local = os.environ.get('LOCALAPPDATA')
    if not local:
        local = str(Path.home()/'AppData'/'Local')
    return Path(local)/'TDSMacro'


def load_auto_update(path: Path) -> bool:
    try:
        value = json.loads(Path(path).read_text(encoding='utf-8'))
        return type(value) is dict and value.get('auto_update') is True
    except (OSError,ValueError,TypeError):
        return False


def save_auto_update(path: Path, enabled: bool):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp-'+str(os.getpid()))
    try:
        temp.write_text(json.dumps({'auto_update':bool(enabled)},indent=2)+'\n',encoding='utf-8')
        os.replace(temp,path)
    finally:
        temp.unlink(missing_ok=True)


@dataclass(frozen=True)
class Release:
    version: str
    archive_url: str
    archive_sha256: str
    archive_name: str
    checksum_url: str
    checksum_sha256: str


def _digest(value):
    if not isinstance(value,str) or not value.startswith('sha256:') or not _SHA.fullmatch(value[7:]):
        raise UpdateError('Published release asset lacks a valid SHA-256 digest.')
    return value[7:]


def _official_url(value: str, expected: str):
    if not isinstance(value,str) or value != expected:
        raise UpdateError('Update asset does not match the official versioned GitHub URL.')
    url=urlparse(value)
    if url.scheme!='https' or url.hostname!='github.com' or url.username or url.password or url.query or url.fragment:
        raise UpdateError('Update asset URL is not trusted.')


def parse_release(data: dict, current=CURRENT_VERSION) -> Release:
    if not isinstance(data,dict) or data.get('draft') is not False or data.get('prerelease') is not False:
        raise UpdateError('Only published stable releases can update the application.')
    tag=data.get('tag_name','')
    if not isinstance(tag,str) or not tag.startswith('v'):
        raise UpdateError('Invalid release tag.')
    version=tag[1:]
    if not is_newer(version,current):
        raise UpdateError('This release is not newer than the installed version.')
    assets=data.get('assets')
    if not isinstance(assets,list) or len(assets)>30:
        raise UpdateError('Unexpected release assets.')
    archive=f'TDSMacro-{version}-windows-x64.zip'
    checksum=f'TDSMacro-v{version}-SHA256SUMS.txt'
    prefix=f'https://github.com/PracticalSwan/TDSMacro/releases/download/v{version}/'
    by_name={a.get('name'):a for a in assets if isinstance(a,dict) and isinstance(a.get('name'),str)}
    if archive not in by_name or checksum not in by_name:
        raise UpdateError('Official Windows ZIP or matching checksum asset is missing.')
    for name in (archive,checksum):
        asset=by_name[name]
        _official_url(asset.get('browser_download_url'),prefix+name)
        if not isinstance(asset.get('size'),int) or not 1<=asset['size']<=(MAX_ZIP_SIZE if name==archive else 4096):
            raise UpdateError('Unexpected release asset size.')
    return Release(version,prefix+archive,_digest(by_name[archive].get('digest')),
                   archive,prefix+checksum,_digest(by_name[checksum].get('digest')))


def parse_checksum(contents: bytes, name: str) -> str:
    try:
        text=contents.decode('ascii')
    except (UnicodeDecodeError,AttributeError):
        raise UpdateError('Checksum file must be ASCII.') from None
    match=re.fullmatch(r'([a-f0-9]{64})  '+re.escape(name)+r'\r?\n?',text)
    if not match:
        raise UpdateError('Checksum file does not contain the exact expected filename and SHA-256.')
    return match[1]


def _read_url(url: str, limit: int, *, opener=urlopen) -> bytes:
    parsed=urlparse(url)
    if parsed.scheme!='https' or parsed.hostname not in _SAFE_HOSTS or parsed.username or parsed.password:
        raise UpdateError('Untrusted update URL.')
    request=Request(url,headers={'User-Agent':f'TDSMacro/{CURRENT_VERSION}',
                                  'Accept':'application/vnd.github+json' if url==RELEASE_API else 'application/octet-stream'})
    with opener(request,timeout=20) as response:
        redirected=urlparse(response.geturl())
        if redirected.scheme!='https' or redirected.hostname not in _SAFE_HOSTS or redirected.username or redirected.password:
            raise UpdateError('Release asset redirected to an untrusted server.')
        chunks=[]
        remaining=limit+1
        while remaining>0:
            block=response.read(min(1024*1024,remaining))
            if not block:break
            chunks.append(block)
            remaining-=len(block)
        if remaining==0:
            raise UpdateError('Release response exceeds the safety size limit.')
        return b''.join(chunks)


def latest_release(current=CURRENT_VERSION, *, fetch=_read_url):
    try:
        payload=json.loads(fetch(RELEASE_API,512*1024))
    except (ValueError,TypeError):
        raise UpdateError('GitHub release metadata is not valid JSON.') from None
    if not isinstance(payload,dict):
        raise UpdateError('Invalid GitHub release metadata.')
    tag=payload.get('tag_name')
    if isinstance(tag,str) and tag.startswith('v') and not is_newer(tag[1:],current):
        return None
    return parse_release(payload,current)


def _safe_name(name: str):
    if (not isinstance(name,str) or not name.startswith('TDSMacro/')
            or chr(92) in name or ':' in name or chr(0) in name or len(name)>240):
        raise UpdateError('ZIP path is outside the application.')
    parts=name.split('/')
    relative=parts[1:-1] if name.endswith('/') else parts[1:]
    if not relative or any(not x or x in ('.','..') or x.endswith((' ','.'))
                           or _RESERVED.fullmatch(x) or any(ord(c)<32 for c in x)
                           for x in relative):
        raise UpdateError('ZIP has an unsafe Windows filename.')
    return relative


def extract_archive(archive: Path, target: Path, version: str):
    parse_version(version)
    target=Path(target)
    if target.exists():
        raise UpdateError('Update extraction target already exists.')
    seen=set()
    entries=[]
    with zipfile.ZipFile(archive) as z:
        members=z.infolist()
        if not 3<=len(members)<=MAX_FILES:
            raise UpdateError('Unexpected number of package entries.')
        total=0
        for item in members:
            parts=_safe_name(item.filename)
            key='/'.join(parts).casefold()
            if key in seen:
                raise UpdateError('ZIP has case-insensitive filename collisions.')
            seen.add(key)
            if (item.external_attr>>16)&0o170000 == 0o120000:
                raise UpdateError('ZIP contains a symlink.')
            total+=item.file_size
            if total>MAX_EXTRACT_SIZE:
                raise UpdateError('ZIP uncompressed size exceeds limit.')
            entries.append((item,parts))
        names={x.filename for x,p in entries if not x.is_dir()}
        if not {'TDSMacro/TDSMacro.exe','TDSMacro/README.txt'}<=names or not any(
                x.startswith('TDSMacro/_internal/') for x in names):
            raise UpdateError('ZIP missing required frozen application files.')
        with z.open('TDSMacro/README.txt') as contents:
            header=contents.read(90).decode('utf-8',errors='replace')
        if header.splitlines()[0:1]!=[f'TDS Macro - Windows v{version}']:
            raise UpdateError('ZIP application version does not match release.')
        try:
            target.mkdir(parents=True)
            for item,parts in entries:
                dest=target.joinpath(*parts)
                if item.is_dir():
                    dest.mkdir(parents=True,exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    with z.open(item) as source,dest.open('xb') as out:
                        shutil.copyfileobj(source,out,1024*1024)
        except BaseException:
            shutil.rmtree(target,ignore_errors=True)
            raise
    return target


def _tree_digest(root: Path):
    hasher=hashlib.sha256()
    files=sorted((p for p in Path(root).rglob('*') if p.is_file()),
                 key=lambda p:p.relative_to(root).as_posix())
    for path in files:
        hasher.update(path.relative_to(root).as_posix().encode('utf-8'))
        hasher.update(bytes((0,)))
        hasher.update(hashlib.sha256(path.read_bytes()).digest())
    return hasher.hexdigest()


def _verified_receipt(staged: Path, version: str):
    staged=Path(staged)
    try:
        receipt=json.loads((staged.parent/'verified.json').read_text(encoding='utf-8'))
        actual=hashlib.sha256((staged/'TDSMacro.exe').read_bytes()).hexdigest()
        header=(staged/'README.txt').read_text(encoding='utf-8')
        if (receipt.get('version')!=version or receipt.get('exe_sha256')!=actual
                or receipt.get('tree_sha256')!=_tree_digest(staged)
                or header.splitlines()[0:1]!=[f'TDS Macro - Windows v{version}']):
            raise UpdateError('Staged files do not match verified update metadata.')
    except (OSError,ValueError,TypeError) as exc:
        raise UpdateError('Staged release is not verified.') from exc
    return receipt


def stage_archive(archive: Path, updates_root: Path, version: str, expected_sha256: str):
    parse_version(version)
    if not _SHA.fullmatch(expected_sha256):
        raise UpdateError('Invalid expected ZIP SHA-256.')
    if hashlib.sha256(Path(archive).read_bytes()).hexdigest()!=expected_sha256:
        raise UpdateError('ZIP differs from the official release digest.')
    updates_root=Path(updates_root)
    updates_root.mkdir(parents=True,exist_ok=True)
    final=updates_root/f'v{version}'
    if final.exists():
        _verified_receipt(final/'TDSMacro',version)
        return final/'TDSMacro'
    temporary=Path(tempfile.mkdtemp(prefix='staging-',dir=updates_root))
    try:
        extract_archive(archive,temporary/'TDSMacro',version)
        exe=(temporary/'TDSMacro'/'TDSMacro.exe').read_bytes()
        (temporary/'verified.json').write_text(json.dumps({
            'version':version,'zip_sha256':expected_sha256,
            'exe_sha256':hashlib.sha256(exe).hexdigest(),
            'tree_sha256':_tree_digest(temporary/'TDSMacro')}),encoding='utf-8')
        os.rename(temporary,final)
        return final/'TDSMacro'
    except BaseException:
        shutil.rmtree(temporary,ignore_errors=True)
        raise


def validate_frozen_candidate(staged: Path, version: str, *, run=subprocess.run):
    # Every published update must pass the same self-check as a normal release
    # before the current installation can be replaced.
    staged=Path(staged).resolve()
    output=(staged.parent/'self-check.json').resolve()
    try:
        run([str(staged/'TDSMacro.exe'),'--self-check',str(output)],
            cwd=staged,timeout=65,check=True,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        data=json.loads(output.read_text(encoding='utf-8'))
        if (data.get('frozen') is not True or data.get('version')!=version
                or type(data.get('hardcore_phases')) is not int
                or data['hardcore_phases']<1):
            raise UpdateError('New frozen application self-check does not match the release.')
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        raise UpdateError('New application failed its pre-install self-check.') from exc
    finally:
        output.unlink(missing_ok=True)


def prepare_release(release: Release, update_dir: Path, *, fetch=_read_url):
    checksum=fetch(release.checksum_url,4096)
    if hashlib.sha256(checksum).hexdigest()!=release.checksum_sha256:
        raise UpdateError('Checksum file differs from official GitHub SHA-256.')
    expected=parse_checksum(checksum,release.archive_name)
    if expected!=release.archive_sha256:
        raise UpdateError('Official asset digest and checksum file disagree.')
    root=Path(update_dir)
    root.mkdir(parents=True,exist_ok=True)
    temp=root/f'download-{os.getpid()}-{threading.get_ident()}.zip'
    if temp.exists():
        raise UpdateError('Another download already occupies the update path.')
    try:
        data=fetch(release.archive_url,MAX_ZIP_SIZE)
        temp.write_bytes(data)
        staged=stage_archive(temp,root,release.version,expected)
        validate_frozen_candidate(staged,release.version)
        return staged
    finally:
        temp.unlink(missing_ok=True)

def apply_staged(staged: Path, install: Path, *, expected_version: str, rename=os.rename):
    """Copy a verified release, atomically swap only while the old app is gone."""
    parse_version(expected_version)
    staged=Path(staged).resolve()
    install=Path(install).resolve()
    receipt=_verified_receipt(staged,expected_version)
    if install.name!='TDSMacro' or not (install/'TDSMacro.exe').is_file():
        raise UpdateError('Target is not an existing TDSMacro installation.')
    if staged==install or staged in install.parents or install in staged.parents:
        raise UpdateError('Staging must be separate from the installed application.')
    info=install/'README.txt'
    if info.exists() and info.read_text(encoding='utf-8').splitlines()[0:1]==[
            f'TDS Macro - Windows v{expected_version}']:
        raise UpdateError('Installation already has the requested version.')
    suffix=f'{time.strftime("%Y%m%d_%H%M%S")}-{os.getpid()}'
    incoming=install.parent/f'.TDSMacro-incoming-{suffix}'
    backup=install.parent/f'TDSMacro-previous-before-v{expected_version}-{suffix}'
    if incoming.exists() or backup.exists():
        raise UpdateError('An installation or backup path already exists.')
    try:
        shutil.copytree(staged,incoming,symlinks=False)
        digest=hashlib.sha256((incoming/'TDSMacro.exe').read_bytes()).hexdigest()
        if digest!=receipt['exe_sha256']:
            raise UpdateError('Copied executable digest changed.')
        rename(install,backup)
        try:
            rename(incoming,install)
        except BaseException:
            rename(backup,install)
            raise
    finally:
        if incoming.exists():
            shutil.rmtree(incoming,ignore_errors=True)
    return backup


def wait_process_exit(pid: int, timeout_seconds=90):
    """Wait for the old GUI using a Windows process handle, never kill it."""
    if type(pid) is not int or pid<=0:
        raise UpdateError('Invalid previous GUI PID.')
    import ctypes
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=(ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32)
    kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes=(ctypes.c_void_p,ctypes.c_uint32)
    kernel.WaitForSingleObject.restype=ctypes.c_uint32
    kernel.CloseHandle.argtypes=(ctypes.c_void_p,)
    handle=kernel.OpenProcess(0x00100000,False,pid)
    if not handle:
        if ctypes.get_last_error()==87:  # previous PID already exited
            return
        raise UpdateError('Unable to verify previous GUI process exit.')
    try:
        if kernel.WaitForSingleObject(handle,int(timeout_seconds*1000))!=0:
            raise UpdateError('Previous GUI did not exit; update deferred.')
    finally:
        kernel.CloseHandle(handle)


def apply_from_helper(install: Path, previous_pid: int, expected_version: str):
    if not getattr(sys,'frozen',False):
        raise UpdateError('Update install is available only from the frozen application.')
    staged=Path(sys.executable).resolve().parent
    _verified_receipt(staged,expected_version)
    install=Path(install).resolve()
    if install==staged:
        raise UpdateError('Cannot replace running updater executable.')
    wait_process_exit(previous_pid)
    backup=apply_staged(staged,install,expected_version=expected_version)
    # Startup is idle; do not automatically resume an interrupted game.
    try:
        subprocess.Popen([str(install/'TDSMacro.exe')],cwd=install,
                         creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    except OSError:
        failed=install.parent/f'.TDSMacro-launch-failed-{os.getpid()}'
        if failed.exists():
            raise UpdateError('New application failed to launch; rollback path occupied.')
        os.rename(install,failed)
        try:
            os.rename(backup,install)
        except OSError:
            # Preserve the newly copied installation as a last resort.
            if not install.exists():
                os.rename(failed,install)
            raise UpdateError('New GUI launch failed and rollback could not complete.')
        raise
    return backup


class UpdateService:
    """A single background network operation; UI code polls completion events."""
    def __init__(self, *, install_root: Path, current=CURRENT_VERSION,
                 state_dir: Path | None=None, check=latest_release,
                 prepare=prepare_release):
        self.install_root=Path(install_root)
        self.current=current
        self.state_dir=Path(state_dir) if state_dir is not None else settings_dir()
        self.preference=self.state_dir/'settings.json'
        self.enabled=load_auto_update(self.preference)
        self.release=None
        self.staged=None
        self.messages=queue.Queue()
        self.error=None
        self.busy=False
        self.next_check=0.0
        self.check_func=check
        self.prepare_func=prepare
        self.status=('Automatic updates ON. Checking at startup.' if self.enabled
                     else 'Automatic updates OFF. Check manually or enable.')
        self._lock=threading.Lock()

    def clear_failed(self):
        marker=self.state_dir/'failed-update.json'
        marker.unlink(missing_ok=True)
        self.error=None

    def _blocked_version(self, version: str):
        try:
            record=json.loads((self.state_dir/'failed-update.json').read_text(encoding='utf-8'))
            return record.get('version')==version
        except (OSError,ValueError,TypeError):
            return False

    def set_enabled(self, value: bool):
        requested=bool(value)
        save_auto_update(self.preference,requested)
        self.enabled=requested
        self.status='Automatic updates ON.' if self.enabled else 'Automatic updates OFF.'
        self.error=None
        if self.enabled:
            self.next_check=0.0

    def _start(self,kind,fn):
        with self._lock:
            if self.busy:
                return False
            self.busy=True
        def run():
            try:
                self.messages.put((kind,fn(),None))
            except Exception as exc:
                self.messages.put((kind,None,str(exc)))
        threading.Thread(target=run,name='TDS-updates-'+kind,daemon=True).start()
        return True

    def check_now(self):
        if not self._start('check',lambda:self.check_func(current=self.current)):
            return False
        self.error=None
        self.next_check=time.monotonic()+CHECK_INTERVAL_SECONDS
        self.status='Checking the official GitHub releases…'
        return True

    def prepare_now(self):
        if self.release is None or self.staged is not None:
            return False
        if not self._start('prepare',lambda:self.prepare_func(self.release,self.state_dir/'updates')):
            return False
        self.error=None
        self.status=f'Verifying and staging v{self.release.version}…'
        return True

    def poll(self):
        events=[]
        while True:
            try:
                kind,value,error=self.messages.get_nowait()
            except queue.Empty:
                break
            self.busy=False
            if error:
                self.error=error
                self.status='Update '+kind+' failed: '+error
            elif kind=='check':
                self.error=None
                self.release=value
                self.staged=None
                if value is not None and self._blocked_version(value.version):
                    self.error='A previous installation attempt failed.'
                    self.status=(f'v{value.version} previously failed to install. '
                                 'Automatic retry blocked; use Check now for a manual retry.')
                else:
                    self.status=(f'v{value.version} available. Waiting for idle update.'
                                 if value else f'Up to date (v{self.current}).')
            elif kind=='prepare':
                self.error=None
                self.staged=value
                self.status=f'v{self.release.version} verified and ready to install.'
            events.append(kind)
        return events

    def launch_installer(self, *, spawn=subprocess.Popen):
        if not self.staged or not self.release or self.busy:
            raise UpdateError('No verified release is staged.')
        if not getattr(sys,'frozen',False):
            raise UpdateError('Automatic installation requires the frozen Windows application.')
        _verified_receipt(self.staged,self.release.version)
        staged=self.staged.resolve()
        args=[str(staged/'TDSMacro.exe'),'--apply-update',
              str(self.install_root.resolve()),str(os.getpid()),self.release.version]
        return spawn(args,cwd=staged,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
