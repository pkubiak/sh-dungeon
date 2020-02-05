from .material import Material
from ..utils import Point3f, Vector3f
from ..image import Color4f


class DummyMaterial(Material):
    def get_reflectance(self, point: Point3f, normal: Vector3f, out_dir: Vector3f, in_dir: Vector3f) -> Color4f:
        color = Vector3f.dot(normal, in_dir) / in_dir.length
        return Color4f(color, color, color, 1.0)

    def get_emission(self, point: Point3f, normal: Vector3f, out_dir: Vector3f) -> Color4f:
        return Color4f(0.0, 0.0, 0.0, 0.0)