import math

from .integrator import Integrator
from ..utils import Ray, Vector3f
from ..image import Color4f
from ..world import World
from ..lights import Light, LightHit


class RayTracingIntegrator(Integrator):
    def get_radiance(self, ray: Ray) -> Color4f:
        intersection = self.world.scene.intersect(ray)

        if intersection:
            if intersection.solid.coord_mapper:
                texture_point = intersection.solid.coord_mapper.get_coords(intersection)
            else:
                texture_point = intersection.hit_point

            color = intersection.solid.material.get_emission(texture_point, intersection.normal, intersection.ray.d)

            for light in self.world.lights:
                light_hit: LightHit = light.get_light_hit(intersection.hit_point)
            
                light_intersection = self.world.scene.intersect(Ray(intersection.ray(intersection.distance - 0.000001), -light_hit.direction))
                if light_intersection and light_hit.distance - light_intersection.distance > 0.000001:
                    continue

                intensity = light.get_intensity(light_hit)
                if Vector3f.dot(intersection.normal, light_hit.direction) > 0:
                    reflected = intersection.solid.material.get_reflectance(texture_point, intersection.normal, intersection.ray.d, light_hit.direction)
                else:
                    reflected = intersection.solid.material.get_reflectance(texture_point, -intersection.normal, intersection.ray.d, light_hit.direction)

                # print(intensity, reflected)
                color += intensity * reflected

            return color
        else:
            return Color4f(0.0, 0.0, 0.0, 1.0)