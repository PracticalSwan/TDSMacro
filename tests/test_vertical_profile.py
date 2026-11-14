import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tds_auto.calibration import load_profile

class VerticalProfileTests(unittest.TestCase):
    def test_public_golden_scout_strategy_has_verified_vertical_layout(self):
        profile,strategy=load_profile(ROOT/'calibrations/dead_ahead_vertical_nine_v4.json')
        points=[s.args for s in strategy.steps if s.operation=='SpawnTower']
        self.assertEqual((len(strategy.steps),len(points)),(44,9))
        self.assertEqual(len({p[:2] for p in points}),9)
        self.assertTrue(all(p[2]==1 for p in points))
        self.assertEqual([p[0] for p in points[:6]],[855]*5+[825])
        self.assertEqual([p[1] for p in points[:6]],[330,375,420,465,510,555])
        levels={}
        for step in strategy.steps:
            if step.operation=='SpawnTower':levels[step.args[3]]=0
            else:levels[step.args[0]]+=1
        self.assertEqual(levels,{**{i:4 for i in range(1,9)},9:3})
        self.assertEqual(profile['status'],'calibrated_current_setup')
