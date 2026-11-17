"""Runtime work budgets and unchanged safety behavior; no live game input."""
import json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from test_control import FakeOS
from tds_auto.control import GuardedInput,StopRun
from tds_auto.observer import Observer
from tds_auto.resources import Hud
from tds_auto.match import Snapshot
from tds_auto.run import Playback,Progress,MatchFinished
from tds_auto.results import GameResult
from tds_auto.strategy import Step
try:
    from tds_auto.recording import LatestFrame
except ImportError:
    LatestFrame=None


class EfficiencyTests(unittest.TestCase):
    def setUp(self):
        directory=tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup)
        self.path=Path(directory.name)

    def test_one_frame_is_classified_once_and_still_returns_its_live_state(self):
        playback=Playback.__new__(Playback);playback.observer=Observer()
        with Image.open(ROOT/'tests/fixtures/in_match.png') as image:frame=image.copy()
        playback.frame=lambda:frame;playback.profile={'slot':1};playback.preview_point=None
        playback.camera=SimpleNamespace(check=lambda f:True)
        playback.hud=SimpleNamespace(read=lambda f:Hud(500,1,'Scout',0,150,1))
        original=playback.observer.observe;observations=[]
        def observe(f):observations.append(f);return original(f)
        playback.observer.observe=observe
        with patch('tds_auto.run.read_hotbar',return_value=SimpleNamespace(valid=True,price=250)):
            snapshot=playback.read()
        self.assertEqual(snapshot.state,'in_match')
        self.assertEqual((snapshot.hud.cash,snapshot.camera_ok),(500,True))
        self.assertEqual(len(observations),1,'A frozen frame needs one classification, not a repeated full scan.')

    def test_result_wait_does_not_discard_a_measured_camera_failure(self):
        platform=FakeOS();playback=Playback.__new__(Playback)
        playback.driver=GuardedInput(platform.window,platform);playback.window=platform.window
        playback.profile={'slot':1,'dpi':120,'strategy_sha256':'test'}
        playback.strategy=SimpleNamespace(steps=(Step('SpawnTower',(855,330,1,1)),))
        playback.output=self.path;playback.full_evidence=False
        playback.recording=SimpleNamespace(flush=lambda:None)
        playback.frame=lambda:Image.new('RGB',(1920,991))
        playback.observer=SimpleNamespace(observe=lambda f:SimpleNamespace(state='in_match'))
        playback.hud=SimpleNamespace(read=lambda f:Hud(500,1,'Scout',0,150,20))
        playback.camera=SimpleNamespace(bind=lambda f:True,map_point=lambda p:p)
        playback.pause=lambda read:None;playback.notify=lambda data:None
        calls=[]
        def read():
            calls.append(1)
            if len(calls)==3:raise MatchFinished(GameResult('victory','Dead Ahead','Easy',20,464,450))
            return Snapshot('in_match',Hud(500,1,'Scout',0,150,20),len(calls)!=1)
        playback.read=read
        result=playback.play(progress=Progress(1,1,{1:0}),wait_result=True)
        self.assertEqual(result['status'],'stopped')
        self.assertIn('camera/character',result['reason'])
        self.assertEqual(len(calls),1)
        self.assertEqual(platform.events,[])

    def test_latest_image_limits_disk_writes_but_flushes_the_actual_last_frame(self):
        self.assertIsNotNone(LatestFrame,'bounded diagnostic image writer is missing')
        clock=[0.0];recorder=LatestFrame(self.path/'latest.png',now=lambda:clock[0])
        red=Image.new('RGB',(40,40),'red');blue=Image.new('RGB',(40,40),'blue')
        recorder.write(red);first=(self.path/'latest.png').read_bytes()
        clock[0]=.2;recorder.write(blue)
        self.assertEqual((self.path/'latest.png').read_bytes(),first)
        recorder.flush()
        with Image.open(self.path/'latest.png') as image:self.assertEqual(image.getpixel((20,20)),(0,0,255))

    def test_latest_image_refreshes_without_loss_after_its_interval(self):
        self.assertIsNotNone(LatestFrame,'bounded diagnostic image writer is missing')
        clock=[0.0];recorder=LatestFrame(self.path/'latest.png',now=lambda:clock[0])
        recorder.write(Image.new('RGB',(40,40),'red'))
        clock[0]=1.01;recorder.write(Image.new('RGB',(40,40),(11,22,33)))
        with Image.open(self.path/'latest.png') as image:self.assertEqual(image.getpixel((20,20)),(11,22,33))

    def test_failed_final_png_does_not_erase_a_confirmed_victory(self):
        platform=FakeOS();playback=Playback.__new__(Playback)
        playback.driver=GuardedInput(platform.window,platform);playback.window=platform.window
        playback.profile={'slot':1,'dpi':120,'strategy_sha256':'test'}
        playback.strategy=SimpleNamespace(steps=(Step('SpawnTower',(855,330,1,1)),))
        playback.output=self.path;playback.full_evidence=False
        def fail_flush():raise OSError('latest PNG is locked')
        playback.recording=SimpleNamespace(flush=fail_flush)
        playback.frame=lambda:Image.new('RGB',(1920,991))
        playback.observer=SimpleNamespace(observe=lambda f:SimpleNamespace(state='in_match'))
        playback.hud=SimpleNamespace(read=lambda f:Hud(500,1,'Scout',0,150,20))
        playback.camera=SimpleNamespace(bind=lambda f:True,map_point=lambda p:p)
        playback.pause=lambda read:None;notifications=[];playback.notify=notifications.append
        def read():raise MatchFinished(GameResult('victory','Dead Ahead','Easy',20,464,450))
        playback.read=read
        result=playback.play(progress=Progress(1,1,{1:0}),wait_result=True)
        self.assertEqual((result['status'],result['coins']),('victory',450))
        self.assertEqual(result['diagnostic_error'],'latest PNG is locked')
        self.assertEqual(json.loads((self.path/'result.json').read_text())['status'],'victory')
        self.assertEqual(notifications[-1]['status'],'victory')

    def test_latest_png_write_failure_is_a_protected_storage_stop(self):
        platform=FakeOS();playback=Playback.__new__(Playback)
        playback.driver=GuardedInput(platform.window,platform);playback.window=platform.window
        playback.recording=SimpleNamespace(write=lambda *args,**kwargs:(_ for _ in ()).throw(OSError('latest PNG is locked')))
        with patch('tds_auto.run.capture',return_value=Image.new('RGB',(1920,991))):
            with self.assertRaises(StopRun) as caught:playback.frame()
        self.assertEqual(caught.exception.kind,'storage')

    def test_final_evidence_failure_keeps_confirmed_win_and_stops_for_storage(self):
        platform=FakeOS();playback=Playback.__new__(Playback)
        frame=Image.new('RGB',(1920,991));confirmed=GameResult('victory','Dead Ahead','Easy',20,464,450)
        playback.driver=GuardedInput(platform.window,platform)
        playback.observer=SimpleNamespace(observe=lambda image:SimpleNamespace(state='victory'))
        playback.results=SimpleNamespace(read=lambda image:confirmed)
        playback.frame=lambda:frame
        playback.save_evidence=lambda image,name:(_ for _ in ()).throw(OSError('final PNG is locked'))
        with patch('tds_auto.run.time.monotonic',side_effect=[0,.1,.2]):
            with self.assertRaises(MatchFinished) as caught:playback.finish_if_result(frame)
        self.assertEqual(caught.exception.result.status,'victory')
        self.assertEqual(caught.exception.diagnostic_error_kind,'storage')

    def test_progress_checkpoint_write_failure_is_a_protected_storage_stop(self):
        platform=FakeOS();playback=Playback.__new__(Playback)
        playback.driver=GuardedInput(platform.window,platform);playback.window=platform.window
        playback.profile={'slot':1,'dpi':120,'strategy_sha256':'test'}
        playback.strategy=SimpleNamespace(steps=());playback.output=self.path;playback.full_evidence=False
        playback.recording=SimpleNamespace(write=lambda *args,**kwargs:None,flush=lambda:None)
        playback.observer=SimpleNamespace(observe=lambda image:SimpleNamespace(state='match_ready'))
        playback.camera=SimpleNamespace(bind=lambda image:True)
        playback.hud=SimpleNamespace(read=lambda image:SimpleNamespace(tower_count=0))
        def fail_progress(path,*args,**kwargs):
            if path.name=='progress.json':raise PermissionError('progress is read-only')
            return original_write_text(path,*args,**kwargs)
        original_write_text=Path.write_text
        with patch('tds_auto.run.capture',return_value=Image.new('RGB',(1920,991))), \
             patch.object(Path,'write_text',fail_progress):
            with self.assertRaises(StopRun) as caught:playback.play(progress=Progress())
        self.assertEqual(caught.exception.kind,'storage')
