from abc import ABC, abstractmethod
from ..intersection import Intersection
from ..utils import Point3f


class CoordMapper(ABC):
    @abstractmethod
    def get_coords(self, intersection: Intersection) -> Point3f:
        pass