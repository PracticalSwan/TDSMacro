"""Bounded, read-only camera checkpoint rereads; no movement on uncertainty."""
import sys,unittest
from pathlib import Path
from unittest.mock import Mock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from tds_auto.hardcore_match import HardcoreMatchV2
class TimedWait:
    def __init__(self):
        self.time=0.0
        self.moves=[]
    def wait(self,s):
        self.time+=s
    def key(self,*args):
        self.moves.append(("key",args))
    def orbit(self,*args):
        self.moves.append(("orbit",args))
class RouteReadbackTests(unittest.TestCase):
    def worker(self,valid_from):
        driver=TimedWait()
        worker=HardcoreMatchV2.__new__(HardcoreMatchV2)
        worker.driver=driver
        worker.session=Mock()
        worker.session.now.side_effect=lambda:driver.time
        worker.session.pause.return_value=None
        worker.session.frame.return_value="terrain"
        worker.route_ready=Mock(return_value=True)
        worker.camera=Mock()
        worker.camera.estimate.return_value=None
        route=Mock()
        route.matching_steps.side_effect=lambda frame,indices:[2] if driver.time >= valid_from else []
        return worker,route,driver
    def test_late_stable_terrain_is_verified_twice_without_movement(self):
        worker,route,driver=self.worker(5.4)
        frame,pose,index,ready=worker.settled_camera_view(route,(2,))
        self.assertEqual((frame,pose,index,ready),("terrain",None,2,True))
        self.assertGreaterEqual(driver.time,5.6)
        self.assertLess(driver.time,8)
        self.assertEqual(driver.moves,[])
    def test_persistently_unknown_terrain_stops_after_bounded_passive_reads(self):
        worker,route,driver=self.worker(30)
        frame,pose,index,ready=worker.settled_camera_view(route,(2,))
        self.assertEqual((frame,pose,index,ready),("terrain",None,None,True))
        self.assertGreaterEqual(driver.time,8)
        self.assertLess(driver.time,8.5)
        self.assertEqual(driver.moves,[])
if __name__=="__main__":
    unittest.main()
