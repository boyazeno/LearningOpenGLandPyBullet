import OpenGL.GL as gl
import numpy as np

class VertexBuffer(object):
    def __init__(self,data):
        '''
        Create a vertex buffer.
        :param data: buffer data, should be numpy array. Each raw is one vertex, type is np.float.
        '''
        if type(data)!=np.ndarray or data.dtype!=np.float32:
            raise TypeError(f"[Type Error] Data should be numpy array with dtype float32! "
                            f"But the given type is {type(data)}.")
        self.__rendererID = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.__rendererID)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_STATIC_DRAW)

    def __del__(self):
        gl.glDeleteBuffers(1,self.__rendererID)

    def bind(self):
        '''
        Bind this buffer to current context.
        '''
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.__rendererID)

    def unbind(self):
        '''
        Unbind this buffer from current context.
        :return:
        '''
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)