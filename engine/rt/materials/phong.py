from .material import Material
from ..image import Image, Color4f
from ..utils import Vector3f, Point3f
import math


class PhongMaterial(Material):
    def __init__(self, specular: Image, exponent: float):
        self.specular = specular
        self.exponent = exponent
    
    def get_reflectance(self, point: Point3f, normal: Vector3f, out_dir: Vector3f, in_dir: Vector3f) -> Color4f:
        r_out_dir = (2.0 * Vector3f.dot(normal, out_dir)) * normal - out_dir

        ang = Vector3f.dot(in_dir, r_out_dir)
        cos_ = Vector3f.dot(normal, in_dir.normalized())

        c = (self.exponent + 2.0) / (2.0 * math.pi) * max(0.0, ang) ** self.exponent * cos_

        return c * self.specular.get_color(point)

    def get_emission(self, point: Point3f, normal: Vector3f, out_dir: Vector3f) -> Color4f:
        return Color4f(0.0, 0.0, 0.0, 0.0)