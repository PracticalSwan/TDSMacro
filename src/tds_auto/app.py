"""Small Windows strategy selector; game input remains in the guarded worker."""
from __future__ import annotations

import argparse
import ctypes
from dataclasses import asdict
import json
import queue
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from ctypes import wintypes
from .hardcore_plan_v2 import PLAN_ID as PLAN_V2_ID
from .calibration import GOLDEN_V031_ACCEPTED_SHA

ROOT = Path(__file__).resolve().parents[2]
STRATEGIES = {
    'Golden Scout — 10 Max / Dead Ahead / Easy': 'dead_ahead_vertical_ten_v031_v2202_trial.json',
    'Golden Scout — 9 Scouts (legacy fallback)': 'dead_ahead_vertical_nine_v4.json',
    'Hardcore Gem Grind — Wretched Front / Solo': PLAN_V2_ID,
}



def preflight_roblox_start(cancelled=None, allow_recovery=False):
    """Verify the client, or let the guarded recovery worker launch it."""
    from .phase1 import RobloxWindowUnavailable, capture, focus_roblox

    try:
        window = focus_roblox(cancelled=cancelled)
    except RobloxWindowUnavailable:
        if not allow_recovery:
            raise
        if cancelled is not None and cancelled():
            raise RuntimeError('Roblox start preflight cancelled.')
        return None
    capture(window)
    if cancelled is not None and cancelled():
        raise RuntimeError('Roblox start preflight cancelled.')
    return window


class Hotkeys:
    """Own F1/F2 on a separate message queue, independent of Tk's event pump."""
    ids = {0x5441: 'start', 0x5442: 'stop'}

    def __init__(self):
        self.events = queue.Queue()
        self._generation_lock = threading.Lock()
        self._stop_generation = 0
        self.ready = threading.Event()
        self.error = None
        self.thread_id = None
        self.thread = threading.Thread(target=self.listen, daemon=True)
        self.thread.start()
        if not self.ready.wait(3) or self.error:
            self.close()
            raise RuntimeError(self.error or 'F1/F2 registration timed out.')

    def listen(self):
        user = ctypes.WinDLL('user32', use_last_error=True)
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        user.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
        user.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
        user.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
        user.GetMessageW.restype = ctypes.c_int
        self.thread_id = kernel.GetCurrentThreadId()
        registered = []
        try:
            for ident, key in ((0x5441, 0x70), (0x5442, 0x71)):
                if not user.RegisterHotKey(None, ident, 0x4000, key):
                    raise RuntimeError('F1/F2 are already in use. Close the other macro app first.')
                registered.append(ident)
            self.ready.set()
            message = wintypes.MSG()
            while user.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
                if message.message == 0x0312 and message.wParam in self.ids:
                    self._queue_event(self.ids[message.wParam])
        except Exception as exc:
            self.error = str(exc)
        finally:
            for ident in registered:
                user.UnregisterHotKey(None, ident)
            self.ready.set()

    def _queue_event(self, event):
        """Bind F1 to the stop generation at keypress time, before Tk drains it."""
        with self._generation_lock:
            if event == 'stop':
                self._stop_generation += 1
            generation = self._stop_generation
        self.events.put((event, generation))
        return generation

    def current_generation(self):
        with self._generation_lock:
            return self._stop_generation

    def cancelled_since(self, generation):
        with self._generation_lock:
            return self._stop_generation != generation

    def cancel_start_requests(self):
        with self._generation_lock:
            self._stop_generation += 1

    def close(self):
        if self.thread_id and self.thread.is_alive():
            user = ctypes.WinDLL('user32', use_last_error=True)
            user.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
            user.PostThreadMessageW(self.thread_id, 0x0012, 0, 0)
            self.thread.join(1)


