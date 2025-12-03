"""Item definitions for inventory and hotbar."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..world import block


@dataclass
class Item:
    id: str
    block_id: int
    name: str


ITEMS: Dict[str, Item] = {}


def register(item: Item):
    ITEMS[item.id] = item


def get(item_id: str) -> Item:
    return ITEMS[item_id]


register(Item("stone", block.STONE.id, "Stone"))
register(Item("dirt", block.DIRT.id, "Dirt"))
register(Item("grass", block.GRASS.id, "Grass"))
register(Item("sand", block.SAND.id, "Sand"))
register(Item("wood", block.WOOD.id, "Wood"))
register(Item("leaves", block.LEAVES.id, "Leaves"))
