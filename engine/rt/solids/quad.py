from typing import NamedTuple, Optional

from .solid import Solid
from ..utils import Vector3f, Point3f, Ray
from ..intersection import Intersection
from ..materials import Material
from ..coordmappers import CoordMapper
# from ..coordmappers import CoordMapper


class Quad(Solid):
    def __init__(self, p0: Point3f, v0: Vector3f, v1: Vector3f, *, material: Optional[Material] = None, coord_mapper: Optional[CoordMapper] = None):
        self.p0 = p0
        self.v0 = v0
        self.v1 = v1
        self.normal = Vector3f.normal(v0, v1)
        self.material = material
        self.coord_mapper = coord_mapper


    def intersect(self, ray: Ray, previous_best: Optional[Intersection] = None) -> Optional[Intersection]:
        try:
            ti = Vector3f.dot(self.normal, self.p0 - ray.o) / Vector3f.dot(ray.d, self.normal)
        except ZeroDivisionError:
            return None

        if ti < 0 or (previous_best is not None and (ti > previous_best.distance or (ti == previous_best.distance and id(previous_best.solid) >= id(self)))):
            return None

        # compute barycentric coordinates
        u, v, w = self.v0, self.v1, ray(ti) - self.p0

        uv = Vector3f.dot(u, v)
        wv = Vector3f.dot(w, v)
        vv = Vector3f.dot(v, v)
        wu = Vector3f.dot(w, u)
        uu = Vector3f.dot(u, u)

        s = (uv*wv-vv*wu)/(uv*uv-uu*vv)
        t = (uv*wu-uu*wv)/(uv*uv-uu*vv)

        if 0.0 <= s <= 1.0 and 0.0 <= t <= 1.0:
            return Intersection(
                solid=self,
                ray=ray,
                distance=ti,
                normal=self.normal,
                local=Point3f(1 - s - t, s, t)
            )

        return None
