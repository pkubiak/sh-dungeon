from engine.screen import SubPixelScreen
from engine.activity import GameLoop, KeyboardEvent
from engine.keyboard import Keyboard, Keys
from engine.rt.image import Image
from engine.font import Font
from engine.drawing.text import puttext, puttextblock
from engine.drawing.draw import clear

import random


class GenericMenuActivity:
    def __init__(self):
        assert (self.OPTIONS) and (self.TITLE)
        self.font = Font('media/fonts/default.pnm')
        self.index = 0
        self.redraw = True

    def interact(self, event):
        self.redraw = True
        if event.key == Keys.UP:
            self.index -= 1
        elif event.key == Keys.DOWN:
            self.index += 1
        elif event.key == Keys.ESC:
            self.loop.exit()
        elif hasattr(self, f"interact_{self.index}"):
            getattr(self, f"interact_{self.index}")(event)

        self.index %= len(self.OPTIONS)

        return True

    def render(self, timestamp, canvas):
        if not self.redraw:
            return False
        self.redraw = False
        clear(canvas, (128,128,128))

        puttextblock(canvas, 0, 4, canvas.width, self.TITLE, font_color=(255,0,0), font=self.font, shadow_color=(0,0,0), align='center')

        for i, value in enumerate(self.OPTIONS):
            puttextblock(
                canvas,
                0, int((1.5+i)*(self.font.line_height+1)) + 4,
                canvas.width,
                value,
                font_color=(255,255,0) if i == self.index else (255,0,0),
                font=self.font, shadow_color=(70,0, 0), align='center')

        return True


@GameLoop.register('MainMenu')
class MainMenuActivity(GenericMenuActivity):
    TITLE = 'Main Menu'
    OPTIONS = ['New Game', 'Settings', 'Read Text', 'Help', 'Exit']
    
    def interact_0(self, event):
        if event.key == Keys.ENTER:
            self.loop.exit()

    def interact_1(self, event):
        if event.key == Keys.ENTER:
            self.loop.enter('SettingMenu')
    
    def interact_2(self, event):
        self.loop.enter('ScrollingText', text='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.')
        
    def interact_3(self, event):
        self.loop.enter('ScrollingText', text='Sed orci luctus et magnis dis parturient montes, nascetur ridiculus mus. Vivamus hendrerit tellus porttitor magna. Donec nonummy eget, rutrum ac, tempus erat'.upper())

    def interact_4(self, event):
        if event.key == Keys.ENTER:
            self.loop.exit()


@GameLoop.register('SettingMenu')
class SettingMenuActivity(GenericMenuActivity):
    TITLE = '- Settings -'
    OPTIONS = ['Music: ON', 'Sound: OFF', 'Res: 63x63', 'Key: ?', 'Back']
    
    def interact_0(self, event):
        if event.key in {Keys.LEFT, Keys.RIGHT, Keys.ENTER}:
            self.OPTIONS[0] = 'Music: OFF' if self.OPTIONS[0] == 'Music: ON' else 'Music: ON'
        # self.loop.exit()

    def interact_3(self, event):
        self.OPTIONS[3] = f"Key: {event.key}"

    def interact_4(self, event):
        self.loop.exit()

@GameLoop.register('ScrollingText')
class ScrollingTextActivity:
    def __init__(self, text: str):
        self.text = text
        self.offset = 0
        self.redraw = True
        self.font = Font('media/fonts/default.pnm')

    def interact(self, event):
        self.redraw = True
        if event.key == Keys.UP:
            self.offset += 5
        elif event.key == Keys.DOWN:
            self.offset -= 5
        elif event.key == Keys.ESC:
            self.loop.exit()
        else:
            self.redraw = False

        return True
    
    def render(self, timestamp, canvas):
        self.offset -= 1
        self.redraw = False
        clear(canvas, (100, 100, 100))
        puttextblock(canvas, 0, self.offset, canvas.width, self.text, font_color=(255,0,0), font=self.font, shadow_color=(70,0,0), align='center')

        return True



if __name__ == '__main__':
    loop = GameLoop()
    loop.enter('MainMenu')

    event = None

    with SubPixelScreen(width=63, height=63) as screen, Keyboard() as keyboard:

        while loop:
            while True:
                if event is None:
                    key = keyboard.getch(block=False)
                    if key is None:
                        break
                    event = KeyboardEvent(key=key)

                if not loop.interact(event):
                    break
                event = None

            if loop.render(screen.canvas):
                screen.sync()

            loop.wait(5)
