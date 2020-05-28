from typing import NamedTuple

class Vector3f(NamedTuple):    
    x: float
    y: float
    z: float

    @property
    def length(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    def __neg__(self) -> 'Vector3f':
        return Vector3f(-self.x, -self.y, -self.z)

    def __mul__(self, value: float):
        if isinstance(value, float):
            return Vector3f(self.x * value, self.y * value, self.z * value)
        raise TypeError(f"Can't multiple Vector3f by {type(value)}")

    def __rmul__(self, value: float):
        return self * value

    def __add__(self, other: 'Vector3f') -> 'Vector3f':
        if isinstance(other, Vector3f):
            return Vector3f(self.x + other.x, self.y + other.y, self.z + other.z)
        raise TypeError()

    def __sub__(self, other: 'Vector3f') -> 'Vector3f':
        if isinstance(other, Vector3f):
            return Vector3f(self.x - other.x, self.y - other.y, self.z - other.z)
        raise TypeError()

    def normalized(self) -> 'Vector3f':
        l = self.length
        return Vector3f(self.x / l, self.y / l, self.z / l)

    @classmethod
    def normal(cls, v0: 'Vector3f', v1: 'Vector3f') -> 'Vector3f':
        return Vector3f(
            v0.y * v1.z - v0.z * v1.y,
            v0.z * v1.x - v0.x * v1.z,
            v0.x * v1.y - v0.y * v1.x
        ).normalized()

    @classmethod
    def dot(cls, v0: 'Vector3f', v1: 'Vector3f') -> float:
        return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z


class Point3f(NamedTuple):
    x: float
    y: float
    z: float

    def __eq__(self, other: 'Point3f') -> bool:
        if not isinstance(other, Point3f):
            return False
        return (self.x == other.x) and (self.y == other.y) and (self.z == other.z)

    def __sub__(self, other: 'Point3f') -> Vector3f:
        if isinstance(other, Point3f):
            return Vector3f(self.x - other.x, self.y - other.y, self.z - other.z)
        raise TypeError()

    def __add__(self, other: Vector3f):
        if isinstance(other, Vector3f):
            return Point3f(self.x + other.x, self.y + other.y, self.z + other.z)
        raise TypeError()


class Ray(NamedTuple):
    o: Point3f  # origin
    d: Vector3f  # direction

    def __call__(self, t: float):
        return self.o + (t * self.d)



if __name__ == '__main__':
    p0 = Point3f(1,2,3)
    print(p0)
    p1 = Point3f(3,3,3)

    print(p1 - p0)

    normal = Vector3f.normal(p1 - p0, Vector3f(1, 1, 1))
    print(normal, normal.length)