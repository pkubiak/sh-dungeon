import math

from .texture import Texture
from ..image import Image, Color4f
from ..utils import Point3f




def lerp2d(v00, v10, v01, v11, scale_x, scale_y):
    return (1.0 - scale_x)*(1.0 - scale_y)*v00 + \
        scale_x * (1.0 - scale_y) * v10 + \
        (1.0 - scale_x) * scale_y * v01 + \
        scale_x * scale_y * v11


class ImageTexture(Texture):
    INTERPOLATION_NEAREST = 'INTERPOLATION_NEAREST'
    INTERPOLATION_LINEAR = 'INTERPOLATION_LINEAR'
    INTERPOLATION_BILINEAR = 'INTERPOLATION_BILINEAR'

    BORDER_CLAMP = 'BORDER_CLAMP'
    BORDER_MIRROR = 'BORDER_MIRROR'
    BORDER_REPEAT = 'BORDER_REPEAT'

    def __init__(self, image: Image, *, interpolation=INTERPOLATION_NEAREST, border_handling=BORDER_CLAMP):
        self.image = image
        self.interpolation = interpolation
        self.border_handling = border_handling


    def _get_color(self, x: int, y: int) -> Color4f:
        w, h = self.image.size

        if self.border_handling == self.BORDER_CLAMP:
            x = 0 if x < 0 else (w-1 if x>=w else x)
            y = 0 if y < 0 else (h-1 if y>=h else y)
        elif self.border_handling == self.BORDER_REPEAT:
            x %= w
            y %= h
        else:
            raise NotImplementedError()

        return self.image[x, y]

    def get_color(self, point: Point3f) -> Color4f:
        x, y = point.x, point.y
        x = point.x * self.image.width
        y = point.y * self.image.height

        if self.interpolation == self.INTERPOLATION_NEAREST:
            return self._get_color(round(x), round(y))
        elif self.interpolation == self.INTERPOLATION_LINEAR:
            fx = math.floor(x)
            fy = math.floor(y)

            return lerp2d(
                self._get_color(fx, fy),
                self._get_color(fx+1, fy),
                self._get_color(fx, fy+1),
                self._get_color(fx+1, fy+1),
                x - fx,
                y - fy
            )
        elif self.interpolation == self.INTERPOLATION_BILINEAR:
            fx = math.floor(x)
            fy = math.floor(y)

            v0 = (fx+1 - x)*self._get_color(fx, fy) + (x - fx)*self._get_color(fx+1, fy)
            v1 = (fx+1 - x)*self._get_color(fx, fy+1) + (x - fx)*self._get_color(fx+1, fy+1)

            return (fy+1 - y)*v0 + (y - fy)*v1
        else:
            raise NotImplementedError()

    