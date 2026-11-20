"""Deterministic frame-driven user flow; all input terminates at a fake OS."""
import sys
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tds_auto.observer import Observer
from tds_auto.control import GuardedInput, StopRun
from test_control import FakeOS
try:
    from tds_auto.navigation import Navigator
except ImportError:
    Navigator = None


class Clock:
    def __init__(self):
        self.value = 0
    def now(self):
        return self.value
    def sleep(self, seconds):
        self.value += seconds


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Navigator, "navigation controller is not implemented")
        self.platform = FakeOS()
        self.clock = Clock()
        self.observer = Observer()

    def frames(self, names):
        sequence = iter(names)
        last = "unknown"
        def read():
            nonlocal last
            last = next(sequence, last)
            fixture = ("squad_hardcore.png" if last == "squad_hardcore" else
                       "inventory_search_shell_2192.png" if last == "inventory_search_2192" else f"{last}.png")
            path = ROOT / "tests/fixtures" / fixture
            return Image.open(path).convert("RGB") if path.is_file() else Image.new("RGB", (1920, 991))
        return read

    def nav(self, names):
        return Navigator(self.observer, GuardedInput(self.platform.window, self.platform),
                         self.frames(names), self.clock.now, self.clock.sleep)

    def test_complete_menu_flow_stops_at_map_vote(self):
        nav = self.nav(["lobby", "lobby", "play_menu", "play_menu",
                        "play_menu", "play_menu", "survival_menu", "survival_menu",
                        "survival_menu", "survival_menu", "squad_easy", "squad_easy",
                        "squad_easy", "squad_easy", "loading", "loading", "map_vote", "map_vote"])
        result = [nav.step(name) for name in ("open_play", "survival", "easy", "solo")]
        self.assertEqual(result, ["play_menu", "survival_menu", "squad_easy", "map_vote"])
        clicks = [event for event in self.platform.events if event == ("left_down",)]
        self.assertEqual(len(clicks), 4)

    def test_menu_click_follows_two_spaced_confirmations_without_an_extra_blind_wait(self):
        nav=self.nav(['lobby','lobby','play_menu','play_menu'])
        read=nav.read_frame;observed=[];clicked=[]
        def measured_read():observed.append(self.clock.now());return read()
        click=nav.driver.click
        def measured_click(*point):clicked.append(self.clock.now());return click(*point)
        nav.read_frame=measured_read;nav.driver.click=measured_click
        self.assertEqual(nav.step('open_play'),'play_menu')
        self.assertEqual(observed[:2],[0,.2])
        self.assertEqual(clicked,[.2],'A third unobserved delay adds latency without another screen check.')
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_wrong_start_unknown_or_wrong_mode_sends_no_input(self):
        for state in ("unknown", "settings", "map_vote"):
            with self.subTest(state=state):
                with self.assertRaises(StopRun):
                    self.nav([state, state]).step("easy")
        self.assertEqual(self.platform.events, [])

    def test_failed_transition_times_out_without_retrying_click(self):
        nav = self.nav(["lobby"] * 100)
        with self.assertRaisesRegex(StopRun, "Timed out"):
            nav.step("open_play", timeout=2)
        self.assertEqual(self.platform.events.count(("left_down",)), 1)

    def test_wrong_postcondition_stops_without_next_action(self):
        with self.assertRaisesRegex(StopRun, "Unexpected"):
            self.nav(["lobby", "lobby", "settings"]).step("open_play")
        self.assertEqual(self.platform.events.count(("left_down",)), 1)

    def test_emergency_stop_sends_no_input(self):
        self.platform.stopped = True
        with self.assertRaises(StopRun):
            self.nav(["lobby", "lobby"]).step("open_play")
        self.assertEqual(self.platform.events, [])

    def test_unknown_step_cannot_be_used_as_arbitrary_input(self):
        with self.assertRaises(StopRun):
            self.nav(["lobby", "lobby"]).step("purchase")
        self.assertEqual(self.platform.events, [])

    def test_supervised_return_after_defeat_verifies_lobby(self):
        result=self.nav(["defeat","defeat","in_match","loading","loading","lobby","lobby"]).step("return_lobby")
        self.assertEqual(result,"lobby")
        self.assertEqual(self.platform.events.count(("left_down",)),1)

    def test_login_dismissal_and_result_routes_send_one_click(self):
        cases=[('dismiss_login','login_rewards','lobby'),('return_victory','victory','lobby'),
               ('play_again','victory','match_ready'),('restart_match','defeat','match_ready')]
        for transition,source,target in cases:
            with self.subTest(transition=transition):
                self.platform.events.clear()
                self.assertEqual(self.nav([source,source,target,target]).step(transition),target)
                self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_play_again_can_return_to_the_map_vote_room(self):
        result=self.nav(['victory','victory','loading','map_vote','map_vote']).step('play_again')
        self.assertEqual(result,'map_vote')
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_lobby_return_can_arrive_with_login_overlay(self):
        result=self.nav(['victory','victory','loading','login_rewards','login_rewards']).step('return_victory')
        self.assertEqual(result,'login_rewards')
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_inventory_can_remember_the_selected_scout_details(self):
        self.assertEqual(self.nav(['lobby','lobby','inventory_scout','inventory_scout']).step('open_inventory'),'inventory_scout')
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_open_inventory_accepts_verified_search_shell_after_filter_hides_cards(self):
        self.assertEqual(self.nav(['lobby','lobby','inventory_search_2192','inventory_search_2192']).step('open_inventory'),
                         'inventory_search_2192')
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_fixed_scout_card_transition_is_removed(self):
        nav=self.nav(['inventory_list_2192','inventory_list_2192'])
        with self.assertRaises(StopRun):nav.step('scout_details')
        self.assertEqual(self.platform.events,[])

    def test_search_tower_types_query_before_clicking_moved_readable_card(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        clock=Clock()
        self.platform.now=clock.now
        self.platform.sleep=clock.sleep
        frame=Image.new('RGB',(1,1))
        nav=Navigator(self.observer,GuardedInput(self.platform.window,self.platform),
            lambda:frame,now=clock.now,sleep=clock.sleep,ocr=object())
        query=patch('tds_auto.navigation.read_inventory_search_query',
                    side_effect=['crook boss','crook boss','','','boomerang','boomerang'])
        search=patch('tds_auto.navigation.inventory_search_point',
                     side_effect=[(489,190),(489,190),(489,190),(489,190)])
        card=patch('tds_auto.navigation.find_inventory_tower_card',
                   side_effect=[(930,440),(930,440)])
        detail=patch('tds_auto.navigation.read_selected_tower',
                     side_effect=[('boomerang','unequip'),('boomerang','unequip')])
        with patch.object(nav.observer,'observe',return_value=SimpleNamespace(state='inventory_list')), \
             query,search,card,detail:
            self.assertEqual(nav.search_tower('Boomerang'),('boomerang','unequip'))
        downs=[i for i,event in enumerate(self.platform.events) if event[0]=='left_down']
        text_start=next(i for i,event in enumerate(self.platform.events)
                        if event[:2]==('key_down','B'))
        clear=next(i for i,event in enumerate(self.platform.events)
                   if event==('key_down','BACKSPACE'))
        cursor_clear=next(i for i,event in enumerate(self.platform.events)
                          if i>clear and event[:3]==('move',1750,529))
        self.assertEqual(len(downs),2)
        self.assertLess(downs[0],text_start)
        self.assertLess(clear,text_start)
        self.assertLess(clear,cursor_clear)
        self.assertLess(cursor_clear,text_start)
        self.assertLess(text_start,downs[1])

    def test_search_tower_does_not_type_until_field_clear_is_visibly_confirmed(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        clock=Clock()
        self.platform.now=clock.now
        self.platform.sleep=clock.sleep
        frame=Image.new('RGB',(1,1))
        nav=Navigator(self.observer,GuardedInput(self.platform.window,self.platform),
            lambda:frame,now=clock.now,sleep=clock.sleep,ocr=object())
        query=patch('tds_auto.navigation.read_inventory_search_query',return_value='crook boss')
        search=patch('tds_auto.navigation.inventory_search_point',return_value=(489,190))
        with patch.object(nav.observer,'observe',return_value=SimpleNamespace(state='inventory_list')),query,search:
            with self.assertRaisesRegex(StopRun,'did not clear visibly'):
                nav.search_tower('boomerang',timeout=2)
        self.assertEqual(self.platform.events.count(('left_down',)),1)
        self.assertIn(('key_down','BACKSPACE'),self.platform.events)
        self.assertFalse(any(event[:2]==('key_down','B') for event in self.platform.events))

    def test_exact_visible_search_query_selects_without_retyping(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        clock=Clock()
        self.platform.now=clock.now
        self.platform.sleep=clock.sleep
        frame=Image.new('RGB',(1,1))
        nav=Navigator(self.observer,GuardedInput(self.platform.window,self.platform),
            lambda:frame,now=clock.now,sleep=clock.sleep,ocr=object())
        query_reads=[]
        def read_query(*_):
            query_reads.append(len(self.platform.events))
            return 'boomerang'
        query=patch('tds_auto.navigation.read_inventory_search_query',side_effect=read_query)
        search=patch('tds_auto.navigation.inventory_search_point',return_value=(489,190))
        card=patch('tds_auto.navigation.find_inventory_tower_card',side_effect=[(930,440),(930,440)])
        detail=patch('tds_auto.navigation.read_selected_tower',side_effect=[('boomerang','unequip')]*2)
        with patch.object(nav.observer,'observe',return_value=SimpleNamespace(state='inventory_list')),query,search,card,detail:
            self.assertEqual(nav.search_tower('boomerang',timeout=2),('boomerang','unequip'))
        cursor_clear=next(i for i,event in enumerate(self.platform.events) if event[:3]==('move',1750,529))
        self.assertLess(cursor_clear,query_reads[0])
        self.assertGreater(clock.value,0)
        self.assertLess(clock.value,2)
        self.assertEqual(self.platform.events.count(('left_down',)),1)
        self.assertFalse(any(event[0].startswith('key_') for event in self.platform.events))

    def test_blank_capture_during_teleport_is_observed_without_another_click(self):
        from tds_auto.phase1 import BlankCapture
        nav=self.nav(['squad_easy','squad_easy','map_vote','map_vote'])
        original=nav.read_frame
        blank_sent=False
        def read():
            nonlocal blank_sent
            if ('left_down',) in self.platform.events and not blank_sent:
                blank_sent=True
                raise BlankCapture('Transient GDK blank')
            return original()
        nav.read_frame=read
        self.assertEqual(nav.step('solo'),'map_vote')
        self.assertTrue(blank_sent)
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_blank_capture_does_not_allow_an_unverified_source_or_menu_transition(self):
        from tds_auto.phase1 import BlankCapture
        nav=self.nav(['lobby','lobby'])
        def blank():raise BlankCapture('Blank')
        nav.read_frame=blank
        with self.assertRaises(BlankCapture):nav.step('solo')
        self.assertEqual(self.platform.events,[])
        nav=self.nav(['lobby','lobby'])
        original=nav.read_frame
        def after_click():
            if ('left_down',) in self.platform.events:raise BlankCapture('Blank')
            return original()
        nav.read_frame=after_click
        with self.assertRaises(BlankCapture):nav.step('open_play')
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_slow_teleport_can_finish_after_two_minutes_without_reclicking(self):
        from types import SimpleNamespace
        observer=SimpleNamespace(observe=lambda frame:SimpleNamespace(state=frame))
        def read():
            if not ('left_down',) in self.platform.events:return 'squad_easy'
            return 'map_vote' if self.clock.now()>=125 else 'loading'
        nav=Navigator(observer,GuardedInput(self.platform.window,self.platform),read,self.clock.now,self.clock.sleep)
        self.assertEqual(nav.step('solo',timeout=180),'map_vote')
        self.assertEqual(self.platform.events.count(('left_down',)),1)

    def test_hardcore_route_requires_hardcore_modal_before_solo(self):
        nav=self.nav(['survival_menu','survival_menu','squad_hardcore','squad_hardcore',
                      'squad_hardcore','squad_hardcore','loading','loading','map_vote','map_vote'])
        result=[nav.step(name) for name in ('hardcore','solo_hardcore')]
        self.assertEqual(result,['squad_hardcore','map_vote'])
        self.assertEqual(self.platform.events.count(('left_down',)),2)

    def test_easy_squad_cannot_satisfy_hardcore_solo_transition(self):
        with self.assertRaises(StopRun):
            self.nav(['squad_easy','squad_easy']).step('solo_hardcore')
        self.assertEqual(self.platform.events,[])
