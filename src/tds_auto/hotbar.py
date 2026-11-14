"""Verify the observed tower-price anchors before sending any hotbar key."""
from pathlib import Path
from dataclasses import dataclass
from PIL import Image,ImageOps
from .observer import overlap
from .resources import LocalOCR,parse_cash

BOXES=((733,947,797,973),(833,947,898,973))


def green_ink(image,min_green=110):
    image=image.convert('RGB')
    mask=Image.new('L',image.size)
    mask.putdata([255 if g>min_green and g>r*1.35 and g>b*1.2 else 0
                  for r,g,b in image.get_flattened_data()])
    return mask


@dataclass(frozen=True)
class Hotbar:
    valid: bool
    price: int | None = None


def read_hotbar(frame,slot=1):
    if frame.size!=(1920,991):
        return Hotbar(False)
    folder=Path(__file__).resolve().parents[2]/'assets/ui_2191'
    if slot==1:
        crop=frame.crop((733,947,798,973))
        ocr=LocalOCR()
        values=[ocr.read(sample) for sample in (crop,green_ink(crop),ImageOps.invert(crop.convert('RGB')))]
        parsed=[parse_cash(value) for value in values if value.startswith('$')]
        agreed={value for value in parsed if value is not None and parsed.count(value)>=2}
        price=next(iter(agreed)) if len(agreed)==1 else None
        # Price lettering is bright green; dim terrain through transparent empty
        # slots is not an equipped tower. Keep the extra-price rejection.
        empty=all(sum(green_ink(frame.crop((733+i*100,947,798+i*100,973)),min_green=180).get_flattened_data())<255*10 for i in range(1,5))
        return Hotbar(price is not None and empty,price)
    if slot!=2:
        return Hotbar(False)
    # Historical slot-2 diagnostic profile, never the new lobby baseline.
    for index,box in enumerate(BOXES):
        with Image.open(folder/f'hotbar_price_{index}.png') as template:
            if overlap(green_ink(frame.crop(box)),green_ink(template))<0.90:
                return Hotbar(False)
    return Hotbar(True,250)


def tower_hotbar(frame,slot=1):
    return read_hotbar(frame,slot).valid
