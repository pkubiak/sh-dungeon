from .font import Font
from .drawing import text, draw
from .rt.image import Image, Color4f
from .keyboard import Keys


class Input:
    FONT = Font('media/fonts/default.pnm')
    INPUT = Image.load('media/gfx/ui-frame3.pnm')
    CARET_SPEED = 0.75

    def __init__(self, x, y, width, text: str = '', *, placeholder=None):
        self._text = text
        self._caret = True
        self._index = len(text)
        self._last_blink = 0
        self._offset = (x, y)
        self._width = width
        self.placeholder = placeholder
        self.has_focus = False

    def interact(self, event):
        show_carret = True
        if event.key == Keys.BACKSPACE:
            self._text = self._text[:max(0, self._index - 1)] + self._text[self._index: ]
            self._index -= 1
        elif event.key == Keys.DELETE:
            self._text = self._text[:self._index] + self._text[self._index+1:]
        elif event.key == Keys.LEFT:
            self._index -= 1
        elif event.key == Keys.RIGHT:
            self._index += 1
        elif event.key == Keys.HOME:
            self._index = 0
        elif event.key == Keys.END:
            self._index = len(self._text)
        elif event.key == Keys.SPACE:
            self._text = self._text[:self._index] + ' ' + self._text[self._index:]
            self._index += 1
        elif len(event.key) == 1:
            self._text = self._text[:self._index] + event.key + self._text[self._index:]
            self._index += 1
        else:
            show_carret = False

        self._index = max(0, min(self._index, len(self._text)))

        if show_carret:
            self._caret = True
        return True

    def render(self, timestamp, canvas):
        canvas.imshow(self.INPUT, offset=self._offset)
        # draw.rect(canvas, )
        ox, oy = self._offset

        text.puttext(canvas, ox+4, oy+4, self._text or self.placeholder or '', font_color=0x442434, font=self.FONT)
        if self._text:
            text.puttext(canvas, ox+3, oy+3, self._text, font_color=0xdeeed6, font=self.FONT)
        text.puttext(canvas, ox+3, oy+14, str(self._index) +','+str(len(self._text)), font_color=0x442434, font=self.FONT)

        if self.has_focus and self._caret:
            offset_x = text.measure_text(self._text[:self._index], self.FONT)
            draw.vline(canvas, ox + 4 + offset_x, oy + 3, oy + 10, 0xff0000)

        if timestamp - self._last_blink > self.CARET_SPEED:
            self._last_blink = timestamp
            self._caret = not self._caret
