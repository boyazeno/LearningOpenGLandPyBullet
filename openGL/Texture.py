import OpenGL.GL as gl
import ctypes
from PIL import Image
import numpy as np

class Texture(object):
    def __init__(self, filepath):
        self.__filePath = filepath
        self.__rendererID = None
        self.__height = None
        self.__width = None
        self.__image = None
        self.__imageBuffer = None
        self.__imageType = None

        # load image:
        self.__image = Image.open(filepath,'r')
        flippedImg = self.__image.transpose(Image.FLIP_TOP_BOTTOM)
        self.__imageBuffer = flippedImg.tobytes() #np.array(list(flippedImg.getdata()), np.uint8)
        self.__width,self.__height = flippedImg.size
        self.__imageType = gl.GL_RGB if len(str(self.__image.mode))==3 else gl.GL_RGBA

        # build texture buffer
        self.__rendererID = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.__rendererID)

        # set parameters
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE) # x direction clip
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE) # y direction clip

        # build image buffer and fills the texture buffer
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, self.__width, self.__height, 0, self.__imageType,
                        gl.GL_UNSIGNED_BYTE, ctypes.c_char_p(self.__imageBuffer)) #self.__imageBuffer
        gl.glBindTexture(gl.GL_TEXTURE_2D,0)

    def __del__(self):
        gl.glDeleteTextures(1,self.__rendererID)

    def bind(self,slot=0):
        gl.glActiveTexture(gl.GL_TEXTURE0+slot) # image will be loaded in activated slot in GPU (0-31)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.__rendererID)

    def unbind(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
