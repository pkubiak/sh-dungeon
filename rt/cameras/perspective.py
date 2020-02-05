from .camera import Camera
from ..utils import Point3f, Vector3f, Ray
import math


class PerspectiveCamera(Camera):
    def __init__(self, center: Point3f, forward: Vector3f, up: Vector3f, vertical_view_angle: float, horizontal_view_angle: float):
        assert (0 <= vertical_view_angle <= 2.0 * math.pi) and (0 <= horizontal_view_angle <= 2.0 * math.pi), "Camera view's angles should be given in radians"
        self.center = center
        self.forward = forward

        self.fx = (math.tan(0.5 * horizontal_view_angle) * forward.length) * Vector3f.normal(forward, up)
        self.fy = (-math.tan(0.5 * vertical_view_angle) * forward.length) * Vector3f.normal(forward, self.fx)

    def get_primary_ray(self, x: float, y: float) -> Ray:
        vxy = (x * self.fx) + (y * self.fy)
        return Ray(self.center, self.forward + vxy)