"""Inventory and hotbar handling."""
from __future__ import annotations

from typing import List, Optional

from . import items


class Inventory:
    def __init__(self):
        self.slots: List[Optional[str]] = ["stone", "dirt", "grass", "sand", "wood", "leaves", None, None, None]
        self.selected = 0

    def next_slot(self, delta: int):
        self.selected = (self.selected + delta) % len(self.slots)

    def set_slot(self, index: int, item_id: Optional[str]):
        if 0 <= index < len(self.slots):
            self.slots[index] = item_id

    def current_item(self):
        item_id = self.slots[self.selected]
        if item_id is None:
            return None
        return items.get(item_id)

    def item_name(self) -> str:
        item = self.current_item()
        return item.name if item else "Empty"

    def as_dict(self):
        return {"slots": self.slots, "selected": self.selected}

    def load(self, data):
        if not data:
            return
        self.slots = data.get("slots", self.slots)
        self.selected = data.get("selected", self.selected)
