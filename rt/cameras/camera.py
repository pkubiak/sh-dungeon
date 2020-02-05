from abc import ABC, abstractmethod
from ..utils import Ray


class Camera(ABC):
    @abstractmethod
    def get_primary_ray(self, x: float, y: float) -> Ray:
        pass