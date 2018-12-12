import numpy as np

from OpenGL.GL import *

from .framework import Texture


class Framebuffer:

    def __init__(self, width, height):
        self._id = -1
        self._rbo_id = -1
        self._valid = False
        self._prev_viewport = (0, 0, 1, 1)
        self._prev_fbo_id = -1

        self._width = width
        self._height = height
        self._pending_width = -1
        self._pending_height = -1

        self._attachment = GL_COLOR_ATTACHMENT0
        self._bind_point = GL_FRAMEBUFFER

        self._texformat = GL_RGB
        self._textarget = GL_TEXTURE_2D

        self._setup_texture()
        self._setup_framebuffer()

    def __del__(self):
        glDeleteFramebuffers(1, np.array([self.id]))

    def __enter__(self):
        self._prev_viewport = glGetIntegerv(GL_VIEWPORT)
        self._prev_fbo_id = glGetIntegerv(GL_FRAMEBUFFER_BINDING)
        glBindFramebuffer(self._bind_point, self.id)
        self._update_size()
        glViewport(0, 0, self.width, self.height)

        return self

    def __exit__(self, exc_type, exc_value, tb):
        glBindFramebuffer(self._bind_point, self._prev_fbo_id)
        glViewport(
            self._prev_viewport[0],
            self._prev_viewport[1],
            self._prev_viewport[2],
            self._prev_viewport[3],
        )

    def _setup_texture(self):
        tex_desc = {
            'target': self._textarget,
            'unit': GL_TEXTURE0,
            'width': self.width,
            'height': self.height,
        }
        self._texture = Texture(**tex_desc)

    def _setup_framebuffer(self):
        self._prev_fbo_id = glGetIntegerv(GL_FRAMEBUFFER_BINDING)
        self._id = glGenFramebuffers(1)
        glBindFramebuffer(self._bind_point, self.id)

        glFramebufferTexture2D(
            self._bind_point,
            self._attachment,
            self._textarget,
            self._texture.id,
            0
        )

        status = glCheckFramebufferStatus(self._bind_point)
        self._valid = status == GL_FRAMEBUFFER_COMPLETE
        if not self._valid:
            print('Framebuffer Error: FBO is not complete!')

        glBindFramebuffer(self._bind_point, self._prev_fbo_id)

    def _update_size(self):
        # This method is needed to be called with fbo binding
        if self._pending_width < 0 and self._pending_height < 0:
            return

        self._width = self._pending_width
        self._height = self._pending_height

        self._setup_texture()
        glFramebufferTexture2D(
            self._bind_point,
            self._attachment,
            self._textarget,
            self._texture.id,
            0
        )

        self._pending_width = self._pending_height = -1

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        # id is a read-only property
        raise AttributeError

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._pending_width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._pending_height = value

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, value):
        # texture is a read-only property
        raise AttributeError
