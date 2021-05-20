import OpenGL.GL as gl
import ctypes
from .VertexArrayLayout import VertexArrayLayout
from .VertexBuffer import VertexBuffer

class VertexArray(object):
    def __init__(self):
        self.__rendererID = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.__rendererID)

    def __del__(self):
        gl.glDeleteVertexArrays(1,self.__rendererID)

    def addBuffer(self, vb: VertexBuffer, layout: VertexArrayLayout):
        '''
        Add vertex buffer and its layout.
        :param vb: vertex buffer
        :param layout: the layout of this buffer (e.g. 3 float position, 4 float color ...)
                       indicates structure of the buffer
        '''
        vb.bind()
        elements = layout.elements
        offset = 0
        for idx,element in enumerate(elements):
            gl.glEnableVertexAttribArray(idx)
            gl.glVertexAttribPointer(idx,element.count,element.type,element.normalized,layout.stride,ctypes.c_void_p(offset))
            offset+=element.count*element.getSizeOfType(element.type) # must be the size of bytes!

    def bind(self):
        gl.glBindVertexArray(self.__rendererID)

    def unbind(self):
        gl.glBindVertexArray(0)