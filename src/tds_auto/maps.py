"""Read-only identification of the four physical vote-board headers."""
from dataclasses import dataclass
from pathlib import Path
from PIL import Image
import cv2
import numpy as np
import re
from .resources import LocalOCR
from .observer import ink,overlap

@dataclass(frozen=True)
class Board:
    index: int
    box: tuple[int,int,int,int]
    title: str


def voting_floor(frame,require_both=True):
    """Flat voting walkway beside both feet in the verified third-person view."""
    if frame.size!=(1920,991):
        return False
    supported=0
    for box in ((835,680,875,725),(1045,680,1085,725)):
        pixels=np.asarray(frame.crop(box).convert('RGB')).astype(np.int16)
        stone=(pixels.max(axis=2)-pixels.min(axis=2)<30)&(pixels.min(axis=2)>80)
        supported+=int(stone.mean()>=.70)
    return supported==2 if require_both else supported>=1


def title_matches(text,name='Dead Ahead'):
    """Read the complete map phrase within harmless surrounding OCR noise."""
    phrase=re.escape(name.casefold()).replace(r'\ ',r'\s*')
    return bool(re.search(r'(?<![a-z])'+phrase+r'(?:[il])?(?![a-z])',text.casefold()))


def spawn_board_row(frame):
    """Locate the distant four-banner row before walking; no map identity implied."""
    if frame.size!=(1920,991):
        return None
    pixels=np.asarray(frame.convert('RGB')).astype(np.float32)
    red,green,blue=(pixels[:,:,i] for i in range(3))
    mask=np.uint8((red>170)&(red>green*1.4)&(red>blue*1.4))*255
    mask[:240]=0
    # Trim red thumbnail decorations beneath the upper four map-board ribbons.
    # Retain the existing four-header, alignment, and separation checks.
    mask[320:]=0
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    boxes=[]
    for contour in contours:
        x,y,w,h=cv2.boundingRect(contour)
        if 55<=w<=180 and 10<=h<=40 and 3<=w/h<=8 and cv2.contourArea(contour)>600:
            boxes.append((x+w/2,y+h/2,w))
    if len(boxes)!=4:
        return None
    boxes.sort()
    if max(b[1] for b in boxes)-min(b[1] for b in boxes)>12:
        return None
    if any(not 60<=right[0]-left[0]<=200 for left,right in zip(boxes,boxes[1:])):
        return None
    if max(b[2] for b in boxes)>1.7*min(b[2] for b in boxes):
        return None
    return tuple(sum(b[i] for b in boxes)/4 for i in (0,1))


