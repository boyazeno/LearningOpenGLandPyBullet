import OpenGL.GL as gl
import ctypes

from .VertexBuffer import VertexBuffer  # self defined vertex buffer wrapper
from .IndexBuffer import IndexBuffer    # self defined index buffer wrapper
from .VertexArrayLayout import VertexArrayLayout # self defined structure of vertex buffer
from .VertexArray import VertexArray    # self defined vertex array object
from .Shader import Shader              # self defined shader generator
from .Texture import Texture            # self defined image texture class
from . import Utility
import numpy as np
import copy

class Renderer(object):
    def __init__(self):
        gl.glEnable(gl.GL_BLEND) # using  blending function: overlap current image with previous image(background if after clear)
        gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA) # (multiplier of current, multiplier of background)
        gl.glBlendEquation(gl.GL_FUNC_ADD) # alpha*cur + (1-alpha)*background
        pass

    def draw(self, va: VertexArray, vi: IndexBuffer, shader: Shader, texture):
        va.bind()
        vi.bind()
        shader.bind()
        if texture:
            texture.bind()
        gl.glDrawElements(gl.GL_TRIANGLES, vi.count, gl.GL_UNSIGNED_INT, ctypes.c_void_p(0))
        # clear
        va.unbind()
        vi.unbind()
        shader.unbind()
        if texture:
            texture.unbind()

    def clear(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)


def GLClearError():
    while gl.glGetError() != gl.GL_NO_ERROR:
        pass


def GLCheckError():
    error = gl.glGetError()
    while error != gl.GL_NO_ERROR:
        print(f"[OpenGL Error] ({str(error)})")
        error = gl.glGetError()



class VisualObject(object):
    def __init__(self, data:list, index:list, shaderFile:str, renderer:Renderer, proj:np.ndarray, color:tuple):

        assert len(data)==len(index), f"Number of vertex array and index array not equal! Got {len(data)} and {len(index)}"

        self.data = copy.deepcopy(data)
        self.index = copy.deepcopy(index)
        self.arrayGroup = []
        for va,vi in zip(self.data,self.index):
            vertexBuffer = VertexBuffer(va)  # vertex buffer
            vertexBufferLayout = VertexArrayLayout()  # structure of the vertex buffer
            vertexArray = VertexArray()  # 产生一个vertex array，用于绑定buffer
            vertexBufferLayout.push(gl.GL_FLOAT, 3)  # here draw 2D vertex position, so (float, 2)
            vertexArray.addBuffer(vertexBuffer, vertexBufferLayout)  # add buffer and its structure

            indexBuffer = IndexBuffer(vi)  # index buffer, tells how to use the vertex in vertex buffer
            self.arrayGroup.append((vertexArray,indexBuffer))

        # renderer
        self.renderer = renderer

        # 加入shader
        self.shader = Shader(shaderFile)  # shader, tells how to give each point color, and so on

        # 定义fragment shader中 uniform变量（即颜色）
        self.shader.setUniform4f("u_Color",*color)  # set the param used in shader code, which is a "vec4" here.
        #self.shader.setUniform1i("u_Texture", 0)  # set the slot of the texture to 0
        self.proj = proj
        self.view = Utility.matAffine([np.pi / 3., np.pi / 6., 0.] )  # set camera view (translation, rotation)
        self.model = Utility.matTranslation(0., 0.)  # set model pose
        mvp = self.proj.dot(self.view).dot(self.model)
        self.shader.setUniformMatrix4fv("u_MVP", mvp)  # projection matrix for torsion

    def setPose(self,pose:np.ndarray):
        mvp = self.proj.dot(self.view).dot(pose)
        self.shader.setUniformMatrix4fv("u_MVP", mvp)

    def setView(self,view:np.ndarray):
        self.view = view

    def draw(self):
        for va, vi in self.arrayGroup:
            va.bind()
            vi.bind()
            self.shader.bind()
            self.renderer.draw(va,vi,self.shader,None)
            va.unbind()
            vi.unbind()
            self.shader.unbind()
