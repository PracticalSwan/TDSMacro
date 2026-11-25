"""Bounded failure recovery into a new, independently verified lobby session."""
from __future__ import annotations
import ctypes
from ctypes import wintypes
from dataclasses import replace
import json
import os
from pathlib import Path
from datetime import datetime,timezone

from .control import GuardedInput,StopRun
from .phase1 import locate_roblox,capture,USER
from .observer import Observer
from .session import Session,SessionControl
from .resources import LocalOCR
from .recording import append_jsonl,write_json

ROBLOX_URI='roblox://experiences/start?placeId=3260590327'
LAUNCHER_SETTLE_SECONDS=60
FOCUS_RETURN_SECONDS=5
DISCONNECT_HOME_SECONDS=5
NO_RECOVERY={'user_stop','focus_lost','focus_interrupted','window_changed','setup','storage','strategy'}


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


def await_foreground(control,platform,expected,*,locate=locate_client,report=lambda **detail:None):
    """Observe natural focus return only; the interrupted strategy never resumes."""
    if expected is None or not expected.foreground or (expected.width,expected.height,expected.dpi)!=(1920,991,120):
        raise StopRun('No verified foreground client before interruption; recovery cancelled.',kind='focus_interrupted')
    report(stage='awaiting_foreground',seconds=FOCUS_RETURN_SECONDS,client_pid=expected.pid,client_hwnd=expected.hwnd)
    deadline=platform.now()+FOCUS_RETURN_SECONDS
    stable=0
    while platform.now()<deadline:
        check_cancel(control,platform)
        try:current=locate()
        except StopRun:raise
        except (RuntimeError,OSError) as exc:
            raise StopRun('Interrupted Roblox client could not be verified; no relaunch.',kind='focus_interrupted') from exc
        if replace(current,foreground=True)!=expected:
            raise StopRun('Roblox identity, position, size or DPI changed during focus interruption; no relaunch.',kind='window_changed')
        stable=stable+1 if current.foreground else 0
        if stable>=2:
            report(stage='foreground_restored',client_pid=current.pid,client_hwnd=current.hwnd)
            return
        wait(control,platform,min(.2,max(0,deadline-platform.now())))
    raise StopRun('Roblox did not regain foreground naturally within five seconds; no relaunch.',kind='focus_interrupted')


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


