"""Bounded failure recovery into a new, independently verified lobby session."""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path

from .control import GuardedInput,StopRun
from .phase1 import locate_roblox,capture,USER
from .observer import Observer
from .session import Session,SessionControl
from .resources import LocalOCR

ROBLOX_URI='roblox://experiences/start?placeId=3260590327'
NO_RECOVERY={'user_stop','focus_lost','window_changed','setup','storage'}


def locate_client():
    try:return locate_roblox()
    except (RuntimeError,OSError) as exc:
        # A minimized/unverifiable existing window is a user/setup boundary,
        # not evidence that the client crashed and should be reopened.
        if USER.FindWindowW(None,'Roblox'):
            raise StopRun(str(exc),kind='window_changed') from exc
        raise


def optional_window(locate):
    try:return locate()
    except (RuntimeError,OSError) as exc:
        if getattr(exc,'kind',None) in NO_RECOVERY:raise
        return None


def check_cancel(control,platform):
    if control.stopped() or control.paused() or platform.stop_requested():
        raise StopRun('Stop/pause requested; automatic recovery cancelled.',kind='user_stop')


def wait(control,platform,seconds):
    deadline=platform.now()+seconds
    while (remaining:=deadline-platform.now())>0:
        check_cancel(control,platform)
        platform.sleep(min(.05,remaining))
    check_cancel(control,platform)


