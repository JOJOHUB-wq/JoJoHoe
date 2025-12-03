"""Main pyglet window and game loop."""
from __future__ import annotations

import math

import numpy as np
import pyglet
from pyglet.window import key, mouse
from pyglet.gl import glClearColor, glViewport

from ..gui.hud import HUD
from ..gui.menus import MainMenu, PauseMenu
from ..inventory.inventory import Inventory
from ..player.physics import Physics
from ..player.player import Player
from ..utils import resources
from ..utils.math3d import vec3
from ..world import block
from ..world.world import World
from .camera import Camera
from .input import InputHandler
from .renderer import Renderer


class GameWindow(pyglet.window.Window):
    def __init__(self, config_path):
        self.config_data = resources.load_config(resources.data_path("config.json"))
        wcfg = self.config_data["window"]
        super().__init__(wcfg["width"], wcfg["height"], "Voxel Sandbox", vsync=self.config_data["graphics"].get("vsync", True), resizable=True)
        glClearColor(0.5, 0.7, 1.0, 1.0)
        self.state = "menu"
        self.inventory = Inventory()
        self.world = World(self.config_data)
        loaded = self.world.load()
        self.player = Player(self.config_data)
        self.physics = Physics(self.world)
        if loaded:
            pdata = loaded.get("player")
            inv_data = loaded.get("inventory")
            if pdata:
                self.player.position = np.array(pdata.get("position", self.player.position))
                self.player.yaw = pdata.get("yaw", 0)
                self.player.pitch = pdata.get("pitch", 0)
            if inv_data:
                self.inventory.load(inv_data)
        aspect = wcfg["width"] / wcfg["height"]
        self.camera = Camera(wcfg["fov"], aspect)
        self.renderer = Renderer()
        self.hud = HUD(self, self.inventory, self.config_data)
        self.input = InputHandler(self)
        self.main_menu = MainMenu(self)
        self.pause_menu = PauseMenu(self)
        self.capture_mouse = False
        self.selected_block = None
        self.place_position = None
        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    # -- State helpers --
    def start_game(self):
        self.state = "game"
        self.set_exclusive_mouse(True)
        self.capture_mouse = True

    def resume_game(self):
        self.state = "game"
        self.set_exclusive_mouse(True)
        self.capture_mouse = True

    def show_options(self):
        self.state = "options"
        self.set_exclusive_mouse(False)
        self.capture_mouse = False

    def save_and_quit(self):
        self.save_game()
        self.close()

    # -- Event handlers --
    def on_draw(self):
        self.clear()
        if self.state == "menu":
            self.main_menu.draw()
            return
        if self.state == "options":
            self.main_menu.title.text = "Options (press ESC)"
            self.main_menu.draw()
            return
        # 3D render
        width, height = self.get_framebuffer_size()
        self.camera.aspect_ratio = width / max(1, height)
        glViewport(0, 0, width, height)
        self.camera.set_perspective()
        self.camera.look(self.player.eye_position, self.player.direction())
        self.renderer.draw_chunks(self.world, self.camera, self.player)
        self.renderer.draw_selection(self.selected_block)
        # HUD
        self.hud.draw()
        if self.state == "paused":
            self.pause_menu.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.state == "game" and self.capture_mouse:
            self.player.look(dx, dy, self.config_data["controls"]["mouse_sensitivity"])

    def on_mouse_press(self, x, y, button, modifiers):
        if self.state == "menu":
            self.main_menu.on_mouse_press(x, y, button, modifiers)
            return
        if self.state == "paused":
            self.pause_menu.on_mouse_press(x, y, button, modifiers)
            return
        if self.state != "game":
            return
        if button == mouse.LEFT:
            if self.selected_block:
                bx, by, bz = self.selected_block
                self.world.set_block(bx, by, bz, block.AIR.id)
        elif button == mouse.RIGHT:
            item = self.inventory.current_item()
            if item and self.place_position:
                px, py, pz = self.place_position
                if 0 <= py < self.world.chunk_height:
                    self.world.set_block(px, py, pz, item.block_id)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            if self.state == "game":
                self.state = "paused"
                self.set_exclusive_mouse(False)
                self.capture_mouse = False
            else:
                self.resume_game()
        if symbol == key.E:
            if self.state == "game":
                self.state = "paused"
                self.set_exclusive_mouse(False)
                self.capture_mouse = False
        if symbol == key.F5 and self.state == "game":
            self.save_game()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.inventory.next_slot(-int(math.copysign(1, scroll_y)) if scroll_y != 0 else 0)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.hud.on_resize(width, height)
        self.main_menu.on_resize(width, height)
        self.pause_menu.on_resize(width, height)

    # -- Game loop --
    def update(self, dt):
        if self.state != "game":
            return
        self._handle_input(dt)
        self.world.load_visible(self.player.position)
        self.world.unload_far_chunks(self.player.position)
        hit, prev = self.world.raycast_block(self.player.eye_position, self.player.direction())
        self.selected_block = hit
        self.place_position = prev
        cx, cz = self.world.chunk_coords(int(self.player.position[0]), int(self.player.position[2]))
        fps = pyglet.clock.get_fps()
        self.hud.update(fps, self.player.position, (cx, cz))

    def _handle_input(self, dt):
        forward = 0
        right = 0
        if self.input.is_pressed(key.W):
            forward += 1
        if self.input.is_pressed(key.S):
            forward -= 1
        if self.input.is_pressed(key.D):
            right += 1
        if self.input.is_pressed(key.A):
            right -= 1
        move = self.player.strafe_vector(forward, right)
        self.player.velocity[0] = move[0] * self.player.speed
        self.player.velocity[2] = move[2] * self.player.speed
        if self.input.is_pressed(key.SPACE) and self.player.on_ground:
            self.player.velocity[1] = self.player.jump_strength
        self.player.position, self.player.velocity, grounded = self.physics.step(self.player.position, self.player.velocity, dt, self.player.size)
        self.player.on_ground = grounded

    def save_game(self):
        data = {
            "player": {
                "position": self.player.position.tolist(),
                "yaw": self.player.yaw,
                "pitch": self.player.pitch,
            },
            "inventory": self.inventory.as_dict(),
        }
        self.world.save(data)


def run():
    window = GameWindow(resources.data_path("config.json"))
    pyglet.app.run()

