from typing import Tuple
from ..font import Font
from ..rt.image import Color4f, Image

def blend(background: Color4f, foreground: Color4f) -> Color4f:
    if foreground.a == 1.0:
        return foreground
    return (foreground.a * foreground) + (1 - foreground.a) * background


def getbbox(text: str, font: Font) -> Tuple[int, int]:
    pass

def measure_text(text: str, font):
    width = 0
    for char in text:
        width += (2 if char == ' ' else font.glyphs.get(char, font.glyphs['?']).width) + font.char_spacing
    return width

def puttextblock(image: Image, x0, y0, line_width, text, *, font_color, font, shadow_color=None, align='left'):
    pos = start = width = 0
    text += '\n'
    while pos < len(text):
        if text[pos] == ' ':
            new_width = width + 2
        elif text[pos] != '\n':
            new_width = width + font.glyphs.get(text[pos], font.glyphs['?']).width
        new_width += font.char_spacing

        if (text[pos] == '\n') or (new_width >= line_width):
            if align=='left':
                offset=x0
            elif align=='right':
                offset=x0+line_width-width
            elif align=='center':
                offset=x0 +(line_width -width)//2
            puttext(image, offset, y0, text[start: pos], font_color=font_color, font=font, shadow_color=shadow_color)
            y0 += font.line_height
            start = pos if text[pos] != '\n' else pos + 1
            width = (new_width - width)
        else:
            width = new_width

        pos += 1


def puttext(image: Image, x0, y0, text, *, font_color, font: Font, shadow_color = None):
    # if font.full_color:
    #     raise NotImplementedError('Full Color fonts are not supported')
    if isinstance(font_color, int):
        font_color = Color4f.from_int(font_color)
    elif isinstance(font_color, tuple):
        font_color = Color4f.from_tuple(font_color)
    if isinstance(shadow_color, tuple):
        shadow_color = Color4f.from_tuple(shadow_color)

    offset_x = 0
    offset_y = 0
    for char in text:
        if char == '\n':
            offset_x = 0
            offset_y += font.line_height
            continue
        if char == ' ':
            offset_x += 2
            continue
        glyph = font.glyphs.get(char, font.glyphs['?'])

        for y in range(glyph.height):
            for x in range(glyph.width):
                xx, yy = x0+offset_x+x, y0+offset_y+y
                if not (0<=xx<image.width and 0<=yy<image.height):
                    continue
                orig_color = image[xx, yy]
                color = glyph[x, y]
                if color.a == 0.0:
                    continue

                if color == font.shadow:
                    if shadow_color is None:
                        continue
                    color = shadow_color
                    # color = blend(orig_color, shadow_color)
                elif color == font.foreground:
                    color = font_color
                #     # color = blend(orig_color, font_color)
                else:
                    raise ValueError(f"{color}")
                image[x0 + offset_x + x, y0 + offset_y + y] = color

        offset_x += glyph.width + font.char_spacing