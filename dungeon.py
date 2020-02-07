import random, math, time
from rt.solids import Triangle, Quad
from rt.utils import Point3f, Ray, Vector3f
from rt.scene import Scene
from rt.cameras import PerspectiveCamera
from rt.renderer import Renderer
from rt.image import Image, Color4f
from rt.integrators import RayTracingIntegrator
from screen import Screen
from keyboard import Keyboard, Keys
from rt.materials import DummyMaterial, FlatMaterial, PhongMaterial
from rt.world import World
from rt.lights import PointLight
from rt.coordmappers import TriangleMapper
from rt.textures import ConstantTexture, ImageTexture

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
# ### # ### # ###
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

def build_scene(tileset):
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
    floor_mapper = TriangleMapper(Point3f(0.0,0.0,0.0), Point3f(20+width, 0.0, 0.0), Point3f(0.0, 20+height, 0.0))
    floor = FlatMaterial(floor_tex)

    # Door
    # door_tex = ImageTexture(Image.from_pnm('./gfx/doors.pnm'))
    # door = FlatMaterial(door_tex)

    # Wall
    # wall_tex = ConstantTexture(Color4f(0.5, 0.5, 0.5, 1.0))
    # wall_tex = ImageTexture(Image.from_pnm('./gfx/wall3.pnm'),)
    # wall = FlatMaterial(wall_tex)

    if DEBUG:
        sky = wall = floor = dummy

    # wall = dummy
    s = Scene()
    # add sky
    s.add(Quad(Point3f(-1000,-20, -1000), Vector3f(2000+width, 0, 0), Vector3f(0, 0, 2000+height), material=sky, coord_mapper=sky_mapper))

    # add ground
    s.add(Quad(Point3f(-10, 0, -10), Vector3f(20+width, 0, 0), Vector3f(0, 0, 20 + height), material=floor, coord_mapper=floor_mapper))

    # horizontal walls
    mapping = {
        '#': 19*64-20,
        'S': 18*64+32,
        'D': 15*64+32,
        'd': 15*64+34,
    }

    tex_mapping = {key: FlatMaterial(ImageTexture(tileset[value])) for key, value in mapping.items()}

    for y in range(height+1):
        for x in range(width):
            c = LEVEL[2*y][2*x+1]
            if c != ' ':
                q = Quad(Point3f(x, -1, y), Vector3f(0, 1, 0), Vector3f(1, 0, 0), material=tex_mapping[c], coord_mapper=mapper)
                s.add(q)
    # vertical walls
    for y in range(height):
        for x in range(width+1):
            c = LEVEL[2*y+1][2*x]
            if c != ' ':
                q = Quad(Point3f(x, -1, y), Vector3f(0, 1, 0), Vector3f(0, 0, 1), material=tex_mapping[c], coord_mapper=mapper)
                s.add(q)
    return s

if __name__ == '__main__':
    def random_point():
        return Point3f(random.random(), random.random(), random.random())

    tileset = Image.from_pnm('./gfx/tileset.pnm', transparency=(0,255,255)).as_tileset(32,32)
    
    s = build_scene(tileset)

    N = 31
    scr  = Screen(2*N+1, 2*N+1)
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

    item_idx = 0
    item = items[item_idx].hflip().scale(2)
    show_item = True

    try:
        Keyboard.init()

        while True:
            if states:
                pos_x, pos_y, pos_z, ang = states[0]
                states = states[1:]
                torch.position = Point3f(pos_x, pos_y, pos_z)

                view_angle = 100 / 180 * math.pi

                camera = PerspectiveCamera(Point3f(pos_x, pos_y, pos_z), Vector3f(math.sin(ang), 0, math.cos(ang)), Vector3f(0, 1, 0), view_angle, view_angle)

                r = Renderer(camera, integrator)
                r.render(output)

                scr.imshow(output)
                if show_item:
                    scr.imshow(item, (8, 16))
                scr.sync()
            else:
                key = Keyboard.getch()
                if key == Keys.UP:
                    for i in range(FPT):
                        states.append((pos_x +  math.sin(ang)*step_length * (i+1) / FPT, pos_y, pos_z + math.cos(ang)*step_length * (i+1) / FPT, ang))
                if key == Keys.DOWN:
                    for i in range(FPT):
                        states.append((pos_x -  math.sin(ang)*step_length * (i+1) / FPT, pos_y, pos_z - math.cos(ang)*step_length * (i+1) / FPT, ang))
                if key == Keys.LEFT:
                    for i in range(FPT):
                        states.append((pos_x, pos_y, pos_z, ang + math.pi/2 * (i+1) / FPT))
                if key == Keys.RIGHT:
                    for i in range(FPT):
                        states.append((pos_x, pos_y, pos_z, ang - math.pi/2 * (i+1) / FPT))
                if key == Keys.SPACE:
                    for j in [-0.2, -0.3, -0.35, -0.3, -0.2, 0.0]:
                        states.append((pos_x, pos_y + j, pos_z, ang))
                if key in (Keys.PAGE_UP, Keys.PAGE_DOWN):
                    torch_intensity += 0.1 if key == Keys.PAGE_UP else -0.1
                    torch.intensity = torch_intensity * torch_color
                    states.append((pos_x, pos_y, pos_z, ang))
                if key in '<>':
                    item_idx = (item_idx + (1 if key == '>' else -1)) % len(items)
                    item = items[item_idx].hflip().scale(2)
                    states.append((pos_x, pos_y, pos_z, ang))
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
                if key == Keys.ESC:
                    break

    finally:
        Keyboard.close()
        scr.close()


