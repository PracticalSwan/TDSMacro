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
from .calibration import CameraGate,load_profile
from .control import GuardedInput,StopRun,WindowsOS
from .hotbar import read_hotbar
from .loadout import verify_inventory
from .maps import read_boards,find_target,read_headers,visible_target,vip_target_matches,vote_prompt,badge_is_one,spawn_board_row
from .navigation import Navigator,MENU_ROUTE
from .observer import Observer
from .phase1 import capture,locate_roblox,BlankCapture
from .resources import LocalOCR,HudReader,parse_cash
from .run import Playback,ROOT
from .timing import READ_SECONDS, TELEPORT_SECONDS


class SessionControl:
    def __init__(self,path):
        self.path=Path(path)
    def stopped(self):
        return (self.path/'stop').exists()
    def paused(self):
        return (self.path/'pause').exists()
    def write(self,data):
        # Atomic replace so status readers never consume partially written JSON.
        temporary=self.path/'status.tmp'
        temporary.write_text(json.dumps(data,indent=2),encoding='utf-8')
        temporary.replace(self.path/'status.json')


class Session:
    def __init__(self,driver,output,profile_path=None,read_frame=None,now=time.monotonic):
        self.driver=driver
        self.output=Path(output)
        self.control=SessionControl(output)
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
        self.totals={"attempts":0,"matches_completed":0,"wins":0,"coins_total":0}

    def frame(self):
        self.driver.check()
        frame=self.capture()
        frame.save(self.output/'latest.png')
        return frame

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
                raise StopRun('Pause exceeded five minutes; stopped without further input.')
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
        while self.now()<deadline:
            state=self.observer.observe(self.frame()).state
            if state=='login_rewards' and not dismissed:
                self.transition('dismiss_login')
                dismissed=True
                stable_since=None
            elif state=='lobby':
                if stable_since is None:
                    stable_since=self.now()
                if self.now()-stable_since>=2:
                    return
            elif state not in {'unknown','loading'}:
                raise StopRun(f'Expected lobby/login rewards; saw {state}.')
            else:
                stable_since=None
            self.driver.wait(.2)
        raise StopRun('Lobby did not settle after login-reward check.')

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
                frame.save(self.output/'loadout_identity.png')
                break
            self.driver.wait(.2)
        else:
            raise StopRun('Equipped Scout/Golden label/slot-1 perk not confirmed; skin portraits are not checked.')
        self.transition('close_inventory')
        self.lobby()
        for name in MENU_ROUTE:
            self.transition(name)
        bar=read_hotbar(self.frame(),slot=1)
        if not bar.valid or bar.price is None:
            raise StopRun('Require Scout in slot 1 and no tower prices in slots 2..5.')
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
                frame.save(self.output/'voting_spawn.png')
            row=spawn_board_row(frame)
            if row and 975<=row[0]<=1005 and 285<=row[1]<=330:
                stable+=1
                if stable>=2:
                    frame.save(self.output/'voting_aligned.png')
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
            self.driver.key('D',1.7)
            self.driver.wait(.3)
            self.driver.key('E',.8)
            self.wait_state('vip_maps',10,{'map_vote'})
            self.allowed={'vip_maps'}
            self.driver.click(946,231)
            self.driver.select_all()
            self.driver.text('dead ahead')
            self.driver.move(694,371)
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
            self.driver.click(694,371)
            self.wait_state('map_vote',10,{'vip_maps'})
            self.allowed={'map_vote'}
            self.driver.key('A',1.7)
            self.driver.key('W',.9)
            self.driver.wait(.3)
            boards=self.boards()
            target=find_target(boards)
            if target is None:
                raise StopRun('VIP choice did not leave Dead Ahead on any readable board.')
        self.vote_target(target)

    def vote_target(self,target):
        self.board_index=target.index
        self.frame().save(self.output/f'boards_target{target.index}.png')
        self.status('walk_to_target',physical_board=target.index,title=target.title)
        frame,current=self.approach_target()
        frame.save(self.output/'before_vote.png')
        self.driver.key('E',.8)
        self.driver.key('S',.5)  # Clear the proximity prompt from the numeric vote badge.
        self.driver.wait(.3)
        frame=self.frame()
        frame.save(self.output/'after_vote.png')
        current=visible_target(frame)
        if current is None:
            raise StopRun('Target identity was lost after voting; Ready was not clicked.')
        # The target's red vote badge sits beneath the header. Read the badge
        # nearest this verified title; thumbnails/reward numbers are excluded.
        count=self.vote_count(frame,current)
        if count is None and self.observer.observe(frame).state=='map_vote':
            # The fixed avatar/head can hide a world-space badge after backing
            # away. Clear that occlusion once; never repeat the vote action.
            self.status('vote_badge_view_adjustment',physical_board=self.board_index)
            self.driver.key('D',.35)  # Open floor; left can climb the board-1 bench.
            self.driver.wait(.2)
            frame=self.frame()
            frame.save(self.output/'after_vote_clear.png')
            current=visible_target(frame)
            count=self.vote_count(frame,current) if current is not None else None
        if count!=1:
            raise StopRun('The verified target does not show one solo vote; Ready was not clicked.')
        self.status('target_voted',physical_board=self.board_index)
        self.driver.click(960,778)
        self.wait_state('match_ready',TELEPORT_SECONDS,{'map_vote','loading','in_match'})

    def approach_target(self):
        # Keep the physical board index from the original four-header view.
        # Movement is bounded and each step is followed by fresh visual feedback.
        for _ in range(22):
            self.pause()
            frame=self.frame()
            if self.observer.observe(frame).state!='map_vote':
                raise StopRun('Map-vote state changed while approaching the target.')
            current=visible_target(frame)
            prompt=vote_prompt(frame,current)
            if current is None:
                if not prompt:
                    raise StopRun('Lost the target title without a known Vote prompt; no further walking.')
                self.driver.key('S',.12)  # A close header can be hidden by the fixed HUD.
            else:
                center=(current.box[0]+current.box[2])/2
                error=center-960
                if prompt and abs(error)<=140:
                    return frame,current
                if current.box[2]-current.box[0]>400:
                    self.driver.key('S',.12)
                elif abs(error)>90:
                    self.driver.key('A' if error<0 else 'D',min(.20,max(.06,abs(error)/950)))
                else:
                    self.driver.key('W',.10)
            self.driver.wait(.2)
        raise StopRun('Target title and Vote proximity did not converge within bounded walking steps.')

    def vote_count(self,frame,target):
        import cv2
        import numpy as np
        pixels=np.asarray(frame.convert('RGB')).astype(np.float32)
        red,green,blue=(pixels[:,:,i] for i in range(3))
        mask=np.uint8((red>180)&(green>65)&(green<200)&(blue>65)&(blue<200)&(red>green*1.2))*255
        mask[:320]=0
        mask[650:]=0
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        center=(target.box[0]+target.box[2])/2
        expected_badge=center+(target.box[2]-target.box[0])*.35
        candidates=[]
        for contour in contours:
            x,y,w,h=cv2.boundingRect(contour)
            if 25<=w<=120 and 25<=h<=120 and .65<w/h<1.5 and abs(x+w/2-expected_badge)<100:
                value=parse_cash(self.ocr.read(frame.crop((x,y,x+w,y+h))))
                if value is None and badge_is_one(frame,(x,y,x+w,y+h)):
                    value=1
                if value is not None:
                    candidates.append((abs(x+w/2-expected_badge),value))
        candidates.sort()
        return candidates[0][1] if candidates else None

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
            if not gate.bind(self.frame()):
                raise StopRun('Fresh overhead pose did not match the map calibration.')
        bar=read_hotbar(self.frame(),slot=1)
        if not bar.valid:
            raise StopRun('Tower hotbar not confirmed after camera setup.')
        self.frame().save(self.output/'prepared.png')
        self.status('prepared',physical_board=self.board_index,placement_price=bar.price)

    def run(self,matches=1,repeat_route='play-again',prepare_only=False,continuous=False):
        if not 1<=matches<=10 or repeat_route not in {'play-again','lobby'} or (continuous and prepare_only):
            raise StopRun('Require 1..10 bounded matches or explicit continuous play, with a supported repeat route.')
        if shutil.disk_usage(self.output).free<2*1024**3:
            raise StopRun('Less than 2 GiB free on the evidence disk; no game input sent.')
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
            raise StopRun('Less than 2 GiB free on the evidence disk; no game input sent.')
        results=[]
        index=0
        while True:
            self.pause()
            self.totals['attempts']=index+1
            self.status('playing',match=index+1,continuous=continuous)
            full_evidence=not continuous or index<2
            playback=Playback(self.profile_path,self.driver,self.output/f'match_{index+1:04}',
                notify=lambda data:self.status('playing',match=index+1,progress=data),pause=self.pause,
                full_evidence=full_evidence,latest_path=None if full_evidence else self.output/'latest.png')
            if playback.profile['strategy_sha256']!=self.profile['strategy_sha256']:
                raise StopRun('Strategy changed during this session; no new-match playback sent.')
            result=playback.play(operations=len(self.strategy.steps),start_waves=True,wait_result=True)
            index+=1
            self.totals['matches_completed']+=int(result['status'] in {'victory','defeat'})
            self.totals['wins']+=int(result['status']=='victory')
            self.totals['coins_total']+=result.get('coins') or 0
            row={'match':index,'elapsed_seconds':round(self.now()-self.started,1),'result':result}
            with (self.output/'matches.jsonl').open('a',encoding='utf-8') as ledger:
                ledger.write(json.dumps(row)+'\n')
            results.append(result)
            results=results[-20:]
            summary={'status':result['status'],**self.totals,'matches':results,
                'continuous':continuous,'all_requested_matches_won':not continuous and index==matches and self.totals['wins']==matches}
            (self.output/'result.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
            self.status('match_complete' if result['status'] in {'victory','defeat'} else 'stopped',match=index,last_result=result,continuous=continuous)
            if result['status']=='victory' and (type(result.get('coins')) is not int or result['coins']<0):
                summary.update(status='stopped',reason='Victory observed but coin reward is unreadable; no repeat started.',all_requested_matches_won=False)
                (self.output/'result.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
                return summary
            if result['status']!='victory' or (not continuous and index>=matches):
                return summary
            if shutil.disk_usage(self.output).free<2*1024**3:
                raise StopRun('Less than 2 GiB free on the evidence disk; stopped before another match.')
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
    parser.add_argument('--continuous',action='store_true',help='Explicit Solo grind until stop, focus loss, failure or low disk space')
    parser.add_argument('--repeat-route',choices=['play-again','lobby'],default='play-again')
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--startup-delay',type=int,default=0,choices=range(0,11),help='Seconds to switch focus to Roblox; no automatic refocus')
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
                raise StopRun('Emergency stop during startup countdown.')
            time.sleep(.025)
        driver=GuardedInput(locate_roblox(),platform)
        driver.check()
        if (driver.expected.width,driver.expected.height,driver.expected.dpi)!=(1920,991,120):
            raise StopRun(f'Roblox client is {driver.expected.width}x{driver.expected.height} at {driver.expected.dpi} DPI; this profile requires 1920x991 at 120 DPI (125% scaling), windowed mode.')
        session=Session(driver,args.output,args.profile)
        pointer=ROOT/'captures/last_session.txt'
        pointer.parent.mkdir(parents=True,exist_ok=True)
        pointer.write_text(str(args.output.resolve()),encoding='utf-8')
        result=session.run(args.matches,args.repeat_route,args.prepare_only,args.continuous)
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
