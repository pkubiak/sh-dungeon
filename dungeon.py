"""
sh-dungeon engine demo game

Keyboard:
up/down    - move forward/backward
left/right - rotate left/right
space      - jump
e          - use object
x          - attack
s          - save screenshot to /tmp/
q          - debug view
< >        - change weapon
?          - show/hide weapon
esc        - exit game

Ideas:
- jumping to destroy floor
- secret language
- compas
- real torch
- speel system by keys order
- nauka czarów od magów poprzez kopiowanie
- hiden places
- jumping to press floor plate
- alchemy
- worek pieniędzy (różne waluty, nie tylko złoto)
- transmutacja w małe zwierzątko
- wchodzenie po schodach na pól pietro
- fluorescentic glyphs on walls
- slavic names (https://pl.wikipedia.org/wiki/M%C4%99skie_imiona_s%C5%82owia%C5%84skie)
- secret codes

Like wizardry / HOMM:
- https://www.youtube.com/watch?v=DkwJ8RtmUco 
- 
"""

import random, math, time
from datetime import datetime

from engine.rt.solids import Triangle, Quad
from engine.rt.utils import Point3f, Ray, Vector3f
from engine.rt.scene import Scene
from engine.rt.cameras import PerspectiveCamera
from engine.rt.renderer import Renderer
from engine.rt.image import Image, Color4f
from engine.rt.integrators import RayTracingIntegrator
from engine.rt.materials import DummyMaterial, FlatMaterial, PhongMaterial
from engine.rt.world import World
from engine.rt.lights import PointLight
from engine.rt.coordmappers import TriangleMapper
from engine.rt.textures import ConstantTexture, ImageTexture

# from engine.font import BOXY_BOLD_FONT_PLUS, MAGIC_FONT
from engine.screen import SubPixelScreen
from engine.keyboard import Keyboard, Keys
from engine.sound import Sound

from engine.drawing.text import puttextblock, puttext, measure_text
from engine.drawing.draw import clear
from engine.font import Font


FONT = Font('media/fonts/default.pnm')

DEBUG = False

LEVEL = """\
#################
D               #
# ###d######### #
# # S S #       #
# ###S### #######
#   # #         #
# # ########### #
# #   #     #   #
#X### # ### # ###
#   #   #   #   #
####### # #######
# #     #       #
# # ########### #
#   #           #
# ### ######### #
#   #     #     #
#################\
""".split("\n")

#LEVEL = """\
######
##   D
##  ##
##   #
######\
#""".split("\n")

TEXTURES = {}
DRAGON = None

def create_sprite(texture, width, height, pos_x, pos_y, pos_z, angle=0.0):
    mapper = TriangleMapper(Point3f(1.0,0.0,0.0), Point3f(1.0, 1.0, 0.0), Point3f(0.0, 0.0, 0.0))
    material = FlatMaterial(ImageTexture(texture))

    x = width * math.sin(angle)
    z = width * math.cos(angle)

    return Quad(Point3f(pos_x - 0.5*x, pos_y - height, pos_z - 0.5*z), Vector3f(0, height, 0), Vector3f(x, 0, z), material=material, coord_mapper=mapper)


