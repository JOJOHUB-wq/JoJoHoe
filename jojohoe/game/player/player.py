"""Player controller and camera interaction."""
from __future__ import annotations

import math
import numpy as np

from ..utils.math3d import vec3, normalize


class Player:
    def __init__(self, config):
        self.position = vec3(0, config["world"]["chunk_height"] // 2, 0)
        self.velocity = vec3(0, 0, 0)
        self.pitch = 0.0
        self.yaw = 0.0
        self.height = 1.8
        self.width = 0.6
        self.speed = config["controls"]["movement_speed"]
        self.jump_strength = config["controls"]["jump_strength"]
        self.invert_y = config["controls"].get("invert_y", False)
        self.on_ground = False

    @property
    def eye_height(self):
        return self.height * 0.9

    @property
    def eye_position(self):
        return self.position + vec3(0, self.eye_height, 0)

    @property
    def size(self):
        return vec3(self.width, self.height, self.width)

    def look(self, dx: float, dy: float, sensitivity: float):
        dy = -dy if self.invert_y else dy
        self.yaw += dx * sensitivity
        self.pitch -= dy * sensitivity
        self.pitch = max(-89.9, min(89.9, self.pitch))

    def direction(self) -> np.ndarray:
        rad_pitch = math.radians(self.pitch)
        rad_yaw = math.radians(self.yaw)
        x = math.cos(rad_pitch) * math.sin(rad_yaw)
        y = math.sin(rad_pitch)
        z = -math.cos(rad_pitch) * math.cos(rad_yaw)
        return normalize(vec3(x, y, z))

    def strafe_vector(self, forward: float, right: float) -> np.ndarray:
        dir_vec = self.direction()
        forward_vec = vec3(dir_vec[0], 0, dir_vec[2])
        forward_vec = normalize(forward_vec)
        right_vec = vec3(-forward_vec[2], 0, forward_vec[0])
        move = forward_vec * forward + right_vec * right
        if np.linalg.norm(move) > 0:
            move = normalize(move)
        return move
