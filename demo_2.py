
from engine.activity import GameLoop, KeyboardEvent
from engine.rt.image import Image, Color4f
from engine.font import Font
from engine.gui import Input
from engine.drawing.draw import clear
from engine.drawing.text import puttextblock
from engine.keyboard import Keys


@GameLoop.register('Inventory')
class InventoryActivity:
    UI = Image.load('media/gfx/ui.pnm').crop((132, 34, 234, 137))
    SCROLLBAR = Image.load('media/gfx/scrollbar.pnm')
    FRAME = Image.load('media/gfx/ui-frame2.pnm')
    FONT = Font('media/fonts/default.pnm')

    def __init__(self, inventory):
        self.inventory = inventory
        self.items = [
            Input(1, 1+10, 50, 'Inventory', placeholder='First name'),
            Input(1, 16+10, 50, 'Inventory', placeholder='Last name'),
            Input(1, 31+10, 50, 'Inventory', placeholder='City')
        ]
        self.focus = 0


    def interact(self, event):
        if event.key == Keys.ESC:
            self.loop.exit()
        elif event.key in {Keys.UP, Keys.DOWN, Keys.TAB}:
            self.focus = (self.focus + (-1 if event.key == Keys.UP else 1)) % len(self.items)
            for i, el in enumerate(self.items):
                el.has_focus = (i == self.focus)
        else:
            self.items[self.focus].interact(event)

        return True


    def render(self, timestamp, canvas):
        clear(canvas, 0x4e4a4e)
        for item in self.items:
            item.render(timestamp, canvas)
        puttextblock(canvas, 0, 1, canvas.width, '> HERO <', font_color=0xdeeed6, font=self.FONT, align='center')

        return True


from dungeon import default_loop

if __name__ == '__main__':
    default_loop('Inventory', inventory=None)
