"""Read-only loadout checks; callers own any separately authorized equip action."""
import re

import cv2
import numpy as np
from PIL import Image

from .observer import Observer, ink
from .resources import LocalOCR

INVENTORY_SLOTS=((1117,626,1197,706),(1201,626,1281,706),(1284,626,1364,706),
                 (1367,626,1447,706),(1450,626,1530,706))
SELECTED_INVENTORY_SLOTS=((1117,789,1197,869),(1201,789,1281,869),(1284,789,1364,869),
                         (1367,789,1447,869),(1450,789,1530,869))
SELECTED_INVENTORY_SLOTS_HIGH=((1117,765,1197,845),(1201,765,1281,845),(1284,765,1364,845),
                              (1367,765,1447,845),(1450,765,1530,845))
INVENTORY_SEARCH_BOX=(289,166,640,212)
INVENTORY_SEARCH_ICON_BOX=(0,0,64,46)
# Screenshot-verified blank area outside the inventory panel; keep the hover cursor off OCR targets.
INVENTORY_CURSOR_CLEAR_POINT=(1750,500)
INVENTORY_CARD_GRID=(300,220,1030,905)
INVENTORY_TOWER_NAME=(1076,161,1370,206)
INVENTORY_TOWER_NAME_TIGHT=(1080,160,1250,215)
INVENTORY_EQUIP_BUTTON=(1190,675,1322,738)
INVENTORY_XP_LABEL=(1080,545,1195,590)
HARDCORE_LOADOUT=('boomerang','crook boss','farm','','')
HARDCORE_TOWERS=frozenset(HARDCORE_LOADOUT[:3])
LOADOUT_SEARCH_TOWERS=HARDCORE_TOWERS|{'scout'}
# Manual, exact-text inventory selection may inspect a verified slot-4 Minigunner.
INVENTORY_SEARCH_TOWERS=LOADOUT_SEARCH_TOWERS|{'minigunner'}
# Evolution sources and evolved towers documented in current Tower Evolution.
# A free-form OCR caption is never sufficient to authorize optional placement.
OPTIONAL_EXP_TOWERS={
    'scout':'Scout','minigunner':'Minigunner','crook boss':'Crook Boss',
    'shotgunner':'Shotgunner',
    'operator':'Operator','juggernaut':'Juggernaut',
    'kingpin':'Kingpin','enforcer':'Enforcer',
}

INVENTORY_LIST_STATES=frozenset({'inventory_list','inventory_list_2192','inventory_search_2192','inventory_scout'})
HARDCORE_HOTBAR_POINTS={1:(760,925),2:(865,925),3:(960,925),4:(1060,925),5:(1154,925)}


def _inventory_list_open(frame):
    return frame.size==(1920,991) and Observer().observe(frame).state in INVENTORY_LIST_STATES


def _slot_name(text):
    return ' '.join(re.sub(r'[^a-z0-9 ]',' ',text.casefold()).split())


def _search_field_lines(frame, ocr):
    crop = frame.crop(INVENTORY_SEARCH_BOX)
    pixels = np.array(crop.convert('RGB'))
    text_start = INVENTORY_SEARCH_ICON_BOX[2]
    # The blinking caret is one pixel wide and taller than the search glyphs.
    bright = pixels[8:40, text_start:].min(axis=2) >= 190
    columns = np.flatnonzero(bright.sum(axis=0) >= 24)
    if len(columns) == 1:
        caret = text_start + columns[0]
        pixels[8:40, caret] = pixels[5, caret]
        crop = Image.fromarray(pixels)
    return ocr.read_lines(crop)


