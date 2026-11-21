"""Guarded normal-speed Wretched Front actions and natural-result observation."""
from dataclasses import replace

import cv2
import numpy as np
from PIL import Image

from .control import StopRun
from .hardcore_plan import PROFILE_ID, ROOT
from .hardcore_vision import (
    WRETCHED_TRAVEL_PITCH, WretchedCamera, WretchedRoute, wretched_hover, wretched_preview,
    wretched_match_ready, wretched_price, wretched_ready,
)
from .maps import vote_players
from .recording import append_jsonl
from .results import read_hardcore_result
from .resources import HudReader, read_hardcore_wave
from .timing import ACTION_CONFIRM_SECONDS, READ_SECONDS, RESULT_CONFIRM_SECONDS, SELECTION_SECONDS

SPEED_BOX = (644, 956, 671, 977)
FARM_UPGRADE_PROOF = ((35, 197, 325, 620), (547, 33, 1417, 123),
                      (1270, 890, 1402, 975), (1795, 140, 1910, 180))

# The native trial leaked at wave 5 and lost at wave 19 with the formation
# unfinished. Begin reserving before each target and keep overdue defense active.
DEFENSE_DEADLINES = (
    (4, 1, (('B1', 0),)),
    # In a native wave-23 defeat, C1 urgency bought ahead of B1 L2; the
    # first Boomerang remained L1 until wave 9 and HP had fallen to 87/100.
    # The credited wave-30 run bought B1 L2 at wave 5 with full HP.
    (7, 2, (('B1', 2),)),
    # Keep wave 8 available to finish F5 L3 after the first Boomerang.
    # Both wave-23 losses left F5 L3 until wave 11; the credited run bought
    # it at wave 7 and still completed C1 L2 by wave 10, B1 L3 at wave 11.
    (11, 2, (('C1', 2), ('B1', 3))),
    (16, 2, (('C2', 2),)),
    (17, 2, (('B2', 0), ('B3', 0))),
    (18, 2, (('B2', 3), ('B3', 3), ('C3', 0), ('C4', 0), ('C5', 0))),
    # Phase 11 intentionally buys C1/C2 L3 before B1 L4. The old,
    # repeatedly missed wave-19 rule reversed that approved ordering.
)


def affordable_purchase(pending, levels, price_for, cash):
    """Respect dependencies and choose the first affordable eligible purchase."""
    unread_price = None
    required_pending = any(not action.optional for _, action in pending)
    for index, (_, action) in enumerate(pending):
        if action.optional and required_pending:
            continue
        current = levels.get(action.tower_id)
        if action.operation == 'place':
            if current is not None:
                continue
        elif current != action.level - 1:
            continue
        price = price_for(action, current)
        if price is not None and price <= cash:
            return index
        if price is None and unread_price is None:
            unread_price = index
    return unread_price


class MatchEnded(Exception):
    def __init__(self, state, frame):
        self.state = state
        self.frame = frame


class TargetWaveReached(Exception):
    """A guarded purchase stopped before input at the target wave."""


class UpgradeDeferred(Exception):
    """A live quote or budget changed before mouse-down."""


