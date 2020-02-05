from .coordmapper import CoordMapper
from ..utils import Point3f
from ..intersection import Intersection
from typing import NamedTuple


class TriangleMapper(CoordMapper):
    def __init__(self, p0: Point3f, p1: Point3f, p2: Point3f):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2

    
    def get_coords(self, intersection: Intersection) -> Point3f:
        p = intersection.local

        res = Point3f(
            (self.p0.x * p.x + self.p1.x * p.y + self.p2.x * p.z),
            (self.p0.y * p.x + self.p1.y * p.y + self.p2.y * p.z),
            (self.p0.z * p.x + self.p1.z * p.y + self.p2.z * p.z),
        )

        return res