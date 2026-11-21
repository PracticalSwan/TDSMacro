import sys
import unittest
from unittest.mock import patch
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
try:
    from tds_auto.loadout import (read_selected_tower,read_slot_occupancy,
        verify_hardcore_loadout,verify_inventory)
except ImportError:
    verify_inventory=None

class LoadoutTests(unittest.TestCase):
    def frame(self):
        with Image.open(ROOT/'tests/fixtures/inventory_scout_slot1.png') as frame:
            return frame.copy()

    def test_manual_minigunner_search_is_exact_and_does_not_enable_auto_equip(self):
        from tds_auto.loadout import LOADOUT_SEARCH_TOWERS, INVENTORY_SEARCH_TOWERS, read_textually_empty_hotbar
        self.assertIn('minigunner', INVENTORY_SEARCH_TOWERS)
        self.assertNotIn('minigunner', LOADOUT_SEARCH_TOWERS)
        self.assertNotIn('random tower', INVENTORY_SEARCH_TOWERS)
        self.assertFalse(read_textually_empty_hotbar(self.frame()))

    def test_live_golden_scout_only_slot1_is_accepted(self):
        self.assertIsNotNone(verify_inventory,'read-only Golden Scout baseline check is missing')
        self.assertIsNone(verify_inventory(self.frame()))

    def test_portrait_and_skin_changes_do_not_affect_identity(self):
        self.assertIsNotNone(verify_inventory)
        frame=self.frame()
        for x in (1155,1240,1325,1410,1495):
            ImageDraw.Draw(frame).rectangle((x-25,750,x+25,805),fill='magenta')
        self.assertIsNone(verify_inventory(frame))

    def test_v031_golden_perk_requires_text_not_colored_marker(self):
        f=self.frame()
        ImageDraw.Draw(f).rectangle((1180,720,1208,754),fill='black')
        self.assertIsNone(verify_inventory(f,text_only=True))
        ImageDraw.Draw(f).rectangle((1095,505,1174,545),fill='black')
        self.assertIsNotNone(verify_inventory(f,text_only=True))

    def test_missing_golden_marker_is_rejected(self):
        self.assertIsNotNone(verify_inventory)
        frame=self.frame();ImageDraw.Draw(frame).rectangle((1180,720,1208,754),fill='black')
        self.assertIn('Golden',verify_inventory(frame))

    def test_blank_or_wrong_state_is_rejected(self):
        self.assertIsNotNone(verify_inventory)
        self.assertIsNotNone(verify_inventory(Image.new('RGB',(1920,991))))

    def test_current_inventory_state_is_accepted_by_loadout_readers(self):
        with Image.open(ROOT/'tests/fixtures/inventory_list_2192.png') as source:
            frame=source.copy()
        empty=(False,False,False,False,False)
        with patch('tds_auto.loadout.Observer') as observer, \
             patch('tds_auto.loadout._read_slot_occupancy',return_value=empty), \
             patch('tds_auto.loadout._selected_details',return_value=('','')):
            observer.return_value.observe.return_value.state='inventory_list_2192'
            self.assertEqual(read_slot_occupancy(frame),empty)
            self.assertIsNone(read_selected_tower(frame))

    def test_native_scout_equip_hover_retains_exact_button_identity(self):
        # Sanitized native Scout title/button crops without any account data.
        from tds_auto.loadout import inventory_action_point
        with Image.open(ROOT/'tests/fixtures/inventory_scout_hover_equip_native.png') as source:
            frame=source.copy()
        with patch('tds_auto.loadout._inventory_list_open',return_value=True):
            self.assertEqual(inventory_action_point(frame,'equip'),(1256,686))
            self.assertEqual(read_selected_tower(frame),('scout','equip'))
            ImageDraw.Draw(frame).rectangle((1195,643,1334,727),fill='black')
            self.assertIsNone(read_selected_tower(frame))

    def test_inventory_search_click_point_uses_the_readable_search_field(self):
        from tds_auto.loadout import inventory_search_point
        class OCR:
            def read_lines(self,image):
                return [('[ Search I',(142,14,258,35))] if image.size==(351,46) else []
        frame=Image.new('RGB',(1920,991))
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            point=inventory_search_point(frame,None,OCR())
        self.assertEqual(point,(489,190))

    def test_inventory_search_query_distinguishes_placeholder_from_readable_text(self):
        from tds_auto.loadout import read_inventory_search_query
        class OCR:
            text='[ Search I'
            def read_lines(self,image):return [(self.text,(140,14,260,35))]
        frame=Image.new('RGB',(1920,991));ocr=OCR()
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            self.assertEqual(read_inventory_search_query(frame,ocr),'')
            ocr.text='Crook Boss'
            self.assertEqual(read_inventory_search_query(frame,ocr),'crook boss')

    def test_inventory_search_query_ignores_live_magnifier_q_but_rejects_other_extra_text(self):
        from tds_auto.loadout import read_inventory_search_query
        class OCR:
            lines=[('Q',(32,19,50,37)),('boomerang',(129,16,266,36))]
            def read_lines(self,image):return self.lines
        frame=Image.new('RGB',(1920,991));ocr=OCR()
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            self.assertEqual(read_inventory_search_query(frame,ocr),'boomerang')
            ocr.lines.append(('Farm',(275,16,320,36)))
            self.assertIsNone(read_inventory_search_query(frame,ocr))

    def test_occluded_search_placeholder_is_not_mistaken_for_empty(self):
        from tds_auto.loadout import read_inventory_search_query
        class OCR:
            def read_lines(self,image):return [('Seat>h I',(157,15,252,46))]
        with Image.open(ROOT/'tests/fixtures/inventory_search_shell_2192.png') as frame:
            self.assertEqual(read_inventory_search_query(frame,OCR()),'seat h i')

    def test_saved_native_search_caret_keeps_exact_crook_query_readable(self):
        from tds_auto.loadout import inventory_search_point,read_inventory_search_query
        frame=Image.new('RGB',(1920,991))
        with Image.open(ROOT/'tests/fixtures/inventory_crook_search_caret.png') as query:
            frame.paste(query,(289,166))
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            self.assertEqual(read_inventory_search_query(frame),'crook boss')
            self.assertEqual(inventory_search_point(frame,'crook boss'),(487,190))

    def test_filtered_empty_inventory_keeps_its_visible_query_readable(self):
        from tds_auto.loadout import read_inventory_search_query
        with Image.open(ROOT/'tests/fixtures/inventory_search_empty_2192.png') as frame:
            self.assertEqual(read_inventory_search_query(frame),'boomerangerang')

    def test_tower_card_search_uses_exact_readable_name_after_reorder(self):
        from tds_auto.loadout import find_inventory_tower_card
        class OCR:
            def read_lines(self,image):
                if image.size==(351,46):
                    return [('Crook Boss',(130,12,264,34))]
                if image.size==(730,685):
                    return [('Scout',(20,200,80,224)),('Crook Boss',(490,575,640,601))]
                return []
        frame=Image.new('RGB',(1920,991))
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            point=find_inventory_tower_card(frame,'Crook Boss',OCR())
        self.assertEqual(point,(865,808))

    def test_tower_card_search_refuses_unsearched_or_ambiguous_labels(self):
        from tds_auto.loadout import find_inventory_tower_card
        frame=Image.new('RGB',(1920,991))
        class OCR:
            field='Search'
            labels=[('Crook Boss',(100,100,200,125))]
            def read_lines(self,image):
                if image.size==(351,46):return [(self.field,(140,12,240,34))]
                if image.size==(730,685):return self.labels
                return []
        ocr=OCR()
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            self.assertIsNone(find_inventory_tower_card(frame,'Crook Boss',ocr))
            ocr.field='Crook Boss';ocr.labels=[('Crook Boss',(100,100,200,125)),('Crook Boss',(400,500,500,525))]
            self.assertIsNone(find_inventory_tower_card(frame,'Crook Boss',ocr))

    def test_live_inventory_rows_confirm_all_five_empty_slots(self):
        from tds_auto.loadout import INVENTORY_SLOTS
        with Image.open(ROOT/'tests/fixtures/inventory_empty_loadout_slots.png') as source:
            row=source.copy()
        frame=Image.new('RGB',(1920,991))
        frame.paste(row,(INVENTORY_SLOTS[0][0],INVENTORY_SLOTS[0][1]))
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            slots=read_slot_occupancy(frame)
        self.assertEqual(slots,(False,False,False,False,False))

    def test_selected_inventory_details_read_the_lower_hotbar_row(self):
        with Image.open(ROOT/'tests/fixtures/inventory_selected_empty_loadout.png') as source:
            panel=source.copy()
        frame=Image.new('RGB',(1920,991))
        frame.paste(panel,(1110,610))
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            slots=read_slot_occupancy(frame)
        self.assertEqual(slots,(False,False,False,False,False))

    def test_live_hotbar_names_do_not_depend_on_tile_border_or_model(self):
        from tds_auto.loadout import HARDCORE_HOTBAR_POINTS,read_hardcore_hotbar_name

        for slot,expected in ((1,'boomerang'),(2,'crook boss'),(3,'farm')):
            with self.subTest(slot=slot):
                frame=Image.new('RGB',(1920,991))
                x,_=HARDCORE_HOTBAR_POINTS[slot]
                ImageDraw.Draw(frame).rectangle((x-40,890,x+40,974),fill='magenta',outline='green',width=5)
                self.assertIsNone(read_hardcore_hotbar_name(frame,slot))
                with Image.open(ROOT/'tests'/'fixtures'/f'hardcore_hotbar_name_slot_{slot}.png') as tooltip:
                    frame.paste(tooltip,(x+8,749))
                self.assertEqual(read_hardcore_hotbar_name(frame,slot),expected)

    def test_one_pixel_inventory_text_center_jitter_is_not_a_new_button(self):
        from tds_auto.loadout import same_inventory_button
        self.assertTrue(same_inventory_button((1256,732),(1257,731)))
        self.assertFalse(same_inventory_button((1256,732),(1256,695)))
        self.assertFalse(same_inventory_button((1256,732),None))

    def test_native_unequip_label_is_detected_textually(self):
        from tds_auto.loadout import inventory_action_point
        with Image.open(ROOT/'tests/fixtures/inventory_farm_unequip_slot3_live_20261118.png') as image:
            frame=image.copy()
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            self.assertEqual(inventory_action_point(frame,'unequip'),(1256,705))
            self.assertIsNone(inventory_action_point(frame,'equip'))
            self.assertIsNone(inventory_action_point(frame,'invalid'))

    def test_current_equip_button_click_point_comes_from_exact_word(self):
        from tds_auto.loadout import inventory_equip_point
        with Image.open(ROOT/'tests/fixtures/inventory_boomerang_equip_2200_button.png') as f:
            frame=f.copy()
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            self.assertEqual(inventory_equip_point(frame),(1256,732))
            class OCR:
                def read_lines(self,image):
                    return [('UNEQUIP',(206,134,267,150))]
            self.assertIsNone(inventory_equip_point(frame,OCR()))

    def test_explicit_empty_slot_caption_is_not_mistaken_for_a_tower(self):
        from tds_auto.loadout import _slot_occupied,INVENTORY_SLOTS
        class Reader:
            text='EMPTY'
            def read(self,image):return self.text
        frame=Image.new('RGB',(1920,991))
        reader=Reader()
        self.assertIs(_slot_occupied(frame,INVENTORY_SLOTS[0],reader),False)
        reader.text='Scout'
        self.assertIs(_slot_occupied(frame,INVENTORY_SLOTS[0],reader),True)

    def test_auto_equip_requires_explicit_empty_labels_not_blank_graphics(self):
        from tds_auto.loadout import read_textually_empty_hotbar,INVENTORY_SLOTS
        class OCR:
            text='EMPTY'
            def read(self,image):return self.text
        frame=Image.new('RGB',(1920,991))
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            o=OCR()
            self.assertTrue(read_textually_empty_hotbar(frame,o))
            o.text=''
            self.assertFalse(read_textually_empty_hotbar(frame,o))
            o.text='SLOT 1'
            self.assertFalse(read_textually_empty_hotbar(frame,o))

    def test_native_optional_minigunner_lower_tooltip_is_readable(self):
        from tds_auto.loadout import read_hardcore_hotbar_name
        frame = Image.new('RGB',(1920,991), 'black')
        with Image.open(ROOT/'tests/fixtures/hardcore_minigunner_title_lower_native.png') as tip:
            frame.paste(tip,(1068,775))
        self.assertEqual(read_hardcore_hotbar_name(frame,4,optional=True),'minigunner')
        self.assertIsNone(read_hardcore_hotbar_name(frame,4))

    def test_optional_slot4_uses_only_verified_xp_tower_tooltip_text(self):
        from tds_auto.loadout import read_hardcore_hotbar_name, HARDCORE_HOTBAR_POINTS
        class OCR:
            text='Minigunner'
            def read(self, image):
                return self.text
        frame=Image.new('RGB',(1920,991))
        ocr=OCR()
        self.assertIsNone(read_hardcore_hotbar_name(frame,4,ocr))
        self.assertEqual(read_hardcore_hotbar_name(frame,4,ocr,optional=True),'minigunner')
        ocr.text='Settings'
        self.assertIsNone(read_hardcore_hotbar_name(frame,4,ocr,optional=True))
        ocr.text='Military Base'
        self.assertIsNone(read_hardcore_hotbar_name(frame,4,ocr,optional=True))
        ocr.text='Crook Boss'
        self.assertEqual(read_hardcore_hotbar_name(frame,4,ocr,optional=True),'crook boss')
        ocr.text='ABC 123 $'
        self.assertIsNone(read_hardcore_hotbar_name(frame,4,ocr,optional=True))

    def test_optional_hardcore_loadout_requires_exact_fourth_name_and_empty_fifth(self):
        self.assertIsNone(verify_hardcore_loadout(
            ('boomerang','crook boss','farm','minigunner',''),
            optional_tower='minigunner'))
        self.assertIsNotNone(verify_hardcore_loadout(
            ('boomerang','crook boss','farm','minigunner','scout'),
            optional_tower='minigunner'))

    def test_actual_unselected_farm_slot_is_occupied_without_skin_border_identity(self):
        from tds_auto.loadout import INVENTORY_SLOTS
        with Image.open(ROOT/'tests/fixtures/inventory_three_equipped_live_unselected.png') as row:
            frame=Image.new('RGB',(1920,991))
            frame.paste(row,INVENTORY_SLOTS[0][:2])
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list_2192'
            self.assertEqual(read_slot_occupancy(frame),(True,True,True,False,False))

    def test_native_v2200_equip_button_wider_crop_requires_exact_label(self):
        with Image.open(ROOT/'tests/fixtures/inventory_boomerang_equip_2200_button.png') as source:
            frame=source.copy()
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list_2192'
            self.assertEqual(read_selected_tower(frame),('boomerang','equip'))
            self.assertEqual(read_slot_occupancy(frame),(False,False,False,False,False))
            frame.paste('black',(1170,687,1340,765))
            self.assertIsNone(read_selected_tower(frame))

    def test_saved_native_farm_label_and_occupancy_verify(self):
        with Image.open(ROOT/'tests/fixtures/inventory_farm_unequip_slot3_live_20261118.png') as frame:
            self.assertEqual(read_selected_tower(frame),('farm','unequip'))
            self.assertEqual(read_slot_occupancy(frame),(True,True,True,False,False))

    def test_saved_native_crook_title_and_equip_action_verify(self):
        frame=Image.new('RGB',(1920,991))
        with Image.open(ROOT/'tests/fixtures/inventory_crook_title_live_slot2.png') as panel:
            frame.paste(panel,(1076,160))
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            self.assertEqual(read_selected_tower(frame),('crook boss','unequip'))

    def test_crook_title_is_readable_with_bright_lobby_behind_it(self):
        with Image.open(ROOT/'tests/fixtures/inventory_crook_title_bright_lobby.png') as frame, patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            self.assertEqual(read_selected_tower(frame), ('crook boss', 'unequip'))

    def test_farm_inventory_glare_preserves_occupancy_and_exact_equipped_name(self):
        with Image.open(ROOT/'tests/fixtures/inventory_farm_slot3_lobby_glare.png') as frame, patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            self.assertEqual(read_selected_tower(frame),('farm','unequip'))
            self.assertEqual(read_slot_occupancy(frame),(True,True,True,False,False))

    def test_slot_occupancy_is_separate_from_selected_tower_identity(self):
        from tds_auto.loadout import read_selected_tower,read_slot_occupancy
        with Image.open(ROOT/'tests/fixtures/inventory_selected_boomerang_slot1.png') as source:
            panel=source.copy()
        frame=Image.new('RGB',(1920,991))
        frame.paste(panel,(1080,160))
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            occupancy=read_slot_occupancy(frame)
            selected=read_selected_tower(frame)
        self.assertEqual(occupancy,(True,False,False,False,False))
        self.assertEqual(selected,('boomerang','unequip'))

    def test_xp_detail_panel_uses_its_shifted_hotbar_row(self):
        from tds_auto.loadout import read_selected_tower,read_slot_occupancy
        with Image.open(ROOT/'tests/fixtures/inventory_crook_details_with_boomerang_slot1.png') as source:
            panel=source.copy()
        frame=Image.new('RGB',(1920,991))
        frame.paste(panel,(1080,160))
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            occupancy=read_slot_occupancy(frame)
            selected=read_selected_tower(frame)
        self.assertEqual(occupancy,(True,False,False,False,False))
        self.assertEqual(selected,('crook boss','equip'))

    def test_hovered_xp_equip_button_remains_readable(self):
        from tds_auto.loadout import read_selected_tower,read_slot_occupancy
        with Image.open(ROOT/'tests/fixtures/inventory_crook_hovered_equip_boomerang_slot1.png') as source:
            panel=source.copy()
        frame=Image.new('RGB',(1920,991))
        frame.paste(panel,(1080,160))
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            occupancy=read_slot_occupancy(frame)
            selected=read_selected_tower(frame)
        self.assertEqual(occupancy,(True,False,False,False,False))
        self.assertEqual(selected,('crook boss','equip'))

    def test_dynamic_backdrop_does_not_make_an_empty_slot_unknown(self):
        from tds_auto.loadout import read_slot_occupancy
        with Image.open(ROOT/'tests/fixtures/inventory_crook_dynamic_background_slot2.png') as source:
            panel=source.copy()
        frame=Image.new('RGB',(1920,991))
        frame.paste(panel,(1080,160))
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            occupancy=read_slot_occupancy(frame)
        self.assertEqual(occupancy,(True,False,False,False,False))

    def test_farm_detail_uses_higher_hotbar_row_without_xp_label(self):
        from tds_auto.loadout import read_selected_tower,read_slot_occupancy
        with Image.open(ROOT/'tests/fixtures/inventory_farm_filtered_loadout.png') as source:
            panel=source.copy()
        frame=Image.new('RGB',(1920,991))
        frame.paste(panel,(1080,160))
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            occupancy=read_slot_occupancy(frame)
            selected=read_selected_tower(frame)
        self.assertEqual(occupancy,(True,True,False,False,False))
        self.assertEqual(selected,('farm','equip'))

    def test_one_selected_tower_does_not_mask_another_occupied_slot(self):
        with Image.open(ROOT/'tests/fixtures/inventory_selected_boomerang_slot1.png') as source:
            panel=source.copy()
        frame=Image.new('RGB',(1920,991))
        frame.paste(panel,(1080,160))
        draw=ImageDraw.Draw(frame)
        for x in range(1208,1274,8):
            draw.line((x,798,x,858),fill='white',width=2)
        with patch('tds_auto.loadout.Observer') as observer:
            observer.return_value.observe.return_value.state='inventory_list'
            slots=read_slot_occupancy(frame)
        self.assertEqual(slots,(True,True,False,False,False))

    def test_current_low_texture_tower_slot_is_still_occupied(self):
        from tds_auto.loadout import _slot_occupied
        class EmptyOCR:
            def read(self,image):return ''
        with Image.open(ROOT/'tests/fixtures/inventory_hotbar_row_three_filled.png') as row:
            boxes=((0,0,80,80),(84,0,164,80),(167,0,247,80),
                   (250,0,330,80),(333,0,413,80))
            occupied=tuple(_slot_occupied(row,box,EmptyOCR()) for box in boxes)
        self.assertEqual(occupied,(True,True,True,False,False))

    def test_hardcore_loadout_requires_exact_typed_names_and_empty_tail(self):
        self.assertIsNone(verify_hardcore_loadout(('boomerang','crook boss','farm','','')))
        self.assertIsNotNone(verify_hardcore_loadout(('boomerang','','farm','','')))
        self.assertIsNotNone(verify_hardcore_loadout(('boomerang','golden crook boss','farm','','')))
        self.assertIsNotNone(verify_hardcore_loadout(('boomerang','crook boss','farm','scout','')))
