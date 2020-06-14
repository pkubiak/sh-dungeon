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


def line(canvas: Image, x0, y0, x1, y1, color):
    """
    Bresenham's line algorithm
    @from: https://rosettacode.org/wiki/Bitmap/Bresenham%27s_line_algorithm#Python
    """
    color = _parse_color(color)
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1

    if dx > dy:
        err = dx / 2.0
        while x != x1:
            canvas[x, y] = color
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            canvas[x, y] = color
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy

    canvas[x, y] = color