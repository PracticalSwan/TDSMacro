"""Bounded, visually verified menu, lobby-popup and result transitions."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from .control import GuardedInput, StopRun, WindowsOS
from .observer import Observer, StableState
from .phase1 import USER, capture, locate_roblox, BlankCapture
from .timing import TELEPORT_SECONDS

TRANSITIONS = {
    # Upper button padding keeps a 3D player's profile tooltip above PLAY text.
    "open_play": ("lobby", "play_menu", (960, 758)),
    "survival": ("play_menu", "survival_menu", (830, 48)),
    "easy": ("survival_menu", "squad_easy", (365, 430)),
    "solo": ("squad_easy", "map_vote", (745, 420)),
    "return_lobby": ("defeat", "lobby", (835, 768)),
    "dismiss_login": ("login_rewards", "lobby", (1718, 42)),
    "return_victory": ("victory", "lobby", (835, 768)),
    "play_again": ("victory", "match_ready", (1095,768)),
    "restart_match": ("defeat", "match_ready", (1095,768)),
    "open_inventory": ("lobby", "inventory_list", (120,430)),
    "scout_details": ("inventory_list", "inventory_scout", (390,370)),
    "close_inventory": ("inventory_scout", "lobby", (1130,80)),
}
MENU_ROUTE = ("open_play", "survival", "easy", "solo")


class Navigator:
    def __init__(self, observer, driver, read_frame, now=time.monotonic, sleep=time.sleep):
        self.observer, self.driver, self.read_frame = observer, driver, read_frame
        self.now, self.sleep = now, sleep

    def step(self, name, timeout=45):
        if name not in TRANSITIONS or not math.isfinite(timeout) or not 0 < timeout <= TELEPORT_SECONDS:
            raise StopRun("Unsupported transition or unbounded timeout.")
        source, target, point = TRANSITIONS[name]
        targets={target}
        if name=='open_inventory':
            targets.add('inventory_scout')
        if name in {'return_lobby','return_victory'}:
            targets.add('login_rewards')
        if name=='play_again':
            targets.add('map_vote')  # Current TDS can start a new voting room.
        for _ in range(2):
            self.driver.check()
            observed = self.observer.observe(self.read_frame())
            if observed.state != source:
                raise StopRun(f"Expected {source}; saw {observed.state}. No click sent.")
            self.sleep(0.2)
        self.driver.click(*point)
        deadline, stable = self.now() + timeout, StableState()
        while self.now() < deadline:
            self.driver.check()
            try:
                observed = self.observer.observe(self.read_frame())
            except BlankCapture:
                if name not in {'solo','return_lobby','return_victory','play_again','restart_match'}:
                    raise
                stable.update('unknown')
                self.sleep(.2)
                continue
            confirmed=stable.update(observed.state)
            if confirmed in targets:
                return confirmed
            allowed = {source, *targets, "unknown"}
            if name in {"solo", "return_lobby", "return_victory", "play_again", "restart_match"}:
                allowed.add("loading")
            if name in {"return_lobby","return_victory","play_again","restart_match"}:
                allowed.add("in_match")  # Results close before the teleport/loading frame.
            if observed.state not in allowed:
                raise StopRun(f"Unexpected post-action state: {observed.state}.")
            self.sleep(0.2)
        raise StopRun(f"Timed out waiting for {target}; no retry sent.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", choices=TRANSITIONS)
    parser.add_argument("--to-map-vote", action="store_true", help="Four steps from confirmed lobby; never votes or presses Ready")
    parser.add_argument("--confirm-start", action="store_true")
    parser.add_argument("--activate", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.confirm_start or bool(args.step) == args.to_map_vote:
        parser.error("Choose --step or --to-map-vote and --confirm-start; F8/Escape stops.")
    platform = None
    try:
        platform = WindowsOS(stop_hotkey=True)
        window = locate_roblox()
        if args.activate:
            USER.SetForegroundWindow(window.hwnd)
            time.sleep(0.3)
            window = locate_roblox()
        if (window.width, window.height) != (1920, 991):
            raise StopRun("Navigation is calibrated only for the 1920x991 physical client.")
        args.output.mkdir(parents=True, exist_ok=True)
        observer, index = Observer(), 0
        last_state = None
        def read_frame():
            nonlocal index, last_state
            frame = capture(window)
            state = observer.observe(frame).state
            if state != last_state:
                index += 1
                frame.save(args.output / f"{index:02}_{state}.png")
                last_state = state
            return frame
        nav = Navigator(observer, GuardedInput(window, platform), read_frame)
        for name in MENU_ROUTE if args.to_map_vote else (args.step,):
            result = nav.step(name)
            print(json.dumps({"transition": name, "verified": result}), flush=True)
        print("STOPPED: requested transition verified; no further actions.")
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"NAVIGATION_STOP: {exc}")
        return 2
    finally:
        if platform:
            platform.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
