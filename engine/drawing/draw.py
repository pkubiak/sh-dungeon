from ..rt.image import Image

def _parse_color(color):
    if isinstance(color, int):
        color = (
            (color & 0xff0000) >> 16,
            (color & 0xff00) >> 8,
            color & 0xff
        )
    return color

def clear(image: Image, color=(0,0,0)):
    color = _parse_color(color)

    for y in range(image.height):
        for x in range(image.width):
            image[x, y] = color

def vline(image: Image, x: int, y0: int, y1: int, color):
    color = _parse_color(color)
    assert y0<=y1
    if not 0 <= x < image.width:
        return

    for y in range(y0, y1+1):
        if 0 <= y < image.height:
            image[x, y] = color
