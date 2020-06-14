import time
from random import randint
from engine.keyboard import Keyboard, Keys
from engine.screen import SubPixelScreen
from engine.drawing import draw


with SubPixelScreen(width=63, height=63) as screen, Keyboard() as keyboard:
    t0 = time.time()

    count = 0
    draw.clear(screen.canvas, 0xff0000)
    draw.line(screen.canvas, 0,0,screen.width-1, screen.height-1, 0x00ff00)
    screen.sync()
    keyboard.getch()
    
    while True:
        if keyboard.getch(False) == Keys.ESC:
            break
        x0 = randint(0, screen.width-1)
        x1 = randint(0, screen.width-1)
        y0 = randint(0, screen.height-1)
        y1 = randint(0, screen.height-1)
        color = randint(0,0xffffff)

        draw.line(screen.canvas, x0, y0, x1, y1, color)
        screen.sync()
        count += 1

    t1 = time.time()

print("FPS: %.2f" % (count / (t1 - t0)))