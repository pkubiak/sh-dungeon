from .solid import Solid
from ..utils import Vector3f, Point3f, Ray
from typing import NamedTuple, Optional


class Triangle(Solid):
    def __init__(self, p0: Point3f, v0: Vector3f, v1: Vector3f):
        self.p0 = p0
        self.v0 = v0
        self.v1 = v1
        self.normal = Vector3f.normal(v0, v1)

    @classmethod
    def from_points(self, p0: Point3f, p1: Point3f, p2: Point3f) -> 'Triangle':
        return Triangle(p0, p1 - p0, p2 - p0)

    def intersect(self, ray: Ray, previous_best: Optional[float] = None) -> Optional[float]:
        raise NotImplementedError()
        ti = Vector3f.dot(self.normal, self.p0 - ray.o) / Vector3f.dot(ray.d, self.normal)

        if ti < 0 or (previous_best is not None and ti > previous_best):
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

        if s < 0.0 or t < 0.0 or s + t > 1.0:
            return None

        return ti


if __name__ == '__main__':
    t = Triangle.from_points(Point3f(0, 0, 0), Point3f(1, 0, 0), Point3f(0, 1, 0))
    print(t)
    import sys
    print(sys.getsizeof(t))

    r = Ray(Point3f(1,1,1), -Vector3f(0.5, 0.5, 1))
    print(r)

    print(t.intersect(r))