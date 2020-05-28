from typing import Tuple, Optional
from .solids.solid import Solid
from .utils import Ray
from .intersection import Intersection



class Scene:
    def __init__(self):
        self._objects = []

    def add(self, obj: Solid):
        self._objects.append(obj)

    def intersect(self, r: Ray, previous_best: Optional[Intersection] = None, lower_bound: Optional[Intersection] = None) -> Optional[Intersection]:
        best = previous_best

        for obj in self._objects:
            intersection = obj.intersect(r, best)
            if intersection and (lower_bound is None or lower_bound < intersection) and (best is None or intersection < best):
                best = intersection

        return best



