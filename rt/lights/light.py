from abc import ABC, abstractmethod
from typing import NamedTuple
from ..utils import Vector3f, Point3f
from ..image import Color4f


class LightHit(NamedTuple):
    direction: Vector3f
    normal: Vector3f
    distance: float

    
class Light:
    @abstractmethod
    def get_light_hit(self, point: Point3f) -> LightHit:
        pass

    @abstractmethod
    def get_intensity(self, irr: LightHit) -> Color4f:
        pass
