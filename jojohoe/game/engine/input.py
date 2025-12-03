"""Input helper to track pressed keys."""
from __future__ import annotations

import pyglet


class InputHandler:
    def __init__(self, window):
        self.window = window
        self.keys = pyglet.window.key.KeyStateHandler()
        window.push_handlers(self.keys)

    def is_pressed(self, key):
        return self.keys[key]

    def scroll(self, x, y, scroll_x, scroll_y):
        window = self.window
        if scroll_y > 0:
            window.inventory.next_slot(-1)
        elif scroll_y < 0:
            window.inventory.next_slot(1)
