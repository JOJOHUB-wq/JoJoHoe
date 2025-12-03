"""Block registry and helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

Color = Tuple[float, float, float, float]


@dataclass(frozen=True)
class Block:
    id: int
    name: str
    solid: bool = True
    color: Color = (1.0, 1.0, 1.0, 1.0)


REGISTRY: Dict[int, Block] = {}
NAME_MAP: Dict[str, Block] = {}


def register(block: Block):
    REGISTRY[block.id] = block
    NAME_MAP[block.name] = block


def get(block_id: int) -> Block:
    return REGISTRY.get(block_id, AIR)


def get_by_name(name: str) -> Block:
    return NAME_MAP.get(name, AIR)


# Define base blocks
AIR = Block(0, "air", solid=False, color=(0, 0, 0, 0))
STONE = Block(1, "stone", color=(0.5, 0.5, 0.5, 1))
DIRT = Block(2, "dirt", color=(0.59, 0.29, 0.0, 1))
GRASS = Block(3, "grass", color=(0.3, 0.8, 0.3, 1))
SAND = Block(4, "sand", color=(0.92, 0.86, 0.5, 1))
WATER = Block(5, "water", solid=False, color=(0.2, 0.4, 0.9, 0.6))
WOOD = Block(6, "wood", color=(0.55, 0.27, 0.07, 1))
LEAVES = Block(7, "leaves", solid=True, color=(0.25, 0.6, 0.25, 0.8))

for b in [AIR, STONE, DIRT, GRASS, SAND, WATER, WOOD, LEAVES]:
    register(b)