def build_scene(tileset):
    global TEXTURES, DRAGON
    width, height = len(LEVEL[0])//2, len(LEVEL)//2

    mapper = TriangleMapper(Point3f(1.0,0.0,0.0), Point3f(1.0, 1.0, 0.0), Point3f(0.0, 0.0, 0.0))

    dummy = DummyMaterial()

    # Sky
    # sky_tex = ConstantTexture(Color4f(183/255, 225/255, 243/255, 1.0))
    sky_tex = ImageTexture(Image.load('media/gfx/sky.pnm'), border_handling=ImageTexture.BORDER_REPEAT, interpolation=ImageTexture.INTERPOLATION_LINEAR)
    sky_mapper = TriangleMapper(Point3f(0.0,0.0,0.0), Point3f(10+width, 0.0, 0.0), Point3f(0.0, 20+height, 0.0))
    sky = FlatMaterial(sky_tex)

    # Floor
    # floor_tex = ConstantTexture(Color4f(170/255, 211/255, 86/255, 1.0))
    floor_tex = ImageTexture(tileset[13*64+18], border_handling=ImageTexture.BORDER_REPEAT)
    floor_mapper = TriangleMapper(Point3f(0.0,0.0,0.0), Point3f(200+width, 0.0, 0.0), Point3f(0.0, 200+height, 0.0))
    floor = FlatMaterial(floor_tex)

    ceil_tex = ImageTexture(tileset[19*64-18], border_handling=ImageTexture.BORDER_REPEAT)
    ceil_mapper = TriangleMapper(Point3f(0.0, 0.0, 0.0), Point3f(width, 0.0, 0.0), Point3f(0.0, height, 0.0))
    ceil = FlatMaterial(ceil_tex)


    if DEBUG:
        sky = wall = floor = dummy

    s = Scene()
    # add sky
    s.add(Quad(Point3f(-1000,-20, -1000), Vector3f(2000+width, 0, 0), Vector3f(0, 0, 2000+height), material=sky, coord_mapper=sky_mapper))

    # add ground
    s.add(Quad(Point3f(-100, 0, -100), Vector3f(200+width, 0, 0), Vector3f(0, 0, 200 + height), material=floor, coord_mapper=floor_mapper))

    # add ceil
    s.add(Quad(Point3f(0, -1, 0), Vector3f(width, 0, 0), Vector3f(0, 0, height), material=ceil, coord_mapper=ceil_mapper))

    # horizontal walls
    mapping = {
        '#': 19*64-20,
        'S': 18*64+32,
        'D': 11*64+32-5-4, #15*64+32,
        'd': 15*64+34,
        'm': 3*64+1, # dragon
        'X': 17*64+11, # magic wall
        'q': 9*64+27, # queen
        'c': 45*64+44, # chest
        's': 11*64+32-5-4-3 # squll
    }

    TEXTURES = {key: FlatMaterial(ImageTexture(tileset[value])) for key, value in mapping.items()}


    # t64 = Image.load('./gfx/64x64.pam').as_tileset(64, 64)
    # FlatMaterial(ImageTexture(t64[8*16+10]))

    # monster = Quad(Point3f(0, -1, 2.75), Vector3f(0, 1, 0), Vector3f(1, 0, 0), material=TEXTURES['m'], coord_mapper=mapper)
    # DRAGON = monster
    DRAGON = create_sprite(tileset[mapping['m']], 1, 1, 0.5, 0, 2.75, 0.5*math.pi)
    s.add(DRAGON)

    tex = Image.load('media/gfx/tree.pam')
    for i in range(5):
        for j in (0-0.3, 1+0.3):
            r = 0.001*random.random()
            tree = create_sprite(tex, 2, 3, -0.5 - i + r, 0.3 + r, j+r)
            s.add(tree)
            tree = create_sprite(tex, 2, 3, -0.5 - i + r, 0.3 + r, j+r, 0.5*math.pi)
            s.add(tree)

    queen = Quad(Point3f(-1, -0.75, 1.25), Vector3f(0, 0.75, 0), Vector3f(0.75, 0, 0), material=TEXTURES['q'], coord_mapper=mapper)
    s.add(queen)

    cheest = Quad(Point3f(1.75, -0.5, 4.25), Vector3f(0, 0.5, 0), Vector3f(0, 0, 0.5), material=TEXTURES['c'], coord_mapper=mapper)
    s.add(cheest)

    # FlatMaterial(ImageTexture(tileset2[64*12+27])),
    squll = Quad(Point3f(2.1, -0.8, 1.75), Vector3f(0.0, 0.8, 0.0), Vector3f(0.8, 0, 0), material=TEXTURES['s'], coord_mapper=mapper)
    s.add(squll)

    for y in range(height+1):
        for x in range(width):
            c = LEVEL[2*y][2*x+1]
            if c != ' ':
                t = TEXTURES[c] if c != '#' else FlatMaterial(ImageTexture(tileset[random.randint(19*64-24, 19*64-18)]))
                q = Quad(Point3f(x, -1, y), Vector3f(0, 1, 0), Vector3f(1, 0, 0), material=t, coord_mapper=mapper)
                s.add(q)
    # vertical walls
    for y in range(height):
        for x in range(width+1):
            c = LEVEL[2*y+1][2*x]
            if c != ' ':
                t = TEXTURES[c] if c != '#' else FlatMaterial(ImageTexture(tileset[random.randint(19*64-24, 19*64-18)]))
                q = Quad(Point3f(x, -1, y), Vector3f(0, 1, 0), Vector3f(0, 0, 1), material=t, coord_mapper=mapper)
                s.add(q)
    return s


