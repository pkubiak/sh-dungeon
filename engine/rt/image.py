import os.path
from enum import Enum
from typing import Tuple, Union, Optional, NamedTuple, List
from .utils import Point3f

Rect = Tuple[int, int, int, int]
Color3i = Tuple[int, int, int]
# Color4i = Tuple[int, int, int, int]
Color3f = Tuple[float, float, float]


class Color4f():
    r: float
    g: float
    b: float
    a: float

    def __init__(self, r: float, g: float, b: float, a: float = 1.0):
        assert (0 <= r <= 1.0) and (0 <= g <= 1.0) and (0 <= b <= 1.0) and (0 <= a <= 1.0)

        self.r, self.g, self.b, self.a = r, g, b, a

    def __add__(self, other: 'Color4f') -> 'Color4f':
        if isinstance(other, Color4f):
            return Color4f(self.r + other.r, self.g + other.g, self.b + other.b, 1.0)
        raise TypeError()

    def __mul__(self, other: float):
        if isinstance(other, float):
            return Color4f(self.r * other, self.g * other, self.b * other, 1.0)
        if isinstance(other, Color4f):
            return Color4f(self.r * other.r, self.g * other.g, self.b * other.b, 1.0)
        raise TypeError(f"Can't multiply Color4f by {type(other)}")

    def __rmul__(self, other: float):
        return self * other

    def trim(self) -> 'Color4f':
        return Color4f(
            0.0 if self.r < 0.0 else (1.0 if self.r > 1.0 else self.r),
            0.0 if self.g < 0.0 else (1.0 if self.g > 1.0 else self.g),
            0.0 if self.b < 0.0 else (1.0 if self.b > 1.0 else self.b),
            0.0 if self.a < 0.0 else (1.0 if self.a > 1.0 else self.a),
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, Color4f):
            return (self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a)
        return False
    
    @property
    def as_3i(self):
        return (int(255 * self.r), int(255 * self.g), int(255 * self.b))


class Interpolation(Enum):
    NONE = 0
    LINEAR = 1


class PNMLoader:
    @classmethod
    def from_pnm(cls, path: str, *,
                 transparency: Optional[Color3i] = None) -> 'Image':
        """
        Read texture from P3 (RGB ascii) or P6 (RGB raw) PNM format.
        
        @param path:
        @param crop_to:
        @param transparency:
        """
        with open(path, 'rb') as file:
            pos = 0
            lines = file.read().split(b"\n")

            while lines[pos].strip().startswith(b'#'):
                pos += 1
            version = lines[pos].strip()
            assert version in (b'P3', b'P6')
            pos += 1
            while lines[pos].strip().startswith(b'#'):
                pos += 1
            width, height = map(int, lines[pos].strip().split())
            pos += 1
            while lines[pos].strip().startswith(b'#'):
                pos += 1
            assert lines[pos].strip() == b'255'
            pos += 1

            # Read colors info
            values = []
            if version == b'P3':
                # Read image in Ascii encoding
                for i in range(width*height):
                    r, g, b = map(int, lines[pos+3*i: pos+3*i+3])
                    color = Color4f(r/255, g/255, b/255, 0.0 if (r, g, b) == transparency else 1.0)
                    values.append(color)
            else:
                # Read image in raw encoding
                data = b'\n'.join(lines[pos:])

                for i in range(0, width*height):
                    r, g, b = data[3*i: 3*i+3]
                    
                    color = Color4f(r/255, g/255, b/255, 0.0 if (r, g, b) == transparency else 1.0)
                    values.append(color)
                
            assert len(values) == width * height

        # Build Image instance
        texture = Image(width=width, height=height)
        for y in range(height):
            for x in range(width):
                texture[x, y] = values[y * width + x]

        return texture


