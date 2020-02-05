from abc import ABC, abstractmethod
from ..utils import Point3f, Vector3f
from ..image import Color4f


class Material(ABC):
    @abstractmethod
    def get_reflectance(self, point: Point3f, normal: Vector3f, out_dir: Vector3f, in_dir: Vector3f) -> Color4f:
        pass

    @abstractmethod
    def get_emission(self, point: Point3f, normal: Vector3f, out_dir: Vector3f) -> Color4f:
        pass

