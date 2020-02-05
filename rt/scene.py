from typing import Tuple, Optional
from .solids.solid import Solid
from .utils import Ray
from .intersection import Intersection



class Scene:
    def __init__(self):
        self._objects = []

    def add(self, obj: Solid):
        self._objects.append(obj)

    def intersect(self, r: Ray, previous_best: Optional[float] = None) -> Optional[Intersection]:
        best, best_obj = previous_best, None

        for obj in self._objects:
            intersection = obj.intersect(r, best)
            if intersection and (best is None or intersection.distance < best):
                best, best_obj = intersection.distance, intersection

        return best_obj



