from typing import List
from .scene import Scene
from .lights import Light


class World:
    def __init__(self, scene, lights: List[Light] = None):
        self.scene = scene
        self.lights = lights or []
