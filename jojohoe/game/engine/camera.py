"""Camera transforms for first-person view."""
from __future__ import annotations

import math

from pyglet.gl import glLoadIdentity, glMatrixMode, gluLookAt, gluPerspective, GL_MODELVIEW, GL_PROJECTION


class Camera:
    def __init__(self, fov: float, aspect_ratio: float, near: float = 0.1, far: float = 500.0):
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

    def set_perspective(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.aspect_ratio, self.near, self.far)
        glMatrixMode(GL_MODELVIEW)

    def look(self, position, direction):
        glLoadIdentity()
        eye_x, eye_y, eye_z = position
        dir_x, dir_y, dir_z = direction
        center_x = eye_x + dir_x
        center_y = eye_y + dir_y
        center_z = eye_z + dir_z
        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 1, 0)