from types import SimpleNamespace

from engine.activity import GameLoop, KeyboardEvent

class Inventory:
    @property
    def current(self):
        return self.items[self.idx]

    def __init__(self, items):
        self.idx = 0
        self.items = items or []

    def next(self):
        self.idx = (self.idx+1) % len(self.items)

    def prev(self):
        self.idx = (self.idx-1) % len(self.items)


@GameLoop.register('GamePlay')
class DungeonActivity:
    MAIN_SOUND = "media/sound/Memoraphile - Spooky Dungeon.ogg"
    STEP_LENGTH = 1.0
    DOF = 100
    FPT = 5  # frames per turn

    def __init__(self):
        self.sound = Sound()
        self.sound.play(self.MAIN_SOUND, loop=True)
        self.sound_effects = Sound()

        self.tileset = Image.load('media/gfx/tileset.pnm', transparency=(0,255,255)).as_tileset(32,32)

        self.scene = build_scene(self.tileset)
        self.integrator = RayTracingIntegrator(World(self.scene, None))

        self.inventory = Inventory(['shovel', 'compass'])

        self.env = SimpleNamespace(
            door_open = False,
            has_key = False,
            dragon_hp = 5,
            debug_mode = False,
            tresure_pos = (3.5, 2.5),
        )

        self.states = [(0.5, -0.5, 0.5, -math.pi, 0)]

        self.swords = Image.load('media/gfx/swords2.pnm', transparency=(0,255,255)).as_tileset(32, 32)
        self.compass = Image.load('media/gfx/compass.pnm', transparency=(0, 255, 255)).as_tileset(32, 32)
        self.shovel = Image.load('media/gfx/shovel.pnm', transparency=(0,255,255))

        self.overlay_count = 0
        self.overlay = Image(width=63, height=63)
        
    def on_exit(self):
        self.sound.close()
        self.sound_effects.close()

    def render(self, timestamp, canvas) -> bool:
        if self.overlay_count > 0:
            self.overlay_count -= 1
            if self.overlay_count == 0:
                self.states.append(self.prev_state)
    
        if not self.states:
            return False

        pos_x, pos_y, pos_z, ang, item_pos = self.prev_state = self.states[0]
        self.states = self.states[1:]
        # torch.position = Point3f(pos_x, pos_y, pos_z)

        view_angle = 90 / 180 * math.pi
        forward = Vector3f(math.sin(ang), 0, math.cos(ang))
        camera = PerspectiveCamera(Point3f(pos_x, pos_y, pos_z) + (-0.25*forward), forward, Vector3f(0, 1, 0), view_angle, view_angle)

        r = Renderer(camera, self.integrator)
        r.render(canvas)

        if item_pos > 0:
            if self.inventory.current == 'compass':
                if self.env.tresure_pos:
                    if (abs(self.env.tresure_pos[0] - pos_x) < 0.001) and (abs(self.env.tresure_pos[1] - pos_z) < 0.001):
                        compass_idx = random.randint(0,7)
                    else:
                        ang2 = ang - math.atan2(self.env.tresure_pos[0] - pos_x, self.env.tresure_pos[1] - pos_z)
                        compass_idx = round(-8.0 * (0.5 * ang2 / math.pi)) % 8
                else:
                    compass_idx = round(-8.0 * (0.5 * ang / math.pi)) % 8

                item = self.compass[compass_idx].hflip(), (30, 36)
            elif self.inventory.current == 'shovel':
                item = self.shovel.scale(2), (4, 12)
            elif self.inventory.current == 'sword':
                item = self.swords[1].hflip().scale(2), (4, 12)
            elif self.inventory.current == 'gold_key':
                item = self.tileset[46*64-10].hflip(), (30, 36)
            item, pos = item
            canvas.imshow(item, (pos[0], pos[1] + int(canvas.height*(1-item_pos))))

        if self.overlay_count > 0:
            canvas.imshow(self.overlay)
        
        return True
        
    def interact(self, event) -> bool:
        if self.states:
            return False
        key = event.key
        pos_x, pos_y, pos_z, ang, item_pos = self.prev_state
        show_item = item_pos > 0
        if key in (Keys.UP, Keys.DOWN, 'x'):
            if key == 'x' and not (round(2*pos_x) == 1 and round(2*pos_z) == 5 and self.inventory.current == 'sword' and self.env.dragon_hp is not None):
                return True
            mult = -1 if key == Keys.DOWN else 1

            new_pos_x = round(2 * pos_x + mult * math.sin(ang) * self.STEP_LENGTH)
            new_pos_z = round(2 * pos_z + mult * math.cos(ang) * self.STEP_LENGTH)
            cell = LEVEL[new_pos_z][new_pos_x]

            if key == 'x':
                if self.inventory.current == 'sword':
                    f = [0.1, 0.2, 0.25, 0.2, 0.1, 0.0]
                    self.env.dragon_hp -= 1
                    self.sound_effects.play('media/sound/sword-unsheathe.ogg')
                else:
                    return True
            elif (cell in (' ', 'd') or (cell == 'X' and not show_item) or (cell == 'D' and self.env.door_open)) and (self.env.dragon_hp is None or new_pos_x!=1 or new_pos_z !=6):
                f = [(i+1)/self.FPT for i in range(self.FPT)]
                self.sound_effects.play('media/sound/interface2.ogg')
            else:
                f = [0.1, 0.25, 0.35, 0.20, 0.1, 0.0]
                if mult == -1:
                    f = [0.5*i for i in f]
                self.sound_effects.play('media/sound/interface1.ogg')

            for m in f:
                self.states.append((pos_x + mult * math.sin(ang)*self.STEP_LENGTH * m, pos_y, pos_z + mult * math.cos(ang)*self.STEP_LENGTH * m, ang, item_pos))
            
            if self.env.dragon_hp is not None and self.env.dragon_hp <= 0:
                self.scene._objects.remove(DRAGON)
                self.env.dragon_hp = None
                self.sound_effects.play('media/sound/random1.ogg')


        if key in (Keys.LEFT, Keys.RIGHT):  # Turn left / right
            mult = 1 if key == Keys.LEFT else -1
            for i in range(self.FPT):
                self.states.append((pos_x, pos_y, pos_z, (ang + mult * math.pi/2 * (i+1) / self.FPT) % (2*math.pi), item_pos))

        if key == Keys.SPACE:  # Jumping 
            for j in [-0.2, -0.3, -0.35, -0.3, -0.2, 0.0]:
                self.states.append((pos_x, pos_y + j, pos_z, ang, item_pos))
    
        if key in ('n', 'm'): # Ascend / Descend
            mult = 1 if key == 'n' else -1
            for i in range(self.FPT):
                self.states.append((pos_x, pos_y + 0.45 * mult * (i+1) / self.FPT, pos_z, ang, item_pos))

        if key in '<>' and item_pos > 0:  # Switch active inventory item
            self.inventory.prev() if key == '<' else self.inventory.next()
            self.states.append((pos_x, pos_y, pos_z, ang, item_pos))
        
        if key == '?':
            if show_item:
                for i in range(self.FPT):
                    self.states.append((pos_x, pos_y, pos_z, ang, 1 - (i+1)/self.FPT))
            else:
                for i in range(self.FPT):
                    self.states.append((pos_x, pos_y, pos_z, ang, (i+1)/self.FPT))

        if key == 'e':
            new_pos_x = round(2 * pos_x + math.sin(ang) * self.STEP_LENGTH)
            new_pos_z = round(2 * pos_z + math.cos(ang) * self.STEP_LENGTH)

            if not show_item:
                if LEVEL[new_pos_z][new_pos_x] == 'D' and not self.env.door_open:
                    clear(self.overlay, Color4f(0,0,0,0))
                    puttextblock(self.overlay, 6, 10, 63, "Locked!!!", font_color=(255,255,255), font=FONT, shadow_color=(0,0,0))
                    self.overlay_count = 50
                if round(2*pos_x) == 3 and round(2*pos_z) == 9 and not self.env.has_key:
                    TEXTURES['c'].texture = ImageTexture(self.tileset[45*64+45])
                    self.env.has_key = True
                    clear(self.overlay, Color4f(0,0,0,0))
                    puttextblock(self.overlay, 6, 10, 63, "You found", font_color=(255,255,255), font=FONT, shadow_color=(0,0,0))
                    puttextblock(self.overlay, 6, 22, 63, "   Gold Key", font_color=(255,255,0), font=FONT, shadow_color=(0,0,0))
                    self.overlay_count = 50
                    self.inventory.items.append('gold_key')
            elif show_item and self.inventory.current == 'gold_key':
                if LEVEL[new_pos_z][new_pos_x] == 'D':
                    if self.env.door_open:
                        TEXTURES['D'].texture = ImageTexture(self.tileset[11*64+32-5-4])
                    else:
                        TEXTURES['D'].texture = ImageTexture(self.tileset[11*64+32-5])
                    self.env.door_open = not self.env.door_open
                    self.sound_effects.play('media/sound/door.ogg')
                        
            elif show_item and self.inventory.current == 'shovel':
                if self.env.tresure_pos and abs(self.env.tresure_pos[0] - pos_x) < 0.01 and abs(self.env.tresure_pos[1] -pos_z) < 0.01:
                    clear(self.overlay, Color4f(0,0,0,0))
                    puttextblock(self.overlay, 6, 10, 63, "You found", font_color=(255,255,255), font=FONT, shadow_color=(0,0,0))
                    puttextblock(self.overlay, 6, 22, 63, "Long Sword", font_color=(255,255,0), font=FONT, shadow_color=(0,0,0))
                    self.overlay_count = 50
                    self.inventory.items.append('sword')
                    self.env.tresure_pos = None
                else:
                    clear(self.overlay, Color4f(0,0,0,0))
                    puttextblock(self.overlay, 6, 10, 63, "You dig!!!", font_color=(255,255,255), font=FONT, shadow_color=(0,0,0))
                    self.overlay_count = 50
                
            self.states.append(self.prev_state)

        if key == Keys.ESC:
            self.loop.exit()
    
        return True



