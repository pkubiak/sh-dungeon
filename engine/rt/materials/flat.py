from .material import Material
from ..image import Image, Color4f
from ..utils import Point3f, Vector3f


class FlatMaterial(Material):
    def __init__(self, texture: Image):
        self.texture = texture

    def get_reflectance(self, point: Point3f, normal: Vector3f, out_dir: Vector3f, in_dir: Vector3f) -> Color4f:
        return Color4f(0.0, 0.0, 0.0, 0.0)

    def get_emission(self, point: Point3f, normal: Vector3f, out_dir: Vector3f) -> Color4f:
        return self.texture.get_color(point)