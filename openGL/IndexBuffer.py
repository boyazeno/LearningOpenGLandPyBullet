import OpenGL.GL as gl
import numpy as np

class IndexBuffer(object):
    def __init__(self,index):
        '''
        Create a index buffer.
        :param index: buffer data, should be numpy array. Each element is the index, type is np.int32.
        '''
        if type(index)!=np.ndarray or index.dtype!=np.int32:
            raise TypeError(f"[Type Error] Index should be numpy array with dtype int32! "
                            f"But the given type is {type(index)}.")
        self.__renderID = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.__renderID)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, index.nbytes, index, gl.GL_STATIC_DRAW)
        self.__count = index.size

    def __del__(self):
        gl.glDeleteBuffers(1,self.__renderID)

    def bind(self):
        '''
        Bind this buffer to current context.
        '''
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.__renderID)

    def unbind(self):
        '''
        Unbind this buffer from current context.
        '''
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

    @property
    def count(self):
        return self.__count