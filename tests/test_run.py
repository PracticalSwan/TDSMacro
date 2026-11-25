import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tds_auto.strategy import Step
from tds_auto.resources import Hud
from tds_auto.control import StopRun
try:
    from tds_auto.run import Progress,run_sequence
except ImportError:
    Progress=None


class GameBoundary:
    def __init__(self,fail=False):
        self.commands=[]
        self.fail=fail
    def place(self,point,slot,count,*,tower_id):
        self.commands.append(('place',point,slot,count,tower_id))
        return Hud(500,count+1,'Scout',0,150,1)
    def upgrade(self,point,level,count,*,tower_id):
        if self.fail:
            raise StopRun('unconfirmed')
        self.commands.append(('upgrade',point,level,count,tower_id))
        return Hud(350,count,'Scout',level+1,600,1)


class RunTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Progress,'ordered single-match coordinator is not implemented')
        self.strategy=SimpleNamespace(steps=(Step('SpawnTower',(855,330,2,1)),Step('UpgradeTower',(1,)),Step('SpawnTower',(1020,330,2,2))))

    def test_operations_keep_order_and_use_adjusted_points(self):
        game=GameBoundary(); progress=Progress()
        run_sequence(self.strategy,game,progress,lambda p:(p[0]+5,p[1]-4),3)
        self.assertEqual(game.commands,[('place',(860,326),2,0,1),('upgrade',(860,326),0,1,1),('place',(1025,326),2,1,2)])
        self.assertEqual((progress.next_step,progress.count,progress.levels),(3,2,{1:1,2:0}))

    def test_unconfirmed_action_does_not_advance_saved_progress(self):
        game=GameBoundary(fail=True); progress=Progress()
        with self.assertRaises(StopRun):
            run_sequence(self.strategy,game,progress,lambda p:p,3)
        self.assertEqual((progress.next_step,progress.count,progress.levels),(1,1,{1:0}))

    def test_operation_limit_does_not_silently_loop(self):
        game=GameBoundary(); progress=Progress()
        run_sequence(self.strategy,game,progress,lambda p:p,1)
        self.assertEqual(progress.next_step,1)
        self.assertEqual(len(game.commands),1)

    def test_confirmed_maxed_noop_advances_step_but_not_level(self):
        game=GameBoundary()
        game.upgrade=lambda p,l,c,**kwargs: Hud(1000,c,'Scout',4,None,16,False,True)
        progress=Progress(1,1,{1:4})
        run_sequence(self.strategy,game,progress,lambda p:p,1)
        self.assertEqual((progress.next_step,progress.levels),(2,{1:4}))

    def test_unconfirmed_noop_does_not_advance(self):
        game=GameBoundary()
        game.upgrade=lambda p,l,c,**kwargs: Hud(1000,c,'Scout',l,600,16)
        progress=Progress(1,1,{1:1})
        with self.assertRaises(StopRun):run_sequence(self.strategy,game,progress,lambda p:p,1)
        self.assertEqual(progress.next_step,1)

    def test_resume_progress_must_match_the_exact_source_prefix(self):
        from tds_auto.run import validate_progress
        validate_progress(self.strategy,Progress(2,1,{1:1}))
        for progress in (Progress(2,1,{1:4}),Progress(1,1,{2:0}),Progress(0,1,{1:0}),Progress(99,0,{})):
            with self.assertRaises(StopRun):
                validate_progress(self.strategy,progress)
