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


class MatchRunner:
    def __init__(self, driver, read, now=time.monotonic, sleep=time.sleep, slot=1, hover_check=None):
        self.driver, self.read, self.now, self.sleep = driver, read, now, sleep
        self.slot=slot
        self.hover_check=hover_check

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

    def upgrade(self, point, expected_level, count, timeout=180):
        self.bounded(timeout)
        initial = self.checked()
        if initial.hud.tower_count != count:
            raise StopRun("Unexpected tower count before selection.")
        # Placement auto-selects the tower; clicking it again toggles its panel
        # closed. Clear selection on empty scenery before selecting this target.
        self.driver.click(1450, 500)
        self.driver.check()
        self.driver.click(*point)
        self.sleep(0.2)
        deadline, affordable = self.now() + timeout, 0
        selection_until = self.now() + SELECTION_SECONDS
        reselected = False
        cost, max_confirmed = None, 0
        while self.now() < deadline:
            shot = self.checked()
            if (shot.hud.tower_name, shot.hud.level, shot.hud.tower_count) != ("Scout", expected_level, count):
                if shot.hud.tower_count == count and self.now() < selection_until:
                    self.sleep(0.2)
                    continue
                # A tower can be hovered yet its panel stays closed after the
                # first selection click. Only retry selection (never spending),
                # once, after TWO independent tooltip confirmations.
                if (not reselected and shot.hud.tower_count == count
                        and shot.hud.tower_name is None and shot.hud.level is None
                        and self.hover_check is not None and self.hover_check(point)):
                    self.sleep(0.15)
                    if self.hover_check(point):
                        self.driver.click(*point)
                        reselected = True
                        selection_until = self.now() + SELECTION_SECONDS
                        continue
                raise StopRun("Selected tower/level/count does not match the expected target.")
            if expected_level==4:
                max_confirmed=max_confirmed+1 if shot.hud.maxed else 0
                if max_confirmed>=2:
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
        self.driver.click(220, 578)
        confirm_until = self.now() + ACTION_CONFIRM_SECONDS
        while self.now() < confirm_until:
            shot = self.checked()
            if shot.hud.tower_name == "Scout" and shot.hud.level == expected_level + 1 and shot.hud.tower_count == count:
                return shot.hud
            self.sleep(0.2)
        raise StopRun("Could not confirm upgrade; no retry sent.")

    def place(self, point, slot, count, timeout=180):
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
        self.driver.click(*point)
        confirm_until = self.now() + ACTION_CONFIRM_SECONDS
        while self.now() < confirm_until:
            shot = self.checked()
            if (shot.hud.tower_count, shot.hud.tower_name, shot.hud.level) == (count + 1, "Scout", 0):
                return shot.hud
            self.sleep(0.2)
        raise StopRun("Could not confirm placement; no retry sent.")
