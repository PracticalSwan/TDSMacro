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
import time
from datetime import datetime
from pathlib import Path
from ctypes import wintypes
from .hardcore_plan_v2 import PLAN_ID as PLAN_V2_ID, XP_PLAN_ID as PLAN_V2_XP_ID, is_hardcore_v2
from .calibration import GOLDEN_V031_ACCEPTED_SHA
from .updates import CURRENT_VERSION, UpdateError, UpdateService

ROOT = Path(__file__).resolve().parents[2]
STRATEGIES = {
    'Golden Scout — 10 Max / Dead Ahead / Easy': 'dead_ahead_vertical_ten_v031_v2202_trial.json',
    'Golden Scout — 9 Scouts (legacy fallback)': 'dead_ahead_vertical_nine_v4.json',
    'Hardcore Gem Grind — 3 Towers / Solo': PLAN_V2_ID,
    'Hardcore Gems + Tower XP — Slot 4 / Solo': PLAN_V2_XP_ID,
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
        hardcore = is_hardcore_v2(selection)
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
            command.extend(['--strategy', selection])
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

        def read_snapshot(name):
            try:
                snapshot = json.loads((self.output/name).read_text(encoding='utf-8'))
            except (OSError, ValueError):
                return {}
            return snapshot if isinstance(snapshot, dict) else {}

        data = read_snapshot('status.json')
        exit_code = self.worker.poll() if self.worker is not None else None
        if exit_code:
            result = read_snapshot('result.json')
            if result.get('reason'):
                return {**data, **result, 'phase': result.get('status', 'stopped')}
            if data.get('phase') not in {'stopped', 'defeat', 'early_result', 'late_result', 'unverified_reward'}:
                data['reason'] = f'Worker exited with exit code {exit_code}. See Diagnostics.'
        return data


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
        if data.get('phase') == 'stopped':
            return 'Stopped. Open Diagnostics for session details.'
        if data.get('phase') == 'defeat':
            return 'Defeat — stopped. Return to the TDS lobby before starting again.'
        if data.get('phase') in {'early_result', 'late_result', 'unverified_reward'}:
            return 'Hardcore stopped — the result did not qualify as a credited cycle.'
        return 'Ready — open the TDS lobby, then press F1.'
    phase = data.get('phase', 'starting')
    if phase == 'hardcore_early_result_retry':
        return (f"Verified wave-{data.get('wave', '?')} early Defeat · "
                f"Restart Match {data.get('consecutive_early_defeats', 1)}/2 · "
                "no full-cycle Gems counted.")
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
    """Windows dashboard for the guarded strategy worker."""

    BG = '#0e131b'
    PANEL = '#19222e'
    FIELD = '#263344'
    TEXT = '#f0f4f8'
    MUTED = '#aab8ca'
    MINT = '#c3ef93'
    ROSE = '#ffaca9'
    SUBTLE = '#121a24'

    def __init__(self):
        import tkinter as tk
        from tkinter import ttk

        self.hotkeys = Hotkeys()
        self.controller = Controller()
        self.root = tk.Tk()
        self.root.title(f'TDS Macro v{CURRENT_VERSION}')
        self.root.geometry('1010x600')
        self.root.minsize(960, 570)
        self.root.configure(bg=self.BG)
        self.closing = False
        self.update_handoff = False
        self.updater = UpdateService(install_root=ROOT)
        self.start_error = None

        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('Dashboard.TCombobox', padding=(10, 9), foreground=self.TEXT,
                        fieldbackground=self.FIELD, background=self.FIELD,
                        arrowcolor=self.TEXT, bordercolor=self.FIELD,
                        lightcolor=self.FIELD, darkcolor=self.FIELD)
        style.map('Dashboard.TCombobox',
                  fieldbackground=[('disabled', self.SUBTLE), ('readonly', self.FIELD)],
                  foreground=[('disabled', self.MUTED), ('readonly', self.TEXT)],
                  bordercolor=[('focus', self.MINT)])
        self.root.option_add('*TCombobox*Listbox.background', self.FIELD)
        self.root.option_add('*TCombobox*Listbox.foreground', self.TEXT)
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.MINT)
        self.root.option_add('*TCombobox*Listbox.selectForeground', self.BG)
        style.configure('Dashboard.Horizontal.TProgressbar', troughcolor=self.SUBTLE,
                        background=self.MINT, bordercolor=self.PANEL, borderwidth=0,
                        lightcolor=self.MINT, darkcolor=self.MINT, thickness=6)

        top = tk.Frame(self.root, bg=self.BG)
        top.pack(fill='x', padx=32, pady=(23, 0))
        self._label(top, 'TDS Macro', size=13, bold=True).pack(side='left')
        self._label(top, f'v{CURRENT_VERSION}', color=self.MUTED, size=9).pack(side='left', padx=10)
        self._button(top, 'Updates', lambda: self._show_window(self.updates_window),
                     quiet=True).pack(side='right')
        self._button(top, 'Diagnostics', self.show_diagnostics,
                     quiet=True).pack(side='right', padx=(0, 8))

        heading = tk.Frame(self.root, bg=self.BG)
        heading.pack(fill='x', padx=32, pady=(23, 16))
        self._label(heading, 'Strategy dashboard', size=26, bold=True).pack(side='left')
        self.state_label = self._label(heading, 'Ready', size=10, bold=True,
                                       color=self.MUTED, bg=self.FIELD, padx=13, pady=6)
        self.state_label.pack(side='right')

        body = tk.Frame(self.root, bg=self.BG)
        body.pack(fill='both', expand=True, padx=32)
        body.grid_columnconfigure(0, weight=1, uniform='dashboard')
        body.grid_columnconfigure(1, weight=1, uniform='dashboard')
        body.grid_rowconfigure(0, weight=1)
        setup = tk.Frame(body, bg=self.PANEL, padx=20, pady=16)
        setup.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        session = tk.Frame(body, bg=self.PANEL, padx=20, pady=16)
        session.grid(row=0, column=1, sticky='nsew', padx=(8, 0))
        self._build_setup(setup, ttk)
        self._build_session(session, ttk)

        footer = tk.Frame(self.root, bg=self.BG)
        footer.pack(fill='x', padx=32, pady=(13, 18))
        self._label(footer, 'F8 / Esc  Emergency stop', size=9,
                    color=self.MUTED).pack(side='left')
        self._label(footer, 'Keep Roblox in the foreground during a run', size=9,
                    color=self.MUTED).pack(side='right')

        self._build_diagnostics(ttk)
        self._build_updates()
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.root.after(100, self.tick)

    def _label(self, parent, text='', *, size=10, bold=False, color=None, **options):
        import tkinter as tk

        bg = options.pop('bg', parent.cget('bg'))
        font = ('Segoe UI Semibold' if bold else 'Segoe UI', size)
        return tk.Label(parent, text=text, bg=bg, fg=color or self.TEXT, font=font, **options)

    def _button(self, parent, text, command, *, primary=False, quiet=False):
        import tkinter as tk

        background = parent.cget('bg')
        normal = self.MINT if primary else background if quiet else self.FIELD
        hover = '#dbf9b9' if primary else '#34465b'
        button = tk.Button(
            parent, text=text, command=command, font=('Segoe UI Semibold', 10),
            bg=normal, fg=self.BG if primary else self.TEXT, disabledforeground=self.MUTED,
            activebackground=hover, activeforeground=self.BG if primary else self.TEXT,
            padx=13, pady=8, relief='flat', bd=0, cursor='hand2', takefocus=True,
            highlightthickness=1, highlightbackground=background, highlightcolor=self.MINT)
        self._button_hover(button, normal, hover)
        return button

    def _build_setup(self, panel, ttk):
        import tkinter as tk

        self._label(panel, 'Run setup', size=16, bold=True).pack(anchor='w')
        self._label(panel, 'Strategy', size=10, color=self.MUTED).pack(anchor='w', pady=(11, 4))
        self.strategy = tk.StringVar(value=next(
            name for name, plan in STRATEGIES.items() if plan == PLAN_V2_ID))
        self.selector = ttk.Combobox(panel, textvariable=self.strategy, values=list(STRATEGIES),
                                     state='readonly', style='Dashboard.TCombobox',
                                     font=('Segoe UI', 10), takefocus=True)
        self.selector.pack(fill='x')
        self.selector.bind('<<ComboboxSelected>>', self._strategy_changed)
        self.loadout_summary = tk.StringVar()
        self._label(panel, textvariable=self.loadout_summary, bg=self.SUBTLE,
                    justify='left', anchor='w', padx=12, pady=9,
                    wraplength=390).pack(fill='x', pady=(9, 6))
        self._strategy_changed()
        self.auto_recover = tk.BooleanVar(value=True)
        self.recover_toggle = tk.Checkbutton(
            panel, text='Recover game failures (up to 3 relaunches)', variable=self.auto_recover,
            bg=self.PANEL, fg=self.TEXT, selectcolor=self.FIELD,
            activebackground=self.PANEL, activeforeground=self.TEXT,
            highlightthickness=1, highlightbackground=self.PANEL, highlightcolor=self.MINT,
            cursor='hand2', font=('Segoe UI', 10), takefocus=True)
        self.recover_toggle.pack(anchor='w')
        self.auto_equip = tk.BooleanVar(value=False)
        self._label(panel, 'Equip towers manually. Auto-Equip is unavailable.',
                    color=self.MUTED, size=9).pack(anchor='w', pady=(3, 0))

        self.start_button = self._button(panel, 'Start run  ·  F1', self.start, primary=True)
        self.start_button.pack(side='bottom', fill='x', pady=(10, 0))

    def _build_session(self, panel, ttk):
        import tkinter as tk

        self._label(panel, 'Live session', size=16, bold=True).pack(anchor='w')
        self.stats = tk.StringVar(value='0 cycles  ·  0 gems displayed')
        self._label(panel, textvariable=self.stats, size=13, bold=True,
                    anchor='w', justify='left', wraplength=386).pack(fill='x', pady=(10, 12))
        metrics = tk.Frame(panel, bg=self.PANEL)
        metrics.pack(fill='x')
        self.wave_display = tk.StringVar(value='—')
        self.action_display = tk.StringVar(value='—')
        self.recoveries_display = tk.StringVar(value='0')
        for column, (title, value) in enumerate((
            ('Wave', self.wave_display), ('Actions', self.action_display),
            ('Recoveries', self.recoveries_display),
        )):
            metrics.grid_columnconfigure(column, weight=1, uniform='metrics')
            tile = tk.Frame(metrics, bg=self.SUBTLE, padx=11, pady=7)
            tile.grid(row=0, column=column, sticky='nsew', padx=(0, 4) if column < 2 else 0)
            self._label(tile, title, size=9, color=self.MUTED).pack(anchor='w')
            self._label(tile, textvariable=value, size=17, bold=True).pack(anchor='w')

        self.progress_bar = ttk.Progressbar(panel, style='Dashboard.Horizontal.TProgressbar')
        self.progress_bar.pack(fill='x', pady=(10, 7))
        self.message = tk.StringVar(value='Open the TDS lobby to start.')
        self._label(panel, textvariable=self.message, justify='left', anchor='w',
                    color=self.MUTED, wraplength=386).pack(fill='x')

        self.stop_button = self._button(panel, 'Stop safely  ·  F2', self.stop)
        self.stop_button.configure(state='disabled')
        self.stop_button.pack(side='bottom', fill='x', pady=(10, 0))

    def _utility_window(self, title, size):
        import tkinter as tk

        window = tk.Toplevel(self.root, bg=self.BG)
        window.withdraw()
        window.title(f'{title} | TDS Macro')
        window.geometry(size)
        window.protocol('WM_DELETE_WINDOW', window.withdraw)
        window.bind('<Control-w>', lambda _event: window.withdraw())
        return window

    @staticmethod
    def _show_window(window):
        window.deiconify()
        window.lift()

    def _build_diagnostics(self, ttk):
        import tkinter as tk

        self.diagnostics_window = self._utility_window('Diagnostics', '690x450')
        self.diagnostics_window.minsize(520, 320)
        panel = tk.Frame(self.diagnostics_window, bg=self.BG)
        panel.pack(fill='both', expand=True, padx=24, pady=20)
        self._label(panel, 'Session diagnostics', size=19, bold=True).pack(anchor='w')
        self.diagnostics_message = tk.StringVar(value='Sanitized session details')
        self._label(panel, textvariable=self.diagnostics_message,
                    color=self.MUTED).pack(anchor='w', pady=(2, 10))
        commands = tk.Frame(panel, bg=self.BG)
        commands.pack(side='bottom', fill='x', pady=(10, 0))
        self._button(commands, 'Copy', self.copy_diagnostics, primary=True).pack(side='left')
        self._button(commands, 'Export .txt', self.export_diagnostics).pack(side='left', padx=8)
        content = tk.Frame(panel, bg=self.PANEL)
        content.pack(fill='both', expand=True)
        self.diag_text = tk.Text(content, wrap='word', bg=self.PANEL, fg=self.TEXT,
                                relief='flat', bd=0, padx=12, pady=10, font=('Consolas', 10),
                                selectbackground=self.FIELD, takefocus=True,
                                highlightthickness=0, state='disabled')
        scroll = ttk.Scrollbar(content, command=self.diag_text.yview)
        self.diag_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.diag_text.pack(side='left', fill='both', expand=True)
        self._last_diagnostics = ''

    def _build_updates(self):
        import tkinter as tk

        self.updates_window = self._utility_window('Updates', '600x360')
        self.updates_window.minsize(575, 325)
        panel = tk.Frame(self.updates_window, bg=self.PANEL, padx=22, pady=18)
        panel.pack(fill='both', expand=True, padx=22, pady=20)
        self._label(panel, 'Application updates', size=19, bold=True).pack(anchor='w')
        self._label(panel, f'Installed version  ·  {CURRENT_VERSION}', color=self.MUTED).pack(
            anchor='w', pady=(4, 16))
        self.auto_updates = tk.BooleanVar(value=self.updater.enabled)
        self.update_toggle = tk.Checkbutton(
            panel, text='Automatic updates', variable=self.auto_updates, command=self.toggle_updates,
            bg=self.PANEL, fg=self.TEXT, selectcolor=self.FIELD,
            activeforeground=self.TEXT, activebackground=self.PANEL,
            highlightthickness=1, highlightbackground=self.PANEL, highlightcolor=self.MINT,
            font=('Segoe UI Semibold', 11), cursor='hand2', takefocus=True)
        self.update_toggle.pack(anchor='w')
        self._label(panel, 'Downloads and installation wait until gameplay is stopped.',
                    color=self.MUTED).pack(anchor='w', pady=(4, 13))
        self.update_message = tk.StringVar(value=self.updater.status)
        self._label(panel, textvariable=self.update_message, color=self.MINT, anchor='w',
                    justify='left', wraplength=480).pack(fill='x')
        actions = tk.Frame(panel, bg=self.PANEL)
        actions.pack(side='bottom', fill='x')
        self.check_update_button = self._button(actions, 'Check now', self.check_updates)
        self.check_update_button.pack(side='left', padx=(0, 8))
        self.install_update_button = self._button(actions, 'Download update', self.install_update,
                                                  primary=True)
        self.install_update_button.configure(state='disabled', bg=self.FIELD)
        self.install_update_button.pack(side='left')

    def toggle_updates(self):
        try:
            self.updater.set_enabled(self.auto_updates.get())
            self.update_message.set(self.updater.status)
        except OSError as exc:
            self.auto_updates.set(self.updater.enabled)
            self.update_message.set('Cannot save update preference: '+str(exc))

    def check_updates(self):
        # An explicit user request may retry a version that failed previously.
        self.updater.clear_failed()
        if self.updater.check_now():
            self.update_message.set(self.updater.status)

    def install_update(self):
        # The update helper only starts when this GUI owns no live worker.
        if self.controller.running:
            self.update_message.set('Stop the current match safely before installing.')
            return
        if getattr(self,'closing',False) or getattr(self,'update_handoff',False):
            return
        if self.updater.busy:
            self.update_message.set('Update verification is still running.')
            return
        if not self.updater.staged:
            if self.updater.release is not None:
                self.updater.prepare_now()
                self.update_message.set(self.updater.status)
            else:
                self.update_message.set('Check for a new release first.')
            return
        try:
            self.hotkeys.cancel_start_requests()
            self.updater.launch_installer()
        except (OSError,RuntimeError,ValueError) as exc:
            self.update_message.set('Update handover failed: '+str(exc))
            return
        self.update_handoff=True
        self.closing=True
        self.hotkeys.close()
        self.root.destroy()

    def maintain_updates(self, running):
        self.updater.poll()
        if (not self.closing and self.updater.enabled and not self.updater.busy
                and not self.updater.staged and not self.updater.error):
            if time.monotonic()>=self.updater.next_check:
                self.updater.check_now()
            elif self.updater.release is not None and not running:
                self.updater.prepare_now()
        if (not self.closing and not running and self.updater.enabled
                and self.updater.staged and not self.updater.busy):
            self.install_update()
            return
        self.update_message.set(self.updater.status)
        self.check_update_button.configure(
            state='disabled' if self.updater.busy else 'normal')
        can_install=bool(self.updater.release and not running and not self.updater.busy)
        self.install_update_button.configure(
            text=('Install verified update' if self.updater.staged else 'Download update'),
            state='normal' if can_install else 'disabled',
            bg=self.MINT if can_install else self.FIELD,
            fg=self.BG if can_install else self.MUTED)

    def _strategy_changed(self, _event=None):
        selection = STRATEGIES.get(self.strategy.get())
        hardcore = is_hardcore_v2(selection)
        if hardcore:
            self.loadout_summary.set(
                'WRETCHED FRONT  /  HARDCORE SOLO\n'
                '1 Boomerang   ·   2 Crook Boss   ·   3 Farm\n'
                + ('4 XP tower (e.g. Juggernaut)   ·   5 empty\n'
                 'Place only with verified spare cash.' if selection == PLAN_V2_XP_ID
                 else 'Slots 4–5 must be empty for the 3-tower run.'))
        else:
            self.loadout_summary.set(
                'DEAD AHEAD  /  EASY SOLO\n'
                'Golden Scout in slot 1; other slots empty.\n'
                'The loadout is verified before gameplay.')
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
        if not self.diagnostics_window.winfo_viewable():
            return
        report=self.diagnostics_report()
        if report!=self._last_diagnostics:
            self.diag_text.configure(state='normal')
            self.diag_text.delete('1.0','end')
            self.diag_text.insert('1.0',report)
            self.diag_text.configure(state='disabled')
            self._last_diagnostics=report

    def show_diagnostics(self):
        self._show_window(self.diagnostics_window)
        self.diagnostics_window.update_idletasks()
        self.refresh_diagnostics()

    def copy_diagnostics(self):
        report=self.diagnostics_report()
        self.root.clipboard_clear()
        self.root.clipboard_append(report)
        self.diagnostics_message.set('Copied sanitized diagnostics.')

    def export_diagnostics(self):
        from tkinter import filedialog
        path=filedialog.asksaveasfilename(parent=self.diagnostics_window,
                                          defaultextension='.txt',
                                          filetypes=[('Text diagnostics','*.txt')],
                                          initialfile='tds-diagnostics.txt')
        if path:
            try:
                Path(path).write_text(self.diagnostics_report(),encoding='utf-8')
            except OSError as exc:
                self.diagnostics_message.set('Export failed: '+type(exc).__name__)
            else:
                self.diagnostics_message.set('Exported sanitized diagnostics.')

    def start(self, generation=None):
        if self.closing or self.update_handoff:
            return
        self.start_error = None
        if generation is None:
            generation = self.hotkeys.current_generation()
        cancelled = lambda: self.hotkeys.cancelled_since(generation)
        try:
            if self.controller.start(self.strategy.get(),auto_recover=self.auto_recover.get(),
                                     cancelled=cancelled,auto_equip=self.auto_equip.get()):
                self.message.set(self.controller.startup_message)
                self.diagnostics_window.withdraw()
                self.updates_window.withdraw()
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
        self.maintain_updates(running)
        if self.update_handoff:
            return
        data = self.controller.status()
        self.message.set(status_text(data, running, self.controller.stop_requested, self.start_error))
        selected_hardcore = is_hardcore_v2(STRATEGIES.get(self.strategy.get()))
        hardcore = is_hardcore_v2(data.get('strategy_id')) if data else selected_hardcore
        if hardcore:
            stat=f"{data.get('gem_cycles', 0)} cycles  ·  {data.get('gems_total', 0):,} gems displayed"
            if data.get('strategy_id') == PLAN_V2_XP_ID:
                stat+=f"  ·  {data.get('xp_placement_cycles', 0)} XP placements"
            self.stats.set(stat)
        else:
            self.stats.set(f"{data.get('wins', 0)} wins  ·  {data.get('coins_total', 0):,} coins")
        wave = data.get('wave')
        actions = data.get('confirmed_actions')
        self.wave_display.set(f"{wave}/{45 if hardcore else 20}" if isinstance(wave, int) else '—')
        target=76 if (data.get('strategy_id') if data else STRATEGIES.get(self.strategy.get())) == PLAN_V2_XP_ID else (75 if hardcore else 50)
        self.action_display.set(f"{actions}/{target}" if isinstance(actions, int) else '—')
        self.recoveries_display.set(str(data.get('recoveries', 0)))
        self.progress_bar.configure(maximum=target,
                                    value=actions if isinstance(actions, int) else 0)
        if running:
            if self.controller.stop_requested:
                state, color = 'Stopping', self.ROSE
            elif data.get('phase') == 'recovering':
                state, color = 'Recovering', self.ROSE
            elif data.get('phase', 'starting') in {'starting', 'lobby_popup_check'}:
                state, color = 'Starting', self.MINT
            else:
                state, color = 'Running', self.MINT
        elif (self.controller.stop_requested or self.start_error or self.message.get().startswith('Stopped')
              or data.get('phase') in {'defeat', 'early_result', 'late_result', 'unverified_reward'}):
            state, color = 'Stopped', self.ROSE
        else:
            state, color = 'Ready', self.MUTED
        self.state_label.configure(text=state, fg=color)
        start_state = 'disabled' if running else 'normal'
        if str(self.start_button.cget('state')) != start_state:
            self.start_button.configure(state=start_state, bg=self.FIELD if running else self.MINT)
            self.stop_button.configure(state='normal' if running else 'disabled', bg=self.FIELD)
        self.selector.configure(state='disabled' if running else 'readonly')
        self.recover_toggle.configure(state='disabled' if running else 'normal')
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
              'hardcore_phases': len(hardcore.phases), 'hardcore_plan_sha256': PLAN_SHA256, 'version': CURRENT_VERSION}
    Path(path).write_text(json.dumps(result, indent=2), encoding='utf-8')
    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0]=='--apply-update':
        if len(args)!=4:
            return 2
        from .updates import apply_from_helper,settings_dir
        try:
            apply_from_helper(Path(args[1]),int(args[2]),args[3])
            return 0
        except (OSError,RuntimeError,ValueError) as exc:
            error_path=settings_dir()/'last-update-error.txt'
            try:
                error_path.parent.mkdir(parents=True,exist_ok=True)
                error_path.write_text(str(exc),encoding='utf-8')
                (error_path.parent/'failed-update.json').write_text(
                    json.dumps({'version':args[3], 'error':type(exc).__name__}),
                    encoding='utf-8')
            except OSError:
                pass
            old=Path(args[1])/'TDSMacro.exe'
            if old.is_file():
                try:
                    subprocess.Popen([str(old)],cwd=old.parent,
                                     creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                except OSError:
                    pass
            return 2
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