class PAMLoader:
    @staticmethod
    def _readline(file, keyword: str = None):
        while True:
            line = file.readline().strip()
            if not line.startswith(b'#'):
                if keyword:
                    key, *items = line.split()
                    if keyword != key:
                        raise SyntaxError(f"Expected keyword {keyword} but get {key}")
                    return items

                return line

    @classmethod
    def from_pam(cls, path: str):
        with open(path, 'rb') as file:
            cls._readline(file, b'P7')

            width, = map(int, cls._readline(file, b'WIDTH'))
            height, = map(int, cls._readline(file, b'HEIGHT'))
            depth, = map(int, cls._readline(file, b'DEPTH'))
            
            maxval, = map(int, cls._readline(file, b'MAXVAL'))
            assert maxval == 255

            tupltype, = cls._readline(file, b'TUPLTYPE')
            if depth == 3:
                assert tupltype == b'RGB'
            elif depth == 4:
                assert tupltype == b'RGB_ALPHA'
            else:
                raise ValueError(f"Unknown TUPLTYPE: {tupltype}")
            cls._readline(file, b'ENDHDR')

            image = Image(width=width, height=height)
            for y in range(height):
                for x in range(width):
                    color = file.read(depth)
                    color = [i / maxval for i in color]
                    if color == 3:
                        color.append(1.0)

                    image[x, y] = Color4f(*color)
            return image


class ImageLoader:
    @classmethod
    def load(cls, path: str, crop_to: Optional[Rect] = None, *args, **kwargs) -> 'Image':
        _root, ext = os.path.splitext(path)

        if ext == '.pnm':
            image = PNMLoader.from_pnm(path, *args, **kwargs)
        elif ext == '.pam':
            image = PAMLoader.from_pam(path, *args, **kwargs)
        else:
            raise ValueError(f"Unsupported image type '{ext}'")

        if crop_to:
            image = image.crop(crop_to)
            
        return image

class Image(ImageLoader):
    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def size(self):
        return (self._width, self._height)


    def __init__(self, *, width: int, height: int):
        """Create empty white texture of given size."""
        assert (width > 0) and (height > 0)

        self._width = width
        self._height = height
        self._data = [Color4f(1.0, 1.0, 1.0, 1.0)] * (width*height)


    def __setitem__(self, position: Tuple[int, int], value: Union[Color3f, Color4f]):
        if isinstance(value, tuple) and len(value) == 3:
            value = Color4f(*value)

        assert isinstance(value, Color4f), f"{value}"

        x, y = position
        assert (0 <= x < self._width) and (0 <= y < self._height)

        self._data[y*self._width + x] = value


    def __getitem__(self, position: Tuple[int, int]) -> Color4f:
        x, y = position
        assert (0 <= x < self._width) and (0 <= y < self._height)

        return self._data[y * self._width + x]

    def crop(self, crop_to: Rect) -> 'Image':
        """
        Crop texture to given rectangle.
        
        @param crop_to_: (x0, y0, x1, y1)
        """
        x0, y0, x1, y1 = crop_to
        assert (0 <= x0 <= x1 < self._width) and (0 <= y0 <= y1 < self._height)

        texture = Image(width=(x1-x0+1), height=(y1-y0+1))
        for y in range(y0, y1+1):
            for x in range(x0, x1+1):
                texture[x - x0, y - y0] = self[x,y]

        return texture
    
    def hflip(self) -> 'Image':
        out = Image(width=self.width, height=self.height)
        for y in range(self.height):
            for x in range(self.width):
                out[x, y] = self[self.width - 1 - x, y]
        return out

    def scale(self, scale_x: int, scale_y: Optional[int] = None) -> 'Image':
        if not scale_y:
            scale_y = scale_x
            
        assert isinstance(scale_x, int) and scale_x > 0 and isinstance(scale_y, int) and scale_y > 0

        out = Image(width=scale_x*self.width, height=scale_y*self.height)
        
        for y in range(self.height):
            for x in range(self.width):
                for i in range(scale_x):
                    for j in range(scale_y):
                        out[scale_x*x+i, scale_y*y+j] = self[x, y]
        return out

    def as_tileset(self, width: int, height: int) -> List['Image']:
        assert self.width % width == 0
        assert self.height % height == 0
        return [
            self.crop((width*x, height*y, width*(x+1)-1, height*(y+1)-1))
            for y in range(self.height // height)
            for x in range(self.width // width)
        ]

    
    # def interpolate(self, point: Point3f, *, interpolation: Interpolation = Interpolation.NONE) -> Color4f:
    #     # print(point)
    #     x, y = round((self.width-1) * point.x), round((self.height-1) * point.y)
    #     return self[x, y]
    #     # raise NotImplementedError()

 

if __name__ == '__main__':
    torch = Image.load('gfx/torch.pnm')
    print(torch.width, torch.height)
    print(torch[12,12])
    torch = Image.load('gfx/torch.pnm', transparency=(0, 255, 255))
    print(torch[12,12])
    torch2 = torch.crop((0, 0, 4, 4))
    print(torch2.width, torch2.height)
