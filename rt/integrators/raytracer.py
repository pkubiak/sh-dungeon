import math
from typing import Optional

from .integrator import Integrator
from ..utils import Ray, Vector3f
from ..image import Color4f
from ..world import World
from ..lights import Light, LightHit
from ..intersection import Intersection

EPS = 0.001
MAX_DEPTH = 16

class RayTracingIntegrator(Integrator):
    def get_radiance(self, ray: Ray, depth: int = 0, lower_bound: Optional[Intersection] = None) -> Color4f:
        intersection = self.world.scene.intersect(ray, lower_bound=lower_bound)

        if intersection:
            if depth >= MAX_DEPTH:
                return Color4f(1.0, 0.0, 0.0, 1.0)
            if intersection.solid.coord_mapper:
                texture_point = intersection.solid.coord_mapper.get_coords(intersection)
            else:
                texture_point = intersection.hit_point

            color = intersection.solid.material.get_emission(texture_point, intersection.normal, intersection.ray.d)
            if color.a < 1.0:
                # ray2 = Ray(ray(intersection.distance), ray.d)
                # intersection2 = Intersection(intersection.solid, intersection.ray, 0, intersection.normal, intersection.local) 
                other = self.get_radiance(ray, depth+1, lower_bound=intersection)
                color = color.a*color + (1.0 - color.a)*other
                # color = 0.8*color + 0.2*Color4f(0,0,0,1)

            # for light in self.world.lights:
            #     light_hit: LightHit = light.get_light_hit(intersection.hit_point)

            #     light_intersection = self.world.scene.intersect(Ray(intersection.ray(intersection.distance - EPS), -light_hit.direction))
            #     if light_intersection and light_hit.distance - light_intersection.distance < EPS:
            #         continue

            #     intensity = light.get_intensity(light_hit)
            #     if Vector3f.dot(intersection.normal, light_hit.direction) > 0:
            #         reflected = intersection.solid.material.get_reflectance(texture_point, intersection.normal, intersection.ray.d, light_hit.direction)
            #     else:
            #         reflected = intersection.solid.material.get_reflectance(texture_point, -intersection.normal, intersection.ray.d, light_hit.direction)

            #     # print(intensity, reflected)
            #     color += intensity * reflected

            return color
        else:
            return Color4f(0.0, 0.0, 0.0, 1.0)
