"""Bounded supervised strategy calibration trial; never starts a second match."""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .calibration import CameraGate, load_profile, valid_preview
from .control import GuardedInput, StopRun, WindowsOS
from .hotbar import read_hotbar
from .match import MatchRunner, Snapshot
from .observer import Observer
from .phase1 import capture, locate_roblox
from .resources import HudReader, hovered_scout_at
from .results import ResultReader
from .recording import LatestFrame,write_json
from .timing import READ_SECONDS, MATCH_START_SECONDS, RESULT_CONFIRM_SECONDS

ROOT=Path(__file__).resolve().parents[2]


@dataclass
class Progress:
    next_step: int = 0
    count: int = 0
    levels: dict[int,int] = field(default_factory=dict)


def run_sequence(strategy,runner,progress,map_point,limit,before_step=None,checkpoint=None):
    if not 1 <= limit <= 224 or not 0 <= progress.next_step <= len(strategy.steps):
        raise StopRun("Invalid operation limit or progress.")
    positions={step.args[3]:(step.args[0],step.args[1]) for step in strategy.steps if step.operation=='SpawnTower'}
    end=min(len(strategy.steps),progress.next_step+limit)
    while progress.next_step<end:
        step=strategy.steps[progress.next_step]
        if before_step:
            before_step(step,progress)
        if step.operation=='SpawnTower':
            x,y,slot,ident=step.args
            runner.place(map_point((x,y)),slot,progress.count)
            progress.count+=1
            progress.levels[ident]=0
        elif step.operation=='UpgradeTower':
            ident=step.args[0]
            if ident not in progress.levels:
                raise StopRun("Progress does not contain the target tower.")
            previous=progress.levels[ident]
            result=runner.upgrade(map_point(positions[ident]),previous,progress.count)
            increment=result.level==previous+1 and result.level<=4
            maxed_noop=previous==result.level==4 and result.maxed
            if result.tower_count!=progress.count or result.tower_name!='Scout' or not (increment or maxed_noop):
                raise StopRun('Upgrade result does not confirm an increment or verified max level.')
            progress.levels[ident]=result.level
        else:
            raise StopRun("Unsupported operation; no input sent.")
        progress.next_step+=1
        if checkpoint:
            checkpoint(progress)
    return progress


def validate_progress(strategy,progress):
    """A checkpoint must describe exactly the confirmed source prefix."""
    if type(progress.next_step) is not int or not 0<=progress.next_step<=len(strategy.steps):
        raise StopRun('Invalid saved operation index.')
    expected={}
    for step in strategy.steps[:progress.next_step]:
        if step.operation=='SpawnTower':
            expected[step.args[3]]=0
        elif step.operation=='UpgradeTower' and step.args[0] in expected:
            expected[step.args[0]]=min(4,expected[step.args[0]]+1)
        else:
            raise StopRun('Invalid saved operation prefix.')
    if progress.count!=len(expected) or progress.levels!=expected:
        raise StopRun('Saved count/levels do not match the exact source prefix.')


class MatchFinished(Exception):
    def __init__(self,result,diagnostic_error=None,diagnostic_error_kind=None):
        self.result=result
        self.diagnostic_error=diagnostic_error
        self.diagnostic_error_kind=diagnostic_error_kind


