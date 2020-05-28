"""
Module for handling Bitmap Fonts stored in PNM files.

TBA

"""
import re
from typing import List, Optional
from .rt.image import Image, Color3i, Color4f



class Font:
    COLOR_REGEX = re.compile(r'\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)')

    @classmethod
    def _parse_color(self, text: str):
        return tuple(map(int, self.COLOR_REGEX.fullmatch(text).groups()))

    def __init__(self, path: str): #, foreground: Color3i, transparency: Color3i, glyphs: List[str], line_height: int, shadow: Optional[Color3i] = None, char_spacing: int = 1,):
        image = Image.load(path)

        assert 'Transparency' in image.meta
        transparency = Color4f.from_hex(image.meta['Transparency'])
        image = Image.load(path, transparency=transparency.as_3i)

        limit = 0
        while f"Glyphs_{limit}" in image.meta: limit += 1
        glyphs = [image.meta[f"Glyphs_{i}"] for i in range(limit)]

        self.glyphs = self._detect_glyphs(image, glyphs)
        # self.glyphs = {}
        
        self.foreground = Color4f.from_hex(image.meta['Foreground'])
        print(self.foreground)
        self.shadow = Color4f.from_hex(image.meta['Shadow']) if 'Shadow' in image.meta else None 
        
        print(self.shadow)
        self.char_spacing = int(image.meta.get('CharSpacing', 0))
        self.line_height = int(image.meta.get('LineHeight', 0))

    @classmethod
    def _detect_glyphs(cls, image, glyphs):
        is_empty = []
        for y in range(image.height):
        
            is_empty.append(all(image[i, y].a == 0 for i in range(image.width)))

        is_empty.append(True) # add guardian

        line_start = None
        lines = []
        for i in range(len(is_empty)):
            if not is_empty[i] and line_start is None:
                line_start = i
            if is_empty[i] and line_start is not None:
                lines.append((line_start, i-1))
                line_start = None

        assert len(lines) == len(glyphs)

        chars = {}
        for lineno, line in enumerate(lines):
            line_glyphs = []
            is_empty = []
            glyph_start = None
            for x in range(image.width):
                is_empty.append(all(image[x, i].a == 0 for i in range(line[0], line[1]+1)))
            is_empty.append(True)

            for x in range(len(is_empty)):
                if glyph_start is None and not is_empty[x]:
                    glyph_start = x
                if glyph_start is not None and is_empty[x]:
                    line_glyphs.append((glyph_start, x-1))
                    glyph_start = None
            
            assert len(line_glyphs) == len(glyphs[lineno]), f"Line #{lineno} expected to has {len(glyphs[lineno])} glyphs, but it has {len(line_glyphs)}"

            for c, pos in zip(glyphs[lineno], line_glyphs):
                chars[c] = image.crop((pos[0], line[0], pos[1], line[1]))

        return chars

# NOTE: https://opengameart.org/content/boxy-bold-font-0
# BOXY_BOLD_FONT_PLUS = Font('gfx/font.pnm', foreground=(255,255,255), shadow=(0,0,0), transparency=(0, 255,255), glyphs=[
#     '!"#$%&\'()*+,-./',
#     '0123456789',
#     ':;<=>?@',
#     'ABCDEFGHIJKLM',
#     'NOPQRSTUVWXYZ',
#     '[\\]^_`{|}~',
#     'abcdefghijklmn',
#     'opqrstuvwxyz'
# ], char_spacing=-1, line_height=8)


# MAGIC_FONT = Font('gfx/magic_font.pnm', foreground=(0, 0, 0), transparency=(0, 255,255), glyphs=[
#     '.ABCDEFGHIJKLMNO',
#     'PQRSTUVWXYZ()',
#     '-abcdefghijklmnopqrstuvwxyz<>',
# ], line_height=12)