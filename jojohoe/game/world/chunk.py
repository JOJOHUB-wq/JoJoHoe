"""Chunk data container and mesh state."""
from __future__ import annotations

import numpy as np
from typing import Dict, Tuple

from .block import AIR


class Chunk:
    def __init__(self, position: Tuple[int, int], size: int, height: int):
        self.cx, self.cz = position
        self.size = size
        self.height = height
        self.data = np.zeros((size, height, size), dtype=np.uint8)
        self.dirty = True
        self.mesh = None

    def __repr__(self):
        return f"Chunk({self.cx}, {self.cz})"

    def get(self, x: int, y: int, z: int) -> int:
        if 0 <= x < self.size and 0 <= y < self.height and 0 <= z < self.size:
            return int(self.data[x, y, z])
        return AIR.id

    def set(self, x: int, y: int, z: int, block_id: int):
        if 0 <= x < self.size and 0 <= y < self.height and 0 <= z < self.size:
            self.data[x, y, z] = block_id
            self.dirty = True

    def to_dict(self) -> Dict:
        return {
            "position": [self.cx, self.cz],
            "data": self.data.flatten().tolist(),
        }

    @classmethod
    def from_dict(cls, data: Dict, size: int, height: int) -> "Chunk":
        chunk = cls(tuple(data["position"]), size, height)
        arr = np.array(data["data"], dtype=np.uint8)
        chunk.data = arr.reshape((size, height, size))
        chunk.dirty = True
        return chunk