class Playback:
    """One prepared match. Navigation and repeat policy belong to session.py."""
    def __init__(self,profile_path,driver,output,notify=None,pause=None,full_evidence=True,latest_path=None):
        self.profile_path=Path(profile_path)
        self.profile,self.strategy=load_profile(profile_path)
        self.driver,self.window=driver,driver.expected
        self.output=Path(output)
        self.output.mkdir(parents=True,exist_ok=False)
        self.full_evidence=full_evidence
        self.latest_path=Path(latest_path) if latest_path else self.output/'latest.png'
        self.recording=LatestFrame(self.latest_path)
        self.observer,self.hud=Observer(),HudReader()
        self.results=ResultReader(self.observer)
        self.camera=CameraGate(profile_path)
        self.preview_point=None
        self.notify=notify or (lambda data: print(json.dumps(data),flush=True))
        self.pause=pause or (lambda read: None)

    def frame(self):
        self.driver.check()
        image=capture(self.window)
        try:self.recording.write(image)
        except OSError as exc:
            raise StopRun(f'Cannot write latest frame ({type(exc).__name__}).',kind='storage') from exc
        return image

    def save_evidence(self,image,name):
        try:
            if self.full_evidence:
                image.save(self.output/name)
            elif name=='final.png':
                image.crop((630,350,1290,805)).save(self.output/name)
        except OSError as exc:
            raise StopRun(f'Cannot save {name} ({type(exc).__name__}).',kind='storage') from exc

    def finish_if_result(self,frame):
        state=self.observer.observe(frame).state
        if state not in {'victory','defeat'} and not getattr(self.observer,'result_banner',lambda frame:None)(frame):
            return state
        # No purchase/placement input after even one observed result banner.
        deadline=time.monotonic()+RESULT_CONFIRM_SECONDS
        previous=None
        while time.monotonic()<deadline:
            self.driver.check()
            result=self.results.read(frame)
            if result is not None and result==previous:
                final_frame=frame
                diagnostic_error=None;diagnostic_error_kind=None
                if result.coins is None:
                    # Scroll only the verified reward pane, once; never zoom the map.
                    try:
                        self.driver.move(850,600)
                        self.driver.zoom(-3)
                        self.driver.wait(.3)
                        final_frame=self.frame()
                        scrolled=self.results.read(final_frame)
                        if scrolled and (scrolled.status,scrolled.map_name,scrolled.difficulty,scrolled.wave,scrolled.duration_seconds)==(result.status,result.map_name,result.difficulty,result.wave,result.duration_seconds):
                            result=scrolled
                    except (RuntimeError,OSError) as exc:
                        diagnostic_error=str(exc)
                        diagnostic_error_kind=getattr(exc,'kind','setup')
                try:self.save_evidence(final_frame,'final.png')
                except (RuntimeError,OSError) as exc:
                    if diagnostic_error is None:
                        diagnostic_error=str(exc)
                        diagnostic_error_kind=getattr(exc,'kind','storage' if isinstance(exc,OSError) else 'setup')
                raise MatchFinished(result,diagnostic_error,diagnostic_error_kind)
            previous=result
            self.driver.wait(.2)
            frame=self.frame()
        raise StopRun('Result banner appeared but map/mode/wave/duration were not confirmed; no further game input.')

    def read(self):
        frame=self.frame()
        state=self.finish_if_result(frame)
        bar=read_hotbar(frame,slot=self.profile['slot'])
        return Snapshot(state,self.hud.read(frame),self.camera.check(frame),
                        valid_preview(frame,*self.preview_point) if self.preview_point else False,bar.valid,bar.price)

    def click_gate(self):
        deadline=time.monotonic()+READ_SECONDS
        while True:
            frame=self.frame()
            state=self.finish_if_result(frame)
            if state=='unknown' and time.monotonic()<deadline:
                self.driver.wait(.15)  # Observe a HUD animation; no click retry.
                continue
            if state not in {'match_ready','in_match'}:
                raise StopRun('Match click precondition changed during pointer movement.')
            camera=self.camera.check(frame)
            if camera is None and time.monotonic()<deadline:
                self.driver.wait(.15)
                continue
            if not camera:
                raise StopRun('Camera/character view changed before the click; no button press sent.')
            return

    def play(self,operations=224,start_waves=False,progress=None,wait_result=False,result_timeout=900):
        progress=progress or Progress()
        validate_progress(self.strategy,progress)
        if self.profile['slot']!=1 or self.window.dpi!=self.profile['dpi']:
            raise StopRun('Require calibrated DPI and Golden Scout only in slot 1.')
        initial=self.frame()
        if self.observer.observe(initial).state not in {'match_ready','in_match'} or not self.camera.bind(initial):
            raise StopRun('Prepared Dead Ahead view is not calibrated; no input sent.')
        if self.hud.read(initial).tower_count!=progress.count:
            raise StopRun('Live tower count differs from confirmed progress.')
        self.save_evidence(initial,'initial.png')
        def hover_selection(point):
            frame=self.frame()
            if self.observer.observe(frame).state not in {'match_ready','in_match'} or not self.camera.check(frame):
                return False
            return hovered_scout_at(frame,point,self.hud.ocr)
        golden_ten = (self.profile.get('status','').startswith('v031_candidate')
                      and len(self.strategy.steps)==50)
        runner=MatchRunner(self.driver,self.read,slot=1,hover_check=hover_selection,
                           use_e_upgrades=golden_ten)
        old_gate=self.driver.before_click
        self.driver.before_click=self.click_gate
        def save(current):
            data={'strategy_sha256':self.profile['strategy_sha256'],'pid':self.window.pid,'progress':asdict(current)}
            write_json(self.output/'progress.json',data)
            if self.full_evidence:
                self.save_evidence(self.frame(),f'step_{current.next_step:03}.png')
            self.notify({'confirmed_step':current.next_step,'total_actions':len(self.strategy.steps),
                         'count':current.count,'levels':current.levels})
        def before(step,current):
            self.pause(self.read)
            self.preview_point=self.camera.map_point(step.args[:2]) if step.operation=='SpawnTower' else None
            shot=runner.checked()
            price=shot.placement_cost if step.operation=='SpawnTower' else shot.hud.upgrade_cost
            needs_income=price is not None and shot.hud.cash<price
            if shot.state=='match_ready' and (current.next_step>=2 or needs_income):
                if not start_waves:
                    raise StopRun('Ready requires --start-waves to obtain further income.')
                self.driver.click(1035,190)
                deadline=time.monotonic()+MATCH_START_SECONDS
                while time.monotonic()<deadline:
                    self.driver.check()
                    active=self.frame()
                    if self.observer.observe(active).state=='in_match' and self.hud.read(active).wave is not None:
                        return
                    self.driver.wait(.2)
                raise StopRun('Active-match HUD not confirmed after Ready.')
        save(progress)
        diagnostic_error=None;diagnostic_error_kind=None
        try:
            run_sequence(self.strategy,runner,progress,self.camera.map_point,operations,before,save)
            if wait_result and progress.next_step==len(self.strategy.steps):
                if not 0<result_timeout<=1200:
                    raise StopRun('Invalid result deadline.')
                deadline=time.monotonic()+result_timeout
                while time.monotonic()<deadline:
                    self.pause(self.read)
                    runner.checked()
                    self.driver.wait(.25)
                raise StopRun('Timed out waiting for a verified match result.')
            result={'status':'operation_limit_reached','full_strategy_verified':False}
        except MatchFinished as finished:
            result=asdict(finished.result)
            result['full_strategy_verified']=finished.result.status=='victory' and progress.next_step==len(self.strategy.steps)
            diagnostic_error=finished.diagnostic_error
            diagnostic_error_kind=finished.diagnostic_error_kind
        except (RuntimeError,ValueError,OSError) as exc:
            result={'status':'stopped','reason':str(exc),'stop_kind':getattr(exc,'kind','failure'),'full_strategy_verified':False}
        finally:
            self.driver.before_click=old_gate
            try:self.recording.flush()
            except OSError as exc:
                diagnostic_error=diagnostic_error or str(exc)
                diagnostic_error_kind=diagnostic_error_kind or 'storage'
        if diagnostic_error is not None:
            result['diagnostic_error']=diagnostic_error
            result['diagnostic_error_kind']=diagnostic_error_kind or 'storage'
        result['progress']=asdict(progress)
        result['strategy_sha256']=self.profile['strategy_sha256']
        result['modifier_scope']='Observed current account only; active modifiers may change income and win timing.'
        write_json(self.output/'result.json',result)
        self.notify(result)
        return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',type=Path,default=ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
    parser.add_argument('--confirm-start',action='store_true')
    parser.add_argument('--calibration-trial',action='store_true')
    parser.add_argument('--start-waves',action='store_true')
    parser.add_argument('--wait-result',action='store_true')
    parser.add_argument('--operations',type=int,default=6)
    parser.add_argument('--resume',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    if not args.confirm_start or not args.calibration_trial or not 1<=args.operations<=224:
        parser.error('Require --confirm-start --calibration-trial and 1..224 operations; F8/Escape stops.')
    platform=None
    try:
        platform=WindowsOS(stop_hotkey=True)
        window=locate_roblox()
        driver=GuardedInput(window,platform)
        driver.check()
        playback=Playback(args.profile,driver,args.output)
        progress=Progress()
        if args.resume:
            if args.resume.stat().st_size>20000:
                raise StopRun('Progress file is oversized.')
            saved=json.loads(args.resume.read_text(encoding='utf-8'))
            if saved['strategy_sha256']!=playback.profile['strategy_sha256'] or saved['pid']!=window.pid:
                raise StopRun('Progress belongs to a different strategy/client.')
            data=saved['progress']
            progress=Progress(data['next_step'],data['count'],{int(k):v for k,v in data['levels'].items()})
        result=playback.play(args.operations,args.start_waves,progress,args.wait_result)
        return 0 if result['status'] in {'victory','operation_limit_reached'} else 2
    except (RuntimeError,ValueError,OSError,KeyError,TypeError) as exc:
        print(f'RUN_STOP: {exc}',flush=True)
        return 2
    finally:
        if platform:
            platform.close()


if __name__=='__main__':
    raise SystemExit(main())
