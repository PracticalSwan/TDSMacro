"""Small Windows strategy selector; game input remains in the guarded worker."""
from __future__ import annotations

import argparse
import ctypes
import json
import queue
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from ctypes import wintypes

ROOT = Path(__file__).resolve().parents[2]
STRATEGIES = {'Golden Scout — Dead Ahead / Easy / Solo': 'dead_ahead_vertical_nine_v4.json'}


class Hotkeys:
    """Own F1/F2 on a separate message queue, independent of Tk's event pump."""
    ids = {0x5441: 'start', 0x5442: 'stop'}

    def __init__(self):
        self.events = queue.Queue()
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
                    self.events.put(self.ids[message.wParam])
        except Exception as exc:
            self.error = str(exc)
        finally:
            for ident in registered:
                user.UnregisterHotKey(None, ident)
            self.ready.set()

    def close(self):
        if self.thread_id and self.thread.is_alive():
            user = ctypes.WinDLL('user32', use_last_error=True)
            user.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
            user.PostThreadMessageW(self.thread_id, 0x0012, 0, 0)
            self.thread.join(1)


class Controller:
    def __init__(self, root=ROOT, launch=subprocess.Popen):
        self.root, self.launch = Path(root), launch
        self.worker = None
        self.output = None
        self.stop_requested = False

    @property
    def running(self):
        return self.worker is not None and self.worker.poll() is None

    def start(self, strategy, auto_recover=True):
        if self.running:
            return False
        if strategy not in STRATEGIES:
            raise ValueError('Choose the available Golden Scout strategy.')
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        self.output = self.root/'captures'/'runs'/f'app_{stamp}'
        self.output.parent.mkdir(parents=True, exist_ok=True)
        profile = self.root/'calibrations'/STRATEGIES[strategy]
        entry = [sys.executable] if getattr(sys, 'frozen', False) else [sys.executable, str(self.root/'tds_launcher.py')]
        command = [*entry, '--engine', 'start', '--confirm-start', '--continuous',
                   '--startup-delay', '5', '--profile', str(profile), '--output', str(self.output)]
        if auto_recover:
            command.append('--auto-recover')
        # A windowed application has no inherited console streams.
        with (self.output.parent/f'{self.output.name}.log').open('wb') as log:
            self.worker = self.launch(command, cwd=self.root, stdout=log, stderr=log,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
        self.stop_requested = False
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


def status_text(data, running, stopping=False):
    if stopping and running:
        return 'Stopping… releasing controls safely.'
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
        return 'Ready — open the TDS lobby, then press F1.'
    phase = data.get('phase', 'starting')
    if phase=='recovering':
        stages={'cooldown':'restarting shortly','closing':'leaving the failed game','launching':'opening Roblox','waiting_lobby':'waiting for the lobby'}
        return f"Recovery {data.get('recovery_attempt',1)}/{data.get('max_recoveries',3)} · {stages.get(data.get('stage'),'restarting TDS')} · F2 cancels."
    progress = data.get('progress', {})
    if phase == 'playing' and 'confirmed_step' in progress:
        return f"Match {data.get('match', 1)} · {progress.get('count', 0)} Scouts · {progress['confirmed_step']}/44 actions"
    names = {'starting': 'Starting in 5 seconds — switch to Roblox.',
             'playing': 'Playing the Golden Scout strategy…', 'play_again': 'Play Again — waiting for the next match…',
             'vip_map_selection': 'Choosing Dead Ahead with VIP…', 'vote_badge_view_adjustment': 'Clearing the vote view…',
             'camera_check': 'Setting the overhead view…', 'prepared': 'Map and overhead view confirmed.',
             'lobby_popup_check': 'Checking the lobby…', 'loadout_identity': 'Checking Golden Scout…'}
    return names.get(phase, phase.replace('_', ' ').capitalize()+'…')


class App:
    def __init__(self):
        import tkinter as tk
        from tkinter import ttk
        self.hotkeys = Hotkeys()
        self.controller = Controller()
        self.root = tk.Tk()
        self.root.title('TDS Strategy Macro')
        self.root.geometry('650x465')
        self.root.resizable(False, False)
        self.root.configure(bg='#101827')
        self.closing = False
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TCombobox', font=('Segoe UI', 11), padding=9)
        tk.Label(self.root, text='TDS Strategy Macro', font=('Segoe UI Semibold', 23),
                 bg='#101827', fg='#f2f5fa').pack(anchor='w', padx=28, pady=(22, 3))
        tk.Label(self.root, text='Solo grinding · verified map and fixed overhead view',
                 font=('Segoe UI', 10), bg='#101827', fg='#a4b2c6').pack(anchor='w', padx=30)
        tk.Label(self.root, text='STRATEGY', font=('Segoe UI Semibold', 10),
                 bg='#101827', fg='#a4b2c6').pack(anchor='w', padx=30, pady=(22, 6))
        self.strategy = tk.StringVar(value=next(iter(STRATEGIES)))
        self.selector = ttk.Combobox(self.root, textvariable=self.strategy, values=list(STRATEGIES), state='readonly')
        self.selector.pack(fill='x', padx=30)
        self.auto_recover=tk.BooleanVar(value=True)
        self.recover_toggle=tk.Checkbutton(self.root,text='Recover game failures automatically',variable=self.auto_recover,
            bg='#101827',fg='#c1cede',selectcolor='#25334a',activebackground='#101827',activeforeground='#f2f5fa',
            font=('Segoe UI',10),highlightthickness=0)
        self.recover_toggle.pack(anchor='w',padx=27,pady=(9,0))
        actions = tk.Frame(self.root, bg='#101827')
        actions.pack(fill='x', padx=30, pady=18)
        self.start_button = tk.Button(actions, text='Start  ·  F1', command=self.start,
            bg='#70dfb0', fg='#09271b', activebackground='#92ebc6', font=('Segoe UI Semibold', 12), relief='flat', pady=9)
        self.start_button.pack(side='left', fill='x', expand=True, padx=(0, 8))
        self.stop_button = tk.Button(actions, text='Stop  ·  F2', command=self.stop,
            bg='#e78a95', fg='#391119', font=('Segoe UI Semibold', 12), relief='flat', pady=9)
        self.stop_button.pack(side='left', fill='x', expand=True, padx=(8, 0))
        self.message = tk.StringVar(value='Ready — open the TDS lobby, then press F1.')
        self.stats = tk.StringVar(value='0 wins     ·     0 coins')
        tk.Label(self.root, textvariable=self.stats, font=('Segoe UI Semibold', 15),
                 bg='#101827', fg='#f2f5fa').pack(anchor='w', padx=30)
        tk.Label(self.root, textvariable=self.message, font=('Segoe UI', 10), justify='left',
                 wraplength=585, bg='#101827', fg='#c1cede').pack(anchor='w', padx=30, pady=(8, 6))
        tk.Label(self.root, text='Choose a strategy, open Roblox at the TDS lobby, then press F1.\nF2 stops at any time. Keep Roblox in front while the macro plays.',
                 font=('Segoe UI', 9), justify='left', bg='#101827', fg='#92a3ba').pack(side='bottom', anchor='w', padx=30, pady=18)
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.root.after(100, self.tick)

    def start(self):
        if self.closing:
            return
        try:
            if self.controller.start(self.strategy.get(),auto_recover=self.auto_recover.get()):
                self.message.set('Starting in 5 seconds — switch to Roblox.')
                self.root.iconify()
        except (OSError, ValueError) as exc:
            self.message.set(str(exc))

    def stop(self):
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
                action = self.hotkeys.events.get_nowait()
            except queue.Empty:
                break
            self.start() if action == 'start' else self.stop()
        running = self.controller.running
        data = self.controller.status()
        self.message.set(status_text(data, running, self.controller.stop_requested))
        self.stats.set(f"{data.get('wins', 0)} wins     ·     {data.get('coins_total', 0):,} coins")
        self.start_button.configure(state='disabled' if running else 'normal')
        self.stop_button.configure(state='normal' if running else 'disabled')
        self.selector.configure(state='disabled' if running else 'readonly')
        self.recover_toggle.configure(state='disabled' if running else 'normal')
        if self.closing and not running:
            self.hotkeys.close()
            self.root.destroy()
            return
        self.root.after(100, self.tick)


def self_check(path):
    from .calibration import load_profile
    from .observer import Observer
    from .resources import LocalOCR
    import tkinter as tk
    from PIL import Image
    profile, strategy = load_profile(ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
    observer = Observer()
    ocr = LocalOCR()
    with Image.open(ROOT/'assets/ui_2191/victory_play_again_normal.png') as label:
        text = ocr.read(label)
    # Validate Tcl without creating a window or changing Roblox foreground.
    tcl_version = tk.Tcl().eval('info patchlevel')
    result = {'root': str(ROOT), 'frozen': bool(getattr(sys, 'frozen', False)), 'operations': len(strategy.steps),
              'observer_states': len(observer.anchors), 'ocr_text': text, 'tcl': tcl_version, 'strategy_sha256': profile['strategy_sha256']}
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