def request_system_close(window):
    """One ordinary Windows Close command for a verified stalled loading screen.

    Unlike process termination, this permits Roblox to handle its normal close
    flow. Never use this for an unknown or background client.
    """
    current=locate_client()
    if not current.foreground:
        raise StopRun('Roblox lost foreground before system Close.',kind='focus_lost')
    if current!=window:
        raise StopRun('Roblox changed before system Close.',kind='window_changed')
    user=ctypes.WinDLL('user32',use_last_error=True)
    user.PostMessageW.argtypes=[wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
    user.PostMessageW.restype=wintypes.BOOL
    # WM_SYSCOMMAND / SC_CLOSE: standard system-menu Close, not a force kill.
    if not user.PostMessageW(window.hwnd,0x0112,0xF060,0):
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


def client_window_hidden(window):
    """The old verified HWND may disappear while its process winds down."""
    user=ctypes.WinDLL('user32',use_last_error=True)
    user.IsWindowVisible.argtypes=[wintypes.HWND]
    user.IsWindowVisible.restype=wintypes.BOOL
    user.IsIconic.argtypes=[wintypes.HWND]
    user.IsIconic.restype=wintypes.BOOL
    return not user.IsWindowVisible(window.hwnd) or bool(user.IsIconic(window.hwnd))


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


def disconnect_prompt(frame):
    """Recognize only the calibrated disconnect dialog and both exact actions."""
    if frame.size!=(1920,991) or Observer().observe(frame).state!='disconnect':return False
    ocr=LocalOCR()
    return (ocr.read(frame.crop((710,344,1215,398))).strip()=='Disconnected'
            and ocr.read(frame.crop((735,582,954,628))).strip()=='Leave'
            and ocr.read(frame.crop((967,582,1185,628))).strip()=='Reconnect')


def roblox_home(frame):
    """Recognize a known Roblox Home navigation layout after disconnect Leave."""
    if frame.size!=(1920,991):return False
    ocr=LocalOCR()
    layouts=(
        (((10,16,95,84),'home'),((735,8,1270,62),'search'),
         ((160,82,258,132),'for you'),((258,82,345,132),'charts')),
        (((10,16,95,84),'home'),((0,90,88,158),'moments'),
         ((0,170,88,240),'build'),((0,248,88,320),'chat')),
    )
    for anchors in layouts:
        if all(' '.join(ocr.read(frame.crop(box)).casefold().split())==expected
               for box,expected in anchors):
            return True
    return False


def confirm_close(window,control,platform,allow_disconnect=True):
    if not client_exists(window):return False
    driver=GuardedInput(window,platform)
    driver.external_stop=lambda:control.stopped() or control.paused()
    driver.check()
    frame=capture(window)
    if close_prompt(frame):
        kind='close';point=(680,715);confirm=lambda image:close_prompt(image)
        changed='Roblox close confirmation changed; no click sent.'
    elif allow_disconnect and disconnect_prompt(frame):
        kind='disconnect';point=(845,605);confirm=lambda image:disconnect_prompt(image)
        changed='Roblox disconnect dialog changed; no Leave click sent.'
    else:return False
    def verify():
        if not confirm(capture(window)):
            raise StopRun(changed,kind='setup')
    driver.before_click=verify
    try:driver.click(*point)
    except (RuntimeError,OSError) as exc:
        # This one click intentionally destroys the guarded window. Stop and
        # focus/geometry signals still cancel; only its absence is expected.
        if getattr(exc,'kind',None) in NO_RECOVERY or client_exists(window):raise
    return kind


def await_disconnect_transition(window,control,platform,*,locate,exists,deadline):
    """Wait for two exact Home reads or an exact close dialog; never click here."""
    home_deadline=min(deadline,platform.now()+DISCONNECT_HOME_SECONDS)
    stable_home=0
    while exists(window):
        check_cancel(control,platform)
        if platform.now()>=home_deadline:
            raise StopRun('Roblox did not reach a verified Home or close-confirmation screen after Leave; no relaunch.',kind='setup')
        current=optional_window(locate)
        if current is not None:
            if not current.foreground:
                raise StopRun('Roblox lost foreground after disconnect Leave; no further input or relaunch.',kind='focus_lost')
            if current!=window:
                raise StopRun('Roblox changed after disconnect Leave; no further close or relaunch.',kind='window_changed')
            try:frame=capture(window)
            except StopRun:raise
            except (RuntimeError,OSError) as exc:
                raise StopRun('Could not verify Roblox after disconnect Leave; no further close or relaunch.',kind='setup') from exc
            if roblox_home(frame):
                stable_home+=1
                if stable_home>=2:return 'home'
            else:
                stable_home=0
                if close_prompt(frame):return 'close_prompt'
        wait(control,platform,.15)
    return 'exited'


def restart_client(control,platform,report,*,locate=locate_client,close=close_client,
                   exists=client_running,launch=launch_client,observe=lobby_state,confirm=confirm_close,timeout=180,expected=None):
    report(stage='cooldown')
    wait(control,platform,5)
    window=optional_window(locate)
    if expected is not None and window is not None and window!=expected:
        raise StopRun('Roblox changed during recovery cooldown; no close or relaunch.',kind='window_changed')
    if window is not None:
        if not window.foreground:
            raise StopRun('Roblox lost foreground; recovery cancelled.',kind='focus_lost')
        report(stage='closing',client_pid=window.pid,client_hwnd=window.hwnd)
        check_cancel(control,platform)
        close(window)
        close_started=platform.now()
        deadline=close_started+30
        confirmed_close=False;disconnect_consumed=False
        loading_close_checked=False
        home_close_requested=False
        while exists(window):
            check_cancel(control,platform)
            if platform.now()>=deadline:
                raise StopRun('Roblox did not close; no force termination was attempted.',kind='setup')
            # The ordinary WM_CLOSE can be ignored during a hung TDS teleport.
            # One distinct standard Close is permitted only after two fresh
            # loading reads from the same original foreground Roblox client.
            if (not loading_close_checked and not confirmed_close and not disconnect_consumed
                    and platform.now()-close_started>=5):
                loading_close_checked=True
                current=optional_window(locate)
                if current is None or current!=window:
                    raise StopRun('Roblox changed during stalled-loading close.',kind='window_changed')
                if not current.foreground:
                    raise StopRun('Roblox lost foreground during stalled-loading close.',kind='focus_lost')
                if observe(window)=='loading':
                    wait(control,platform,.2)
                    current=optional_window(locate)
                    if current is None or current!=window:
                        raise StopRun('Roblox changed during stalled-loading confirmation.',kind='window_changed')
                    if not current.foreground:
                        raise StopRun('Roblox lost foreground during stalled-loading confirmation.',kind='focus_lost')
                    if exists(window) and observe(window)=='loading':
                        check_cancel(control,platform)
                        request_system_close(window)
                        report(stage='closing',client_pid=window.pid,client_hwnd=window.hwnd,
                               close_reason='stalled_loading_system_close')
            if not confirmed_close:
                # After two confirmed Home frames and an ordinary Close,
                # Windows may hide the old HWND before the process exits.
                # Only wait for that original PID; never click a hidden view.
                if home_close_requested and client_window_hidden(window):
                    wait(control,platform,.05)
                    continue
                dialog=confirm(window,control,platform,not disconnect_consumed)
                if dialog=='close':
                    confirmed_close=True
                elif dialog=='disconnect' and not disconnect_consumed:
                    disconnect_consumed=True
                    transition=await_disconnect_transition(window,control,platform,
                        locate=locate,exists=exists,deadline=deadline)
                    if transition=='home' and exists(window):
                        check_cancel(control,platform)
                        try:close(window)
                        except (RuntimeError,OSError) as exc:
                            if getattr(exc,'kind',None) in NO_RECOVERY or exists(window):raise
                        else:
                            home_close_requested=True
                            report(stage='closing',client_pid=window.pid,client_hwnd=window.hwnd,
                                   close_reason='disconnect_leave_home')
            wait(control,platform,.05)
    # The Store broker can still own the old activation after process exit,
    # including a crash before recovery started. Three seconds reproduced
    # 0x800705b4; sixty passed a live normal-close/single-launch cycle.
    report(stage='settling_launcher',seconds=LAUNCHER_SETTLE_SECONDS)
    wait(control,platform,LAUNCHER_SETTLE_SECONDS)
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
        observed=(state,window) if state in {'lobby','login_rewards'} else None
        if observed is not None:
            stable=stable+1 if observed==previous else 1
            if stable>=2:
                report(stage='lobby_ready',client_pid=window.pid,client_hwnd=window.hwnd,lobby_state=state)
                return
        else:stable=0
        previous=observed
        wait(control,platform,.2)
    raise StopRun('Recovery did not reach a foreground supported lobby or Login Rewards screen.',kind='setup')


def supervise(output,platform,profile,*,attempt=None,restart=None,locate=locate_client,max_recoveries=3,
              idle_lobby_seconds=0,initial_expected=None,strategy_id='golden_scout',auto_equip=False):
    from .hardcore_plan_v2 import is_hardcore_v2

    hardcore=is_hardcore_v2(strategy_id)
    if type(idle_lobby_seconds) is not int or (idle_lobby_seconds and not 1200<=idle_lobby_seconds<=1800):
        raise StopRun('AFK lobby monitoring is bounded to 1200..1800 seconds.',kind='setup')
    output=Path(output)
    started=platform.now()
    context={'recoveries':0,'max_recoveries':max_recoveries}
    control=SessionControl(output,context=context)
    totals={'attempts':0,'matches_completed':0,'wins':0,'coins_total':0}
    if hardcore:
        context['strategy_id']=strategy_id
        totals.update(gem_cycles=0,gems_total=0)
    success_key='gem_cycles' if hardcore else 'wins'
    consecutive=0;number=0;first_expected=initial_expected
    def run_attempt(path,control,totals):
        driver=GuardedInput(expected or locate(),platform);driver.check()
        if (driver.expected.width,driver.expected.height,driver.expected.dpi)!=(1920,991,120):
            raise StopRun('This profile requires a 1920x991 client at 120 DPI.',kind='setup')
        session=Session(driver,path,profile,control=control,totals=totals,
                        strategy_id=strategy_id,auto_equip=auto_equip)
        idle_pending=(idle_lobby_seconds and not context.get('idle_lobby_monitor_completed')
                      and not context.get('idle_lobby_disconnect_confirmed'))
        return session.run(continuous=True,idle_lobby_seconds=idle_lobby_seconds if idle_pending else 0)
    attempt=attempt or run_attempt
    def finish(result):
        result={**result,**totals,'recoveries':context['recoveries']}
        write_json(output/'result.json',result)
        control.write({'phase':result['status'],'runner_pid':os.getpid(),**result})
        return result
    while True:
        try:check_cancel(control,platform)
        except StopRun as exc:return finish({'status':'stopped','reason':str(exc),'stop_kind':exc.kind})
        number+=1
        path=output/f'attempt_{number:03}'
        try:path.mkdir()
        except OSError as exc:
            return finish({'status':'stopped','reason':f'Cannot create attempt evidence folder ({type(exc).__name__}).','stop_kind':'storage'})
        context['attempt_folder']=path.name
        successes_before=totals[success_key]
        expected=first_expected
        first_expected=None
        try:
            if expected is None:
                expected=optional_window(locate)
            result=attempt(path,control,totals)
        except (RuntimeError,ValueError,OSError,KeyError,TypeError) as exc:
            fallback='storage' if isinstance(exc,OSError) else 'setup' if isinstance(exc,(ValueError,KeyError,TypeError)) else 'failure'
            kind=getattr(exc,'kind',fallback)
            result={'status':'stopped','reason':str(exc),'stop_kind':kind}
        try:
            write_json(path/'result.json',result)
            append_jsonl(output/'sessions.jsonl',{'attempt_folder':path.name,'result':result,'totals':dict(totals)})
        except StopRun as exc:
            return finish({'status':'stopped','reason':str(exc),'stop_kind':exc.kind})
        last=result.get('matches',[{}])[-1] if result.get('matches') else {}
        kind=result.get('stop_kind') or last.get('stop_kind','failure')
        if result['status']!='stopped' and kind!='uncredited_cycle':
            return finish(result)
        focus_return=kind=='focus_lost' and expected is not None and expected.foreground and (expected.width,expected.height,expected.dpi)==(1920,991,120)
        if kind in NO_RECOVERY and not focus_return:return finish({**result,'stop_kind':kind})
        def report(**detail):
            event={'phase':'recovering','event_time_utc':datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z'),
                   'runner_pid':os.getpid(),'elapsed_seconds':round(platform.now()-started,1),**totals,
                   'recoveries':context['recoveries'],'max_recoveries':max_recoveries,
                   'reason':result.get('reason') or last.get('reason'),'stop_kind':kind,
                   'recovery_attempt':consecutive,**detail}
            control.write(event)
            append_jsonl(output/'recovery.jsonl',event)
        try:
            check_cancel(control,platform)
            if totals[success_key]>successes_before:consecutive=0
            if consecutive>=max_recoveries:
                outcome='a credited gem cycle' if hardcore else 'a credited Golden victory'
                return finish({**result,'status':'stopped','reason':f'Automatic recovery limit reached after {max_recoveries} relaunches without {outcome}.'})
            if focus_return:
                kind='focus_interrupted'
                await_foreground(control,platform,expected,locate=locate,report=report)
            current=optional_window(locate)
            if current is not None and not current.foreground:
                raise StopRun('Roblox lost foreground; recovery cancelled.',kind='focus_lost')
            if current is not None and current!=expected:
                raise StopRun('Roblox changed after the failed attempt; recovery cancelled.',kind='window_changed')
            consecutive+=1;context['recoveries']+=1
            context['recovery_attempt']=consecutive
            if restart is None:restart_client(control,platform,report,locate=locate,expected=expected)
            else:restart(control,platform,report)
        except (RuntimeError,OSError) as exc:
            return finish({'status':'stopped','reason':str(exc),'stop_kind':getattr(exc,'kind','setup')})
