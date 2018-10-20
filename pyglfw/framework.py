import ctypes
import numpy as np
import pyrr

from OpenGL.GL import *
from PIL import Image

from .glutils import *


verbose = False


def debug(msg):
    if verbose:
        print(msg)


class Program:

    def __init__(self, vs_code, fs_code, gs_code=None):
        shaders = []
        shaders.append(create_shader(GL_VERTEX_SHADER, vs_code))
        shaders.append(create_shader(GL_FRAGMENT_SHADER, fs_code))
        if gs_code:
            shaders.append(create_shader(GL_GEOMETRY_SHADER, gs_code))

        self._id = create_program(shaders)

        for shader in shaders:
            glDeleteShader(shader)

    def __del__(self):
        if self._id > 0:
            status = glGetProgramiv(self._id, GL_LINK_STATUS)
            if status != GL_FALSE:
                glDeleteProgram(self._id)

    def __enter__(self):
        glUseProgram(self._id)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        glUseProgram(0)

    def setInt(self, name, value):
        glUniform1i(glGetUniformLocation(self._id, name), value)

    def setFloat(self, name, value):
        glUniform1f(glGetUniformLocation(self._id, name), value)

    def setVec3f(self, name, value):
        count = int(value.shape[0] / 3)
        glUniform3fv(glGetUniformLocation(self._id, name), count, value)

    def setVec4f(self, name, value):
        count = int(value.shape[0] / 4)
        glUniform4fv(glGetUniformLocation(self._id, name), count, value)

    def setMatrix4(self, name, value):
        glUniformMatrix4fv(
            glGetUniformLocation(self._id, name),
            1,
            GL_FALSE,
            value
        )


class VertexObject:

    # vertices: float numpy array (1d)
    # alignment: int Python array
    # indices: uint8 numpy array
    def __init__(self, vertices, alignment, indices=None):
        self._vbo = 0
        self._vao = 0
        self._prev_vao = 0
        self._index_object = None

        total = 0
        for part in alignment:
            total = total + part

        # Checking alignment
        remain = vertices.size % total
        if remain is not 0:
            raise ValueError

        self._size = vertices.size
        self._stride = total
        self._attribute_count = len(alignment)
        self._vertex_count = int(vertices.size / self._stride)

        self._vao = glGenVertexArrays(1)
        with self:
            self._vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
            glBufferData(
                GL_ARRAY_BUFFER,
                vertices,
                GL_STATIC_DRAW
            )

            for i in range(self._attribute_count):
                glVertexAttribPointer(
                    i,
                    alignment[i],
                    GL_FLOAT,
                    False,
                    self._stride * ctypes.sizeof(ctypes.c_float),
                    ctypes.c_void_p(
                        offsetof(i, alignment) * ctypes.sizeof(ctypes.c_float)
                    )
                )
                # Unordered layout would not work!
                glEnableVertexAttribArray(i)

        if indices is not None and indices.size > 0:
            self.index_object = IndexObject(indices)

        debug('vo {} is created VAO({}), VBO({})'.
              format(self, self._vao, self._vbo))

    def __del__(self):
        if self._vbo is not None:
            glDeleteBuffers(1, np.array([self._vbo]))
        if self._vao is not None:
            glDeleteVertexArrays(1, np.array([self._vao]))
        debug('vo {} is deleted'.format(self))

    def __enter__(self):
        self._prev_vao = glGetIntegerv(GL_VERTEX_ARRAY_BINDING)
        glBindVertexArray(self._vao)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        glBindVertexArray(self._prev_vao)

    def update(self, vertices):
        if vertices.size != self._size:
            return False

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(
            GL_ARRAY_BUFFER,
            vertices,
            GL_STATIC_DRAW
        )
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        return True

    @property
    def index_object(self):
        return self._index_object

    @index_object.setter
    def index_object(self, value):
        self._index_object = value
        with self:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, value.id)

    @property
    def vertex_count(self):
        return self._vertex_count

    @property
    def element_count(self):
        if self.index_object is not None:
            return self.index_object.count
        return 0


class IndexObject:

    def __init__(self, indices):
        self._id = 0
        self._prev_ebo = 0
        self.update(indices)
        debug('eo {} is created EBO({})'.format(self, self.id))

    def __del__(self):
        if self._id > 0:
            glDeleteBuffers(1, np.array([self.id]))
        debug('eo {} is deleted'.format(self))

    def update(self, indices):
        if self._id is 0:
            self._id = glGenBuffers(1)

        self._count = indices.size
        with self:
            glBufferData(
                GL_ELEMENT_ARRAY_BUFFER,
                indices,
                GL_STATIC_DRAW
            )

    def __enter__(self):
        self._prev_ebo = glGetIntegerv(GL_ELEMENT_ARRAY_BUFFER_BINDING)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.id)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._prev_ebo)

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        # count is a read-only property
        raise AttributeError

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        # id is a read-only property
        raise AttributeError


class Texture:

    def __init__(self, **kwargs):
        self._id = glGenTextures(1)
        self.update(**kwargs)

    def __del__(self):
        glDeleteTextures(np.array([self.id], dtype='int32'))

    def __enter__(self):
        glActiveTexture(self._unit)
        glBindTexture(self._target, self.id)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        glActiveTexture(self._unit)
        glBindTexture(self._target, 0)

    # image is numpy uint8 array
    def update(self, **kwargs):
        self._target = kwargs.pop('target', GL_TEXTURE_2D)
        self._unit = kwargs.pop('unit', GL_TEXTURE0)
        self._format = kwargs.pop('format', GL_RGB)
        self.unit_number = self._unit - GL_TEXTURE0

        image = kwargs.pop('image', None)
        if image is not None:
            self._width, self._height = image.shape[1], image.shape[0]
        else:
            self._width = kwargs.pop('width', 0)
            self._height = kwargs.pop('height', 0)

        glBindTexture(self._target, self.id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        glTexImage2D(
            self._target,
            0,
            self._format,
            self._width, self._height,
            0,
            self._format,  # GL_RGB,  # BGR
            GL_UNSIGNED_BYTE,
            image
        )

        glBindTexture(self._target, 0)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        # id is a read-only property
        raise AttributeError


class Framebuffer:

    def __init__(self, width, height):
        self._id = -1
        self._rbo_id = -1
        self._valid = False
        self._prev_viewport = (0, 0, 1, 1)
        self._prev_fbo_id = -1

        self._width = width
        self._height = height

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
            'uint': GL_TEXTURE0,
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
        # width is a read-only property
        raise AttributeError

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        # height is a read-only property
        raise AttributeError

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, value):
        # texture is a read-only property
        raise AttributeError
