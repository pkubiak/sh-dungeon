from .texture import Texture
from ..utils import Point3f
from ..image import Color4f


class ConstantTexture(Texture):
    def __init__(self, color: Color4f):
        self.color = color

    def get_color(self, point: Point3f) -> Color4f:
        return self.color