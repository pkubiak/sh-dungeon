from abc import ABC, abstractmethod
from ..utils import Point3f
from ..image import Color4f


class Texture(ABC):
    @abstractmethod
    def get_color(self, point: Point3f) -> Color4f:
        pass