def inventory_search_point(frame,current_query=None,ocr=None):
    """Locate the visible search text before entering or replacing a query."""
    if not _inventory_list_open(frame):
        return None
    reader=ocr or LocalOCR()
    x0,y0,x1,y1=INVENTORY_SEARCH_BOX
    lines=_search_field_lines(frame,reader)
    target=None if current_query in (None,'') else _slot_name(current_query)
    matches=[]
    for text,box in lines:
        normalized=_slot_name(text)
        if (target is None and 'search' in normalized.split()) or normalized==target:
            left,top,right,bottom=box
            if 0<=left<right<=x1-x0 and 0<=top<bottom<=y1-y0:
                matches.append((x0+(left+right)//2,y0+(top+bottom)//2))
    return matches[0] if len(matches)==1 else None


def read_inventory_search_query(frame,ocr=None):
    """Return the visible query, an empty string for the Search placeholder, or None."""
    if not _inventory_list_open(frame):
        return None
    lines=_search_field_lines(frame,ocr or LocalOCR())
    # In the current inventory UI, OCR sometimes reads the magnifier as a
    # separate "Q". Ignore only that token inside the screenshot-verified icon
    # area; any other extra label keeps the query ambiguous.
    x0,y0,x1,y1=INVENTORY_SEARCH_ICON_BOX
    lines=[(text,box) for text,box in lines if not (
        _slot_name(text)=='q' and len(box)==4
        and x0<=box[0]<box[2]<=x1 and y0<=box[1]<box[3]<=y1)]
    if len(lines)!=1:
        return None
    text=_slot_name(lines[0][0])
    return '' if 'search' in text.split() else text


def find_inventory_tower_card(frame,tower,ocr=None):
    """Locate one exact card label only after that same name is in Search."""
    if not _inventory_list_open(frame):
        return None
    target=_slot_name(tower)
    if not target:
        return None
    reader=ocr or LocalOCR()
    search_lines=_search_field_lines(frame,reader)
    if sum(_slot_name(text)==target for text,_ in search_lines)!=1:
        return None
    x0,y0,x1,y1=INVENTORY_CARD_GRID
    matches=[]
    for text,box in reader.read_lines(frame.crop(INVENTORY_CARD_GRID)):
        left,top,right,bottom=box
        if (_slot_name(text)==target and 0<=left<right<=x1-x0
            and 0<=top<bottom<=y1-y0):
            matches.append((x0+(left+right)//2,y0+(top+bottom)//2))
    return matches[0] if len(matches)==1 else None


def _slot_occupied(frame,box,ocr):
    crop=frame.crop(box)
    caption=_slot_name(ocr.read(crop))
    if caption == 'empty':
        return False
    if caption:
        return True
    pixels=np.asarray(crop.convert('L'))[8:-8,8:-8]
    gray=cv2.GaussianBlur(pixels,(3,3),0)
    edge_fraction=float((cv2.Canny(gray,50,100)>0).mean())
    edge_energy=float(cv2.Laplacian(gray,cv2.CV_64F).var())
    # Empty slot tiles reveal a moving blurred lobby backdrop; sparse edges
    # remain empty when local detail energy is still very low.
    if edge_fraction<=.02 and edge_energy<=16:
        return False
    # An occupied Farm tile in the current unselected 2.19.2 tray has
    # edge_fraction=.0776 and energy=129.8. Genuine empty tiles in that same
    # live view have nearly zero edges and energy below 2. Preserve the high
    # energy requirement and fail closed for all intermediate cases.
    if edge_fraction>=.075 and edge_energy>=100:
        return True
    return None


def _selected_details(frame,ocr):
    name=_slot_name(ocr.read(frame.crop(INVENTORY_TOWER_NAME_TIGHT)))
    if name not in INVENTORY_SEARCH_TOWERS:
        title=frame.crop(INVENTORY_TOWER_NAME)
        name=_slot_name(ocr.read(title))
        if name not in INVENTORY_SEARCH_TOWERS:
            name=_slot_name(ocr.read(ink(title)))
    action=_slot_name(ocr.read(frame.crop(INVENTORY_EQUIP_BUTTON)))
    if action not in {'equip','unequip'}:
        # The current green Equip lettering can lose its final glyph inside
        # the narrow crop. Still require an exact label from a complete button.
        action=_slot_name(ocr.read(frame.crop((1170,687,1340,765))))
    if action not in {'equip','unequip'}:
        # Hover moves the entire action label above the tight crops. Keep
        # the existing exact-text, bounded-position and uniqueness checks.
        options=[candidate for candidate in ('equip','unequip')
                 if inventory_action_point(frame,candidate,ocr) is not None]
        action=options[0] if len(options)==1 else ''
    return name,action


def _slot_boxes(frame,ocr,name,action):
    if action not in {'equip','unequip'}:
        return INVENTORY_SLOTS
    xp_label=_slot_name(ocr.read(frame.crop(INVENTORY_XP_LABEL)))
    high_row=name=='farm' or xp_label.startswith('lv ')
    return SELECTED_INVENTORY_SLOTS_HIGH if high_row else SELECTED_INVENTORY_SLOTS


def _read_slot_occupancy(frame,ocr,action=None,name=None):
    if action is None or name is None:
        selected_name,selected_action=_selected_details(frame,ocr)
        name=selected_name if name is None else name
        action=selected_action if action is None else action
    boxes=_slot_boxes(frame,ocr,name,action)
    occupied=tuple(_slot_occupied(frame,box,ocr) for box in boxes)
    return None if any(value is None for value in occupied) else occupied


def read_slot_occupancy(frame):
    """Non-authoritative visual diagnostics only; never authorize equipment."""
    if not _inventory_list_open(frame):
        return None
    return _read_slot_occupancy(frame,LocalOCR())


def inventory_action_point(frame,action,ocr=None):
    """Find the exact EQUIP or UNEQUIP text on the selected panel only."""
    if action not in {'equip','unequip'} or not _inventory_list_open(frame):
        return None
    area=(1020,590,1420,790)
    words=(ocr or LocalOCR()).read_lines(frame.crop(area))
    positions=[]
    for text,box in words:
        if _slot_name(text)!=action:
            continue
        x=(box[0]+box[2])//2+area[0]
        y=(box[1]+box[3])//2+area[1]
        if 1050<=x<=1370 and 600<=y<=780:
            positions.append((x,y))
    return positions[0] if len(positions)==1 else None


def inventory_equip_point(frame,ocr=None):
    return inventory_action_point(frame,'equip',ocr)

def same_inventory_button(first,second):
    '''Permit only tiny OCR center jitter inside the same text-verified button.'''
    return (first is not None and second is not None and
            all(abs(a-b)<=3 for a,b in zip(first,second)))



def read_textually_empty_hotbar(frame,ocr=None):
    '''Only explicit EMPTY labels can authorize auto-equip, never blank tiles.'''
    if not _inventory_list_open(frame):
        return False
    reader=ocr or LocalOCR()
    return all(_slot_name(reader.read(frame.crop(box)))=='empty'
               for box in INVENTORY_SLOTS)


def read_selected_tower(frame,ocr=None):
    """Return the exact selected tower label and Equip/Unequip state, or None."""
    if not _inventory_list_open(frame):
        return None
    name,action=_selected_details(frame,ocr or LocalOCR())
    if name not in INVENTORY_SEARCH_TOWERS or action not in {'equip','unequip'}:
        return None
    return name,action


def read_hardcore_hotbar_name(frame,slot,ocr=None,*,optional=False):
    """Read the native tooltip title from an already-hovered match hotbar slot."""
    if frame.size!=(1920,991) or slot not in HARDCORE_HOTBAR_POINTS:
        return None
    x,_=HARDCORE_HOTBAR_POINTS[slot]
    reader=ocr or LocalOCR()
    boxes=[(x+8,758,x+164,793),(x+8,749,x+187,800)]
    if optional:
        boxes.append((x+8,775,x+187,815))  # native lower tooltip layout
    for box in boxes:
        title=frame.crop(box)
        for sample in (title,ink(title)):
            name=_slot_name(reader.read(sample))
            if name in (OPTIONAL_EXP_TOWERS if optional else LOADOUT_SEARCH_TOWERS):
                return name
    return None


def verify_hardcore_loadout(slots, *, optional_tower=None, require_optional=None):
    if not isinstance(slots,tuple) or len(slots)!=5:
        return 'All five equipped slots must be readable.'
    if (require_optional is not None and require_optional != bool(optional_tower)) or (optional_tower and optional_tower not in OPTIONAL_EXP_TOWERS):
        return 'XP strategy requires a known tower in slot 4; three-tower strategy requires slot 4 empty.'
    expected=(HARDCORE_LOADOUT[:3]+(optional_tower,'')) if optional_tower else HARDCORE_LOADOUT
    if slots!=expected:
        return 'Require Boomerang, regular Crook Boss, Farm and the verified optional slot state.'
    return None


def verify_inventory(frame,*,text_only=False):
    """Verify Scout/Golden/equipped/slot-1 UI; hotbar prices check empty slots.

    Tower portraits and model appearances are deliberately never inspected.
    """
    if Observer().observe(frame).state!='inventory_scout':
        return 'Expected the Scout inventory details.'
    ocr=LocalOCR()
    if text_only and _slot_name(ocr.read(frame.crop(INVENTORY_TOWER_NAME_TIGHT)))!='scout':
        return 'The readable selected tower name is not Scout.'
    if ocr.read(frame.crop((1190,665,1320,701))).casefold()!='unequip':
        return 'The selected Scout is not confirmed equipped.'
    if ocr.read(frame.crop((1095,505,1174,545))).casefold()!='golden':
        return 'Golden Scout label is not confirmed.'
    if not text_only:
        # Historical v0.3.0 fallback only. v0.3.1 relies exclusively on text.
        marker=list(frame.crop((1180,720,1208,754)).convert('RGB').get_flattened_data())
        if sum(r>180 and g>130 and b<180 and r>=g for r,g,b in marker)<40:
            return 'Golden marker on equipped slot 1 is missing.'
    return None