class Controller:
    def __init__(self, root=ROOT, launch=subprocess.Popen, preflight=None):
        self.root, self.launch = Path(root), launch
        self.preflight = preflight or preflight_roblox_start
        self.worker = None
        self.output = None
        self.stop_requested = False
        self.startup_message = 'Starting in 5 seconds — Roblox client verified.'

    @property
    def running(self):
        return self.worker is not None and self.worker.poll() is None

    def start(self, strategy, auto_recover=True, cancelled=None, auto_equip=False):
        if self.running:
            return False
        if strategy not in STRATEGIES:
            raise ValueError('Choose an available strategy.')
        if auto_equip:
            raise RuntimeError('Auto Equip is unavailable: TDS does not expose five verified EMPTY slot labels. Equip manually.')
        selection = STRATEGIES[strategy]
        hardcore = selection == PLAN_V2_ID
        if cancelled is not None and cancelled():
            raise RuntimeError('Roblox start preflight cancelled.')
        preflight_window = self.preflight(cancelled=cancelled, allow_recovery=auto_recover)
        if cancelled is not None and cancelled():
            raise RuntimeError('Roblox start preflight cancelled.')
        if preflight_window is None:
            if not auto_recover:
                raise RuntimeError('Roblox is not visible; enable guarded recovery to launch the official client.')
            self.startup_message = 'Starting recovery in 5 seconds — official Roblox launch is armed.'
        else:
            self.startup_message = 'Starting in 5 seconds — Roblox identity verified.'
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        self.output = self.root/'captures'/'runs'/f'app_{stamp}'
        self.output.parent.mkdir(parents=True, exist_ok=True)
        entry = [sys.executable] if getattr(sys, 'frozen', False) else [sys.executable, str(self.root/'tds_launcher.py')]
        command = [*entry, '--engine', 'start', '--confirm-start', '--continuous',
                   '--startup-delay', '5', '--output', str(self.output)]
        if hardcore:
            command.extend(['--strategy', PLAN_V2_ID])
        else:
            command.extend(['--profile', str(self.root/'calibrations'/selection)])
        if preflight_window is not None:
            command.extend(['--expected-window', json.dumps(asdict(preflight_window), separators=(',', ':'))])
        if auto_recover:
            command.append('--auto-recover')
        if auto_equip:
            command.append('--auto-equip')
        # A windowed application has no inherited console streams.
        with (self.output.parent/f'{self.output.name}.log').open('wb') as log:
            if cancelled is not None and cancelled():
                raise RuntimeError('Roblox start preflight cancelled.')
            self.worker = self.launch(command, cwd=self.root, stdout=log, stderr=log,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
        self.stop_requested = False
        if cancelled is not None and cancelled():
            self.stop()
        return True

    def stop(self):
        if not self.running or self.output is None:
            return False
        self.output.mkdir(parents=True, exist_ok=True)
        (self.output/'stop').write_text('F2 / Stop requested', encoding='utf-8')
        self.stop_requested = True
        return True

    def status(self):
        if self.output is None:
            return {}
        try:
            return json.loads((self.output/'status.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {}


def status_text(data, running, stopping=False, start_error=None):
    if stopping and running:
        return 'Stopping… releasing controls safely.'
    if not running and start_error:
        return 'Start stopped: '+start_error
    if not running:
        if stopping:
            return 'Stopped. Return to the TDS lobby before starting again.'
        result = data.get('result', {})
        matches = result.get('matches', data.get('matches', []))
        reason = data.get('reason') or result.get('reason') or (matches[-1].get('reason') if matches else None)
        if reason:
            return 'Stopped: '+reason
        if data.get('phase') == 'defeat':
            return 'Defeat — stopped. Return to the TDS lobby before starting again.'
        if data.get('phase') in {'early_result', 'late_result', 'unverified_reward'}:
            return 'Hardcore stopped — the result did not qualify as a credited cycle.'
        return 'Ready — open the TDS lobby, then press F1.'
    phase = data.get('phase', 'starting')
    if phase=='recovering':
        if data.get('stage')=='awaiting_foreground':
            return 'Input stopped · waiting up to 5 seconds for Roblox to return naturally · F2 cancels.'
        stages={'cooldown':'restarting shortly','closing':'leaving the failed game',
                'settling_launcher':'waiting 60 seconds for the Roblox launcher',
                'launching':'opening Roblox','waiting_lobby':'waiting for the lobby'}
        return f"Recovery {data.get('recovery_attempt',1)}/{data.get('max_recoveries',3)} · {stages.get(data.get('stage'),'restarting TDS')} · F2 cancels."
    progress = data.get('progress', {})
    if phase == 'playing' and 'confirmed_step' in progress:
        return f"Match {data.get('match', 1)} · {progress.get('count', 0)} Scouts · {progress['confirmed_step']}/{progress.get('total_actions', 44)} actions"
    if phase == 'hardcore_purchase_phase':
        return f"Hardcore phase {data.get('step', 1)}/14"
    if phase == 'hardcore_action':
        return f"Wave {data.get('wave', 0)} · {data.get('tower_id', '')} level {data.get('level', 0)} · {data.get('tower_count', 0)} towers"
    names = {'starting': 'Starting in 5 seconds — startup checks active.',
             'playing': 'Playing the Golden Scout strategy…', 'play_again': 'Play Again — waiting for the next match…',
             'vip_map_selection': 'Choosing Dead Ahead with VIP…', 'vote_badge_view_adjustment': 'Clearing the vote view…',
             'camera_check': 'Setting the overhead view…', 'prepared': 'Map and overhead view confirmed.',
             'lobby_popup_check': 'Checking the lobby…', 'loadout_identity': 'Checking Golden Scout…'}
    return names.get(phase, phase.replace('_', ' ').capitalize()+'…')


class App:
    """Compact, keyboard-friendly control panel; Roblox input remains in Controller."""

    BG = '#0c1322'
    PANEL = '#162238'
    FIELD = '#202f48'
    BORDER = '#344561'
    TEXT = '#eff5ff'
    MUTED = '#a5b4ce'
    MINT = '#75e4b9'
    ROSE = '#ff99a4'

    def __init__(self):
        import tkinter as tk
        from tkinter import ttk

        self.hotkeys = Hotkeys()
        self.controller = Controller()
        self.root = tk.Tk()
        self.root.title('TDS Macro')
        self.root.geometry('790x680')
        self.root.resizable(True, True)
        self.root.minsize(760,610)
        self.root.configure(bg=self.BG)
        self.closing = False
        self.start_error = None

        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('Modern.TCombobox', font=('Segoe UI', 11), padding=11,
                        foreground=self.TEXT, fieldbackground=self.FIELD,
                        background=self.FIELD, arrowcolor=self.MINT, bordercolor=self.BORDER,
                        lightcolor=self.FIELD, darkcolor=self.FIELD)
        style.map('Modern.TCombobox', fieldbackground=[('readonly', self.FIELD)],
                  foreground=[('readonly', self.TEXT)])
        style.configure('Dark.TNotebook', background=self.BG, borderwidth=0)
        style.configure('Dark.TNotebook.Tab', background=self.FIELD, foreground=self.TEXT,
                        padding=(22,10), font=('Segoe UI Semibold',11))
        style.map('Dark.TNotebook.Tab', background=[('selected',self.PANEL)],
                  foreground=[('selected',self.MINT)])
        self.tabs=ttk.Notebook(self.root,style='Dark.TNotebook')
        self.overview=tk.Frame(self.tabs,bg=self.BG)
        self.diagnostics=tk.Frame(self.tabs,bg=self.BG)
        self.tabs.add(self.overview,text='Overview')
        self.tabs.add(self.diagnostics,text='Diagnostics')
        self.tabs.pack(fill='both',expand=True,padx=13,pady=(12,10))

        header = tk.Frame(self.overview, bg=self.BG)
        header.pack(fill='x', padx=30, pady=(24, 0))
        tk.Label(header, text='TDS  /  MACRO', bg=self.BG, fg=self.MINT,
                 font=('Segoe UI Semibold', 11)).pack(side='left', anchor='w')
        self.state_label = tk.Label(header, text='●  READY', bg=self.FIELD, fg=self.MUTED,
                                    font=('Segoe UI Semibold', 10), padx=12, pady=6)
        self.state_label.pack(side='right')
        tk.Label(self.overview, text='Tower defense, on autopilot.', bg=self.BG,
                 fg=self.TEXT, font=('Segoe UI Semibold', 22)).pack(anchor='w', padx=30, pady=(12, 2))
        tk.Label(self.overview, text='Golden Scout and Hardcore verified on TDS v2.20.3.',
                 bg=self.BG, fg=self.MUTED, font=('Segoe UI', 10)).pack(anchor='w', padx=31)

        settings = tk.Frame(self.overview, bg=self.PANEL, highlightbackground=self.BORDER,
                            highlightthickness=1, padx=19, pady=14)
        settings.pack(fill='x', padx=30, pady=(20, 0))
        tk.Label(settings, text='STRATEGY', bg=self.PANEL, fg=self.MUTED,
                 font=('Segoe UI Semibold', 10)).pack(anchor='w')
        self.strategy = tk.StringVar(value=next(iter(STRATEGIES)))
        self.selector = ttk.Combobox(settings, textvariable=self.strategy,
                                    values=list(STRATEGIES), state='readonly',
                                    style='Modern.TCombobox', takefocus=True)
        self.selector.pack(fill='x', pady=(8, 9))
        self.auto_recover = tk.BooleanVar(value=True)
        self.recover_toggle = tk.Checkbutton(
            settings, text='Recover from game failures (up to 3 restarts)',
            variable=self.auto_recover, bg=self.PANEL, fg=self.MUTED,
            selectcolor=self.FIELD, activebackground=self.PANEL,
            activeforeground=self.TEXT, highlightthickness=0,
            cursor='hand2', font=('Segoe UI', 10), takefocus=True)
        self.recover_toggle.pack(anchor='w', pady=(1, 0))
        self.auto_equip=tk.BooleanVar(value=False)
        self.equip_toggle=tk.Checkbutton(
            settings,text='Auto Equip (unavailable on current TDS UI)',
            variable=self.auto_equip,bg=self.PANEL,fg=self.MUTED,
            selectcolor=self.FIELD,activebackground=self.PANEL,
            activeforeground=self.TEXT,highlightthickness=0,
            cursor='arrow',font=('Segoe UI',10),state='disabled',takefocus=False)
        self.equip_toggle.pack(anchor='w',pady=(3,0))
        tk.Label(settings,text='Equip manually. Empty slots lack the required EMPTY text.',
                 bg=self.PANEL,fg=self.ROSE,font=('Segoe UI',9)).pack(anchor='w')

        actions = tk.Frame(self.overview, bg=self.BG)
        actions.pack(fill='x', padx=30, pady=(16, 0))
        self.start_button = tk.Button(
            actions, text='Start   F1', command=self.start, cursor='hand2',
            bg=self.MINT, fg='#10291e', activebackground='#9af2ce',
            activeforeground='#10291e', font=('Segoe UI Semibold', 12),
            relief='flat', bd=0, pady=11, takefocus=True,
            highlightthickness=2, highlightbackground=self.BG,
            highlightcolor='#ffffff')
        self.start_button.pack(side='left', fill='x', expand=True, padx=(0, 7))
        self.stop_button = tk.Button(
            actions, text='Stop   F2', command=self.stop, cursor='hand2',
            state='disabled', bg=self.FIELD, fg=self.ROSE, activebackground='#3a2638',
            activeforeground='#ffd7dc', font=('Segoe UI Semibold', 12),
            relief='flat', bd=0, pady=11, takefocus=True,
            highlightthickness=2, highlightbackground=self.BG,
            highlightcolor='#ffffff')
        self.stop_button.pack(side='left', fill='x', expand=True, padx=(7, 0))
        self._button_hover(self.start_button, self.MINT, '#9af2ce')
        self._button_hover(self.stop_button, self.FIELD, '#3a2638')

        activity = tk.Frame(self.overview, bg=self.PANEL, highlightbackground=self.BORDER,
                            highlightthickness=1, padx=20, pady=14)
        activity.pack(fill='x', padx=30, pady=(18, 0))
        tk.Label(activity, text='SESSION', bg=self.PANEL, fg=self.MUTED,
                 font=('Segoe UI Semibold', 10)).pack(anchor='w')
        self.stats = tk.StringVar(value='0 wins   ·   0 coins')
        tk.Label(activity, textvariable=self.stats, bg=self.PANEL, fg=self.TEXT,
                 font=('Segoe UI Semibold', 17)).pack(anchor='w', pady=(6, 0))
        self.message = tk.StringVar(value='Ready — open the TDS lobby, then press F1.')
        tk.Label(activity, textvariable=self.message, bg=self.PANEL, fg=self.MUTED,
                 font=('Segoe UI', 10), anchor='w', justify='left',
                 wraplength=610).pack(fill='x', anchor='w', pady=(7, 0))

        tk.Label(self.overview, text='F1 Start  |  F2 Stop  |  F8 / Esc Emergency stop', bg=self.BG, fg=self.MUTED,
                 font=('Segoe UI', 9), justify='left').pack(anchor='w', padx=31, pady=(14, 0))
        tk.Label(self.overview, text='Keep Roblox foreground at 1920 x 991 pixels and 120 DPI.',
                 bg=self.BG, fg=self.MUTED, font=('Segoe UI', 9),
                 justify='left').pack(anchor='w', padx=31, pady=(2, 0))
        tk.Label(self.diagnostics,text='Session diagnostics',bg=self.BG,fg=self.TEXT,
                 font=('Segoe UI Semibold',19)).pack(anchor='w',padx=24,pady=(24,3))
        tk.Label(self.diagnostics,text='Sanitized read-only events. No command execution or private screenshots.',
                 bg=self.BG,fg=self.MUTED,font=('Segoe UI',10)).pack(anchor='w',padx=24)
        self.diag_text=tk.Text(self.diagnostics,wrap='word',height=18,bg=self.PANEL,
                              fg=self.TEXT,insertbackground=self.TEXT,relief='flat',
                              padx=16,pady=12,font=('Consolas',10),takefocus=True)
        self.diag_text.pack(fill='both',expand=True,padx=24,pady=(15,10))
        self.diag_text.insert('1.0','No session has started.')
        self.diag_text.configure(state='disabled')
        commands=tk.Frame(self.diagnostics,bg=self.BG)
        commands.pack(fill='x',padx=24,pady=(0,20))
        tk.Button(commands,text='Copy diagnostics',command=self.copy_diagnostics,
                  bg=self.MINT,fg=self.BG,relief='flat',padx=15,pady=9,
                  cursor='hand2').pack(side='left',padx=(0,8))
        tk.Button(commands,text='Export .txt',command=self.export_diagnostics,
                  bg=self.FIELD,fg=self.TEXT,relief='flat',padx=15,pady=9,
                  cursor='hand2').pack(side='left')
        self._last_diagnostics=''
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.root.after(100, self.tick)

    @staticmethod
    def _button_hover(button, normal, hovered):
        """Pointer and keyboard feedback without a separate UI dependency."""
        def paint(color):
            if str(button.cget('state')) == 'normal':
                button.configure(bg=color)
        button.bind('<Enter>', lambda _event: paint(hovered))
        button.bind('<Leave>', lambda _event: paint(normal))
        button.bind('<FocusIn>', lambda _event: paint(hovered))
        button.bind('<FocusOut>', lambda _event: paint(normal))

    def diagnostics_report(self):
        from .diagnostics import collect_diagnostics
        return collect_diagnostics(self.controller.status(),self.controller.output)

    def refresh_diagnostics(self):
        if self.tabs.index(self.tabs.select())!=1:
            return
        report=self.diagnostics_report()
        if report!=self._last_diagnostics:
            self.diag_text.configure(state='normal')
            self.diag_text.delete('1.0','end')
            self.diag_text.insert('1.0',report)
            self.diag_text.configure(state='disabled')
            self._last_diagnostics=report

    def copy_diagnostics(self):
        report=self.diagnostics_report()
        self.root.clipboard_clear()
        self.root.clipboard_append(report)

    def export_diagnostics(self):
        from tkinter import filedialog
        path=filedialog.asksaveasfilename(parent=self.root,
                                          defaultextension='.txt',
                                          filetypes=[('Text diagnostics','*.txt')],
                                          initialfile='tds-diagnostics.txt')
        if path:
            try:
                Path(path).write_text(self.diagnostics_report(),encoding='utf-8')
            except OSError as exc:
                self.message.set('Diagnostics export failed: '+type(exc).__name__)

    def start(self, generation=None):
        if self.closing:
            return
        self.start_error = None
        if generation is None:
            generation = self.hotkeys.current_generation()
        cancelled = lambda: self.hotkeys.cancelled_since(generation)
        try:
            if self.controller.start(self.strategy.get(),auto_recover=self.auto_recover.get(),
                                     cancelled=cancelled,auto_equip=self.auto_equip.get()):
                self.message.set(self.controller.startup_message)
                self.root.iconify()
        except (OSError, ValueError, RuntimeError) as exc:
            self.start_error = str(exc)
            self.message.set('Start stopped: '+self.start_error)

    def stop(self, *, cancel_pending=True):
        if cancel_pending:
            self.hotkeys.cancel_start_requests()
        try:
            self.controller.stop()
        except OSError as exc:
            self.message.set(f'Could not request stop: {exc}. Press F8 in Roblox.')

    def close(self):
        self.closing = True
        self.stop()

    def tick(self):
        while True:
            try:
                action, generation = self.hotkeys.events.get_nowait()
            except queue.Empty:
                break
            self.start(generation) if action == 'start' else self.stop(cancel_pending=False)
        running = self.controller.running
        data = self.controller.status()
        self.message.set(status_text(data, running, self.controller.stop_requested, self.start_error))
        selected_hardcore = STRATEGIES.get(self.strategy.get()) == PLAN_V2_ID
        hardcore = data.get('strategy_id') == PLAN_V2_ID if data else selected_hardcore
        if hardcore:
            self.stats.set(f"{data.get('gem_cycles', 0)} verified results     ·     {data.get('gems_total', 0):,} gems displayed")
        else:
            self.stats.set(f"{data.get('wins', 0)} wins     ·     {data.get('coins_total', 0):,} coins")
        if running:
            state = '●  STOPPING' if self.controller.stop_requested else '●  RUNNING'
            color = self.ROSE if self.controller.stop_requested else self.MINT
        elif self.controller.stop_requested or self.start_error or data.get('reason'):
            state, color = '●  STOPPED', self.ROSE
        else:
            state, color = '●  READY', self.MUTED
        self.state_label.configure(text=state, fg=color)
        self.start_button.configure(state='disabled' if running else 'normal',
                                    bg=self.FIELD if running else self.MINT)
        self.stop_button.configure(state='normal' if running else 'disabled',
                                   bg=self.FIELD)
        self.selector.configure(state='disabled' if running else 'readonly')
        self.recover_toggle.configure(state='disabled' if running else 'normal')
        self.equip_toggle.configure(state='disabled')
        self.refresh_diagnostics()
        if self.closing and not running:
            self.hotkeys.close()
            self.root.destroy()
            return
        self.root.after(100, self.tick)


def self_check(path):
    from .calibration import load_profile
    from .hardcore_plan_v2 import PLAN_SHA256, load_hardcore_plan_v2
    from .hardcore_vision import WretchedCamera, WretchedRoute
    from .observer import Observer
    from .resources import LocalOCR
    import tkinter as tk
    from PIL import Image
    profile, strategy = load_profile(ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
    candidate, expanded = load_profile(ROOT/'calibrations/dead_ahead_vertical_ten_v031_v2202_trial.json')
    if (len(expanded.steps)!=50 or candidate['strategy_sha256'] != GOLDEN_V031_ACCEPTED_SHA
            or candidate['setup'].get('post_alignment_moves')!=[['S',750],['D',100]]):
        raise ValueError('The calibrated ten-Scout profile is not the verified candidate.')
    hardcore = load_hardcore_plan_v2()
    WretchedCamera(hardcore)
    WretchedRoute(hardcore.profile_id)
    observer = Observer()
    ocr = LocalOCR()
    with Image.open(ROOT/'assets/ui_2191/victory_play_again_normal.png') as label:
        text = ocr.read(label)
    # Validate Tcl without creating a window or changing Roblox foreground.
    tcl_version = tk.Tcl().eval('info patchlevel')
    result = {'root': str(ROOT), 'frozen': bool(getattr(sys, 'frozen', False)), 'operations': len(strategy.steps), 'golden_candidate_actions': len(expanded.steps),
              'observer_states': len(observer.anchors), 'ocr_text': text, 'tcl': tcl_version, 'strategy_sha256': profile['strategy_sha256'],
              'hardcore_phases': len(hardcore.phases), 'hardcore_plan_sha256': PLAN_SHA256}
    Path(path).write_text(json.dumps(result, indent=2), encoding='utf-8')
    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == '--engine':
        if sys.stdout is None and '--output' in args:
            output = Path(args[args.index('--output')+1])
            output.parent.mkdir(parents=True, exist_ok=True)
            sys.stdout = sys.stderr = (output.parent/f'{output.name}.log').open('a', encoding='utf-8')
        from .session import main as engine
        return engine(args[1:])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', type=Path)
    options = parser.parse_args(args)
    if options.self_check:
        return self_check(options.self_check)
    try:
        app = App()
        app.root.mainloop()
    except (RuntimeError, OSError) as exc:
        ctypes.windll.user32.MessageBoxW(None, str(exc), 'TDS Strategy Macro', 0x10)
        return 2
    return 0
