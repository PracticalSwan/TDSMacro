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


def voting_floor(frame,require_both=True,for_strafe=False,map_name='Dead Ahead'):
    """Flat voting walkway beside both feet in the verified third-person view."""
    if frame.size!=(1920,991):
        return False
    supported=0
    # Wretched Front uses the same neutral stone, rendered darker in the
    # current map-vote lighting. Keep the Dead Ahead threshold unchanged.
    minimum=45 if map_name=='Wretched Front' else 80
    chroma_limit=60 if map_name=='Wretched Front' else 30
    support_fraction=.55 if map_name=='Wretched Front' and not require_both else .70
    # A sideways step needs ten more pixels of stone toward the feet. The
    # original support regions still govern edge correction and lost-floor stop.
    bottom=735 if for_strafe else 725
    for box in ((835,680,875,bottom),(1045,680,1085,bottom)):
        pixels=np.asarray(frame.crop(box).convert('RGB')).astype(np.int16)
        stone=(pixels.max(axis=2)-pixels.min(axis=2)<chroma_limit)&(pixels.min(axis=2)>minimum)
        supported+=int(stone.mean()>=support_fraction)
    return supported==2 if require_both else supported>=1


def title_matches(text,name='Dead Ahead'):
    """Read the complete map phrase within harmless surrounding OCR noise."""
    phrase=re.escape(name.casefold()).replace(r'\ ',r'\s*')
    return bool(re.search(r'(?<![a-z])'+phrase+r'(?:[il])?(?![a-z])',text.casefold()))


def spawn_board_row(frame):
    """Locate the distant four-banner row before walking; no map identity implied."""
    if frame.size!=(1920,991):
        return None
    pixels=np.asarray(frame.crop((0,240,1920,320)).convert('RGB')).astype(np.float32)
    red,green,blue=(pixels[:,:,i] for i in range(3))
    mask=np.uint8((red>170)&(red>green*1.4)&(red>blue*1.4))*255
    # Trim red thumbnail decorations beneath the upper four map-board ribbons.
    # Retain the existing four-header, alignment, and separation checks.
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    boxes=[]
    for contour in contours:
        x,y,w,h=cv2.boundingRect(contour)
        if 55<=w<=180 and 10<=h<=40 and 3<=w/h<=8 and cv2.contourArea(contour)>600:
            boxes.append((x+w/2,y+240+h/2,w))
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


def read_headers(frame,after_vote=False):
    """Visible headers for tracking while walking; indices are view-relative."""
    if frame.size!=(1920,991):
        return ()
    # Backing away after the vote lowers the ribbon. Keep normal navigation's
    # narrow band; only the post-vote title check needs the taller region.
    bottom=360 if after_vote else 315
    pixels=np.asarray(frame.crop((0,180,1920,bottom)).convert('RGB')).astype(np.float32)
    red,green,blue=(pixels[:,:,i] for i in range(3))
    mask=np.uint8((red>170)&(red>green*1.4)&(red>blue*1.4))*255
    # Same header band; restore client y coordinates after contour detection.
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    boxes=[]
    for contour in contours:
        x,y,w,h=cv2.boundingRect(contour)
        # The Wretched Front voting room uses narrower board ribbons at the
        # closer 1920x991 view; retain them so four-board indices stay physical.
        if w>100 and h>20 and cv2.contourArea(contour)>1000:
            boxes.append((x,y+180,x+w,y+180+int(h*.66)))
    if not 1<=len(boxes)<=4:
        return ()
    ocr=LocalOCR()
    def read_title(box):
        x1,y1,x2,y2=box
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
            # A brief vote-countdown overlap can split the stylized title.
            # Binarize and enlarge only this bounded header crop as a last read.
            enlarged=sample.convert('L').point(lambda value:255 if value>80 else 0)
            enlarged=enlarged.resize((sample.width*2,sample.height*2),Image.Resampling.NEAREST)
            candidate=ocr.read(enlarged)
            if title_matches(candidate):
                return candidate
            # The narrow Wretched Front ribbon needs a tighter, lower-threshold
            # crop to keep the final word from merging into its pink backdrop.
            left=x1+round((x2-x1)*.14)
            top=y1+round((y2-y1)*.18)
            right=x2-round((x2-x1)*.105)
            tight=frame.crop((left,top,right,y2)).convert('L')
            candidate=ocr.read(tight.point(lambda value:255 if value>70 else 0))
            if title_matches(candidate) or title_matches(candidate,'Wretched Front'):
                return candidate
        return text
    return tuple(Board(index,box,read_title(box))
                 for index,box in enumerate(sorted(boxes),1))


