"""Bounded, visually verified menu, lobby-popup and result transitions."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from .control import GuardedInput, StopRun, WindowsOS
from .loadout import (LOADOUT_SEARCH_TOWERS,find_inventory_tower_card,
                      inventory_search_point,read_inventory_search_query,
                      read_selected_tower)
from .observer import Observer, StableState
from .phase1 import USER, capture, locate_roblox, BlankCapture
from .resources import LocalOCR
from .timing import TELEPORT_SECONDS

TRANSITIONS = {
    # Upper-left padding keeps the pointer/profile tooltip clear of PLAY text.
    "open_play": ("lobby", "play_menu", (850, 758)),
    "survival": ("play_menu", "survival_menu", (830, 48)),
    "easy": ("survival_menu", "squad_easy", (365, 430)),
    "solo": ("squad_easy", "map_vote", (745, 420)),
    "hardcore": ("survival_menu", "squad_hardcore", (545, 768)),
    "solo_hardcore": ("squad_hardcore", "map_vote", (745, 420)),
    "return_lobby": ("defeat", "lobby", (835, 768)),
    "dismiss_login": ("login_rewards", "lobby", (1718, 42)),
    "return_victory": ("victory", "lobby", (835, 768)),
    "play_again": ("victory", "match_ready", (1095,768)),
    "restart_match": ("defeat", "match_ready", (1095,768)),
    "open_inventory": ("lobby", "inventory_list", (180,398)),
    "close_inventory": ("inventory_scout", "lobby", (1130,80)),
}
MENU_ROUTE = ("open_play", "survival", "easy", "solo")
HARDCORE_MENU_ROUTE = ("open_play", "survival", "hardcore", "solo_hardcore")


class Navigator:
    def __init__(self, observer, driver, read_frame, now=time.monotonic, sleep=time.sleep,ocr=None):
        self.observer, self.driver, self.read_frame = observer, driver, read_frame
        self.now, self.sleep = now, sleep
        self.ocr=ocr

    def search_tower(self,tower,timeout=8):
        """Search by exact tower name, then select its uniquely OCR-located card."""
        target=' '.join(str(tower).casefold().split())
        if target not in LOADOUT_SEARCH_TOWERS or not math.isfinite(timeout) or not 0<timeout<=30:
            raise StopRun('Unsupported tower name or unbounded inventory-search timeout.')
        from .loadout import INVENTORY_CURSOR_CLEAR_POINT,INVENTORY_LIST_STATES
        ocr=self.ocr or LocalOCR()

        def inventory_frame():
            self.driver.check()
            frame=self.read_frame()
            state=self.observer.observe(frame).state
            if state not in INVENTORY_LIST_STATES:
                raise StopRun(f'Inventory changed during tower search: {state}; no further input.')
            return frame

        inventory_frame()
        self.driver.move(*INVENTORY_CURSOR_CLEAR_POINT)
        first=inventory_frame()
        query=read_inventory_search_query(first,ocr)
        point=inventory_search_point(first,query,ocr) if query is not None else None
        self.driver.wait(.2)
        second=inventory_frame()
        second_query=read_inventory_search_query(second,ocr)
        search_point=inventory_search_point(second,second_query,ocr) if second_query is not None else None
        if query is None or point is None or second_query!=query or search_point is None:
            raise StopRun('Inventory search field was unreadable or changed; no search input sent.',kind='setup')

        if query==target:
            # Already-selected searched tower is a valid postcondition.
            # Avoid a redundant card OCR/click when the highlighted item
            # disappears or loses contrast, but require two fresh text reads.
            first_selected=read_selected_tower(first,ocr)
            second_selected=read_selected_tower(second,ocr)
            if (first_selected is not None and first_selected==second_selected
                    and first_selected[0]==target):
                return first_selected

        if query!=target:
            self.driver.click(*search_point)
            self.driver.select_all()
            self.driver.key('BACKSPACE',.08)
            self.driver.move(*INVENTORY_CURSOR_CLEAR_POINT)
            clear_deadline=self.now()+1.5
            clear_stable=0
            while self.now()<clear_deadline:
                frame=inventory_frame()
                visible_query=read_inventory_search_query(frame,ocr)
                placeholder=inventory_search_point(frame,visible_query,ocr) if visible_query is not None else None
                if visible_query=='' and placeholder is not None:
                    clear_stable+=1
                    if clear_stable>=2:
                        break
                else:
                    clear_stable=0
                self.driver.wait(.15)
            else:
                raise StopRun('Search field did not clear visibly; no tower name typed.',kind='setup')
            self.driver.text(target)

        deadline=self.now()+timeout
        stable_point=None
        stable=0
        selected_point=None
        while self.now()<deadline:
            frame=inventory_frame()
            visible_query=read_inventory_search_query(frame,ocr)
            candidate=find_inventory_tower_card(frame,target,ocr) if visible_query==target else None
            if candidate is not None and candidate==stable_point:
                stable+=1
            else:
                stable=1 if candidate is not None else 0
            stable_point=candidate
            if stable>=2:
                selected_point=candidate
                break
            self.driver.wait(.15)
        if selected_point is None:
            raise StopRun(f'Search did not produce one readable {target.title()} card; no card selected.',kind='setup')

        self.driver.click(*selected_point)
        deadline=self.now()+timeout
        stable=0
        detail=None
        while self.now()<deadline:
            frame=inventory_frame()
            observed=read_selected_tower(frame,ocr)
            if observed is not None and observed[0]==target and observed[1] in {'equip','unequip'}:
                detail=observed
                stable+=1
                if stable>=2:
                    return detail
            else:
                stable=0
                detail=None
            self.driver.wait(.15)
        raise StopRun(f'Selected {target.title()} details did not stabilize; no equip action sent.',kind='setup')

    def step(self, name, timeout=45):
        if name not in TRANSITIONS or not math.isfinite(timeout) or not 0 < timeout <= TELEPORT_SECONDS:
            raise StopRun("Unsupported transition or unbounded timeout.")
        source, target, point = TRANSITIONS[name]
        sources={source}
        targets={target}
        if name=='open_play':
            # A retained Survival tab can bypass the older Play category view.
            targets.update({'survival_menu','survival_menu_2200'})
        if name in {'easy','hardcore'}:
            sources.add('survival_menu_2200')
        if name=='open_inventory':
            targets.add('inventory_scout')
            targets.add('inventory_list_2192')
            targets.add('inventory_search_2192')
        if name=='close_inventory':
            sources.update({'inventory_list','inventory_list_2192','inventory_search_2192'})
        if name in {'return_lobby','return_victory'}:
            targets.add('login_rewards')
        if name=='play_again':
            targets.add('map_vote')  # Current TDS can start a new voting room.
        for index in range(2):
            self.driver.check()
            observed = self.observer.observe(self.read_frame())
            if observed.state not in sources:
                raise StopRun(f"Expected {source}; saw {observed.state}. No click sent.")
            if index==0:
                self.sleep(0.2)
        self.driver.click(*point)
        deadline, stable = self.now() + timeout, StableState()
        while self.now() < deadline:
            self.driver.check()
            try:
                observed = self.observer.observe(self.read_frame())
            except BlankCapture:
                if name not in {'solo','solo_hardcore','return_lobby','return_victory','play_again','restart_match'}:
                    raise
                stable.update('unknown')
                self.sleep(.2)
                continue
            confirmed=stable.update(observed.state)
            if confirmed in targets:
                return confirmed
            allowed = {*sources, *targets, "unknown"}
            if name in {"solo", "solo_hardcore", "return_lobby", "return_victory", "play_again", "restart_match"}:
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
    parser.add_argument("--to-hardcore-map-vote", action="store_true",
                        help="Four screenshot-verified Hardcore/Solo steps from lobby; stops at map vote")
    parser.add_argument("--confirm-start", action="store_true")
    parser.add_argument("--activate", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    selected_routes = sum((args.step is not None, args.to_map_vote, args.to_hardcore_map_vote))
    if not args.confirm_start or selected_routes != 1:
        parser.error("Choose exactly one transition or map-vote route and --confirm-start; F8/Escape stops.")
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
        route = HARDCORE_MENU_ROUTE if args.to_hardcore_map_vote else MENU_ROUTE if args.to_map_vote else (args.step,)
        for name in route:
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