def read_headers(frame):
    """Visible headers for tracking while walking; indices are view-relative."""
    if frame.size!=(1920,991):
        return ()
    pixels=np.asarray(frame.convert('RGB')).astype(np.float32)
    red,green,blue=(pixels[:,:,i] for i in range(3))
    mask=np.uint8((red>170)&(red>green*1.4)&(red>blue*1.4))*255
    mask[:180]=0
    mask[315:]=0  # Header band; lower red thumbnail scenery is not another board.
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    boxes=[]
    for contour in contours:
        x,y,w,h=cv2.boundingRect(contour)
        if w>120 and h>20 and cv2.contourArea(contour)>1000:
            boxes.append((x,y,x+w,y+int(h*.66)))
    if not 1<=len(boxes)<=4:
        return ()
    ocr=LocalOCR()
    def read_title(box):
        sample=frame.crop(box)
        text=ocr.read(sample)
        if not title_matches(text):
            inset=round(sample.width*.09)
            sample=sample.crop((inset,0,sample.width-inset,round(sample.height*.90)))
            candidate=ocr.read(sample)
            if title_matches(candidate):
                return candidate
            # The stylized two-word title can lose Ahead in a whole-line OCR
            # read. Dark glyph groups locate words; read each original crop.
            pixels=np.asarray(sample.convert('RGB'))
            dark=np.uint8(pixels.max(axis=2)<100)*255
            joined=cv2.morphologyEx(dark,cv2.MORPH_CLOSE,np.ones((1,3),np.uint8))
            contours,_=cv2.findContours(joined,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            words=sorted(cv2.boundingRect(c) for c in contours if cv2.boundingRect(c)[2]*cv2.boundingRect(c)[3]>50)
            if len(words)==2:
                candidate=' '.join(ocr.read(sample.crop((max(0,x-2),max(0,y-2),min(sample.width,x+w+2),min(sample.height,y+h+2)))) for x,y,w,h in words)
                if title_matches(candidate):
                    return candidate
        return text
    return tuple(Board(index,box,read_title(box))
                 for index,box in enumerate(sorted(boxes),1))


def read_boards(frame):
    """Only a complete view establishes physical board positions 1..4."""
    boards=read_headers(frame)
    return boards if len(boards)==4 else ()


def visible_target(frame,name='Dead Ahead'):
    targets=[b for b in read_headers(frame) if title_matches(b.title,name)]
    return targets[0] if len(targets)==1 else None


def find_target(boards,name='Dead Ahead'):
    if len(boards)!=4 or sorted(board.index for board in boards)!=[1,2,3,4]:
        return None
    found=[board for board in boards if title_matches(board.title,name)]
    return found[0] if len(found)==1 else None


def vip_target_matches(frame):
    """Confirm the actual hovered card; typed-query OCR is not a game outcome."""
    ocr=LocalOCR()
    card=frame.crop((635,350,752,398))
    return any(title_matches(ocr.read(sample)) for sample in (card,ink(card)))


def vote_prompt(frame,target=None):
    """Locate the generic E keycap, then read its caption at that position."""
    import re
    with Image.open(Path(__file__).resolve().parents[2]/'assets/ui_2191/interaction_e.png') as source:
        template=np.asarray(source.convert('L'))
    crop=frame.crop((750,340,1320,680))
    scores=cv2.matchTemplate(np.asarray(crop.convert('L')),template,cv2.TM_CCOEFF_NORMED)
    _,score,_,(x,y)=cv2.minMaxLoc(scores)
    if score<.93:
        return False
    x+=750;y+=340
    if target is not None and not target.box[0]<=x+template.shape[1]/2<=target.box[2]:
        return False  # A neighbouring board can have the same generic Vote prompt.
    label=frame.crop((x-15,y+55,x+90,y+100))
    ocr=LocalOCR()
    return any('vote' in re.findall(r'[a-z]+',ocr.read(sample).casefold()) for sample in (label,ink(label)))


def vip_prompt(frame):
    """Require the actual Override Map proximity prompt before pressing E."""
    if frame.size!=(1920,991):
        return False
    with Image.open(Path(__file__).resolve().parents[2]/'assets/ui_2191/interaction_e.png') as source:
        template=np.asarray(source.convert('L'))
    crop=frame.crop((900,340,1500,700))
    scores=cv2.matchTemplate(np.asarray(crop.convert('L')),template,cv2.TM_CCOEFF_NORMED)
    _,score,_,(x,y)=cv2.minMaxLoc(scores)
    if score<.93:
        return False
    x+=900;y+=340
    label=frame.crop((x-80,y+55,x+180,y+105))
    ocr=LocalOCR()
    return any(''.join(ocr.read(sample).casefold().split())=='overridemap' for sample in (label,ink(label)))


def badge_is_one(frame,box):
    """Exact UI digit fallback: local OCR often omits a solitary numeral 1."""
    left,top,right,bottom=box
    width,height=right-left,bottom-top
    mask=ink(frame.crop((left+round(width*.25),top+round(height*.15),
                         right-round(width*.25),bottom-round(height*.15))))
    bounds=mask.getbbox()
    if bounds is None:
        return False
    glyph=mask.crop(bounds).resize((24,32)).point(lambda p:255 if p>127 else 0)
    folder=Path(__file__).resolve().parents[2]/'assets/ui_2191'
    for name in ('vote_one.png','vote_one_board4.png','vote_one_replay.png'):
        with Image.open(folder/name) as reference:
            if overlap(glyph,reference.convert('L').point(lambda p:255 if p>127 else 0))>=.90:
                return True
    return False


def solo_vote(frame):
    return vote_players(frame)==1


def vote_players(frame):
    import re
    text=LocalOCR().read(frame.crop((1450,85,1660,130)))
    match=re.fullmatch(r'players\(([0-6])/6\)',''.join(text.casefold().split()))
    return int(match[1]) if match else None
