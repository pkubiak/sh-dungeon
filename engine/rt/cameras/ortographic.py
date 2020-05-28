from .camera import Camera
from ..utils import Ray, Point3f, Vector3f


class OrtographicCamera(Camera):
    def __init__(self, center: Point3f, forward: Vector3f, up: Vector3f, scale_x: float, scale_y: float):
        self.center = center
        self.forward = forward.normalized()
        self.up = up.normalized()

        # camera axies
        self.sx = (0.5 * scale_x) * Vector3f.normal(self.forward, self.up)
        self.sy = (-0.5 * scale_y) * Vector3f.normal(self.forward, self.sx)

    def get_primary_ray(self, x: float, y: float) -> Ray:
        return Ray(
            self.center + (x * self.sx + y * self.sy),
            self.forward
        )