from abc import ABC, abstractmethod
from ..utils import Ray

class Integrator(ABC):
    def __init__(self, world):
        self.world = world
    
    @abstractmethod
    def get_radiance(self, ray: Ray):
        pass