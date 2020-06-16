import time
import sys
from typing import Tuple, Optional

from .rt.image import Image, Color4f

# class Screen:
#     BLOCK = '  '#██'

#     def __init__(self, width, height, offset=(0,0)):
#         self.width = width
#         self.height = height
#         self.offset = offset

#         self.data = [
#             [(0,0,0, False) for _ in range(width)] for _ in range(height)
#         ]

#         wrt("\033[?47h")  # save current screen
#         wrt("\033[?25l")  # Hide cursor
#         wrt("\033[2J")  # clear entire screen
#         sys.stdout.flush()


#     def close(self):
#         wrt("\033[?47l")  # save current screen
#         wrt("\033[?25h")  # Show cursor
#         sys.stdout.flush()

#     def __getitem__(self, coords) -> Color4f:
#         x, y = coords
#         c = self.data[y][x]
#         return Color4f(c[0]/255, c[1]/255, c[2]/255)

#     def __setitem__(self, coords, value):
#         x, y = coords
#         assert isinstance(value, tuple) and 3 <= len(value) <= 4
#         r, g, b, *blink = value

#         if len(blink) == 0 or blink[0] == False:
#             blink= False
#         else:
#             blink = True

#         assert (0<=r<=255) and (0<=g<=255) and (0<=b<=255), f"{value}"

#         self.data[y][x] = (r, g, b, bool(blink))


#     def hline(self, x0, x1, y, color):
#         if x1<0:
#             x1+=self.width
#         for x in range(x0, x1+1):
#             self[x, y] = color

#     def vline(self, x, y0, y1, color):
#         if y1<0:
#             y1+=self.height
#         for y in range(y0, y1+1):
#             self[x,y] = color

#     def rect(self, x0, y0, x1, y1, color):
#         """Draw rectangle"""
#         if x1 < 0:
#             x1 += self.width
#         if y1 < 0:
#             y1 += self.height

#         for x in range(x0, x1+1):
#             self[x, y0] = self[x, y1] = color
#         for y in range(y0, y1+1):
#             self[x0, y] = self[x1, y] = color

#     def fullrect(self, x0, y0, x1, y1, color):
#         if x1 < 0:
#             x1 += self.width
#         if y1 < 0:
#             y1 += self.height

#         for x in range(x0, x1+1):
#             for y in range(y0, y1+1):
#                 self[x, y] = color


#     def sync(self):
#         for y in range(self.height):
#             wrt("\033[%d;%dH" % (1 + y+self.offset[1], 1 + 2 * self.offset[0]))  # move cursor to start of yth row
#             for x in range(self.width):
#                 r, g, b, blink = self.data[y][x]

#                 # if blink:
#                 #     r2, g2, b2, _ = lighten((r, g, b, True),0.6)
#                 #     wrt(f"\033[5m\033[48;2;{r2};{g2};{b2}m") # blinking color

#                 wrt(f"\033[48;2;{r};{g};{b}m%s\033[0m" % self.BLOCK)  # print block in given RGB color
#             sys.stdout.flush()
#         wrt("\033[H")
#         sys.stdout.flush()

#     def imshow(self, image: Image, offset: Tuple[int, int] = (0, 0)):
#         ox, oy = offset
#         for y in range(image.height):
#             for x in range(image.width):
#                 if (0 <= x + ox < self.width) and (0 <= y + oy < self.height):
#                     color = image[x, y]

#                     if color.a == 1.0:
#                         self[x+ox, y+oy] = color.as_3i
#                     elif color.a == 0.0:
#                         pass
#                     else:
#                         raise NotImplementedError('Alpha Blending')

#     def clear(self, color=(0,0,0)):
#         for y in range(self.height):
#             for x in range(self.width):
#                 self[x, y] = color

#     def save_to_pnm(self, path):
#         with open(path, 'wb') as output:
#             output.write(b'P6\n')
#             output.write(f'{self.width} {self.height}\n'.encode('utf-8'))
#             output.write(b'255\n')
#             for y in range(self.height):
#                 for x in range(self.width):
#                     output.write(bytes(self.data[y][x][:3]))

wrt = sys.stdout.write


class SubPixelScreen:
    @property
    def height(self):
        return self.canvas._height

    @property
    def width(self):
        return self.canvas._width

    def __init__(self, width, height, offset: Optional[Tuple[int,int]] = None):
        self._offset = offset or (0, 0)
        self.canvas = Image(width=width, height=height)

    def __enter__(self):
        wrt("\033[?47h")  # save current screen
        wrt("\033[?25l")  # Hide cursor
        wrt("\033[2J")  # clear entire screen
        sys.stdout.flush()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        wrt("\033[?47l")  # save current screen
        wrt("\033[?25h")  # Show cursor
        sys.stdout.flush()

    def sync(self):
        #wrt("\033[2J")  # clear entire screen
        for y in range(self.canvas._height//2):
            wrt("\033[%d;%dH" % (1 + y+self._offset[1], 1 + 2 * self._offset[0]))  # move cursor to start of yth row
            for x in range(self.canvas._width):
                r, g, b = self.canvas[x, 2*y].as_3i
                r2, g2, b2 = self.canvas[x, 2*y+1].as_3i
                wrt(f"\033[38;2;{r};{g};{b}m\033[48;2;{r2};{g2};{b2}m▀")  # print block in given RGB color
            wrt('\033[0m')

        if self.canvas._height % 2:
            wrt("\033[%d;%dH" % (1+self.canvas._height//2+self._offset[1], 1 + 2 * self._offset[0]))
            for x in range(self.canvas._width):
                r, g, b = self.canvas[x, self.canvas._height-1].as_3i
                wrt(f"\033[38;2;{r};{g};{b}m▀")
            wrt('\033[0m')

        wrt("\033[H")
        sys.stdout.flush()