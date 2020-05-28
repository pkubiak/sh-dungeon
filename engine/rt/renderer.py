from .image import Image
from .cameras import Camera

class Renderer:
    def __init__(self, camera: Camera, integrator):
        self.camera = camera
        self.integrator = integrator

    def render(self, texture: Image) -> None:
        for y in range(texture.height):
            for x in range(texture.width):
                rx, ry = 2.0 * x / (texture.width-1) - 1.0, 2.0 * y / (texture.height-1) - 1.0

                ray = self.camera.get_primary_ray(rx, ry)
                texture[x, y] = self.integrator.get_radiance(ray).trim()
            