import time
import sys
from rt.image import Image
from typing import Tuple

wrt = sys.stdout.write

def lighten(color, scale):
    r, g, b, blink = color

    factor = 1.0 + scale
    return (
        max(min(255, int(r * factor)), 0),
        max(min(255, int(g * factor)), 0),
        max(min(255, int(b * factor)), 0),
        blink
    )
 
DEFAULT_FONT={
    ' ': (1, [0, 0, 0, 0, 0]),
    '0': (3, [7, 5, 5, 5, 7]),
    '1': (2, [3, 1, 1, 1, 1]),
    '2': (3, [7, 1, 7, 4, 7]),
    '3': (3, [7, 1, 3, 1, 7]),
    '4': (3, [4, 5, 7, 1, 1]),
    '5': (3, [7, 4, 7, 1, 7]),
    '6': (3, [7, 4, 7, 5, 7]),
    '7': (3, [7, 1, 1, 1, 1]),
    '8': (3, [7, 5, 7, 5, 7]),
    '9': (3, [7, 5, 7, 1, 7]),
    'W': (5, [17, 17, 21, 21, 10]),
    'E': (3, [7, 4, 6, 4, 7]),
    'N': (4, [9, 13, 15, 11, 9]),
    'S': (3, [3, 4, 2, 1, 6]),
    '/': (3, [1, 1, 2, 4, 4]),
    '*': (7, [
        0b0110110,
        0b1111111,
        0b0111110,
        0b0011100,
        0b0001000,
    ]),
}

class Screen:
    BLOCK = '  '#██'
    
    def __init__(self, width, height, offset=(0,0)):
        self.width = width
        self.height = height
        self.offset = offset

        self.data = [
            [(0,0,0, False) for _ in range(width)] for _ in range(height)
        ]

        wrt("\033[?47h")  # save current screen
        wrt("\033[?25l")  # Hide cursor
        sys.stdout.flush()

    def close(self):
        wrt("\033[?47l")  # save current screen
        wrt("\033[?25h")  # Show cursor
        sys.stdout.flush()

    def __setitem__(self, coords, value):
        x, y = coords
        assert isinstance(value, tuple) and 3 <= len(value) <= 4
        r, g, b, *blink = value

        if len(blink) == 0 or blink[0] == False:
            blink= False
        else:
            blink = True

        assert (0<=r<=255) and (0<=g<=255) and (0<=b<=255)

        self.data[y][x] = (r, g, b, bool(blink))
    
    def line(self, x0, y0, x1, y1, color):
        """
        Bresenham's line algorithm
        @from: https://rosettacode.org/wiki/Bitmap/Bresenham%27s_line_algorithm#Python
        """
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1

        if dx > dy:
            err = dx / 2.0
            while x != x1:
                self[x, y] = color
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                self[x, y] = color
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy   

        self[x, y] = color
    

    def hline(self, x0, x1, y, color):
        if x1<0:
            x1+=self.width
        for x in range(x0, x1+1):
            self[x, y] = color

    def vline(self, x, y0, y1, color):
        if y1<0:
            y1+=self.height
        for y in range(y0, y1+1):
            self[x,y] = color
            
    def rect(self, x0, y0, x1, y1, color):
        """Draw rectangle"""
        if x1 < 0:
            x1 += self.width 
        if y1 < 0:
            y1 += self.height

        for x in range(x0, x1+1):
            self[x, y0] = self[x, y1] = color
        for y in range(y0, y1+1):
            self[x0, y] = self[x1, y] = color

    def fullrect(self, x0, y0, x1, y1, color):
        if x1 < 0:
            x1 += self.width 
        if y1 < 0:
            y1 += self.height

        for x in range(x0, x1+1):
            for y in range(y0, y1+1):
                self[x, y] = color

    def puttext(self, x0, y0, text, color, font=DEFAULT_FONT):
        offset = 0
        for char in text:
            length, glyph = font[char]
            for y in range(len(glyph)):
                for x in range(length):
                    if glyph[y] & (1<<(length-1-x)):
                        self[offset+x+x0, y+y0] = color
            offset += length + 1


    def sync(self):
        wrt("\033[2J")  # clear entire screen
        for y in range(self.height):
            wrt("\033[%d;%dH" % (1 + y+self.offset[1], 1 + 2 * self.offset[0]))  # move cursor to start of yth row
            for x in range(self.width):
                r, g, b, blink = self.data[y][x]

                # if blink:
                #     r2, g2, b2, _ = lighten((r, g, b, True),0.6)
                #     wrt(f"\033[5m\033[48;2;{r2};{g2};{b2}m") # blinking color

                wrt(f"\033[48;2;{r};{g};{b}m%s\033[0m" % self.BLOCK)  # print block in given RGB color
            sys.stdout.flush()
        wrt("\033[H")
        sys.stdout.flush()

    def imshow(self, image: Image, offset: Tuple[int, int] = (0, 0)):
        ox, oy = offset
        for y in range(image.height):
            for x in range(image.width):
                if (0 <= x + ox < self.width) and (0 <= y + oy < self.height):
                    *c, alpha = image[x, y]
                    
                    if alpha == 1.0:
                        self[x+ox, y+oy] = (int(255*c[0]), int(255*c[1]), int(255*c[2]))
                    elif alpha == 0.0:
                        pass
                    else:
                        raise NotImplementedError('Alpha Blending')

    def clear(self, color=(0,0,0)):
        for y in range(self.height):
            for x in range(self.width):
                self[x, y] = color