class HardcoreMatch:
    def __init__(self, session):
        self.session = session
        self.driver = session.driver
        self.plan = session.hardcore_plan
        self.camera = WretchedCamera(self.plan)
        self.reader = HudReader(hardcore=True)
        self.ocr = self.reader.ocr
        with Image.open(ROOT / 'assets/ui_2191/hardcore_normal_speed.png') as marker:
            self.normal_speed = np.asarray(marker.crop((26, 74, 53, 95)).convert('L'))
        self.towers = {tower.tower_id: tower for tower in self.plan.towers}
        self.levels = {}
        self.upgrade_costs = {}
        self.selected = None
        self.completed = 0
        self.last_wave = 0
        self.next_wave = None
        self.target_observations = 0
        self.min_target_observations = getattr(self.plan, 'min_target_observations', 2)
        self.opening = True
        self.recorded_wait = set()

    def frame(self, *, require_speed=True):
        deadline = self.session.now() + 1
        while True:
            frame = self.session.frame(record_latest=False)
            result = self.session.observer.result_banner(frame)
            if result:
                raise MatchEnded(result, frame)
            offset = self.camera.estimate(frame)
            if offset is not None and all(abs(a-b) <= 2 for a,b in zip(offset, self.camera.offset)):
                break
            # Roblox disconnects blur the entire playfield. Detect its exact
            # native dialog before misclassifying the missing terrain as drift.
            # No recovery input is sent from the gameplay action path.
            from .recovery import disconnect_prompt
            if disconnect_prompt(frame):
                self.session.save_frame(frame, 'hardcore_disconnect_confirmed.png')
                self.session.status('hardcore_disconnected', wave=self.last_wave)
                raise StopRun('Roblox disconnected during Hardcore gameplay.', kind='failure')
            # A short animation can obscure one landmark. A measured shift
            # still stops immediately, and no input occurs during rereads.
            if offset is not None or self.session.now() >= deadline:
                self.session.save_frame(frame, 'hardcore_camera_unverified.png')
                self.session.status('hardcore_camera_unverified',
                                    bound_offset=self.camera.offset, observed_offset=offset)
                raise StopRun('The Wretched Front back-path camera is unverified.')
            self.driver.wait(.15)
        if require_speed and not self.is_normal_speed(frame):
            self.session.save_frame(frame, 'hardcore_normal_speed_unverified.png')
            raise StopRun('The native Hardcore 1× speed marker is unverified.')
        return frame

    def is_normal_speed(self, frame):
        label = np.asarray(frame.crop(SPEED_BOX).convert('L'))
        return cv2.matchTemplate(label, self.normal_speed, cv2.TM_CCOEFF_NORMED)[0, 0] >= .97

    def click(self, point, guard):
        """Recheck the specific action after the guarded pointer move, before mouse-down."""
        self.session.pause()
        previous = self.driver.before_click
        self.driver.before_click = guard
        try:
            self.driver.click(*point)
        finally:
            self.driver.before_click = previous

    def ready(self):
        frame = self.frame(require_speed=False)
        return self.ready_frame(frame)

    def ready_frame(self, frame, *, require_speed=True):
        if require_speed and not self.is_normal_speed(frame):
            return False
        hud = self.reader.read(frame)
        return (wretched_ready(frame, self.ocr) and hud.tower_count == len(self.levels)
                and hud.wave is None and vote_players(frame) == self.plan.squad_size)

    def confirm_opening_ready(self):
        """Use one guarded frame per check; retry only transient read failures."""
        for attempt in range(3):
            frame = self.frame(require_speed=False)
            if self.ready_frame(frame):
                self.session.save_frame(frame, 'hardcore_opening_farms_ready.png')
                return
            if attempt < 2:
                self.driver.wait(.2)
        self.session.save_frame(frame, 'hardcore_ready_preclick_unverified.png')
        raise StopRun('Wretched Front Ready changed before click.')

    def route_ready(self, frame):
        hud = self.reader.read(frame)
        return (wretched_match_ready(frame, self.session.observer, self.ocr)
                and hud.tower_count == 0 and hud.wave is None and vote_players(frame) == self.plan.squad_size)

    def settled_camera_view(self, route, checkpoints):
        """Read the same zero-tower terrain checkpoint or placement pose twice."""
        from .recovery import disconnect_prompt

        # Moving scenery may obscure a stationary route landmark for several
        # frames. Extend only passive observations; never move on uncertainty.
        deadline = self.session.now() + 8
        previous_ready, previous_pose, previous_index = False, None, None
        previous_disconnect = False
        while True:
            self.session.pause()
            frame = self.session.frame(record_latest=False)
            ready = self.route_ready(frame)
            disconnected = not ready and disconnect_prompt(frame)
            if disconnected and previous_disconnect:
                self.session.save_frame(frame, 'hardcore_camera_disconnected.png')
                raise StopRun('Roblox disconnected during Hardcore camera setup.', kind='failure')
            pose = self.camera.estimate(frame) if ready else None
            matches = route.matching_steps(frame, checkpoints) if ready and pose is None and checkpoints else []
            index = matches[0] if len(matches) == 1 else None
            if pose is not None and previous_pose is not None and all(
                    abs(a - b) <= 2 for a, b in zip(pose, previous_pose)):
                return frame, pose, None, True
            if index is not None and index == previous_index:
                return frame, None, index, True
            if self.session.now() >= deadline:
                return frame, None, None, ready and previous_ready
            previous_ready, previous_pose, previous_index = ready, pose, index
            previous_disconnect = disconnected
            self.driver.wait(.2)

    def align_camera(self):
        """Restore the standard pitch and zoom once if no safe route view settles."""
        route = WretchedRoute(self.plan.profile_id)
        end = len(route.steps)
        checkpoints = range(end)
        minimum = 0
        reset_available = self.plan.profile_id != PROFILE_ID
        while True:
            frame, pose, index, ready = self.settled_camera_view(route, checkpoints)
            # Camera-only normalization is safe at spawn, not after walking.
            # Mid-route checkpoint failures must preserve the last known pose.
            if pose is None and index is None and ready and reset_available and minimum == 0:
                reset_available = False
                self.session.status('hardcore_camera_normalizing', checkpoint=minimum)
                self.session.save_frame(frame, 'hardcore_camera_before_normalizing.png')
                for method, *args in route.steps[0]:
                    getattr(self.driver, method)(*args)
                self.driver.wait(.35)
                remaining = range(minimum, end)
                frame, pose, index, ready = self.settled_camera_view(route, remaining)
                if pose is None and index is None and ready and remaining:
                    # The same position can have a verified oblique gate view.
                    self.driver.orbit(0, WRETCHED_TRAVEL_PITCH)
                    self.driver.wait(.35)
                    frame, pose, index, _ = self.settled_camera_view(route, remaining)
            if pose is not None:
                self.camera.offset = pose
                self.session.save_frame(frame, 'hardcore_camera_calibrated.png')
                return
            if index is None:
                self.session.save_frame(frame, f'hardcore_route_{minimum:02d}_unverified.png')
                raise StopRun(f'Wretched back-path terrain did not verify at checkpoint {minimum}.', kind='setup')
            self.session.status('hardcore_camera_route', checkpoint=index)
            self.session.save_frame(frame, f'hardcore_route_{index:02d}.png')
            for method, *args in route.steps[index]:
                getattr(self.driver, method)(*args)
            self.driver.wait(.35)
            minimum = index + 1
            checkpoints = (minimum,) if minimum < end else ()

    def start(self, opening_phase=None):
        self.align_camera()
        stable = 0
        deadline = self.session.now() + 8
        while self.session.now() < deadline:
            stable = stable + 1 if self.ready() else 0
            if stable == 2:
                break
            self.driver.wait(.2)
        else:
            raise StopRun('Wretched Front Solo Ready and zero towers did not verify twice.')

        stage = self.plan.stages[0] if opening_phase is None else None
        actions = opening_phase.actions if opening_phase is not None else stage.actions
        for action in actions:
            tower = self.towers[action.tower_id]
            if not self.place(tower, stage):
                raise StopRun(f'Starting cash or price is unverified for {tower.tower_id}; Ready was not clicked.')

        self.click((967, 177), self.confirm_opening_ready)
        self.opening = False
        stable = 0
        deadline = self.session.now() + 18
        while self.session.now() < deadline:
            frame = self.frame()
            stable = stable + 1 if read_hardcore_wave(frame, self.ocr) == 1 else 0
            if stable == 2:
                self.session.save_frame(frame, 'hardcore_wave_01.png')
                self.observe_wave(1, frame)
                return
            self.driver.wait(.25)
        raise StopRun('Wave 1 did not verify twice; no placement sent.')

    def observe_wave(self, wave, frame):
        # Crossfade can combine old and new digits into an apparent jump.
        # Such a frame cannot authorize input or invalidate an action deadline.
        if wave not in (self.last_wave, self.last_wave + 1):
            self.next_wave = None
            return False
        if wave != self.last_wave and self.last_wave and self.next_wave != wave:
            self.next_wave = wave
            return False
        confirmed_advance = wave != self.last_wave and self.next_wave == wave
        self.next_wave = None
        if wave != self.last_wave:
            self.last_wave = wave
            self.session.status('hardcore_wave', wave=wave, confirmed_actions=self.completed)
        if wave == self.plan.finish_wave:
            self.target_observations += 2 if confirmed_advance else 1
            if self.target_observations == self.min_target_observations:
                self.session.save_frame(frame, 'hardcore_target_wave.png')
                self.session.status('hardcore_wait_natural_result', wave=wave,
                                    confirmed_actions=self.completed)
        return True

    def read(self, counts, stage=None):
        deadline = self.session.now() + READ_SECONDS
        while True:
            frame = self.frame()
            hud = self.reader.read(frame)
            if self.opening:
                stable_wave = hud.wave is None and wretched_ready(frame, self.ocr)
                if stable_wave:
                    hud = replace(hud, wave=0)
            else:
                stable_wave = self.observe_wave(hud.wave, frame)
            if stable_wave:
                if type(stage) is int:
                    if hud.wave >= self.plan.finish_wave:
                        raise TargetWaveReached()
                if stage is not None and type(stage) is not int and hud.wave > stage.last_wave:
                    raise StopRun(f'Action deadline {stage.last_wave} passed at wave {hud.wave}.')
            if hud.tower_count is not None and hud.tower_count not in counts:
                raise StopRun(f'Unexpected tower count {hud.tower_count}; expected {sorted(counts)}.')
            if hud.cash is not None and hud.tower_count is not None and stable_wave:
                return frame, hud
            if self.session.now() >= deadline:
                self.session.save_frame(frame, 'hardcore_hud_unreadable.png')
                raise StopRun('Hardcore cash, tower count or wave was unreadable.')
            self.driver.wait(.15)

    def confirm(self, tower, level, counts, *, timeout, evidence, stage=None):
        deadline = self.session.now() + timeout
        cursor_parked = False
        while True:
            frame, hud = self.read(counts, stage)
            if hud.tower_count == max(counts) and (hud.tower_name, hud.level) == (tower.tower_type, level):
                if evidence:
                    if tower.tower_type == 'Farm' and level > 0:
                        proof = Image.new('RGB', frame.size)
                        for box in FARM_UPGRADE_PROOF:
                            proof.paste(frame.crop(box), box[:2])
                        frame = proof
                    self.session.save_frame(frame, evidence)
                return hud
            if self.session.now() >= deadline:
                self.session.save_frame(frame, 'hardcore_action_unconfirmed.png')
                raise StopRun(f'Could not confirm {tower.tower_id} level {level}; no repeat click sent.')
            if len(counts) == 2 and hud.tower_count == max(counts) and not cursor_parked:
                # The placement is visible in the count. Clear its hover
                # without clicking or closing the auto-selected tower panel.
                self.driver.move(1450, 450)
                cursor_parked = True
            self.driver.wait(.15)

    def place(self, tower, stage):
        point = self.camera.point(tower.tower_id)
        count = len(self.levels)
        frame, hud = self.read({count}, stage)
        price = wretched_price(frame, tower.slot, self.ocr)
        if price is None or hud.cash < price:
            if tower.tower_id not in self.recorded_wait:
                self.recorded_wait.add(tower.tower_id)
                self.session.save_frame(frame, f'hardcore_{tower.tower_id}_waiting_to_place.png')
                self.session.status('hardcore_wait_placement', tower_id=tower.tower_id,
                                    wave=hud.wave, cash=hud.cash, price=price)
            return False

        # Selecting a hotbar slot cannot spend cash. The commit guard checks
        # a fresh cash/price and green footprint after the pointer moves, so
        # a second pre-slot OCR read only delays the placement.
        self.driver.key(str(tower.slot))
        return self.commit_placement(tower, stage, point, count, price)

    def commit_placement(self, tower, stage, point, count, price):
        """Complete one placement from the slot preview that is already armed."""
        round_footprint = tower.tower_type in {'Boomerang', 'Crook Boss'} or (
            getattr(tower, 'optional', False) and tower.tower_type != 'Military Base')
        try:
            def guard():
                deadline = self.session.now() + 2
                while True:
                    frame, hud = self.read({count}, stage)
                    # Hotbar labels can briefly animate during slot selection.
                    # Wait only for an exact fresh quote and sufficient cash;
                    # never click on a missing, changed, or unaffordable quote.
                    fresh_price = wretched_price(frame, tower.slot, self.ocr)
                    if hud.cash < price or fresh_price != price:
                        if self.session.now() >= deadline:
                            self.session.save_frame(frame, f'hardcore_{tower.tower_id}_price_unverified.png')
                            raise StopRun(f'Placement price or cash changed for {tower.tower_id}.')
                        self.driver.wait(.15)
                        continue
                    if wretched_preview(frame, point, self.ocr, round_footprint=round_footprint):
                        return
                    if self.session.now() >= deadline:
                        self.session.save_frame(frame, f'hardcore_{tower.tower_id}_preview_rejected.png')
                        raise StopRun(f'No valid placement preview for {tower.tower_id}.')
                    self.driver.wait(.15)

            self.click(point, guard)
        except TargetWaveReached:
            self.frame()
            self.driver.key('Q')
            raise
        except StopRun as exc:
            if exc.kind in {'failure', 'strategy'}:
                self.frame()
                self.driver.key('Q')
            raise
        hud = self.confirm(tower, 0, {count, count + 1}, timeout=ACTION_CONFIRM_SECONDS,
                           evidence=f'hardcore_{tower.tower_id}_place.jpg')
        self.levels[tower.tower_id] = 0
        self.selected = tower.tower_id
        self.record(tower, 'place', price, hud)
        return True

    def select(self, tower, stage):
        count = len(self.levels)
        level = self.levels[tower.tower_id]
        _, hud = self.read({count}, stage)
        if self.selected == tower.tower_id and (hud.tower_name, hud.level) == (tower.tower_type, level):
            return hud
        point = self.camera.point(tower.tower_id)

        def guard():
            deadline = self.session.now() + SELECTION_SECONDS
            while True:
                frame, _ = self.read({count}, stage)
                if wretched_hover(frame, point, tower.tower_type, self.ocr):
                    return
                if self.session.now() >= deadline:
                    self.session.save_frame(frame, f'hardcore_{tower.tower_id}_hover_rejected.png')
                    raise StopRun(f'Owned tower hover is unverified for {tower.tower_id}.')
                self.driver.wait(.15)

        self.click(point, guard)
        try:
            hud = self.confirm(tower, level, {count}, timeout=SELECTION_SECONDS,
                               evidence=None, stage=stage)
        except StopRun as exc:
            if str(exc) != f'Could not confirm {tower.tower_id} level {level}; no repeat click sent.':
                raise
            # A native C3 selection showed a stable owned-tower hover with no
            # open panel: the first *selection* click was lost. Retry this
            # harmless selection once, only after two fresh identical
            # ownership/empty-panel checks. Never repeat upgrade/placement.
            for _ in range(2):
                frame, live = self.read({count}, stage)
                if (live.tower_name is not None or live.level is not None
                        or live.upgrade_cost is not None
                        or not wretched_hover(frame, point, tower.tower_type, self.ocr)):
                    raise
                self.driver.wait(.15)
            self.session.status('hardcore_selection_retry', tower_id=tower.tower_id)
            self.click(point, guard)
            hud = self.confirm(tower, level, {count}, timeout=SELECTION_SECONDS,
                               evidence=None, stage=stage)
        self.selected = tower.tower_id
        return hud

    def upgrade(self, tower, level, stage):
        hud = self.select(tower, stage)
        price = hud.upgrade_cost
        self.remember_upgrade_price(tower, hud)
        if price is None or hud.cash < price or not hud.upgrade_affordable:
            return False
        count = len(self.levels)

        def guard():
            # A selected tower's outlined level digit can be unreadable in
            # one frame. Recheck without input for at most two seconds;
            # never send E unless the exact tower and previous level verify.
            deadline = self.session.now() + 2
            while True:
                frame, live = self.read({count}, stage)
                if (live.tower_name, live.level) == (tower.tower_type, level - 1):
                    break
                if self.session.now() >= deadline:
                    self.session.save_frame(frame, f'hardcore_{tower.tower_id}_upgrade_selection_changed.png')
                    raise StopRun(f'Upgrade tower or level changed for {tower.tower_id}.')
                self.driver.wait(.15)
            if live.upgrade_cost != price or live.cash < price or not live.upgrade_affordable:
                key = (tower.tower_id, level)
                if key not in self.recorded_wait:
                    self.recorded_wait.add(key)
                    self.session.save_frame(frame, f'hardcore_{tower.tower_id}_level_{level}_quote_deferred.png')
                    self.session.status('hardcore_upgrade_quote_deferred', tower_id=tower.tower_id,
                                        wave=live.wave, cash=live.cash, price=live.upgrade_cost,
                                        original_cash=hud.cash, original_price=price)
                raise UpgradeDeferred()

        try:
            # E is the native upgrade shortcut. Keep the same fresh quote,
            # selected-tower and cash guard, then emit a focus/stop-checked key
            # instead of moving the pointer onto the upgrade button.
            self.session.pause()
            guard()
            self.driver.key('E', 0.10)
        except UpgradeDeferred:
            return False
        hud = self.confirm(tower, level, {count}, timeout=ACTION_CONFIRM_SECONDS,
                           evidence=f'hardcore_{tower.tower_id}_level_{level}.jpg')
        self.levels[tower.tower_id] = level
        self.record(tower, 'upgrade', price, hud)
        return True

    def record(self, tower, operation, price, hud):
        self.completed += 1
        self.remember_upgrade_price(tower, hud)
        action = dict(action=operation, tower_id=tower.tower_id, tower=tower.tower_type,
                      level=hud.level, wave=hud.wave, price=price, cash=hud.cash,
                      tower_count=hud.tower_count, confirmed_actions=self.completed)
        append_jsonl(self.session.output / 'hardcore_actions.jsonl', action)
        self.session.status('hardcore_action', **action)

    def remember_upgrade_price(self, tower, hud):
        if hud.tower_name == tower.tower_type and hud.level is not None and hud.upgrade_cost is not None:
            self.upgrade_costs[tower.tower_type, hud.level] = hud.upgrade_cost

    def next_purchase(self, pending, frame, cash):
        hotbar = {}

        def price(action, current):
            tower = self.towers[action.tower_id]
            if action.operation == 'upgrade':
                return self.upgrade_costs.get((tower.tower_type, current))
            if tower.slot not in hotbar:
                hotbar[tower.slot] = wretched_price(frame, tower.slot, self.ocr)
            return hotbar[tower.slot]

        return affordable_purchase(pending, self.levels, price, cash)

    def play(self):
        self.start()
        pending = [(stage, action) for stage in self.plan.stages[1:] for action in stage.actions
                   if not self.towers[action.tower_id].optional]
        checks = [(stage, check) for stage in self.plan.stages for check in stage.checks]
        deadline = self.session.now() + 45 * 60
        while self.session.now() < deadline:
            self.session.pause(self.frame)
            if self.last_wave >= self.plan.finish_wave:
                frame = self.frame()
                self.observe_wave(read_hardcore_wave(frame, self.ocr), frame)
                self.driver.wait(.35)
                continue
            frame, hud = self.read({len(self.levels)})
            wave = hud.wave
            if checks and wave >= checks[0][0].first_wave:
                stage, check = checks[0]
                if wave > stage.last_wave:
                    raise StopRun('Required confirmed Farm levels were missing in the wave 14–15 window.')
                if not pending or pending[0][0].first_wave > stage.last_wave:
                    if any(self.levels.get(tower_id) != check.level for tower_id in check.tower_ids):
                        raise StopRun('Required confirmed Farm levels were missing in the wave 14–15 window.')
                    checks.pop(0)
                    self.session.status('hardcore_tower_levels_verified', wave=wave,
                                        tower_ids=list(check.tower_ids), level=check.level)
            while pending and pending[0][1].optional and wave > pending[0][0].last_wave:
                pending.pop(0)
            if pending and wave > pending[0][0].last_wave:
                _, expired = pending[0]
                raise StopRun(f'Wave {wave} passed the deadline for {expired.operation} {expired.tower_id}.')
            index = self.next_purchase(pending, frame, hud.cash)
            if index is not None:
                stage, action = pending[index]
                tower = self.towers[action.tower_id]
                done = (self.place(tower, stage) if action.operation == 'place'
                        else self.upgrade(tower, action.level, stage))
                if done:
                    pending.pop(index)
                    continue
            self.driver.wait(.3)
        raise StopRun('Timed out waiting for the natural Hardcore result.')

    def run(self):
        try:
            self.play()
        except MatchEnded as result:
            self.session.save_frame(result.frame, 'hardcore_result.png')
            target = self.target_observations >= self.min_target_observations
            self.session.status('hardcore_result_observed', result=result.state, wave=self.last_wave,
                                target_wave_verified=target, confirmed_actions=self.completed)
            return {'status': 'unverified_reward' if target else 'early_result', 'outcome': result.state,
                    'wave': self.last_wave, 'target_wave_verified': target, 'levels': self.levels,
                    'confirmed_actions': self.completed}


