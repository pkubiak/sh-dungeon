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
- nauka czarów d magów poprzez kopiowanie
- hiden places
- jumping to press floor plate
- alchemy
- worek pieniędzy (różne waluty, nie tylko złoto)
- transmutacja w małe zwierzątko
- wchodzenie po schodach na pól pietro
- fluorescentic glyphs on walls
"""

import random, math, time
from datetime import datetime

from rt.solids import Triangle, Quad
from rt.utils import Point3f, Ray, Vector3f
from rt.scene import Scene
from rt.cameras import PerspectiveCamera
from rt.renderer import Renderer
from rt.image import Image, Color4f
from rt.integrators import RayTracingIntegrator
from rt.materials import DummyMaterial, FlatMaterial, PhongMaterial
from rt.world import World
from rt.lights import PointLight
from rt.coordmappers import TriangleMapper
from rt.textures import ConstantTexture, ImageTexture

from font import BOXY_BOLD_FONT_PLUS, MAGIC_FONT
from screen import Screen, SubPixelScreen
from keyboard import Keyboard, Keys

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

def build_scene(tileset):
    global TEXTURES, DRAGON
    width, height = len(LEVEL[0])//2, len(LEVEL)//2

    mapper = TriangleMapper(Point3f(1.0,0.0,0.0), Point3f(1.0, 1.0, 0.0), Point3f(0.0, 0.0, 0.0))

    dummy = DummyMaterial()

    # Sky
    # sky_tex = ConstantTexture(Color4f(183/255, 225/255, 243/255, 1.0))
    sky_tex = ImageTexture(Image.load('./gfx/sky.pnm'), border_handling=ImageTexture.BORDER_REPEAT, interpolation=ImageTexture.INTERPOLATION_LINEAR)
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
    monster = Quad(Point3f(0, -1, 2.75), Vector3f(0, 1, 0), Vector3f(1, 0, 0), material=TEXTURES['m'], coord_mapper=mapper)
    s.add(monster)
    DRAGON = monster

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

if __name__ == '__main__':
    # t0 = time.time()
    # # tileset2 = Image.load('./gfx/ProjectUtumno_full.pam').as_tileset(32, 32)
    # t1 = time.time()
    # print(t1 - t0)

    tileset = Image.load('./gfx/tileset.pnm', transparency=(0,255,255)).as_tileset(32,32)

    s = build_scene(tileset)

    output = Image(width=63, height=63)
    scr  = SubPixelScreen(output.width, output.height)
    

    step_length = 1.0
    dof = 100
    states = [(0.5, -0.5, 0.5, -math.pi)]
    FPT = 5

    torch_color = Color4f(1.0, 0.95, 0.8, 1.0)
    torch_intensity = 0.5

    torch = PointLight(Point3f(0.5, -0.5, 0.5), torch_intensity*torch_color)
    blue_light = PointLight(Point3f(0.5, -0.5, 0.5), 0.2*Color4f(0.0, 0.0, 1.0, 1.0))
    integrator = RayTracingIntegrator(World(s, None))

    if DEBUG:
        integrator.world.lights.extend([torch, blue_light])

    swords = Image.load('gfx/swords2.pnm', transparency=(0,255,255)).as_tileset(32, 32)
    compass = Image.load('gfx/compass.pnm', transparency=(0, 255, 255)).as_tileset(32, 32)
    shovel = Image.load('gfx/shovel.pnm', transparency=(0,255,255))

    item_idx = 0
    inventory = ['compass', 'shovel']
    shovel_pos = (3.5, 2.5)
    def get_item():
        if inventory[item_idx] == 'compass':
            if 'sword' not in inventory:
                if (abs(shovel_pos[0] - pos_x) < 0.001) and (abs(shovel_pos[1] - pos_z) < 0.001):
                    # scr.puttext(0,0, f"{pos_x:.2f} {pos_z:.2f} {ang:.3f}", Color4f(1,1,1,1))
                    # scr.puttext(0,10, f"{shovel_pos[0]:.2f} {shovel_pos[1]:.2f}", Color4f(1,1,1,1))
                    compass_idx = random.randint(0,7)
                else:
                    ang2 = ang - math.atan2(shovel_pos[0] - pos_x, shovel_pos[1] - pos_z)
                    compass_idx = round(-8.0 * (0.5 * ang2 / math.pi)) % 8
            else:
                compass_idx = round(-8.0 * (0.5 * ang / math.pi)) % 8

            return compass[compass_idx].hflip(), (30, 36)
        elif inventory[item_idx] == 'shovel':
            item = shovel.scale(2), (4, 12)
        elif inventory[item_idx] == 'sword':
            item = swords[1].hflip().scale(2), (4,12)
        elif inventory[item_idx] == 'gold_key':
            item = tileset[46*64-10].hflip(), (30, 36)
        return item

    # item = items[item_idx].hflip().scale(2)
    show_item = False
    door_open = False
    has_key = False
    dragon_hp = 5
    debug_mode = False
    try:
        Keyboard.init()

        while True:
            if states:
                pos_x, pos_y, pos_z, ang = states[0]
                prev_state = states[0]
                states = states[1:]
                torch.position = Point3f(pos_x, pos_y, pos_z)

                view_angle = 90 / 180 * math.pi
                forward = Vector3f(math.sin(ang), 0, math.cos(ang))
                camera = PerspectiveCamera(Point3f(pos_x, pos_y, pos_z) + (-0.25*forward), forward, Vector3f(0, 1, 0), view_angle, view_angle)

                r = Renderer(camera, integrator)
                r.render(output)

                scr.imshow(output)
                if show_item:
                    # item, imoff = 
                    # if inventory[item_idx] == 'compass':
                    scr.imshow(*get_item())
                    # elif inventory[item_idx] == 'shovel':
                        # scr.imshow(item, (8, 16))

                # tttt = "     Dungeon\n   - - - - - - -\n Start game\n  Load game\n    Settings\n\n          Exit".upper()
                # for dx in (-1, 0, 1):
                #     for dy in (-1, 0, 1):
                #         scr.puttext(2+dx, 3+dy, tttt, Color4f(1.0, 1.0, 1.0, 1.0), shadow_color=Color4f(0, 0, 0, 0.75), font=MAGIC_FONT)
                # scr.puttext(2, 3, tttt, Color4f(1.0, 0, 0, 1.0), shadow_color=Color4f(0, 0, 0, 0.75), font=BOXY_BOLD_FONT_PLUS)
                if debug_mode:
                    scr.puttext(0,0, f"{pos_x:.2f} {pos_z:.2f}\n{ang:.3f}", Color4f(1,1,1,1))
                scr.sync()
            else:
                Keyboard.clear()
                key = Keyboard.getch()
                if key in (Keys.UP, Keys.DOWN, 'x'):
                    if key == 'x' and not (round(2*pos_x) == 1 and round(2*pos_z) == 5 and show_item and dragon_hp is not None):
                        continue
                    mult = -1 if key == Keys.DOWN else 1

                    new_pos_x = round(2 * pos_x + mult * math.sin(ang) * step_length)
                    new_pos_z = round(2 * pos_z + mult * math.cos(ang) * step_length)
                    cell = LEVEL[new_pos_z][new_pos_x]
                    if key == 'x':
                        if show_item and inventory[item_idx] == 'sword':
                            f = [0.1, 0.2, 0.25, 0.2, 0.1, 0.0]
                            dragon_hp -= 1
                        else:
                            continue
                    elif (cell in (' ', 'd') or (cell == 'X' and not show_item) or (cell == 'D' and door_open)) and (dragon_hp is None or new_pos_x!=1 or new_pos_z !=6):
                        f = [(i+1)/FPT for i in range(FPT)]
                    else:
                        f = [0.1, 0.25, 0.35, 0.20, 0.1, 0.0]
                        if mult == -1:
                            f = [0.5*i for i in f]

                    for m in f:
                        states.append((pos_x + mult * math.sin(ang)*step_length * m, pos_y, pos_z + mult * math.cos(ang)*step_length * m, ang))
                    
                    if dragon_hp is not None and dragon_hp <= 0:
                        s._objects.remove(DRAGON)
                        dragon_hp = None

                if key in ('n', 'm'): # Ascend descend
                    mult = 1 if key == 'n' else -1
                    for i in range(FPT):
                        states.append((pos_x, pos_y + 0.45 * mult * (i+1) / FPT, pos_z, ang))
                if key in (Keys.LEFT, Keys.RIGHT):
                    mult = 1 if key == Keys.LEFT else -1
                    for i in range(FPT):
                        states.append((pos_x, pos_y, pos_z, (ang + mult * math.pi/2 * (i+1) / FPT) % (2*math.pi)))
                if key == Keys.SPACE:
                    for j in [-0.2, -0.3, -0.35, -0.3, -0.2, 0.0]:
                        states.append((pos_x, pos_y + j, pos_z, ang))
                # if key in (Keys.PAGE_UP, Keys.PAGE_DOWN):
                #     torch_intensity += 0.1 if key == Keys.PAGE_UP else -0.1
                #     torch.intensity = torch_intensity * torch_color
                #     states.append((pos_x, pos_y, pos_z, ang))
                if key in '<>':
                    item_idx = (item_idx + (1 if key == '>' else -1)) % len(inventory)
                    # item = items[item_idx].hflip().scale(2)
                    states.append((pos_x, pos_y, pos_z, ang))
                if key == 'e':
                    new_pos_x = round(2 * pos_x + math.sin(ang) * step_length)
                    new_pos_z = round(2 * pos_z + math.cos(ang) * step_length)
                    if not show_item:
                        if LEVEL[new_pos_z][new_pos_x] == 'D' and not door_open:
                            scr.puttext(6, 10, "Locked!!!", Color4f(1.0,1.0,1.0), shadow_color=Color4f(0,0,0,1))
                            scr.sync()
                            time.sleep(1)
                        if round(2*pos_x) == 3 and round(2*pos_z) == 9 and not has_key:
                            TEXTURES['c'].texture = ImageTexture(tileset[45*64+45])
                            has_key = True
                            scr.puttext(6, 10, "You found", Color4f(1.0,1.0,1.0), shadow_color=Color4f(0,0,0,1))
                            scr.puttext(6, 22, "   Gold Key", Color4f(1.0,1.0, 0.0), shadow_color=Color4f(0,0,0,1))
                            inventory.append('gold_key')
                            scr.sync()
                            time.sleep(1)
                    elif show_item and inventory[item_idx] == 'gold_key':
                        if LEVEL[new_pos_z][new_pos_x] == 'D':
                            if door_open:
                                TEXTURES['D'].texture = ImageTexture(tileset[11*64+32-5-4])
                            else:
                                TEXTURES['D'].texture = ImageTexture(tileset[11*64+32-5])
                            door_open = not door_open
                                
                    elif show_item and inventory[item_idx] == 'shovel':
                        if ('sword' not in inventory) and abs(shovel_pos[0] - pos_x) < 0.001 and abs(shovel_pos[1] -pos_z) < 0.001:
                            scr.puttext(6, 10, "You found", Color4f(1.0,1.0,1.0), shadow_color=Color4f(0,0,0,1))
                            scr.puttext(4, 22, "Long Sword", Color4f(1.0,1.0, 0.0), shadow_color=Color4f(0,0,0,1))
                            inventory.append('sword')
                        else:
                            scr.puttext(6, 10, "You dig!!!", Color4f(1.0,1.0,1.0), shadow_color=Color4f(0,0,0,1))
                        scr.sync()
                        time.sleep(1)
                    states.append(prev_state)
                if key == '?':
                    im, imof = get_item()
                    if show_item:
                        for i in range(8):
                            scr.imshow(output)
                            scr.imshow(im, (imof[0], imof[1] + 8 * i))
                            scr.sync()
                            time.sleep(0.1)
                        show_item = False
                    else:
                        for i in reversed(range(8)):
                            scr.imshow(output)
                            scr.imshow(im, (imof[0], imof[1] + 8 * i))
                            scr.sync()
                            time.sleep(0.1)
                        show_item = True
                if key == 'q':
                    debug_mode = not debug_mode
                    states.append(prev_state)
                if key == 's':
                    scr.save_to_pnm(f'/tmp/out-{datetime.now()}.pnm')
                if key == Keys.ESC:
                    break

    finally:
        Keyboard.close()
        scr.close()


