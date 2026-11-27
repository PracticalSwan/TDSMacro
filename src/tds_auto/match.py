"""Supervised, single-action match primitives. No farming/restart loop."""
from __future__ import annotations

import math
import time
from dataclasses import dataclass

from .control import StopRun
from .resources import Hud
from .timing import READ_SECONDS, SELECTION_SECONDS, ACTION_CONFIRM_SECONDS


@dataclass(frozen=True)
class Snapshot:
    state: str
    hud: Hud
    camera_ok: bool | None
    preview_ok: bool = False
    hotbar_ok: bool = False
    placement_cost: int | None = None
    sell_button_visible: bool = False


class MatchRunner:
    def __init__(self, driver, read, now=time.monotonic, sleep=time.sleep, slot=1, hover_check=None,
                 use_e_upgrades=False, selection_event=None):
        self.driver, self.read, self.now, self.sleep = driver, read, now, sleep
        self.slot=slot
        self.hover_check=hover_check
        self.use_e_upgrades=use_e_upgrades
        self.selected = None
        self.selection_event = selection_event or (lambda **event: None)
        self.selection_clicks = 0
        self.upgrade_keys = 0

    def checked(self):
        deadline=self.now()+READ_SECONDS
        while True:
            self.driver.check()
            shot = self.read()
            self.driver.check()
            if shot.camera_ok is None and shot.state in {'unknown','match_ready','in_match'} and self.now()<deadline:
                self.sleep(.15)
                continue  # A low-confidence frame sends no input; a measured shift still stops.
            if shot.state=='unknown' and shot.camera_ok and self.now()<deadline:
                self.sleep(.15)
                continue
            if shot.state not in {"match_ready", "in_match"} or not shot.camera_ok:
                raise StopRun("Unexpected match state or camera/character view changed.")
            resources=shot.hud.cash is not None and shot.hud.tower_count is not None
            wave=shot.state != 'in_match' or (shot.hud.wave is not None and shot.hud.wave >= 1)
            if resources and wave:
                return shot
            if self.now() >= deadline:
                raise StopRun('Unreadable cash or tower count; no resource guessing.' if not resources else 'Active wave is unreadable.')
            self.sleep(.15)  # Observe animation again; never repeat an input.

    @staticmethod
    def bounded(timeout):
        if not math.isfinite(timeout) or not 0 < timeout <= 300:
            raise StopRun("Action timeout must be 0..300 seconds.")

    @staticmethod
    def empty_panel(shot):
        hud=shot.hud
        return ((hud.tower_name,hud.level,hud.upgrade_cost)==(None,None,None)
                and not hud.maxed and not shot.sell_button_visible)

    def select_scout(self, point, count):
        # Run after the pointer has moved, immediately before the selection.
        previous = self.driver.before_click
        def guard():
            if previous:
                previous()
            deadline = self.now() + SELECTION_SECONDS
            while True:
                shot = self.checked()
                if shot.hud.tower_count != count or not self.empty_panel(shot):
                    raise StopRun('Golden selection requires a cleared panel and unchanged count.')
                if self.hover_check and self.hover_check(point):
                    return
                if self.now() >= deadline:
                    self.selection_event(event='selection_hover_rejected',point=point,count=count)
                    raise StopRun('Owned Scout hover did not verify at the calibrated target.')
                self.sleep(.15)
        self.driver.before_click = guard
        try:
            self.driver.click(*point)
            self.selection_clicks += 1
        finally:
            self.driver.before_click = previous

    def upgrade(self, point, expected_level, count, timeout=180, *, tower_id=None):
        self.bounded(timeout)
        selected, self.selected = self.selected, None
        initial = self.checked()
        if initial.hud.tower_count != count:
            raise StopRun("Unexpected tower count before selection.")
        affordable = 0
        identity = (tower_id, point, count)
        expected = ('Scout', expected_level, count)
        reuse = self.use_e_upgrades and selected == identity and (
            initial.hud.tower_name, initial.hud.level, initial.hud.tower_count) == expected
        if self.use_e_upgrades:
            if tower_id is None:
                raise StopRun('Golden E requires a verified strategy tower ID.')
            if reuse:
                self.selection_event(event='selection_reused', tower_id=tower_id)
            else:
                if selected is not None and selected[0] == tower_id:
                    self.selection_event(event='selection_invalidated', tower_id=tower_id)
                # A positively closed panel makes the next open panel causal,
                # even if the previous Scout had exactly the same level.
                if not self.empty_panel(initial):
                    self.driver.click(1450, 500)
                    self.selection_clicks += 1
                    self.sleep(.2)
                self.select_scout(point, count)
                self.sleep(.2)
        else:
            # Published nine-Scout fallback retains both selection clicks.
            self.driver.click(1450, 500)
            self.driver.check()
            self.driver.click(*point)
            self.sleep(.2)
        deadline = self.now() + timeout
        selection_until = self.now() + SELECTION_SECONDS
        reselected = False
        switched = self.use_e_upgrades and not reuse
        cost, max_confirmed = None, 0
        while self.now() < deadline:
            shot = self.checked()
            if (shot.hud.tower_name, shot.hud.level, shot.hud.tower_count) != expected:
                if reuse:
                    self.selection_event(event='selection_invalidated', tower_id=tower_id)
                    raise StopRun('Reused Scout panel changed before E.')
                if shot.hud.tower_count == count and self.now() < selection_until:
                    self.sleep(0.2)
                    continue
                # A tower can be hovered yet its panel stays closed after the
                # first selection click. Only retry selection (never spending),
                # once, after TWO independent tooltip confirmations.
                empty = (self.empty_panel(shot) if self.use_e_upgrades
                         else shot.hud.tower_name is None and shot.hud.level is None)
                if (not reselected and shot.hud.tower_count == count and empty
                        and self.hover_check is not None and self.hover_check(point)):
                    self.sleep(0.15)
                    fresh = self.checked() if self.use_e_upgrades else shot
                    if (fresh.hud.tower_count == count
                            and (not self.use_e_upgrades or self.empty_panel(fresh))
                            and self.hover_check(point)):
                        if self.use_e_upgrades:
                            self.select_scout(point, count)
                            self.selection_event(event='selection_fallback', tower_id=tower_id)
                        else:
                            self.driver.click(*point)
                        reselected = True
                        selection_until = self.now() + SELECTION_SECONDS
                        continue
                raise StopRun("Selected tower/level/count does not match the expected target.")
            if switched:
                self.selection_event(event='selection_switched', tower_id=tower_id)
                switched = False
            if expected_level==4:
                max_confirmed=max_confirmed+1 if shot.hud.maxed else 0
                if max_confirmed>=2:
                    if self.use_e_upgrades:
                        self.selected = identity
                    return shot.hud
                if not shot.hud.maxed and self.now()>=selection_until:
                    raise StopRun('Level 4 is missing the observed Fully Upgraded marker.')
                self.sleep(.2)
                continue
            if expected_level not in range(4):
                raise StopRun('Unsupported Golden Scout level.')
            actual=shot.hud.upgrade_cost
            if actual is None or actual<0:
                affordable=0
                self.sleep(.2)
                continue  # Observe price/color animation again; never click.
            can_spend=shot.hud.cash>=actual and shot.hud.upgrade_affordable
            affordable=affordable+1 if actual==cost and can_spend else int(can_spend)
            cost=actual
            if affordable >= 2:
                break
            self.sleep(0.25)
        else:
            raise StopRun("Timed out waiting for cash; upgrade was not sent.")
        if self.use_e_upgrades:
            # A fresh final read immediately before the single irreversible E.
            # Never repeat the key if the postcondition is ambiguous.
            last=self.checked()
            if ((last.hud.tower_name,last.hud.level,last.hud.tower_count) != expected or
                    last.hud.upgrade_cost != cost or
                    last.hud.cash < cost or not last.hud.upgrade_affordable):
                raise StopRun("Golden E precondition changed; no key sent.")
            self.driver.key('E',0.10)
            self.upgrade_keys += 1
        else:
            # Published nine-Scout fallback retains the previous control path.
            self.driver.click(220, 578)
        confirm_until = self.now() + ACTION_CONFIRM_SECONDS
        while self.now() < confirm_until:
            shot = self.checked()
            if shot.hud.tower_name == "Scout" and shot.hud.level == expected_level + 1 and shot.hud.tower_count == count:
                if self.use_e_upgrades:
                    self.selected = identity
                return shot.hud
            self.sleep(0.2)
        raise StopRun("Could not confirm upgrade; no retry sent.")

    def place(self, point, slot, count, timeout=180, *, tower_id=None):
        self.selected = None
        self.bounded(timeout)
        if slot != self.slot or slot not in (1,2):
            raise StopRun("Placement slot differs from the verified Scout profile.")
        if not isinstance(count,int) or not 0<=count<40:
            raise StopRun('Tower count is outside placement capacity.')
        deadline, affordable, cost = self.now() + timeout, 0, None
        while self.now() < deadline:
            shot = self.checked()
            if not shot.hotbar_ok:
                raise StopRun("Tower hotbar is not confirmed; no slot key sent.")
            if shot.hud.tower_count != count:
                raise StopRun("Tower count changed before placement.")
            actual=shot.placement_cost
            if actual is None or actual<0:
                raise StopRun('Placement price is unreadable; no slot key sent.')
            affordable=affordable+1 if actual==cost and shot.hud.cash>=actual else int(shot.hud.cash>=actual)
            cost=actual
            if affordable >= 2:
                break
            self.sleep(0.25)
        else:
            raise StopRun("Timed out waiting for placement cash.")
        self.driver.key(str(slot))
        self.driver.move(*point)
        preview = self.checked()
        preview_until=self.now()+2
        while not preview.preview_ok and self.now()<preview_until:
            self.sleep(.15)
            preview=self.checked()
        if not preview.preview_ok:
            self.driver.key("Q")
            raise StopRun("Invalid or missing placement preview; no click sent.")
        if self.use_e_upgrades and (preview.hud.tower_count != count or not preview.hotbar_ok
                                    or preview.placement_cost != cost or preview.hud.cash < cost):
            raise StopRun('Golden placement quote or cash changed; no placement click sent.')
        cleared = False
        if self.use_e_upgrades:
            previous=self.driver.before_click
            def guard():
                nonlocal cleared
                if previous:
                    previous()
                fresh=self.checked()
                # The preview was verified before pointer movement. Allow one
                # passive reread only if every other purchase predicate still
                # agrees; never retry the slot key, pointer move or paid click.
                if (not fresh.preview_ok and fresh.hotbar_ok and fresh.placement_cost==cost
                        and fresh.hud.cash>=cost and fresh.hud.tower_count==count):
                    self.sleep(.15)
                    fresh=self.checked()
                    if (fresh.preview_ok and fresh.hotbar_ok and fresh.placement_cost==cost
                            and fresh.hud.cash>=cost and fresh.hud.tower_count==count):
                        self.selection_event(event='placement_preview_reobserved',point=point,tower_id=tower_id)
                if (not fresh.preview_ok or not fresh.hotbar_ok or fresh.placement_cost!=cost
                        or fresh.hud.cash<cost or fresh.hud.tower_count!=count):
                    self.selection_event(event='placement_guard_rejected',point=point,tower_id=tower_id,
                        expected_count=count,observed_count=fresh.hud.tower_count,
                        expected_price=cost,observed_price=fresh.placement_cost,cash=fresh.hud.cash,
                        preview_ok=fresh.preview_ok,hotbar_ok=fresh.hotbar_ok)
                    raise StopRun('Golden placement precondition changed before click.')
                cleared=self.empty_panel(fresh)
            self.driver.before_click=guard
            try:
                self.driver.click(*point)
            finally:
                self.driver.before_click=previous
        else:
            self.driver.click(*point)
        confirm_until = self.now() + ACTION_CONFIRM_SECONDS
        while self.now() < confirm_until:
            shot = self.checked()
            if (shot.hud.tower_count, shot.hud.tower_name, shot.hud.level) == (count + 1, "Scout", 0):
                if self.use_e_upgrades and tower_id is not None and cleared:
                    self.selected = (tower_id, point, count + 1)
                return shot.hud
            self.sleep(0.2)
        raise StopRun("Could not confirm placement; no retry sent.")
