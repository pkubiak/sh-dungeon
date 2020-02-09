from rt.image import Image, Color3i, Color4f
from typing import List


class Font:
    full_color = False

    def __init__(self, path: str, foreground: Color3i, shadow: Color3i, transparency: Color3i, glyphs: List[str], line_height: int, char_spacing: int = 1,):
        self.image = Image.from_pnm(path, transparency=transparency)
        self.glyphs = {}
        
        self.foreground = Color4f(foreground[0]/255, foreground[1]/255, foreground[2]/255, 1.0)
        self.shadow = Color4f(shadow[0]/255, shadow[1]/255, shadow[2]/255, 1.0)

        self.char_spacing = char_spacing
        self.line_height = line_height

        self._detect_glyphs(glyphs)

    def _detect_glyphs(self, glyphs):
        is_empty = []
        for y in range(self.image.height):
        
            is_empty.append(all(self.image[i, y].a == 0 for i in range(self.image.width)))

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

        
        for lineno, line in enumerate(lines):
            line_glyphs = []
            is_empty = []
            glyph_start = None
            for x in range(self.image.width):
                is_empty.append(all(self.image[x, i].a == 0 for i in range(line[0], line[1]+1)))
            is_empty.append(True)
            
            for x in range(len(is_empty)):
                if glyph_start is None and not is_empty[x]:
                    glyph_start = x
                if glyph_start is not None and is_empty[x]:
                    line_glyphs.append((glyph_start, x-1))
                    glyph_start = None
            
            assert len(line_glyphs) == len(glyphs[lineno])

            for c, pos in zip(glyphs[lineno], line_glyphs):
                self.glyphs[c] = self.image.crop((pos[0], line[0], pos[1], line[1]))

# NOTE: https://opengameart.org/content/boxy-bold-font-0
BOXY_BOLD_FONT_PLUS = Font('gfx/font.pnm', foreground=(255,255,255), shadow=(0,0,0), transparency=(0, 255,255), glyphs=[
    '!"#$%&\'()*+,-./',
    '0123456789',
    ':;<=>?@',
    'ABCDEFGHIJKLM',
    'NOPQRSTUVWXYZ',
    '[\\]^_`{|}~',
    'abcdefghijklmn',
    'opqrstuvwxyz'
], char_spacing=-1, line_height=8)