def read_boards(frame):
    """Only a complete view establishes physical board positions 1..4."""
    boards=read_headers(frame)
    if len(boards)!=4:
        return ()
    widths=[board.box[2]-board.box[0] for board in boards]
    # At the too-close view, the clipped outer ribbon is much narrower than
    # the others. Keep the farther, balanced distance view accepted.
    if boards[-1].box[2]>=frame.width and max(widths)>1.7*min(widths):
        return ()
    return boards


def visible_target(frame,name='Dead Ahead',after_vote=False,diagnostics=None):
    # Wretched Front ribbons sit lower when the camera is close to the board.
    boards=read_headers(frame,after_vote=after_vote or name=='Wretched Front')
    if diagnostics is not None:
        # Persist only expected map-name tokens, never arbitrary OCR text.
        tokens={token for board in boards for token in re.findall(r'[a-z]+',board.title.casefold())
                if token in {'dead','ahead'}}
        diagnostics.update(header_count=len(boards),title_tokens=[token for token in ('dead','ahead') if token in tokens])
    targets=[b for b in boards if title_matches(b.title,name)]
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
    wretched=target is not None and title_matches(target.title,'Wretched Front')
    if score<(.90 if wretched else .93):
        return False
    x+=750;y+=340
    if target is not None and not target.box[0]<=x+template.shape[1]/2<=target.box[2]:
        return False  # A neighbouring board can have the same generic Vote prompt.
    label=frame.crop((x-65,y+45,x+140,y+110)) if wretched else frame.crop((x-15,y+55,x+90,y+100))
    ocr=LocalOCR()
    return any('vote' in re.findall(r'[a-z]+',ocr.read(sample).casefold()) for sample in (label,ink(label)))


def map_vote_screen(frame):
    """Recover map-vote identity when a hovered button invalidates its template."""
    if frame.size!=(1920,991):
        return False
    ocr=LocalOCR()
    def matches(box,required,count_pattern=None,alternatives=(),red_dominant=False):
        crop=frame.crop(box)
        samples=[crop,ink(crop)]
        if red_dominant:
            pixels=np.asarray(crop.convert('RGB')).astype(np.int16)
            red=(pixels[:,:,0]>pixels[:,:,1]+35)&(pixels[:,:,0]>pixels[:,:,2]+35)
            samples.append(Image.fromarray((red*255).astype(np.uint8)))
        for text in (ocr.read(sample) for sample in samples):
            tokens=set(re.findall(r'[a-z]+',text.casefold()))
            if (required<=tokens
                    and (not alternatives or any(option<=tokens for option in alternatives))
                    and (count_pattern is None or re.search(count_pattern,text))):
                return True
        return False
    return (
        matches((680,75,1280,135),{'vote','for','a','map'})
        and matches((560,170,1370,225),{'vote','a','map','start','timer'},
                    alternatives=({'for'},{'gor'}),red_dominant=True)
        and matches((835,740,1100,818),{'ready'},r'\([01]\s*/\s*1\)')
        and matches((1100,740,1310,818),{'veto'},r'\([01]\s*/\s*1\)')
        and vote_players(frame)==1
    )


