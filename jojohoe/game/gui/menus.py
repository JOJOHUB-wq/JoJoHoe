"""Simple menu screens."""
from __future__ import annotations

import pyglet
from pyglet import shapes


class MenuBase:
    def __init__(self, window):
        self.window = window
        w, h = window.get_framebuffer_size()
        self.batch = pyglet.graphics.Batch()
        self.bg = shapes.Rectangle(0, 0, w, h, color=(20, 20, 30), batch=self.batch)
        self.title = pyglet.text.Label("Voxel Sandbox", font_size=36, x=w // 2, y=h - 100, anchor_x="center", anchor_y="center", batch=self.batch)
        self.buttons = []

    def add_button(self, text, x, y, callback):
        btn = MenuButton(text, x, y, callback, self.batch)
        self.buttons.append(btn)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            if btn.contains(x, y):
                btn.callback()

    def on_resize(self, width, height):
        self.bg.width = width
        self.bg.height = height
        self.title.x = width // 2
        self.title.y = height - 100
        offset = len(self.buttons) * 60
        for i, btn in enumerate(self.buttons):
            btn.x = width // 2 - 100
            btn.y = height // 2 + offset - i * 80

    def draw(self):
        self.batch.draw()


class MenuButton:
    def __init__(self, text, x, y, callback, batch):
        self.callback = callback
        self.rect = shapes.BorderedRectangle(x, y, 200, 50, border=3, color=(60, 60, 80), border_color=(200, 200, 200), batch=batch)
        self.label = pyglet.text.Label(text, font_size=16, x=x + 100, y=y + 25, anchor_x="center", anchor_y="center", batch=batch)

    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, value):
        self.rect.x = value
        self.label.x = value + self.rect.width // 2

    @property
    def y(self):
        return self.rect.y

    @y.setter
    def y(self, value):
        self.rect.y = value
        self.label.y = value + self.rect.height // 2

    def contains(self, x, y):
        return self.rect.x <= x <= self.rect.x + self.rect.width and self.rect.y <= y <= self.rect.y + self.rect.height


class MainMenu(MenuBase):
    def __init__(self, window):
        super().__init__(window)
        w, h = window.get_framebuffer_size()
        self.add_button("Play", w // 2 - 100, h // 2 + 40, lambda: window.start_game())
        self.add_button("Options", w // 2 - 100, h // 2 - 40, lambda: window.show_options())
        self.add_button("Quit", w // 2 - 100, h // 2 - 120, lambda: window.close())


class PauseMenu(MenuBase):
    def __init__(self, window):
        super().__init__(window)
        w, h = window.get_framebuffer_size()
        self.add_button("Resume", w // 2 - 100, h // 2 + 40, lambda: window.resume_game())
        self.add_button("Save & Quit", w // 2 - 100, h // 2 - 40, lambda: window.save_and_quit())
