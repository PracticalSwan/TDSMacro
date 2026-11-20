"""A temporary OS notification may obscure slot five; never click to dismiss it."""
import sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from tds_auto.session import Session,PLAN_V2_ID
from tds_auto.control import StopRun

COMPLETE=(True,True,True,False,False)
OBSCURED=(True,True,True,False,True)

class FakeSession:
    strategy_id=PLAN_V2_ID
    def __init__(self,frames):
        self.frames=frames
        self.calls=0
        self.seconds=0.0
        self.saved=[]
        self.driver=SimpleNamespace(wait=self.wait)
    def now(self):return self.seconds
    def pause(self):pass
    def wait(self,dt):self.seconds+=dt
    def frame(self,**kwargs):
        self.calls+=1
        return self.frames[min(self.calls-1,len(self.frames)-1)]
    def save_frame(self,frame,name):self.saved.append((frame,name))

class ConfirmInventoryTests(unittest.TestCase):
    def verify(self,frames):
        fake=FakeSession(frames)
        slots={"popup":OBSCURED,"good":COMPLETE,"bad":OBSCURED}
        detail={"good":("farm","unequip")}
        with patch("tds_auto.session.read_slot_occupancy",side_effect=lambda f:slots[f]), \
             patch("tds_auto.session.read_selected_tower",side_effect=lambda f:detail.get(f)):
            try:
                result=Session.confirm_hardcore_inventory(fake)
            except StopRun as exc:
                return fake,exc
        return fake,result

    def test_notification_clears_then_two_independent_reads_succeed(self):
        fake,result=self.verify(["popup","good","good"])
        self.assertEqual(result,(COMPLETE,"good"))
        self.assertEqual(fake.calls,3)
        self.assertEqual(fake.saved,[])

    def test_persistent_obstruction_stops_without_any_external_click(self):
        fake,result=self.verify(["popup"])
        self.assertIsInstance(result,StopRun)
        self.assertEqual(result.kind,"setup")
        self.assertEqual(len(fake.saved),1)
        self.assertLessEqual(fake.seconds,8.25)

    def test_stable_wrong_slot_five_is_never_accepted(self):
        fake,result=self.verify(["bad","bad"])
        self.assertIsInstance(result,StopRun)
        self.assertEqual(len(fake.saved),1)

if __name__=="__main__":
    unittest.main()