def farm_action_eligible(action, level):
    return level is None if action.operation == 'place' else level == action.level - 1


def farm_investment_fits(cost, gain, cash, income, defense_price, payouts_left,
                         *, defense_slack_payouts=0):
    """Buy a paying-back Farm without moving critical defense beyond its deadline.

    Only verified Farm payouts count toward the conservative cost ETA. Spending
    may shift a defense by a payout if that payout still precedes its deadline.
    """
    if cost > cash or gain * payouts_left <= cost:
        return False
    if defense_price is None:
        return True
    if income <= 0:
        return False
    before = (max(0, defense_price - cash) + income - 1) // income
    income_after = income + gain
    after = (max(0, defense_price - cash + cost) + income_after - 1) // income_after
    return after <= before or (defense_slack_payouts > 0 and after <= defense_slack_payouts)


def v2_phase_purchase(actions, levels, tower_type, price_for, cash, *, highest_upgrade_first=()):
    """Preserve defense order and apply the appropriate Farm purchase priority."""
    if not actions:
        return None
    # The early Boomerang sequence includes F4's upgrade as a dependency. Keep
    # this mixed block and later combat phases in their specified order.
    if any(tower_type(action) != 'Farm' for action in actions):
        action = actions[0]
        cost = price_for(action, levels.get(action.tower_id))
        return 0 if cost is None or cost <= cash else None

    affordable = []
    unread = None
    for index, action in enumerate(actions):
        current = levels.get(action.tower_id)
        placing = action.operation == 'place'
        if not farm_action_eligible(action, current):
            continue
        cost = price_for(action, current)
        if cost is None:
            if unread is None:
                unread = index
        elif cost <= cash:
            prefer_upgrade = not placing and action.tower_id in highest_upgrade_first
            affordable.append((not prefer_upgrade, -cost if prefer_upgrade else cost, index))
    return min(affordable)[2] if affordable else unread


