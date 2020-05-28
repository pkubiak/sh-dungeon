from .integrator import Integrator
from ..utils import Ray, Vector3f
from ..image import Color4f
import math

COLORS = [
    (230, 25, 75), (60, 180, 75), (255, 225, 25), (0, 130, 200), (245, 130, 48), (145, 30, 180), (70, 240, 240), (240, 50, 230), (210, 245, 60), (250, 190, 190), (0, 128, 128), (230, 190, 255), (170, 110, 40), (255, 250, 200), (128, 0, 0), (170, 255, 195), (128, 128, 0), (255, 215, 180), (0, 0, 128), (128, 128, 128), (255, 255, 255)
]

MAPPING = dict()

class RayCastingIntegrator(Integrator):
    def __init__(self, scene):
        self.scene = scene

    def get_radiance(self, ray: Ray) -> Color4f:
        inter = self.scene.intersect(ray)

        if inter:
            radiance = abs(Vector3f.dot(inter.normal, ray.d) / (ray.d.length))

            # if id(obj) not in MAPPING:
            #     MAPPING[id(obj)] = len(MAPPING)

            return (radiance, radiance, radiance, 1.0)
        else:
            return (0.0, 0.0, 0.0, 1.0)