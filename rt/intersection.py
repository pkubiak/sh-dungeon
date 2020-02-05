from typing import NamedTuple
from .solids import Solid
from .utils import Ray, Vector3f, Point3f


class Intersection(NamedTuple):
    solid: Solid
    ray: Ray

    # ray depended distance to intersection point
    distance: float 

    # normal vector of solid surface in intersection point
    normal: Vector3f

    # local solid coordinates of intersection point
    local: Point3f 

    @property
    def hit_point(self):
        return self.ray(self.distance)