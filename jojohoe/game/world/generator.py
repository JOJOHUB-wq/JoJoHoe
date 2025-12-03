"""Procedural world generation using Perlin noise."""
from __future__ import annotations

import random
from typing import Tuple

from noise import pnoise2

from .block import DIRT, GRASS, SAND, STONE, WATER, WOOD, LEAVES


class WorldGenerator:
    def __init__(self, seed: int, height: int):
        self.seed = seed
        self.height = height
        self.rand = random.Random(seed)

    def height_at(self, x: float, z: float) -> int:
        base = pnoise2(x / 50.0, z / 50.0, octaves=4, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=self.seed)
        variation = pnoise2(x / 12.0, z / 12.0, octaves=2, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=self.seed + 10)
        height = int((base * 0.5 + variation * 0.5 + 1) * (self.height / 4))
        return max(1, min(self.height - 1, height))

    def generate_column(self, world_x: int, world_z: int) -> Tuple[int, list[int]]:
        top = self.height_at(world_x, world_z)
        column = []
        for y in range(self.height):
            if y > top:
                column.append(0)
            elif y == top:
                column.append(GRASS.id if top > 4 else SAND.id)
            elif top - 4 < y < top:
                column.append(DIRT.id)
            else:
                column.append(STONE.id)
        water_level = self.height // 8
        for y in range(top + 1, max(top, water_level)):
            if y < water_level:
                column[y] = WATER.id
        return top, column

    def generate_chunk(self, chunk, world_x: int, world_z: int):
        size = chunk.size
        for x in range(size):
            for z in range(size):
                wx = world_x + x
                wz = world_z + z
                top, column = self.generate_column(wx, wz)
                chunk.data[x, :, z] = column
                if self.rand.random() < 0.02 and top > self.height // 8:
                    self._place_tree(chunk, x, top + 1, z)
        chunk.dirty = True

    def _place_tree(self, chunk, x: int, y: int, z: int):
        height = self.rand.randint(3, 5)
        for dy in range(height):
            if y + dy < chunk.height:
                chunk.set(x, y + dy, z, WOOD.id)
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                for dy in range(2, 5):
                    if dx * dx + dz * dz + (dy - 3) * (dy - 3) <= 6:
                        bx = x + dx
                        by = y + height + dy - 3
                        bz = z + dz
                        if 0 <= bx < chunk.size and 0 <= bz < chunk.size and 0 <= by < chunk.height:
                            chunk.set(bx, by, bz, LEAVES.id)
