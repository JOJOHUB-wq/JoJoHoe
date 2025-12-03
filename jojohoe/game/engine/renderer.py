"""OpenGL renderer for voxel chunks."""
from __future__ import annotations

import math
from typing import Tuple

import pyglet
from pyglet.gl import (
    GL_DEPTH_TEST,
    GL_CULL_FACE,
    GL_QUADS,
    GL_LINES,
    GL_BLEND,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
    glBegin,
    glBlendFunc,
    glColor4f,
    glCullFace,
    glDisable,
    glEnable,
    glEnd,
    glLineWidth,
    glNormal3f,
    glVertex3f,
    glPolygonOffset,
    glHint,
    GL_LINE_SMOOTH,
    GL_LINE_SMOOTH_HINT,
    GL_NICEST,
)

from ..world.block import get
from ..world.chunk import Chunk


class Renderer:
    def __init__(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        self.light_dir = (0.3, 1.0, 0.6)

    def draw_chunks(self, world, camera, player):
        for chunk in list(world.chunks.values()):
            if chunk.dirty or chunk.mesh is None:
                self.build_chunk_mesh(world, chunk)
            if chunk.mesh:
                chunk.mesh.draw(GL_QUADS)

    def build_chunk_mesh(self, world, chunk: Chunk):
        vertices = []
        colors = []
        normals = []
        size = chunk.size
        height = chunk.height
        cx = chunk.cx * size
        cz = chunk.cz * size
        for x in range(size):
            for y in range(height):
                for z in range(size):
                    block_id = chunk.get(x, y, z)
                    block = get(block_id)
                    if block_id == 0:
                        continue
                    wx, wy, wz = cx + x, y, cz + z
                    self._add_block_faces(world, wx, wy, wz, block, vertices, normals, colors)
        if vertices:
            count = len(vertices) // 3
            chunk.mesh = pyglet.graphics.vertex_list(count, ("v3f/static", vertices), ("n3f/static", normals), ("c4f/static", colors))
        else:
            chunk.mesh = None
        chunk.dirty = False

    def _neighbor_solid(self, world, x: int, y: int, z: int) -> bool:
        return world.solid_at(x, y, z)

    def _add_face(self, block, vertices, normals, colors, face_verts, normal):
        lx, ly, lz = normal
        light = max(0.3, min(1.0, (self.light_dir[0] * lx + self.light_dir[1] * ly + self.light_dir[2] * lz + 1) / 2))
        r, g, b, a = block.color
        r *= light
        g *= light
        b *= light
        for vx, vy, vz in face_verts:
            vertices.extend([vx, vy, vz])
            normals.extend(normal)
            colors.extend([r, g, b, a])

    def _add_block_faces(self, world, x: int, y: int, z: int, block, vertices, normals, colors):
        cube = [
            (((x, y, z), (x + 1, y, z + 1), (x + 1, y, z), (x, y, z + 1)), (0, -1, 0)),
            (((x, y + 1, z), (x, y + 1, z + 1), (x + 1, y + 1, z + 1), (x + 1, y + 1, z)), (0, 1, 0)),
            (((x, y, z), (x, y, z + 1), (x, y + 1, z + 1), (x, y + 1, z)), (-1, 0, 0)),
            (((x + 1, y, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x + 1, y, z + 1)), (1, 0, 0)),
            (((x, y, z), (x + 1, y, z), (x + 1, y + 1, z), (x, y + 1, z)), (0, 0, -1)),
            (((x, y, z + 1), (x, y + 1, z + 1), (x + 1, y + 1, z + 1), (x + 1, y, z + 1)), (0, 0, 1)),
        ]
        neighbors = [(0, -1, 0), (0, 1, 0), (-1, 0, 0), (1, 0, 0), (0, 0, -1), (0, 0, 1)]
        for idx, ((v0, v1, v2, v3), normal) in enumerate(cube):
            nx, ny, nz = neighbors[idx]
            if not self._neighbor_solid(world, x + nx, y + ny, z + nz):
                self._add_face(block, vertices, normals, colors, [v0, v1, v2, v3], normal)

    def draw_selection(self, block_pos):
        if not block_pos:
            return
        x, y, z = block_pos
        glDisable(GL_CULL_FACE)
        glLineWidth(2.0)
        glColor4f(1, 1, 0, 1)
        glBegin(GL_LINES)
        lines = [
            ((x, y, z), (x + 1, y, z)), ((x + 1, y, z), (x + 1, y, z + 1)), ((x + 1, y, z + 1), (x, y, z + 1)), ((x, y, z + 1), (x, y, z)),
            ((x, y + 1, z), (x + 1, y + 1, z)), ((x + 1, y + 1, z), (x + 1, y + 1, z + 1)), ((x + 1, y + 1, z + 1), (x, y + 1, z + 1)), ((x, y + 1, z + 1), (x, y + 1, z)),
            ((x, y, z), (x, y + 1, z)), ((x + 1, y, z), (x + 1, y + 1, z)), ((x + 1, y, z + 1), (x + 1, y + 1, z + 1)), ((x, y, z + 1), (x, y + 1, z + 1)),
        ]
        for (ax, ay, az), (bx, by, bz) in lines:
            glVertex3f(ax, ay, az)
            glVertex3f(bx, by, bz)
        glEnd()
        glEnable(GL_CULL_FACE)