class HardcoreMatchV2(HardcoreMatch):
    """The v2 phase order has prerequisites and budgets, without purchase-unlock waves."""
    def __init__(self, session):
        super().__init__(session)
        self.plan_actions = {(action.tower_id, action.level or 0): action
                             for phase in self.plan.phases for action in phase.actions}
        self.later_farm_actions = tuple(
            (phase.step, action) for phase in self.plan.phases for action in phase.actions
            if action.tower_id in self.plan.highest_upgrade_first)
        self.missed_defense_deadlines = set()
        self.optional_tower = getattr(session, 'hardcore_optional_tower', None)
        if self.optional_tower:
            self.towers['X1'] = replace(self.towers['X1'], tower_type=self.optional_tower)
            self.reader.tower_names.add(self.optional_tower)
            # Current 2.20.0 back-path landscape: X1 is away from both fixed
            # combat and Farm clusters. Its runtime preview MUST be green and
            # show Place; the candidate coordinate is not acceptance evidence.
            self.camera.points['X1'] = (840, 330)

    def v2_price_for(self, frame):
        placements = {}

        def price(action, level):
            tower = self.towers[action.tower_id]
            if action.operation == 'upgrade':
                return self.upgrade_costs.get((tower.tower_type, level))
            if tower.slot not in placements:
                placements[tower.slot] = wretched_price(frame, tower.slot, self.ocr)
            return placements[tower.slot]

        return price

    def execution_phases(self):
        # Always complete the 75 required purchases before spending on XP.
        # The optional placement must not delay the last Crook Boss upgrades.
        required, optional = [], []
        for phase in self.plan.phases[1:]:
            (optional if all(action.optional for action in phase.actions) else required).append(phase)
        return tuple(required + (optional if self.optional_tower else []))

    def play(self):
        self.start(self.plan.phases[0])
        deadline = self.session.now() + 45 * 60
        try:
            for phase in self.execution_phases():
                self.play_phase(phase, deadline)
        except TargetWaveReached:
            self.session.status('hardcore_finish_before_all_actions', wave=self.last_wave,
                                confirmed_actions=self.completed)
        while self.session.now() < deadline:
            self.session.pause(self.frame)
            frame = self.frame()
            self.observe_wave(read_hardcore_wave(frame, self.ocr), frame)
            self.driver.wait(.35)
        raise StopRun('Timed out waiting for the natural Hardcore result.')

    def completed_action(self, action):
        level = self.levels.get(action.tower_id)
        return level is not None and level >= (action.level or 0)

    def urgent_defense(self, wave, price_for, cash):
        for due, lead, milestones in DEFENSE_DEADLINES:
            missing = [(tower_id, level) for tower_id, level in milestones
                       if self.levels.get(tower_id, -1) < level]
            if not missing:
                continue
            if wave >= due - lead:
                candidates = [(due, self.plan_actions[tower_id, self.levels.get(tower_id, -1) + 1])
                              for tower_id, _ in missing]
                choice = affordable_purchase(candidates, self.levels, price_for, cash)
                if choice is None:
                    quote = min(price_for(purchase, self.levels.get(purchase.tower_id))
                                for _, purchase in candidates)
                    return due, None, quote
                action = candidates[choice][1]
                return due, action, price_for(action, self.levels.get(action.tower_id))
        return None, None, None

    def crook_upgrade_priority(self, price_for, cash):
        for tower_id, level in self.levels.items():
            if (not self.towers[tower_id].optional
                    and self.towers[tower_id].tower_type == 'Crook Boss'
                    and level < self.plan.crook_level_before_next_purchase):
                action = self.plan_actions[tower_id, level + 1]
                price = price_for(action, level)
                return True, action if price is None or price <= cash else None
        return False, None

    def farm_economy_purchase(self, wave, cash, price_for, defense_price, phase_step,
                              *, defense_slack_payouts=0):
        # Only Farm actions in reached phases may be purchased; never jump from
        # phase 6 to F9/F10 before C2's required preceding phase.
        if self.levels.get('B1', -1) < 3 or self.levels.get('C1', -1) < 2:
            return None
        payouts = self.plan.farm_payout_by_level
        income = sum(payouts[level] for tower_id, level in self.levels.items()
                     if self.towers[tower_id].tower_type == 'Farm')
        payouts_left = self.plan.finish_wave - wave - 1
        choices = []
        for index, (available_phase, action) in enumerate(self.later_farm_actions):
            if available_phase > phase_step:
                continue
            current = self.levels.get(action.tower_id)
            if not farm_action_eligible(action, current):
                continue
            price = price_for(action, current)
            gain = payouts[0] if current is None else payouts[action.level] - payouts[current]
            if price is not None and farm_investment_fits(
                    price, gain, cash, income, defense_price, payouts_left,
                    defense_slack_payouts=defense_slack_payouts):
                choices.append((action.operation == 'place', -price, index))
        return self.later_farm_actions[min(choices)[2]][1] if choices else None

    def play_phase(self, phase, deadline):
        actions = list(phase.actions)
        self.session.status('hardcore_purchase_phase', step=phase.step)
        if actions and actions[0].optional and (not self.optional_tower or 'X1' not in self.camera.points):
            self.session.status('hardcore_optional_skipped', step=phase.step, reason='tower_or_point_unverified')
            return
        while actions and self.session.now() < deadline:
            actions = [action for action in actions if not self.completed_action(action)]
            if not actions:
                break
            self.session.pause(self.frame)
            frame, hud = self.read({len(self.levels)}, self.plan.finish_wave - 1)
            price_for = self.v2_price_for(frame)
            due, action, defense_price = self.urgent_defense(hud.wave, price_for, hud.cash)
            if due is not None and hud.wave > due and due not in self.missed_defense_deadlines:
                self.missed_defense_deadlines.add(due)
                event = dict(step=phase.step, wave=hud.wave, deadline_wave=due, cash=hud.cash)
                append_jsonl(self.session.output / 'hardcore_defense.jsonl', event)
                self.session.status('hardcore_defense_overdue', **event)
            crook_first, crook_action = self.crook_upgrade_priority(price_for, hud.cash)
            economy = None
            # Reevaluate Farm return after every confirmed action. A future
            # deadline can permit a one-payout investment only if the new
            # defense ETA remains strictly ahead of that deadline. Never
            # postpone an already affordable overdue defense or an unknown
            # critical quote; placed Crooks still take both L2 upgrades first.
            if (not crook_first and phase.step >= 6 and
                    (due is None or defense_price is not None) and
                    not (action is not None and due is not None and hud.wave >= due)):
                slack = max(0, due - hud.wave - 1) if due is not None else 0
                economy = self.farm_economy_purchase(
                    hud.wave, hud.cash, price_for, defense_price, phase.step,
                    defense_slack_payouts=slack)
            if crook_first:
                action = crook_action
                if action is not None:
                    self.session.status('hardcore_crook_priority', step=phase.step,
                                        tower_id=action.tower_id, wave=hud.wave, level=action.level)
            elif economy is not None:
                action = economy
                self.session.status('hardcore_farm_budget', step=phase.step, wave=hud.wave,
                                    tower_id=action.tower_id, protected_defense_price=defense_price)
            elif due is None:
                index = v2_phase_purchase(actions, self.levels,
                                          lambda action: self.towers[action.tower_id].tower_type,
                                          price_for, hud.cash,
                                          highest_upgrade_first=self.plan.highest_upgrade_first)
                action = actions[index] if index is not None else None
            elif action is not None:
                self.session.status('hardcore_defense_priority', step=phase.step,
                                    tower_id=action.tower_id, wave=hud.wave, deadline_wave=due)
            if action is not None:
                tower = self.towers[action.tower_id]
                latest = self.plan.finish_wave - 1
                finished = (self.place(tower, latest) if action.operation == 'place'
                            else self.upgrade(tower, action.level, latest))
                if finished:
                    continue
            if actions[0].optional and not crook_first:
                self.session.status('hardcore_optional_skipped', step=phase.step, reason='price_or_cash_unverified')
                return
            self.driver.wait(.3)
        if actions:
            raise StopRun(f'Timed out waiting for required actions in Hardcore phase {phase.step}.')
        self.session.status('hardcore_phase_complete', step=phase.step, wave=self.last_wave,
                            confirmed_actions=self.completed)

    def run(self):
        result = super().run()
        result['missed_defense_deadlines'] = sorted(self.missed_defense_deadlines)
        result['required_levels_verified'] = all(
            self.levels.get(tower_id) == level for tower_id, level in dict(self.plan.final_required_levels).items()
        )
        result['optional_xp_tower'] = self.optional_tower
        result['optional_tower_placed'] = (self.levels.get('X1') == 0) if self.optional_tower else None
        deadline = self.session.now() + RESULT_CONFIRM_SECONDS
        previous = None
        while self.session.now() < deadline:
            self.session.pause()
            frame = self.session.frame(record_latest=False)
            receipt = read_hardcore_result(frame, self.session.observer, self.ocr)
            if receipt is not None and receipt == previous:
                self.session.save_frame(frame, 'hardcore_result_confirmed.png')
                result.update(outcome=receipt.status, result_wave=receipt.wave,
                              displayed_gems=receipt.displayed_gems, match_seconds=receipt.duration_seconds)
                if receipt.wave != self.plan.finish_wave:
                    result['status'] = ('early_result' if receipt.wave < self.plan.finish_wave
                                        else 'late_result')
                elif (result['target_wave_verified'] and result['required_levels_verified']
                      and receipt.displayed_gems == 137 and receipt.status == 'defeat'):
                    result['status'] = ('result_verified' if
                                        self.optional_tower is None or result['optional_tower_placed']
                                        else 'optional_tower_not_placed')
                return result
            previous = receipt
            self.driver.wait(.4)
        return result
