"""
sh-dungeon engine demo game

Keyboard:
up/down    - move forward/backward
left/right - rotate left/right
space      - jump
e          - use object
s          - save screenshot to /tmp/
< >        - change weapon
?          - show/hide weapon
esc        - exit game
"""
import random, math, time
from rt.solids import Triangle, Quad
from rt.utils import Point3f, Ray, Vector3f
from rt.scene import Scene
from rt.cameras import PerspectiveCamera
from rt.renderer import Renderer
from rt.image import Image, Color4f
from rt.integrators import RayTracingIntegrator
from screen import Screen, SubPixelScreen
from keyboard import Keyboard, Keys
from rt.materials import DummyMaterial, FlatMaterial, PhongMaterial
from rt.world import World
from rt.lights import PointLight
from rt.coordmappers import TriangleMapper
from rt.textures import ConstantTexture, ImageTexture
from font import BOXY_BOLD_FONT_PLUS
from datetime import datetime

DEBUG = False

LEVEL = """\
#################
D               #
# #####d####### #
# #   S S       #
# #S# # # #######
#   S   S       #
# # #S#S####### #
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

def build_scene(tileset):
    global TEXTURES
    width, height = len(LEVEL[0])//2, len(LEVEL)//2

    mapper = TriangleMapper(Point3f(0.0,0.0,0.0), Point3f(0.0, 1.0, 0.0), Point3f(1.0, 0.0, 0.0))

    dummy = DummyMaterial()

    # Sky
    # sky_tex = ConstantTexture(Color4f(183/255, 225/255, 243/255, 1.0))
    sky_tex = ImageTexture(Image.from_pnm('./gfx/sky.pnm'), border_handling=ImageTexture.BORDER_REPEAT, interpolation=ImageTexture.INTERPOLATION_LINEAR)
    sky_mapper = TriangleMapper(Point3f(0.0,0.0,0.0), Point3f(10+width, 0.0, 0.0), Point3f(0.0, 20+height, 0.0))
    sky = FlatMaterial(sky_tex)

    # Floor
    # floor_tex = ConstantTexture(Color4f(170/255, 211/255, 86/255, 1.0))
    # Image.from_pnm('./gfx/grass3.pnm')
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
    }

    TEXTURES = {key: FlatMaterial(ImageTexture(tileset[value])) for key, value in mapping.items()}

    monster = Quad(Point3f(0, -1, 2.75), Vector3f(0, 1, 0), Vector3f(1, 0, 0), material=TEXTURES['m'], coord_mapper=mapper)
    s.add(monster)

    queen = Quad(Point3f(-1, -0.75, 1.25), Vector3f(0, 0.75, 0), Vector3f(0.75, 0, 0), material=TEXTURES['q'], coord_mapper=mapper)
    s.add(queen)

    cheest = Quad(Point3f(1.75, -0.5, 4.25), Vector3f(0, 0.5, 0), Vector3f(0, 0, 0.5), material=TEXTURES['c'], coord_mapper=mapper)
    s.add(cheest)

    for y in range(height+1):
        for x in range(width):
            c = LEVEL[2*y][2*x+1]
            if c != ' ':
                q = Quad(Point3f(x, -1, y), Vector3f(0, 1, 0), Vector3f(1, 0, 0), material=TEXTURES[c], coord_mapper=mapper)
                s.add(q)
    # vertical walls
    for y in range(height):
        for x in range(width+1):
            c = LEVEL[2*y+1][2*x]
            if c != ' ':
                q = Quad(Point3f(x, -1, y), Vector3f(0, 1, 0), Vector3f(0, 0, 1), material=TEXTURES[c], coord_mapper=mapper)
                s.add(q)
    return s

if __name__ == '__main__':
    def random_point():
        return Point3f(random.random(), random.random(), random.random())

    tileset = Image.from_pnm('./gfx/tileset.pnm', transparency=(0,255,255)).as_tileset(32,32)

    s = build_scene(tileset)

    N = 31
    scr  = SubPixelScreen(2*N+1, 2*N+1)
    output = Image(width=2*N+1, height=2*N+1)

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

    items = Image.from_pnm('gfx/swords2.pnm', transparency=(0, 255, 255)).as_tileset(32, 32)

    item_idx = 1
    item = items[item_idx].hflip().scale(2)
    show_item = True
    door_open = False
    has_key = False


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
                    scr.imshow(item, (8, 16))
                # tttt = "     Dungeon\n   - - - - - - -\n Start game\n  Load game\n    Settings\n\n          Exit"
                # scr.puttext(2, 3, tttt, Color4f(1.0, 1.0, 1.0, 1.0), shadow_color=Color4f(0, 0, 0, 0.75))
                scr.sync()
            else:
                key = Keyboard.getch()
                if key in (Keys.UP, Keys.DOWN):
                    mult = 1 if key == Keys.UP else -1

                    new_pos_x = round(2 * pos_x + mult * math.sin(ang) * step_length)
                    new_pos_z = round(2 * pos_z + mult * math.cos(ang) * step_length)
                    cell = LEVEL[new_pos_z][new_pos_x]
                    if cell in (' ', 'd', 'X') or (cell == 'D' and door_open):
                        f = [(i+1)/FPT for i in range(FPT)]
                    else:
                        f = [0.1, 0.25, 0.35, 0.20, 0.1, 0.0]
                        if mult == -1:
                            f = [0.5*i for i in f]

                    for m in f:
                        states.append((pos_x + mult * math.sin(ang)*step_length * m, pos_y, pos_z + mult * math.cos(ang)*step_length * m, ang))
                if key in (Keys.LEFT, Keys.RIGHT):
                    mult = 1 if key == Keys.LEFT else -1
                    for i in range(FPT):
                        states.append((pos_x, pos_y, pos_z, ang + mult * math.pi/2 * (i+1) / FPT))
                if key == Keys.SPACE:
                    for j in [-0.2, -0.3, -0.35, -0.3, -0.2, 0.0]:
                        states.append((pos_x, pos_y + j, pos_z, ang))
                # if key in (Keys.PAGE_UP, Keys.PAGE_DOWN):
                #     torch_intensity += 0.1 if key == Keys.PAGE_UP else -0.1
                #     torch.intensity = torch_intensity * torch_color
                #     states.append((pos_x, pos_y, pos_z, ang))
                if key in '<>':
                    item_idx = (item_idx + (1 if key == '>' else -1)) % len(items)
                    item = items[item_idx].hflip().scale(2)
                    states.append((pos_x, pos_y, pos_z, ang))
                if key == 'e':
                    new_pos_x = round(2 * pos_x + math.sin(ang) * step_length)
                    new_pos_z = round(2 * pos_z + math.cos(ang) * step_length)
                    if LEVEL[new_pos_z][new_pos_x] == 'D':
                        if has_key:
                            if door_open:
                                TEXTURES['D'].texture = ImageTexture(tileset[11*64+32-5-4])
                            else:
                                TEXTURES['D'].texture = ImageTexture(tileset[11*64+32-5])
                            door_open = not door_open
                        else:
                            scr.puttext(6, 10, "Locked!!!", Color4f(1.0,1.0,1.0), shadow_color=Color4f(0,0,0,1))
                            scr.sync()
                            time.sleep(1)
                    if round(2*pos_x) == 3 and round(2*pos_z) == 9 and not has_key:
                        TEXTURES['c'].texture = ImageTexture(tileset[45*64+45])
                        has_key = True
                        scr.puttext(6, 10, "You found", Color4f(1.0,1.0,1.0), shadow_color=Color4f(0,0,0,1))
                        scr.puttext(6, 22, "   Gold Key", Color4f(1.0,1.0, 0.0), shadow_color=Color4f(0,0,0,1))
                        scr.sync()
                        time.sleep(1)

                    states.append(prev_state)
                if key == '?':
                    if show_item:
                        for i in range(8):
                            scr.imshow(output)
                            scr.imshow(item, (8, 16 + 8 * i))
                            scr.sync()
                            time.sleep(0.1)
                        show_item = False
                    else:
                        for i in reversed(range(8)):
                            scr.imshow(output)
                            scr.imshow(item, (8, 16 + 8 * i))
                            scr.sync()
                            time.sleep(0.1)
                        show_item = True
                if key == 's':
                    scr.save_to_pnm(f'/tmp/out-{datetime.now()}.pnm')
                if key == Keys.ESC:
                    break

    finally:
        Keyboard.close()
        scr.close()


