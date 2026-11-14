"""Read-only check of the observed inventory baseline, with no auto-equipping."""
from .observer import Observer
from .resources import LocalOCR


def verify_inventory(frame):
    """Verify Scout/Golden/equipped/slot-1 UI; hotbar prices check empty slots.

    Tower portraits and model appearances are deliberately never inspected.
    """
    if Observer().observe(frame).state!='inventory_scout':
        return 'Expected the Scout inventory details.'
    ocr=LocalOCR()
    if ocr.read(frame.crop((1190,665,1320,701))).casefold()!='unequip':
        return 'The selected Scout is not confirmed equipped.'
    if ocr.read(frame.crop((1095,505,1174,545))).casefold()!='golden':
        return 'Golden Scout label is not confirmed.'
    marker=list(frame.crop((1180,720,1208,754)).convert('RGB').get_flattened_data())
    if sum(r>180 and g>130 and b<180 and r>=g for r,g,b in marker)<40:
        return 'Golden marker on equipped slot 1 is missing.'
    return None
