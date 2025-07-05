from typing import Iterable, Set
from PIL import Image, ImageDraw

# --------------------------------------------------------------
def draw_annotations(img: Image.Image,
                     annotations: Iterable[dict],
                     color_map: dict[str, str]) -> Set[str]:
    draw = ImageDraw.Draw(img)
    tipos: Set[str] = set()

    for ann in annotations:
        if not ann.get("in_image", True):
            continue
        vec = ann.get("vector")
        if not vec:
            continue

        t = ann["type"]
        cor = color_map.get(t, "white")
        tipos.add(t)

        if len(vec) == 1:                
            x, y = vec[0]; r = 5
            draw.ellipse((x-r, y-r, x+r, y+r), outline=cor, width=2)
        elif len(vec) == 2:                     # bbox (2 cantos)
            (x1, y1), (x2, y2) = vec
            draw.rectangle((x1, y1, x2, y2), outline=cor, width=2)
        else:                                   # polígono
            draw.polygon([tuple(p) for p in vec], outline=cor, width=2)

    return tipos