def close_client(window):
    current=locate_client()
    if not current.foreground:
        raise StopRun('Roblox lost foreground before recovery close.',kind='focus_lost')
    if current!=window:
        raise StopRun('Roblox changed before recovery close.',kind='window_changed')
    user=ctypes.WinDLL('user32',use_last_error=True)
    user.PostMessageW.argtypes=[wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
    user.PostMessageW.restype=wintypes.BOOL
    if not user.PostMessageW(window.hwnd,0x0010,0,0):
        raise ctypes.WinError(ctypes.get_last_error())


def client_exists(window):
    user=ctypes.WinDLL('user32',use_last_error=True)
    user.IsWindow.argtypes=[wintypes.HWND];user.IsWindow.restype=wintypes.BOOL
    return bool(user.IsWindow(window.hwnd))


def client_running(window):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
    kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
    kernel.WaitForSingleObject.restype=wintypes.DWORD
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=kernel.OpenProcess(0x100000,False,window.pid)
    if not handle:
        if ctypes.get_last_error()==87:return False
        raise ctypes.WinError(ctypes.get_last_error())
    try:return kernel.WaitForSingleObject(handle,0)==258
    finally:kernel.CloseHandle(handle)


def launch_client():
    os.startfile(ROBLOX_URI)


def lobby_state(window):
    return Observer().observe(capture(window)).state


def close_prompt(frame):
    if frame.size!=(1920,991):return False
    ocr=LocalOCR()
    for box,expected in (((680,280,1240,345),'newtotherobloxapp'),
                         ((650,694,954,736),'closeroblox'),((968,694,1268,736),'backtohome')):
        text=''.join(c.lower() for c in ocr.read(frame.crop(box)) if c.isalpha())
        if text!=expected:return False
    return True


def confirm_close(window,control,platform):
    if not client_exists(window):return True
    driver=GuardedInput(window,platform)
    driver.external_stop=control.stopped
    driver.check()
    if not close_prompt(capture(window)):return False
    def verify():
        if not close_prompt(capture(window)):
            raise StopRun('Roblox close confirmation changed; no click sent.',kind='setup')
    driver.before_click=verify
    try:driver.click(800,715)
    except (RuntimeError,OSError) as exc:
        # This one click intentionally destroys the guarded window. Stop and
        # focus/geometry signals still cancel; only its absence is expected.
        if getattr(exc,'kind',None) in NO_RECOVERY or client_exists(window):raise
    return True


def restart_client(control,platform,report,*,locate=locate_client,close=close_client,
                   exists=client_running,launch=launch_client,observe=lobby_state,confirm=confirm_close,timeout=180):
    report(stage='cooldown')
    wait(control,platform,5)
    window=optional_window(locate)
    if window is not None:
        if not window.foreground:
            raise StopRun('Roblox lost foreground; recovery cancelled.',kind='focus_lost')
        report(stage='closing',client_pid=window.pid,client_hwnd=window.hwnd)
        check_cancel(control,platform)
        close(window)
        deadline=platform.now()+30
        confirmed=False
        while exists(window):
            if platform.now()>=deadline:
                raise StopRun('Roblox did not close; no force termination was attempted.',kind='setup')
            if not confirmed:
                confirmed=confirm(window,control,platform)
            wait(control,platform,.05)
        # The Store activation broker can outlive the game process briefly.
        wait(control,platform,3)
    check_cancel(control,platform)
    report(stage='launching')
    launch()
    report(stage='waiting_lobby')
    deadline=platform.now()+timeout
    previous=None;stable=0
    while platform.now()<deadline:
        check_cancel(control,platform)
        try:
            window=locate()
            state=observe(window) if window.foreground and (window.width,window.height,window.dpi)==(1920,991,120) else None
        except (RuntimeError,OSError):state=None
        if state in {'lobby','login_rewards'}:
            stable=stable+1 if state==previous else 1
            if stable>=2:
                report(stage='lobby_ready',client_pid=window.pid,client_hwnd=window.hwnd,lobby_state=state)
                return
        else:stable=0
        previous=state
        wait(control,platform,.2)
    raise StopRun('Recovery did not reach a foreground supported lobby or Login Rewards screen.',kind='setup')


def supervise(output,platform,profile,*,attempt=None,restart=restart_client,locate=locate_client,max_recoveries=3):
    output=Path(output)
    context={'recoveries':0,'max_recoveries':max_recoveries}
    control=SessionControl(output,context=context)
    totals={'attempts':0,'matches_completed':0,'wins':0,'coins_total':0}
    consecutive=0;number=0
    def run_attempt(path,control,totals):
        driver=GuardedInput(locate(),platform);driver.check()
        if (driver.expected.width,driver.expected.height,driver.expected.dpi)!=(1920,991,120):
            raise StopRun('This profile requires a 1920x991 client at 120 DPI.',kind='setup')
        session=Session(driver,path,profile,control=control,totals=totals)
        return session.run(continuous=True)
    attempt=attempt or run_attempt
    def finish(result):
        result={**result,**totals,'recoveries':context['recoveries']}
        (output/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        control.write({'phase':result['status'],'runner_pid':os.getpid(),**result})
        return result
    while True:
        try:check_cancel(control,platform)
        except StopRun as exc:return finish({'status':'stopped','reason':str(exc),'stop_kind':exc.kind})
        number+=1
        path=output/f'attempt_{number:03}';path.mkdir()
        context['attempt_folder']=path.name
        wins_before=totals['wins']
        try:result=attempt(path,control,totals)
        except (RuntimeError,ValueError,OSError,KeyError,TypeError) as exc:
            kind=getattr(exc,'kind','setup' if isinstance(exc,(ValueError,KeyError,TypeError)) else 'failure')
            result={'status':'stopped','reason':str(exc),'stop_kind':kind}
        (path/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        with (output/'sessions.jsonl').open('a',encoding='utf-8') as ledger:
            ledger.write(json.dumps({'attempt_folder':path.name,'result':result,'totals':dict(totals)})+'\n')
        if result['status'] in {'victory','prepared'}:return finish(result)
        last=result.get('matches',[{}])[-1] if result.get('matches') else {}
        kind=result.get('stop_kind') or last.get('stop_kind','failure')
        if kind in NO_RECOVERY:return finish({**result,'stop_kind':kind})
        try:
            check_cancel(control,platform)
            current=optional_window(locate)
            if current is not None and not current.foreground:
                raise StopRun('Roblox lost foreground; recovery cancelled.',kind='focus_lost')
            if totals['wins']>wins_before:consecutive=0
            if consecutive>=max_recoveries:
                return finish({**result,'status':'stopped','reason':f'Automatic recovery limit reached after {max_recoveries} relaunches without a win.'})
            consecutive+=1;context['recoveries']+=1
            context['recovery_attempt']=consecutive
            def report(**detail):
                event={'phase':'recovering','runner_pid':os.getpid(),'elapsed_seconds':platform.now(),**totals,
                       'reason':result.get('reason') or last.get('reason'),'recovery_attempt':consecutive,**detail}
                control.write(event)
                with (output/'recovery.jsonl').open('a',encoding='utf-8') as ledger:
                    ledger.write(json.dumps(event)+'\n')
            restart(control,platform,report)
        except (RuntimeError,OSError) as exc:
            return finish({'status':'stopped','reason':str(exc),'stop_kind':getattr(exc,'kind','setup')})
