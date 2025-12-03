"""World management and chunk loading."""
from __future__ import annotations

import math
from typing import Dict, Tuple

import numpy as np

from .block import AIR, get
from .chunk import Chunk
from .generator import WorldGenerator
from ..utils.math3d import raycast


class World:
    def __init__(self, config):
        world_cfg = config["world"]
        self.chunk_size = world_cfg["chunk_size"]
        self.chunk_height = world_cfg["chunk_height"]
        self.render_distance = world_cfg["render_distance"]
        self.generator = WorldGenerator(world_cfg["seed"], self.chunk_height)
        self.chunks: Dict[Tuple[int, int], Chunk] = {}
        self.save_name = "default"

    def chunk_coords(self, x: int, z: int) -> Tuple[int, int]:
        return math.floor(x / self.chunk_size), math.floor(z / self.chunk_size)

    def ensure_chunk(self, cx: int, cz: int) -> Chunk:
        if (cx, cz) not in self.chunks:
            chunk = Chunk((cx, cz), self.chunk_size, self.chunk_height)
            self.generator.generate_chunk(chunk, cx * self.chunk_size, cz * self.chunk_size)
            self.chunks[(cx, cz)] = chunk
        return self.chunks[(cx, cz)]

    def world_to_chunk(self, x: int, y: int, z: int):
        cx, cz = self.chunk_coords(x, z)
        lx = x - cx * self.chunk_size
        lz = z - cz * self.chunk_size
        return cx, cz, lx, lz

    def get_block(self, x: int, y: int, z: int) -> int:
        cx, cz = self.chunk_coords(x, z)
        chunk = self.ensure_chunk(cx, cz)
        lx = x - cx * self.chunk_size
        lz = z - cz * self.chunk_size
        return chunk.get(lx, y, lz)

    def set_block(self, x: int, y: int, z: int, block_id: int):
        cx, cz = self.chunk_coords(x, z)
        chunk = self.ensure_chunk(cx, cz)
        lx = x - cx * self.chunk_size
        lz = z - cz * self.chunk_size
        chunk.set(lx, y, lz, block_id)
        # Neighboring chunks may also need rebuild if we touched a border
        for dx, dz in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nb = (cx + dx, cz + dz)
            if nb in self.chunks:
                self.chunks[nb].dirty = True

    def unload_far_chunks(self, player_pos):
        px, pz = player_pos[0], player_pos[2]
        keep = set()
        for dx in range(-self.render_distance, self.render_distance + 1):
            for dz in range(-self.render_distance, self.render_distance + 1):
                ccx, ccz = self.chunk_coords(int(px), int(pz))
                keep.add((ccx + dx, ccz + dz))
        for key in list(self.chunks.keys()):
            if key not in keep:
                del self.chunks[key]

    def load_visible(self, player_pos):
        ccx, ccz = self.chunk_coords(int(player_pos[0]), int(player_pos[2]))
        for dx in range(-self.render_distance, self.render_distance + 1):
            for dz in range(-self.render_distance, self.render_distance + 1):
                self.ensure_chunk(ccx + dx, ccz + dz)

    def solid_at(self, x: int, y: int, z: int) -> bool:
        if y < 0 or y >= self.chunk_height:
            return False
        return get(self.get_block(x, y, z)).solid

    def raycast_block(self, origin, direction, max_distance=6.0):
        prev = None
        for (bx, by, bz), distance in raycast(origin, direction, max_distance):
            if self.solid_at(bx, by, bz):
                return (bx, by, bz), prev
            prev = (bx, by, bz)
        return None, None

    def serialize(self):
        return {
            "chunks": [chunk.to_dict() for chunk in self.chunks.values()],
            "meta": {
                "chunk_size": self.chunk_size,
                "chunk_height": self.chunk_height,
                "seed": self.generator.seed,
            },
        }

    def save(self, extra: dict | None = None):
        from ..utils.resources import save_world

        data = self.serialize()
        if extra:
            data.update(extra)
        save_world(self.save_name, data)

    def load(self):
        from ..utils.resources import load_world

        data = load_world(self.save_name)
        if not data:
            return {}
        meta = data.get("meta", {})
        if meta.get("seed", self.generator.seed) != self.generator.seed:
            return {}
        self.chunks.clear()
        for cdict in data.get("chunks", []):
            chunk = Chunk.from_dict(cdict, self.chunk_size, self.chunk_height)
            self.chunks[(chunk.cx, chunk.cz)] = chunk
        return data
