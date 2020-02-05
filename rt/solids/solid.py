from typing import Optional
from abc import abstractmethod, ABC
from ..utils import Ray


class Solid(ABC):
    @abstractmethod
    def intersect(self, ray: Ray, previous_best: Optional[float] = None) -> Optional[float]:
        pass