"""Explicitly started, bounded Golden Scout lobby-to-result session.

F8/Escape or a stop marker stops inside input holds. Pause is honored only
between atomic actions; Roblox keeps simulating while the macro is paused.
"""
from __future__ import annotations
import argparse
import os
import json
import time
import shutil
from dataclasses import asdict
from pathlib import Path
from PIL import ImageStat
from .calibration import CameraGate,load_profile
from .control import GuardedInput,StopRun,WindowsOS
from .hotbar import read_hotbar
from .loadout import verify_inventory
from .maps import read_boards,find_target,read_headers,visible_target,vip_target_matches,vote_prompt,badge_is_one,spawn_board_row,voting_floor,_vip_prompt_evidence
from .navigation import Navigator,MENU_ROUTE
from .observer import Observer
from .phase1 import capture,locate_roblox,BlankCapture
from .resources import LocalOCR,HudReader,parse_cash
from .run import Playback,ROOT
from .recording import append_jsonl,write_json
from .timing import READ_SECONDS, TELEPORT_SECONDS


class SessionControl:
    def __init__(self,path,context=None):
        self.path=Path(path)
        self.context=context if context is not None else {}
    def stopped(self):
        return (self.path/'stop').exists()
    def paused(self):
        return (self.path/'pause').exists()
    def write(self,data):
        # Atomic replace so status readers never consume partially written JSON.
        temporary=self.path/'status.tmp'
        try:
            temporary.write_text(json.dumps({**data,**self.context},indent=2),encoding='utf-8')
            for attempt in range(5):
                try:
                    temporary.replace(self.path/'status.json')
                    return
                except PermissionError as exc:
                    # Windows readers can briefly deny delete sharing. Retry only
                    # the atomic file replacement, never a confirmed game action.
                    if getattr(exc,'winerror',None) not in {5,32} or attempt==4:
                        raise
                    time.sleep(.025)
        except OSError as exc:
            raise StopRun(f'Cannot write status file ({type(exc).__name__}).',kind='storage') from exc


