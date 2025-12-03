"""Simple player physics and collision."""
from __future__ import annotations

import math
import numpy as np


class Physics:
    def __init__(self, world, gravity: float = -20.0):
        self.world = world
        self.gravity = gravity

    def step(self, position: np.ndarray, velocity: np.ndarray, dt: float, size: np.ndarray) -> tuple[np.ndarray, np.ndarray, bool]:
        velocity[1] += self.gravity * dt
        on_ground = False
        deltas = velocity * dt
        for axis in range(3):
            position[axis] += deltas[axis]
            collided, axis_grounded = self._resolve_axis(position, size, axis, deltas[axis])
            if collided:
                velocity[axis] = 0
            on_ground = on_ground or axis_grounded
        return position, velocity, on_ground

    def _resolve_axis(self, pos: np.ndarray, size: np.ndarray, axis: int, delta: float) -> tuple[bool, bool]:
        half_w = size[0] / 2
        half_d = size[2] / 2
        height = size[1]
        min_x = pos[0] - half_w
        max_x = pos[0] + half_w
        min_y = pos[1]
        max_y = pos[1] + height
        min_z = pos[2] - half_d
        max_z = pos[2] + half_d
        collided = False
        grounded = False
        x_range = range(math.floor(min_x), math.ceil(max_x) + 1)
        y_range = range(math.floor(min_y), math.ceil(max_y) + 1)
        z_range = range(math.floor(min_z), math.ceil(max_z) + 1)
        for x in x_range:
            for y in y_range:
                for z in z_range:
                    if self.world.solid_at(x, y, z):
                        if axis == 1 and delta < 0 and pos[1] < y + 1:
                            pos[1] = y + 1
                            grounded = True
                            collided = True
                        elif axis == 1 and delta > 0 and pos[1] + height > y:
                            pos[1] = y - height
                            collided = True
                        elif axis == 0 and delta > 0 and pos[0] + half_w > x:
                            pos[0] = x - half_w
                            collided = True
                        elif axis == 0 and delta < 0 and pos[0] - half_w < x + 1:
                            pos[0] = x + 1 + half_w
                            collided = True
                        elif axis == 2 and delta > 0 and pos[2] + half_d > z:
                            pos[2] = z - half_d
                            collided = True
                        elif axis == 2 and delta < 0 and pos[2] - half_d < z + 1:
                            pos[2] = z + 1 + half_d
                            collided = True
        return collided, grounded
