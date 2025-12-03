"""Heads-up display elements for in-game view."""
from __future__ import annotations

import pyglet
from pyglet import shapes

from ..inventory.inventory import Inventory


class HUD:
    def __init__(self, window, inventory: Inventory, config):
        self.window = window
        self.inventory = inventory
        self.show_fps = config["graphics"].get("show_fps", True)
        self.batch = pyglet.graphics.Batch()
        w, h = window.get_framebuffer_size()
        self.crosshair = shapes.Line(w // 2 - 10, h // 2, w // 2 + 10, h // 2, width=2, color=(255, 255, 255), batch=self.batch)
        self.crosshair_v = shapes.Line(w // 2, h // 2 - 10, w // 2, h // 2 + 10, width=2, color=(255, 255, 255), batch=self.batch)
        self.label = pyglet.text.Label("", font_size=12, x=10, y=10, anchor_x="left", anchor_y="bottom", batch=self.batch)
        self.hotbar_rects = [shapes.BorderedRectangle(0, 0, 0, 0, border=2, color=(50, 50, 50), border_color=(255, 255, 255), batch=self.batch) for _ in range(9)]
        self.hotbar_labels = [pyglet.text.Label("", font_size=10, anchor_x="center", anchor_y="center", batch=self.batch) for _ in range(9)]

    def on_resize(self, width, height):
        self.crosshair.x = width // 2 - 10
        self.crosshair.x2 = width // 2 + 10
        self.crosshair.y = self.crosshair.y2 = height // 2
        self.crosshair_v.x = self.crosshair_v.x2 = width // 2
        self.crosshair_v.y = height // 2 - 10
        self.crosshair_v.y2 = height // 2 + 10
        self._layout_hotbar(width, height)

    def _layout_hotbar(self, width, height):
        slot_size = 42
        margin = 6
        start_x = width // 2 - ((slot_size + margin) * 9 // 2)
        y = 24
        for i in range(9):
            rect = self.hotbar_rects[i]
            rect.x = start_x + i * (slot_size + margin)
            rect.y = y
            rect.width = rect.height = slot_size
            rect.border_color = (255, 255, 0) if i == self.inventory.selected else (255, 255, 255)
            label = self.hotbar_labels[i]
            label.text = str(i + 1)
            label.x = rect.x + slot_size // 2
            label.y = rect.y + slot_size // 2

    def update(self, fps: float, position, chunk):
        if self.show_fps:
            cx, cz = chunk
            x, y, z = position
            self.label.text = f"FPS: {fps:.1f} | Pos: {x:.1f}, {y:.1f}, {z:.1f} | Chunk: {cx},{cz} | Item: {self.inventory.item_name()}"
        else:
            self.label.text = ""
        self._layout_hotbar(*self.window.get_framebuffer_size())

    def draw(self):
        self.batch.draw()