class Session:
    LOGIN_CAPTION_BOX=(910,773,1010,806)
    # Right padding avoids both the caption and the avatar profile tooltip.
    LOGIN_CLAIM_POINT=(1045,787)

    def __init__(self,driver,output,profile_path=None,read_frame=None,now=time.monotonic,control=None,totals=None):
        self.driver=driver
        self.output=Path(output)
        self.control=control if control is not None else SessionControl(output)
        self.driver.external_stop=self.control.stopped
        self.profile_path=Path(profile_path or ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
        self.profile,self.strategy=load_profile(self.profile_path)
        self.observer=Observer()
        self.ocr=LocalOCR()
        self.now=now
        self.capture=read_frame or (lambda:capture(driver.expected))
        self.navigator=Navigator(self.observer,driver,self.frame,sleep=driver.wait)
        self.started=self.now()
        self.phase='starting'
        self.allowed=set()
        self.driver.before_click=self.click_gate
        self.board_index=None
        self.totals=totals if totals is not None else {"attempts":0,"matches_completed":0,"wins":0,"coins_total":0}

    def frame(self,*,record_latest=True):
        self.driver.check()
        frame=self.capture()
        if record_latest:
            self.save_frame(frame,'latest.png')
        return frame

    def save_frame(self,frame,name):
        try:frame.save(self.output/name,compress_level=1)
        except OSError as exc:
            raise StopRun(f'Cannot save session evidence ({name}): {exc}',kind='storage') from exc

    def _login_caption(self,frame):
        """Read the shared Claim/Close control; absent text stays uncertain."""
        button=frame.crop(self.LOGIN_CAPTION_BOX).convert('RGB')
        text=self.ocr.read(button).strip().casefold()
        if text=='claim':
            red,green,blue=ImageStat.Stat(button).mean
            if not (green>150 and green>red*1.1 and green>blue*1.1):
                return None
        return text if text in {'claim','close'} else None

    def _login_click_gate(self,caption):
        frame=self.frame()
        if self.observer.observe(frame).state!='login_rewards' or self._login_caption(frame)!=caption:
            raise StopRun(caption.capitalize()+' label changed before the guarded click.')

    def status(self,phase,**detail):
        self.phase=phase
        data={'phase':phase,'runner_pid':os.getpid(),'elapsed_seconds':round(self.now()-self.started,1),**self.totals,**detail}
        self.control.write(data)
        print(json.dumps(data),flush=True)

    def click_gate(self):
        deadline=self.now()+READ_SECONDS
        state=self.observer.observe(self.frame()).state
        while state=='unknown' and self.now()<deadline:
            self.driver.wait(.15)
            state=self.observer.observe(self.frame()).state
        if state not in self.allowed:
            raise StopRun(f'Click precondition changed: {state}; expected {sorted(self.allowed)}.')

    def pause(self,read=None):
        if not self.control.paused():
            return
        previous=self.phase
        self.status('paused',resume_phase=previous,note='Game time continues; no keys/buttons held.')
        deadline=self.now()+300
        while self.control.paused():
            self.driver.check()
            if self.now()>=deadline:
                raise StopRun('Pause exceeded five minutes; stopped without further input.',kind='user_stop')
            if read:
                read()  # Result/focus/view validation remains active while paused.
            self.driver.wait(.2)
        self.status(previous,resumed=True)

    def wait_state(self,target,timeout=45,allowed=()):
        deadline=self.now()+timeout
        stable=0
        while self.now()<deadline:
            try:
                state=self.observer.observe(self.frame()).state
            except BlankCapture:
                if 'loading' not in allowed:
                    raise
                stable=0
                self.driver.wait(.2)
                continue
            stable=stable+1 if state==target else 0
            if stable>=2:
                return
            if state not in {target,'unknown',*allowed}:
                raise StopRun(f'Unexpected state waiting for {target}: {state}.')
            self.driver.wait(.2)
        raise StopRun(f'Timed out waiting for {target}; no input retry.')

    def transition(self,name):
        from .navigation import TRANSITIONS
        self.pause()
        self.allowed={TRANSITIONS[name][0]}
        self.status(name)
        return self.navigator.step(name,timeout=TELEPORT_SECONDS if name in {'solo','return_victory','play_again','restart_match'} else 45)

    def lobby(self):
        self.status('lobby_popup_check')
        # A login overlay can arrive after the first lobby frame.
        deadline=self.now()+8
        stable_since=None
        dismissed=False
        claim_seen=0
        close_seen=0
        claimed=False
        while self.now()<deadline:
            frame=self.frame()
            state=self.observer.observe(frame).state
            if state=='login_rewards':
                stable_since=None
                caption=self._login_caption(frame)
                if caption=='claim' and not claimed:
                    close_seen=0
                    claim_seen+=1
                    if claim_seen>=2:
                        self.allowed={'login_rewards'}
                        self.status('login_reward_claim_confirmed')
                        guarded_before_click=self.driver.before_click
                        def claim_before_click():
                            self._login_click_gate('claim')
                        self.driver.before_click=claim_before_click
                        try:
                            self.driver.click(*self.LOGIN_CLAIM_POINT)
                        finally:
                            self.driver.before_click=guarded_before_click
                        self.allowed=set()
                        claimed=True
                        # Claim may need the rest of the popup animation, so the
                        # original lobby bound can reset exactly once after it.
                        deadline=self.now()+8
                        stable_since=None
                elif caption=='close' and not dismissed:
                    claim_seen=0
                    close_seen+=1
                    if close_seen>=2:
                        guarded_before_click=self.driver.before_click
                        self.driver.before_click=lambda:self._login_click_gate('close')
                        try:self.transition('dismiss_login')
                        finally:self.driver.before_click=guarded_before_click
                        dismissed=True
                    stable_since=None
                else:
                    # Claim is still animating, or the control is unreadable.
                    # Absence of Claim never becomes a Close inference.
                    stable_since=None
                    claim_seen=close_seen=0
            elif state=='lobby':
                claim_seen=close_seen=0
                if stable_since is None:
                    stable_since=self.now()
                if self.now()-stable_since>=2:
                    return
            elif state not in {'unknown','loading'}:
                raise StopRun(f'Expected lobby/login rewards; saw {state}.')
            else:
                stable_since=None
                claim_seen=close_seen=0
            self.driver.wait(.2)
        raise StopRun('Lobby did not settle: the login reward action did not settle or its caption was unreadable.')

    def wait_for_afk_disconnect(self,seconds):
        """Passively watch a stable TDS lobby for Roblox's exact AFK disconnect dialog."""
        if type(seconds) is not int or not 1200<=seconds<=1800:
            raise StopRun('AFK lobby monitoring is bounded to 1200..1800 seconds.',kind='setup')
        stable_lobby=0
        lobby_deadline=self.now()+60
        while self.now()<lobby_deadline:
            if self.control.paused():
                raise StopRun('Pause requested during the no-input AFK lobby check.',kind='user_stop')
            frame=self.frame(record_latest=False)
            state=self.observer.observe(frame).state
            if state=='lobby':
                stable_lobby+=1
                if stable_lobby>=2:
                    if self.control.paused():
                        raise StopRun('Pause requested during the no-input AFK lobby check.',kind='user_stop')
                    break
            elif state in {'unknown','loading'}:
                stable_lobby=0
            else:
                raise StopRun(f'AFK lobby check requires a stable TDS lobby; saw {state}.',kind='setup')
            self.driver.wait(.2)
        else:
            raise StopRun('AFK lobby check could not confirm two stable TDS lobby reads.',kind='setup')

        started=self.now()
        deadline=started+seconds
        next_heartbeat=started+30
        stable_disconnect=0
        uncertain_since=None
        unverified_disconnect_since=None
        self.status('idle_lobby_monitor_started',idle_requested_seconds=seconds,
                    capture_interval_seconds=1,no_game_input=True,stable_lobby_reads=stable_lobby)
        while self.now()<deadline or stable_disconnect>0 or unverified_disconnect_since is not None:
            if self.control.paused():
                raise StopRun('Pause requested during the no-input AFK lobby check.',kind='user_stop')
            remaining=max(0.0,deadline-self.now())
            self.driver.wait(min(1.0,remaining) if remaining>0 else .2)
            if self.control.paused():
                raise StopRun('Pause requested during the no-input AFK lobby check.',kind='user_stop')
            frame=self.frame(record_latest=False)
            state=self.observer.observe(frame).state
            elapsed=round(self.now()-started,1)
            if state=='disconnect':
                from .recovery import disconnect_prompt
                if not disconnect_prompt(frame):
                    stable_disconnect=0
                    if unverified_disconnect_since is None:
                        unverified_disconnect_since=self.now()
                    elif self.now()-unverified_disconnect_since>8:
                        self.save_frame(frame,'idle_disconnect_unverified.png')
                        self.status('idle_disconnect_unverified',idle_elapsed_seconds=elapsed,no_game_input=True)
                        raise StopRun('Disconnect screen did not show the exact Disconnected, Leave and Reconnect labels; no recovery input sent.',kind='setup')
                else:
                    stable_disconnect+=1
                    uncertain_since=None
                    unverified_disconnect_since=None
                    if stable_disconnect>=2:
                        self.save_frame(frame,'idle_disconnect_confirmed.png')
                        self.control.context['idle_lobby_disconnect_confirmed']=True
                        self.status('idle_disconnect_confirmed',idle_elapsed_seconds=elapsed,
                                    stable_disconnect_reads=stable_disconnect,no_game_input=True)
                        raise StopRun('Stable natural Roblox disconnect observed during no-input TDS lobby idle.',kind='failure')
            elif state=='lobby':
                stable_disconnect=0
                uncertain_since=None
                unverified_disconnect_since=None
            elif state in {'unknown','loading'}:
                stable_disconnect=0
                unverified_disconnect_since=None
                if uncertain_since is None:
                    uncertain_since=self.now()
                elif self.now()-uncertain_since>15:
                    self.save_frame(frame,'idle_lobby_state_unverified.png')
                    self.status('idle_lobby_state_unverified',state=state,idle_elapsed_seconds=elapsed,no_game_input=True)
                    raise StopRun('TDS lobby state remained unreadable for 15 seconds during AFK monitoring.',kind='setup')
            else:
                self.save_frame(frame,'idle_lobby_interrupted.png')
                self.status('idle_lobby_interrupted',state=state,idle_elapsed_seconds=elapsed,no_game_input=True)
                raise StopRun(f'TDS left the lobby during the no-input AFK check (state={state}); recovery was not started.',kind='setup')
            if self.now()>=next_heartbeat:
                self.status('idle_lobby_monitoring',idle_elapsed_seconds=elapsed,
                            idle_remaining_seconds=max(0,round(deadline-self.now())),no_game_input=True)
                next_heartbeat=self.now()+30
        self.control.context['idle_lobby_monitor_completed']=True
        self.status('idle_lobby_monitor_complete',idle_observed_seconds=round(self.now()-started,1),
                    disconnect_observed=False,no_game_input=True)

    def preflight(self):
        self.lobby()
        inventory=self.transition('open_inventory')
        if inventory=='inventory_list':
            self.transition('scout_details')
        deadline=self.now()+5
        stable=0
        while self.now()<deadline:
            frame=self.frame()
            stable=stable+1 if verify_inventory(frame) is None else 0
            if stable>=2:
                self.save_frame(frame,'loadout_identity.png')
                break
            self.driver.wait(.2)
        else:
            raise StopRun('Equipped Scout/Golden label/slot-1 perk not confirmed; skin portraits are not checked.',kind='setup')
        self.transition('close_inventory')
        self.lobby()
        for name in MENU_ROUTE:
            self.transition(name)
        bar=read_hotbar(self.frame(),slot=1)
        if not bar.valid or bar.price is None:
            raise StopRun('Require Scout in slot 1 and no tower prices in slots 2..5.',kind='setup')
        self.status('loadout_verified',placement_price=bar.price)

    def boards(self,timeout=4):
        deadline=self.now()+timeout
        while self.now()<deadline:
            frame=self.frame()
            if self.observer.observe(frame).state!='map_vote':
                raise StopRun('Map vote screen changed while reading boards.')
            boards=read_boards(frame)
            if len(boards)==4:
                return boards
            self.driver.wait(.2)
        raise StopRun('All four board headers were not readable; no board index guessed.')

    def face_boards(self):
        self.status('voting_camera')
        stable=0
        coarse=alignment=0
        for index in range(34):  # 24 search turns, 8 alignment turns, 2 confirmations.
            self.pause()
            frame=self.frame()
            if self.observer.observe(frame).state!='map_vote':
                raise StopRun('Map-vote state changed during the board-row camera search.')
            if index==0:
                self.save_frame(frame,'voting_spawn.png')
            row=spawn_board_row(frame)
            if row and 975<=row[0]<=1005 and 285<=row[1]<=330:
                stable+=1
                if stable>=2:
                    self.save_frame(frame,'voting_aligned.png')
                    self.status('voting_camera_verified',coarse_turns=coarse,alignment_turns=alignment,row_center=row)
                    return
                self.driver.wait(.2)
                continue
            stable=0
            if row:
                if alignment>=8:
                    break
                alignment+=1
                # Live 40px drag moved the row 36.75px; correct half the error.
                dx=max(-120,min(120,round((row[0]-990)*.5)))
                dy=max(-45,min(45,round((row[1]-307)*.5)))
                self.driver.orbit(dx,dy)
            else:
                if coarse>=24:
                    break
                coarse+=1
                self.driver.orbit(120,0)
            self.driver.wait(.2)
        raise StopRun('Distant board row was not verified; no walking or vote sent.')

    def approach_vip(self):
        steps=stable=observations=0
        evidence={'confirmed':False,'keycap_score':None,'literal_caption':False}
        for index in range(16):
            self.pause()
            frame=self.frame()
            self.save_frame(frame,f'vip_step_{index:02}.png')
            if self.observer.observe(frame).state!='map_vote':
                raise StopRun('Map-vote state changed while approaching VIP.')
            evidence=_vip_prompt_evidence(frame)
            observations+=1
            if evidence['confirmed']:
                stable+=1
                if stable>=2:
                    return steps*.15
            else:
                stable=0
                if steps>=12:
                    break
                self.driver.key('D',.15)
                steps+=1
            self.driver.wait(.2)
        self.status('vip_prompt_unconfirmed',physical_board=self.board_index,target_recognized=None,
                    badge_read=False,badge_count=None,keycap_score=evidence['keycap_score'],
                    literal_caption=evidence['literal_caption'],observation_count=observations,
                    steps=steps,stable_reads=stable)
        score='unknown' if evidence['keycap_score'] is None else f"{evidence['keycap_score']:.5f}"
        caption='yes' if evidence['literal_caption'] else 'no'
        raise StopRun(f'VIP proximity prompt was not confirmed (stage=vip_prompt, physical_board={self.board_index}, '
                      f'keycap_score={score}, literal_caption={caption}, observations={observations}, '
                      f'D_steps={steps}, stable_reads={stable}); no E or further walking sent.')

    def choose_map(self):
        self.allowed={'map_vote'}
        frame=self.frame()
        if self.observer.observe(frame).state!='map_vote':
            raise StopRun('Map-vote entry is not confirmed.')
        self.face_boards()
        self.status('read_four_boards')
        # Stop before the near-board perspective clips the outer header.
        # Live recovery of that view verified all four after a 0.5 s backstep.
        self.driver.key('W',2.8)
        self.driver.wait(.3)
        boards=self.boards()
        target=find_target(boards)
        if target is None:
            self.status('vip_map_selection')
            # Return to the spawn reference before the independently observed VIP route.
            self.driver.key('S',2.8)
            self.driver.key('W',1.9)
            self.save_frame(self.frame(),'vip_before_sidewalk.png')
            sideways=self.approach_vip()
            self.save_frame(self.frame(),'vip_machine_approach.png')
            self.driver.key('E',.8)
            self.wait_state('vip_maps',10,{'map_vote'})
            self.allowed={'vip_maps'}
            self.driver.click(946,231)
            self.driver.select_all()
            self.driver.text('dead ahead')
            self.driver.move(694,418)  # Lower card padding leaves the title clear.
            self.driver.wait(.4)
            deadline=self.now()+3
            stable=0
            while self.now()<deadline:
                stable=stable+1 if vip_target_matches(self.frame()) else 0
                if stable>=2:
                    break
                self.driver.wait(.15)
            else:
                raise StopRun('VIP search and matching card text were not confirmed.')
            self.driver.click(694,418)
            self.wait_state('map_vote',10,{'vip_maps'})
            self.allowed={'map_vote'}
            if sideways:
                self.driver.key('A',sideways)
            self.driver.key('W',.9)
            self.driver.wait(.3)
            self.save_frame(self.frame(),'vip_return.png')
            boards=self.boards()
            target=find_target(boards)
            if target is None:
                raise StopRun('VIP choice did not leave Dead Ahead on any readable board.')
        self.vote_target(target)

    def vote_target(self,target):
        self.board_index=target.index
        self.save_frame(self.frame(),f'boards_target{target.index}.png')
        self.status('walk_to_target',physical_board=target.index,title=target.title)
        frame,current=self.approach_target()
        self.save_frame(frame,'before_vote.png')
        self.driver.key('E',.8)
        self.driver.key('S',.15)  # Turn clear of the avatar occlusion without leaving the verified floor.
        self.driver.wait(.3)
        frame=self.frame()
        self.save_frame(frame,'after_vote.png')
        deadline=self.now()+2
        reread=False
        observations=0
        title_diagnostics={}
        while True:
            title_diagnostics={}
            if self.observer.observe(frame).state!='map_vote':
                if reread:self.save_frame(frame,'latest.png')
                self.status('post_vote_state_changed',physical_board=self.board_index,target_recognized=None,
                            badge_read=False,badge_count=None,title_observations=observations,view_clear_steps=0,
                            title_header_count=0,title_tokens=[])
                raise StopRun(f'Map-vote state changed after voting (stage=post_vote_title, physical_board={self.board_index}, '
                              f'title=unverified, badge=not_read, observations={observations}); Ready was not clicked.')
            current=visible_target(frame,after_vote=True,diagnostics=title_diagnostics)
            observations+=1
            if current is not None:
                break
            if self.now()>=deadline:
                break
            self.pause()
            self.driver.wait(.2)
            frame=self.frame(record_latest=False)
            reread=True
        if reread:self.save_frame(frame,'latest.png')
        if current is None:
            self.status('post_vote_title_unconfirmed',physical_board=self.board_index,target_recognized=False,
                        badge_read=False,badge_count=None,title_observations=observations,view_clear_steps=0,
                        title_header_count=title_diagnostics.get('header_count',0),
                        title_tokens=title_diagnostics.get('title_tokens',[]))
            tokens=','.join(title_diagnostics.get('title_tokens',[])) or 'none'
            raise StopRun(f'Target identity was lost after voting (stage=post_vote_title, physical_board={self.board_index}, '
                          f'title=unreadable, title_tokens={tokens}, headers={title_diagnostics.get("header_count",0)}, '
                          f'badge=not_read, observations={observations}); Ready was not clicked.')
        # The target's red vote badge sits beneath the header. Read the badge
        # nearest this verified title; thumbnails/reward numbers are excluded.
        count=self.vote_count(frame,current)
        view_clear_steps=0
        forward_correction_steps=0
        if count is None:
            # The fixed avatar/head can hide a world-space badge after backing
            # away. Recover a marginal floor only by moving forward; lateral
            # view clearing still requires the original two-sided margin.
            if self.observer.observe(frame).state!='map_vote':
                self.status('post_vote_state_changed',physical_board=self.board_index,target_recognized=True,
                            badge_read=False,badge_count=None,title_observations=observations,view_clear_steps=0,
                            title_header_count=title_diagnostics.get('header_count',0),
                            title_tokens=title_diagnostics.get('title_tokens',[]))
                raise StopRun(f'Map-vote state changed before checking the vote badge (stage=post_vote_badge, '
                              f'physical_board={self.board_index}, title=confirmed, badge=not_read); Ready was not clicked.')
            can_strafe=voting_floor(frame,for_strafe=True)
            if not can_strafe and voting_floor(frame,require_both=False):
                self.status('vote_badge_forward_correction',physical_board=self.board_index,target_recognized=True,
                            badge_read=False,badge_count=None,title_observations=observations,view_clear_steps=0,
                            forward_correction_steps=1,title_header_count=title_diagnostics.get('header_count',0),
                            title_tokens=title_diagnostics.get('title_tokens',[]))
                self.driver.key('W',.10)
                forward_correction_steps=1
                self.driver.wait(.2)
                frame=self.frame(record_latest=False)
                if self.observer.observe(frame).state!='map_vote':
                    self.status('post_vote_state_changed',physical_board=self.board_index,target_recognized=None,
                                badge_read=False,badge_count=None,title_observations=observations,view_clear_steps=0,
                                forward_correction_steps=forward_correction_steps,
                                title_header_count=0,title_tokens=[])
                    raise StopRun('Map-vote state changed during the guarded forward floor correction; '
                                  'no view adjustment or Ready click.')
                self.save_frame(frame,'after_vote_forward_correction.png')
                title_diagnostics={}
                current=visible_target(frame,after_vote=True,diagnostics=title_diagnostics)
                observations+=1
                if current is None:
                    self.status('post_vote_title_unconfirmed',physical_board=self.board_index,target_recognized=False,
                                badge_read=False,badge_count=None,title_observations=observations,view_clear_steps=0,
                                forward_correction_steps=forward_correction_steps,
                                title_header_count=title_diagnostics.get('header_count',0),
                                title_tokens=title_diagnostics.get('title_tokens',[]))
                    tokens=','.join(title_diagnostics.get('title_tokens',[])) or 'none'
                    raise StopRun(f'Target identity was lost after the guarded forward correction '
                                  f'(stage=post_vote_title, physical_board={self.board_index}, '
                                  f'title_tokens={tokens}); Ready was not clicked.')
                count=self.vote_count(frame,current)
                if count is None:
                    can_strafe=voting_floor(frame,for_strafe=True)
            if count is None and not can_strafe:
                self.status('post_vote_view_clear_blocked',physical_board=self.board_index,target_recognized=True,
                            badge_read=False,badge_count=None,title_observations=observations,view_clear_steps=0,
                            forward_correction_steps=forward_correction_steps,
                            title_header_count=title_diagnostics.get('header_count',0),
                            title_tokens=title_diagnostics.get('title_tokens',[]))
                raise StopRun(f'Vote badge is unreadable and the voting-floor margin was not confirmed after '
                              f'{forward_correction_steps} forward correction steps '
                              f'(stage=post_vote_badge, physical_board={self.board_index}, '
                              f'title_tokens={",".join(title_diagnostics.get("title_tokens",[])) or "none"}, badge=unknown); '
                              'no view adjustment or Ready click.')
            if count is None:
                self.status('vote_badge_view_adjustment',physical_board=self.board_index,target_recognized=True,
                            badge_read=False,badge_count=None,title_observations=observations,view_clear_steps=0,
                            forward_correction_steps=forward_correction_steps,view_clear_planned_steps=1,
                            title_header_count=title_diagnostics.get('header_count',0),
                            title_tokens=title_diagnostics.get('title_tokens',[]))
                self.driver.key('D',.35)  # Open floor; left can climb the board-1 bench.
                view_clear_steps=1
                self.driver.wait(.2)
                frame=self.frame()
                if self.observer.observe(frame).state!='map_vote':
                    self.status('post_vote_state_changed',physical_board=self.board_index,target_recognized=None,
                                badge_read=False,badge_count=None,title_observations=observations,view_clear_steps=1,
                                forward_correction_steps=forward_correction_steps,
                                title_header_count=title_diagnostics.get('header_count',0),
                                title_tokens=title_diagnostics.get('title_tokens',[]))
                    raise StopRun(f'Map-vote state changed while clearing the vote badge (stage=post_vote_badge, '
                                  f'physical_board={self.board_index}, badge=not_read, view_clear_steps=1); '
                                  'Ready was not clicked.')
                self.save_frame(frame,'after_vote_clear.png')
                title_diagnostics={}
                current=visible_target(frame,after_vote=True,diagnostics=title_diagnostics)
                observations+=1
                count=self.vote_count(frame,current) if current is not None else None
        if count!=1:
            badge='unknown' if count is None else str(count)
            self.status('post_vote_badge_unconfirmed',physical_board=self.board_index,target_recognized=current is not None,
                        badge_read=count is not None,badge_count=count,title_observations=observations,view_clear_steps=view_clear_steps,
                        forward_correction_steps=forward_correction_steps,
                        title_header_count=title_diagnostics.get('header_count',0),
                        title_tokens=title_diagnostics.get('title_tokens',[]))
            raise StopRun(f'The verified target does not show one solo vote (stage=post_vote_badge, '
                          f'physical_board={self.board_index}, title={"confirmed" if current is not None else "unreadable"}, '
                          f'title_tokens={",".join(title_diagnostics.get("title_tokens",[])) or "none"}, '
                          f'badge={badge}, observations={observations}, view_clear_steps={view_clear_steps}, '
                          f'forward_correction_steps={forward_correction_steps}); '
                          'Ready was not clicked.')
        self.status('target_voted',physical_board=self.board_index,view_clear_steps=view_clear_steps,
                    forward_correction_steps=forward_correction_steps)
        self.driver.click(960,778)
        self.wait_state('match_ready',TELEPORT_SECONDS,{'map_vote','loading','in_match'})

    def approach_target(self):
        # Keep the physical board index from the original four-header view.
        # Movement is bounded and each step is followed by fresh visual feedback.
        reached_floor=False
        unreadable_since=None
        for index in range(22):
            self.pause()
            frame=self.frame()
            self.save_frame(frame,f'approach_{index:02}.png')
            if self.observer.observe(frame).state!='map_vote':
                raise StopRun('Map-vote state changed while approaching the target.')
            current=visible_target(frame)
            prompt=vote_prompt(frame,current)
            if current is None:
                if not prompt:
                    if unreadable_since is None:
                        unreadable_since=self.now()
                    if self.now()-unreadable_since>=READ_SECONDS:
                        raise StopRun('Lost the target title without a known Vote prompt; no further walking.')
                    self.driver.wait(.2)
                    continue
                self.driver.key('S',.12)  # A close header can be hidden by the fixed HUD.
            else:
                unreadable_since=None
                center=(current.box[0]+current.box[2])/2
                error=center-960
                on_floor=voting_floor(frame)
                if not on_floor:
                    if reached_floor and not voting_floor(frame,require_both=False):
                        raise StopRun('Lost the verified voting floor; no further walking toward decorations.')
                    self.driver.key('W',.10)
                    self.driver.wait(.2)
                    continue
                reached_floor=True
                if prompt and abs(error)<=140:
                    return frame,current
                width=current.box[2]-current.box[0]
                if width>400:
                    self.driver.key('S',.12)
                elif abs(error)>90:
                    if not voting_floor(frame,for_strafe=True):
                        self.driver.key('W',.10)
                    else:
                        self.driver.key('A' if error<0 else 'D',min(.20,max(.06,abs(error)/950)))
                else:
                    self.driver.key('W',.10)
            self.driver.wait(.2)
        raise StopRun('Target title and Vote proximity did not converge within bounded walking steps.')

    def vote_count(self,frame,target):
        import cv2
        import numpy as np
        center=(target.box[0]+target.box[2])/2
        expected_badge=center+(target.box[2]-target.box[0])*.35
        # Only 25..120px badges within 100px of this target can qualify.
        # The 190px margin retains the entire contour for every eligible badge.
        x1=max(0,int(expected_badge)-190)
        x2=min(frame.width,int(expected_badge)+191)
        if x2<=x1 or frame.height<650:
            return None
        pixels=np.asarray(frame.crop((x1,320,x2,650)).convert('RGB'),dtype=np.uint16)
        red,green,blue=(pixels[:,:,i] for i in range(3))
        # red*5 > green*6 is the exact integer version of red>green*1.2.
        mask=np.uint8((red>180)&(green>65)&(green<200)&(blue>65)&(blue<200)&(red*5>green*6))*255
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        candidates=[]
        for contour in contours:
            x,y,w,h=cv2.boundingRect(contour)
            # A clipped world/decoration contour must never become a fake badge.
            if x==0 or x+w==x2-x1:
                continue
            x+=x1;y+=320
            if 25<=w<=120 and 25<=h<=120 and .65<w/h<1.5 and abs(x+w/2-expected_badge)<100:
                value=parse_cash(self.ocr.read(frame.crop((x,y,x+w,y+h))))
                if value is None and badge_is_one(frame,(x,y,x+w,y+h)):
                    value=1
                if value is not None:
                    candidates.append((abs(x+w/2-expected_badge),value))
        candidates.sort()
        return candidates[0][1] if candidates else None

    def align_fresh_camera(self,gate):
        for attempt in range(7):
            frame=self.frame()
            if self.observer.observe(frame).state!='match_ready' or HudReader().read(frame).tower_count!=0:
                raise StopRun('Require a fresh match with zero towers before camera alignment.')
            if gate.bind(frame):
                return
            step=gate.zoom_step(frame) if attempt<6 else None
            if step is None:
                break
            self.status('camera_alignment',step=attempt+1,wheel_delta=step)
            self.driver.move(1450,450)  # World area, outside the HUD and hotbar.
            self.driver.zoom_fine(step)
            self.driver.wait(.4)
        raise StopRun('Fresh overhead pose did not match the map calibration.')

    def prepare_camera(self,retained=False):
        self.status('camera_check',retained=retained)
        self.allowed={'match_ready'}
        frame=self.frame()
        if self.observer.observe(frame).state!='match_ready' or HudReader().read(frame).tower_count!=0:
            raise StopRun('Require a fresh match with zero towers before camera setup.')
        gate=CameraGate(self.profile_path)
        if retained:
            if not gate.bind(frame):
                raise StopRun('Restart did not retain a calibrated map/camera view.')
        else:
            setup=self.profile['setup']
            self.driver.key(setup['movement'],setup['movement_ms']/1000)
            self.driver.zoom(setup['zoom_in'])
            self.driver.zoom(-setup['zoom_out'])
            for _ in range(setup['pitch_repetitions']):
                self.driver.orbit(0,setup['pitch_down'])
            self.driver.wait(.4)
            self.align_fresh_camera(gate)
        bar=read_hotbar(self.frame(),slot=1)
        if not bar.valid:
            raise StopRun('Tower hotbar not confirmed after camera setup.')
        self.save_frame(self.frame(),'prepared.png')
        self.status('prepared',physical_board=self.board_index,placement_price=bar.price)

    def run(self,matches=1,repeat_route='play-again',prepare_only=False,continuous=False,idle_lobby_seconds=0):
        if not 1<=matches<=10 or repeat_route not in {'play-again','lobby'} or (continuous and prepare_only):
            raise StopRun('Require 1..10 bounded matches or explicit continuous play, with a supported repeat route.')
        if type(idle_lobby_seconds) is not int or (idle_lobby_seconds and
                (not 1200<=idle_lobby_seconds<=1800 or not continuous or prepare_only)):
            raise StopRun('AFK lobby monitoring requires 1200..1800 seconds of continuous play.',kind='setup')
        if shutil.disk_usage(self.output).free<2*1024**3:
            raise StopRun('Less than 2 GiB free on the evidence disk; no game input sent.',kind='storage')
        if idle_lobby_seconds:
            # Resolve a verified login-reward overlay before beginning the
            # no-input interval. Once monitoring starts, every unexpected UI
            # state is a stop rather than an opportunity to click.
            self.lobby()
            self.wait_for_afk_disconnect(idle_lobby_seconds)
        self.preflight()
        self.choose_map()
        self.prepare_camera()
        if prepare_only:
            return {'status':'prepared','matches':[],'all_requested_matches_won':False}
        return self.play_matches(matches,repeat_route,continuous)

    def play_matches(self,matches=1,repeat_route='play-again',continuous=False):
        """Run/repeat from a verified prepared match; run() owns lobby preflight."""
        if not 1<=matches<=10 or repeat_route not in {'play-again','lobby'}:
            raise StopRun('Unsupported repeat route or match count.')
        if shutil.disk_usage(self.output).free<2*1024**3:
            raise StopRun('Less than 2 GiB free on the evidence disk; no game input sent.',kind='storage')
        results=[]
        index=0
        while True:
            self.pause()
            self.totals['attempts']+=1
            match_number=self.totals['attempts']
            self.status('playing',match=match_number,continuous=continuous)
            full_evidence=not continuous or index<2
            playback=Playback(self.profile_path,self.driver,self.output/f'match_{index+1:04}',
                notify=lambda data:self.status('playing',match=match_number,progress=data),pause=self.pause,
                full_evidence=full_evidence,latest_path=None if full_evidence else self.output/'latest.png')
            if playback.profile['strategy_sha256']!=self.profile['strategy_sha256']:
                raise StopRun('Strategy changed during this session; no new-match playback sent.')
            result=playback.play(operations=len(self.strategy.steps),start_waves=True,wait_result=True)
            index+=1
            self.totals['matches_completed']+=int(result['status'] in {'victory','defeat'})
            self.totals['wins']+=int(result['status']=='victory')
            self.totals['coins_total']+=result.get('coins') or 0
            row={'match':match_number,'elapsed_seconds':round(self.now()-self.started,1),'result':result}
            append_jsonl(self.output/'matches.jsonl',row)
            results.append(result)
            results=results[-20:]
            summary={'status':result['status'],**self.totals,'matches':results,
                'continuous':continuous,'all_requested_matches_won':not continuous and index==matches and self.totals['wins']==matches}
            if result.get('diagnostic_error'):
                stop_kind=result.get('diagnostic_error_kind','storage')
                summary.update(status='stopped',stop_kind=stop_kind,reason='Final result confirmed; evidence recording failed: '+result['diagnostic_error'])
                write_json(self.output/'result.json',summary)
                self.status('stopped',reason=summary['reason'],stop_kind=stop_kind,last_result=result)
                return summary
            write_json(self.output/'result.json',summary)
            self.status('match_complete' if result['status'] in {'victory','defeat'} else 'stopped',match=match_number,last_result=result,continuous=continuous)
            if result['status']=='victory' and (type(result.get('coins')) is not int or result['coins']<0):
                summary.update(status='stopped',reason='Victory observed but coin reward is unreadable; no repeat started.',all_requested_matches_won=False)
                write_json(self.output/'result.json',summary)
                return summary
            if result['status']!='victory' or (not continuous and index>=matches):
                return summary
            if shutil.disk_usage(self.output).free<2*1024**3:
                raise StopRun('Less than 2 GiB free on the evidence disk; stopped before another match.',kind='storage')
            if repeat_route=='lobby':
                self.transition('return_victory')
                self.preflight()
                self.choose_map()
                self.prepare_camera()
            else:
                destination=self.transition('play_again')
                if destination=='map_vote':
                    self.choose_map()
                    self.prepare_camera()
                else:
                    self.prepare_camera(retained=True)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['start','status','pause','resume','stop'])
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--confirm-start',action='store_true')
    parser.add_argument('--profile',type=Path,default=ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
    parser.add_argument('--matches',type=int,default=1)
    parser.add_argument('--continuous',action='store_true',help='Explicit Solo grind until stopped, a guard fails or disk space is low')
    parser.add_argument('--auto-recover',action='store_true',help='Fresh TDS session after game failures or verified natural focus return within five seconds; continuous mode only')
    parser.add_argument('--repeat-route',choices=['play-again','lobby'],default='play-again')
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--startup-delay',type=int,default=0,choices=range(0,11),help='Seconds to switch focus to Roblox; no automatic refocus')
    parser.add_argument('--idle-lobby-seconds',type=int,default=0,help='One-time, no-input AFK lobby observation (1200..1800 seconds); requires --continuous --auto-recover')
    args=parser.parse_args(argv)
    if args.action!='start':
        if not args.output.is_dir():
            parser.error('Session output folder does not exist.')
        if args.action=='status':
            status=args.output/'status.json'
            if not status.exists():
                status=args.output/'result.json'
            if not status.exists():
                parser.error('This session has not written status or a result yet.')
            print(status.read_text(encoding='utf-8'))
        elif args.action=='resume':
            (args.output/'pause').unlink(missing_ok=True)
        else:
            (args.output/args.action).write_text('requested',encoding='utf-8')
        return 0
    if not args.confirm_start or not 1<=args.matches<=10 or (args.continuous and (args.matches!=1 or args.prepare_only)):
        parser.error('Start requires --confirm-start and either 1..10 matches or --continuous; F8/Escape stops.')
    if args.auto_recover and not args.continuous:
        parser.error('--auto-recover requires an explicitly started continuous run.')
    if args.idle_lobby_seconds and (not 1200<=args.idle_lobby_seconds<=1800 or not args.auto_recover or not args.continuous):
        parser.error('--idle-lobby-seconds requires 1200..1800 seconds with --continuous --auto-recover.')
    session=None
    platform=None
    try:
        if args.output.exists():
            raise StopRun('Use a new output folder; existing evidence is never overwritten.')
        platform=WindowsOS(stop_hotkey=True)
        args.output.mkdir(parents=True)
        deadline=time.monotonic()+args.startup_delay
        while time.monotonic()<deadline:
            if platform.stop_requested() or (args.output/'stop').exists():
                raise StopRun('Emergency stop during startup countdown.',kind='user_stop')
            time.sleep(.025)
        if args.auto_recover:
            pointer=ROOT/'captures/last_session.txt';pointer.parent.mkdir(parents=True,exist_ok=True)
            pointer.write_text(str(args.output.resolve()),encoding='utf-8')
            from .recovery import supervise
            result=supervise(args.output,platform,args.profile,idle_lobby_seconds=args.idle_lobby_seconds)
            return 0 if result['status'] in {'victory','prepared'} else 2
        driver=GuardedInput(locate_roblox(),platform)
        driver.check()
        if (driver.expected.width,driver.expected.height,driver.expected.dpi)!=(1920,991,120):
            raise StopRun(f'Roblox client is {driver.expected.width}x{driver.expected.height} at {driver.expected.dpi} DPI; this profile requires 1920x991 at 120 DPI (125% scaling), windowed mode.')
        session=Session(driver,args.output,args.profile)
        pointer=ROOT/'captures/last_session.txt'
        pointer.parent.mkdir(parents=True,exist_ok=True)
        pointer.write_text(str(args.output.resolve()),encoding='utf-8')
        result=session.run(args.matches,args.repeat_route,args.prepare_only,args.continuous,args.idle_lobby_seconds)
        session.status(result['status'],result=result)
        (args.output/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        return 0 if result['status'] in {'victory','prepared'} else 2
    except (RuntimeError,ValueError,OSError,KeyError,TypeError) as exc:
        result={'status':'stopped','reason':str(exc),'final_macro_verified':False}
        if session:
            result.update(session.totals)
            session.status('stopped',reason=str(exc))
        if args.output.is_dir():
            (args.output/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps(result),flush=True)
        return 2
    finally:
        if platform:
            platform.close()


if __name__=='__main__':
    raise SystemExit(main())
