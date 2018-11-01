import numpy as np

from abc import *
from OpenGL.GL import *
from os.path import abspath
from os.path import join
from os.path import dirname

from .framework import *


__dir__ = abspath(dirname(__file__))


def resource_path(relpath):
    return join(__dir__, relpath)


class RendererBase(metaclass=ABCMeta):

    @abstractmethod
    def prepare(self):
        pass

    @abstractmethod
    def reshape(self, w, h):
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def dispose(self):
        pass


class Renderer(RendererBase):

    default_vs_path = resource_path('./shader/basic.vs')
    default_fs_path = resource_path('./shader/basic.fs')

    def __init__(
            self,
            vs_path=default_vs_path,
            fs_path=default_fs_path,
            gs_path=None,
            name=''):
        self.name = name
        self._vs_path = vs_path
        self._fs_path = fs_path
        self._gs_path = gs_path
        self._program = None

    def prepare(self):
        with open(self._vs_path) as f:
            vs_code = f.read()
        with open(self._fs_path) as f:
            fs_code = f.read()

        gs_code = None
        if self._gs_path:
            with open(self._gs_path) as f:
                gs_code = f.read()

        self._program = Program(
            vs_code=vs_code,
            fs_code=fs_code,
            gs_code=gs_code
        )

    def reshape(self, w, h):
        glViewport(0, 0, w, h)

    def render(self):
        pass

    def dispose(self):
        self._program = None


class RendererGroup(Renderer):

    def __init__(self, name=''):
        self.name = name
        self.renderers = []

    def prepare(self):
        for r in self.renderers:
            r.prepare()

    def reshape(self, w, h):
        for r in self.renderers:
            r.reshape(w, h)

    def render(self):
        for r in self.renderers:
            r.render()

    def dispose(self):
        for r in self.renderers:
            r.dispose()


class TriangleRenderer(Renderer):

    def __init__(self, name=''):
        super().__init__(
            name=name
        )
        self._vertex_object = None

    def prepare(self):
        super().prepare()

        v = np.array(
            [-0.5, -0.5, +0.0, 1.0, 0.0, 0.0,
             +0.5, -0.5, +0.0, 0.0, 1.0, 0.0,
             +0.0, +0.5, +0.0, 0.0, 0.0, 1.0],
            dtype='float32'
        )
        self._vertex_object = VertexObject(v, [3, 3])

    def render(self):
        with self._program:
            with self._vertex_object as vo:
                glDrawArrays(GL_TRIANGLES, 0, vo.vertex_count)

    def dispose(self):
        super().dispose()
        self._vertex_object = None


class RectangleRenderer(Renderer):

    def __init__(self, name=''):
        super().__init__(
            name=name
        )
        self._vertex_object = None

    def prepare(self):
        super().prepare()

        v = np.array(
            [-0.5, -0.5, +0.0, 1.0, 0.0, 0.0,
             +0.5, -0.5, +0.0, 0.0, 1.0, 0.0,
             -0.5, +0.5, +0.0, 0.0, 0.0, 1.0,
             +0.5, +0.5, +0.0, 1.0, 1.0, 1.0],
            dtype='float32'
        )
        e = np.array(
            [0, 1, 2,
             1, 3, 2],
            dtype='uint8'
        )
        self._vertex_object = VertexObject(v, [3, 3], e)

    def render(self):
        with self._program:
            with self._vertex_object as vo:
                glDrawElements(
                    GL_TRIANGLES,
                    vo.element_count,
                    GL_UNSIGNED_BYTE,
                    None
                )

    def dispose(self):
        super().dispose()
        self._vertex_object = None


class TextureRenderer(Renderer):

    default_vs_path = resource_path('./shader/basic_tex.vs')
    default_fs_path = resource_path('./shader/basic_tex.fs')

    def __init__(self, name='', image=None):
        super().__init__(
            vs_path=self.default_vs_path,
            fs_path=self.default_fs_path,
            name=name
        )

        self._image = None
        self._next_image = None
        self._vertex_object = None
        self._texture = None

        self.image = image

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._next_image = value

    def prepare(self):
        super().prepare()
        v = np.array(
            [-1.0, -1.0, +0.0, 0.0, 0.0,
             +1.0, -1.0, +0.0, 1.0, 0.0,
             -1.0, +1.0, +0.0, 0.0, 1.0,
             +1.0, +1.0, +0.0, 1.0, 1.0],
            dtype='float32'
        )
        e = np.array(
            [0, 1, 2,
             1, 3, 2],
            dtype='uint8'
        )
        self._vertex_object = VertexObject(v, [3, 2], e)
        self._texture = Texture()

    def render(self):
        if self._next_image is not None:
            self._image = self._next_image
            self.texture.update(image=self._image)

            self._next_image = None

        with self._program as program:
            with self._vertex_object as vo:
                with self.texture as tex:
                    program.setInt('inputTexture', tex.unit_number)
                    glDrawElements(
                        GL_TRIANGLES,
                        vo.element_count,
                        GL_UNSIGNED_BYTE,
                        None
                    )

    def dispose(self):
        super().dispose()
        self._vertex_object = None
        self._texture = None
        self._next_image = self._image
        self._image = None

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, value):
        # texture is a read-only property
        raise AttributeError