################
class GenericMenuActivity:
    def __init__(self):
        assert (self.OPTIONS) and (self.TITLE)
        self.font = Font('media/fonts/default.pnm')
        self.index = 0
        self.redraw = True
        self.background = Image.load(self.BACKGROUND) if hasattr(self, 'BACKGROUND') else None

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
        if self.background:
            canvas.imshow(self.background, (0, 0))
        else:
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
    TITLE = 'sh-dungeon'
    OPTIONS = ['New Game', 'Load Game', 'Settings', 'Help', 'Exit']
    BACKGROUND = 'media/gfx/main-menu-bg.pnm'
    
    def interact_0(self, event):
        if event.key == Keys.ENTER:
            self.loop.enter('GamePlay')

    def interact_2(self, event):
        if event.key == Keys.ENTER:
            self.loop.enter('SettingMenu')
    
    def interact_3(self, event):
        self.loop.enter('ScrollingText', text='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.')
        
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

##################



def default_loop(activity='MainMenu', **kwargs):
    loop = GameLoop()
    loop.enter(activity, **kwargs)
    Keyboard.init()

    event = None

    with SubPixelScreen(width=63, height=63) as screen:
        while loop:
            while True:
                if event is None:
                    key = Keyboard.getch(block=False)
                    if key is None:
                        break
                    event = KeyboardEvent(key=key)

                if not loop.interact(event):
                    break
                event = None

            if loop.render(screen.canvas):
                screen.sync()

            loop.wait(30)

if __name__ == '__main__':
    default_loop()
