"""Small 3D math helpers used by the game."""
from __future__ import annotations

import math
from typing import Iterable, Tuple

import numpy as np

Vec3 = Tuple[float, float, float]


def vec3(x: float | Iterable[float], y: float | None = None, z: float | None = None) -> np.ndarray:
    if y is None and z is None:
        arr = np.array(list(x), dtype=float)
    else:
        arr = np.array([x, y, z], dtype=float)
    return arr


def length(v: np.ndarray) -> float:
    return float(np.linalg.norm(v))


def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n == 0:
        return v.copy()
    return v / n


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def aabb_collision(position: np.ndarray, size: np.ndarray, world_solid_test) -> np.ndarray:
    """Resolve collisions for an AABB against the world.

    Args:
        position: Current position vector (x, y, z).
        size: Size of the AABB (width, height, depth).
        world_solid_test: Callable that returns True if a world block is solid at integer coordinates.
    Returns:
        New position with collisions resolved.
    """
    px, py, pz = position
    w, h, d = size
    new_pos = np.array([px, py, pz], dtype=float)
    # Check collisions separately on each axis for simplicity.
    axes = [(0, w), (1, h), (2, d)]
    for axis, extent in axes:
        new_pos[axis] = position[axis]
        min_corner = new_pos - np.array([w / 2, 0, d / 2])
        for offset in [0, h]:
            x0 = int(math.floor(min_corner[0]))
            y0 = int(math.floor(min_corner[1] + offset))
            z0 = int(math.floor(min_corner[2]))
            for dx in range(0, math.ceil(w)):
                for dz in range(0, math.ceil(d)):
                    x = x0 + dx
                    z = z0 + dz
                    if world_solid_test(x, y0, z):
                        if axis == 1 and offset == 0 and position[axis] < y0 + 1:
                            new_pos[axis] = y0 + 1.0
                        elif axis == 1 and offset > 0 and position[axis] + h > y0:
                            new_pos[axis] = y0 - h - 0.001
    return new_pos


def raycast(origin: np.ndarray, direction: np.ndarray, max_distance: float, step: float = 0.1):
    direction = normalize(direction)
    distance = 0.0
    pos = origin.copy()
    while distance <= max_distance:
        block_pos = tuple(int(math.floor(v)) for v in pos)
        yield block_pos, distance
        pos += direction * step
        distance += step
