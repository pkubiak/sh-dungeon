from .light import Light, LightHit
from ..utils import Point3f
from ..image import Color4f


class PointLight(Light):
    def __init__(self, position: Point3f, intensity: Color4f):
        self.position = position
        self.intensity = intensity

    def get_light_hit(self, point: Point3f) -> LightHit:
        hp = point - self.position

        return LightHit(
            direction=hp.normalized(),
            distance=hp.length,
            normal=None
        )

    def get_intensity(self, irr: LightHit) -> Color4f:
        return self.intensity * (irr.distance**-2)