def _vip_prompt_evidence(frame):
    """Return the decision plus non-identifying template/caption scalars."""
    if frame.size!=(1920,991):
        return {'confirmed':False,'keycap_score':None,'literal_caption':False}
    with Image.open(Path(__file__).resolve().parents[2]/'assets/ui_2191/interaction_e.png') as source:
        template=np.asarray(source.convert('L'))
    # The native E keycap sits just below y=700 at the last safe VIP step.
    crop=frame.crop((900,340,1500,720))
    scores=cv2.matchTemplate(np.asarray(crop.convert('L')),template,cv2.TM_CCOEFF_NORMED)
    _,score,_,(x,y)=cv2.minMaxLoc(scores)
    score=round(float(score),5)
    if score<.93:
        return {'confirmed':False,'keycap_score':score,'literal_caption':False}
    x+=900;y+=340
    label=frame.crop((x-80,y+55,x+180,y+105))
    ocr=LocalOCR()
    if any(''.join(ocr.read(sample).casefold().split())=='overridemap' for sample in (label,ink(label))):
        return {'confirmed':True,'keycap_score':score,'literal_caption':True}
    # On the late-step layout, nearby prompt text distorts whole-line OCR.
    # Keep both words literal and anchored to the detected E keycap.
    override=frame.crop((x-65,y+55,x+45,y+90))
    map_word=frame.crop((x+45,y+58,x+105,y+90))
    caption_exact=(
        any(''.join(ocr.read(sample).casefold().split())=='override' for sample in (override,ink(override)))
        and any(''.join(ocr.read(sample).casefold().split())=='map' for sample in (map_word,ink(map_word)))
    )
    return {'confirmed':caption_exact,'keycap_score':score,'literal_caption':bool(caption_exact)}


def vip_prompt(frame):
    """Require the actual Override Map proximity prompt before pressing E."""
    return _vip_prompt_evidence(frame)['confirmed']


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
            reference=reference.convert('L').point(lambda p:255 if p>127 else 0)
            # A slightly different view angle can shift the normalized digit
            # by one pixel. Compare on padded canvases so no glyph pixels are
            # clipped while allowing only that small registration drift.
            registered_reference=Image.new('L',(28,36))
            registered_reference.paste(reference,(2,2))
            for dx in (-2,-1,0,1,2):
                for dy in (-2,-1,0,1,2):
                    registered=Image.new('L',(28,36))
                    registered.paste(glyph,(2+dx,2+dy))
                    if overlap(registered,registered_reference)>=.90:
                        return True
    return False


def solo_vote(frame):
    return vote_players(frame)==1


def vote_players(frame):
    import re
    if frame.size!=(1920,991):
        return None
    ocr=LocalOCR()
    values=[]
    boxes=((1450,85,1660,130),(1430,70,1680,145))
    # The current 2.19.2 header renders the leading 1 as a V in the narrow
    # crop on some frames. The wider crop can resolve it while appending nearby
    # OCR noise; conflicting valid counts remain uncertain.
    for box in boxes:
        text=''.join(ocr.read(frame.crop(box)).casefold().split())
        values.extend(int(value) for value in
                      re.findall(r'(?<![a-z0-9])players\(([0-6])/6\)(?![0-9])',text))
    if not values:
        # Low-contrast frames can lose the same count in both raw OCR crops.
        # Bounded grayscale thresholds recover only the literal 0..6/6 token.
        for box in boxes:
            gray=frame.crop(box).convert('L')
            for threshold in (140,170,200):
                image=gray.point(lambda value,cutoff=threshold:255 if value>cutoff else 0)
                text=''.join(ocr.read(image).casefold().split())
                found=re.findall(r'(?<![a-z0-9])players\(([0-6])/6\)(?![0-9])',text)
                if found:
                    values.extend(int(value) for value in found)
                    break
    return values[0] if values and len(set(values))==1 else None
