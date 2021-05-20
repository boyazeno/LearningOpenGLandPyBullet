import OpenGL.GL as gl
from enum import Enum
import ctypes
import numpy as np

def shader_sparser(filepath):
    '''
    read shader from file path
    output: str[vertex, fragment]
    '''
    shaderType = Enum('shader', ('Vertex', 'Fragment'))
    currentType = shaderType.Vertex
    source = ['', '']
    with open(filepath, 'r') as f:
        for line in f.readlines():
            if '#shader' in line:
                if 'Vertex' in line:
                    currentType = shaderType.Vertex
                else:
                    currentType = shaderType.Fragment
            else:
                source[currentType.value - 1] += line
    return source

def compile_shader(shaderType, source):
        '''
        由于两种shader的生成代码类似，因此代码复用。
        '''
        shaderId = gl.glCreateShader(shaderType)  # build the shader
        gl.glShaderSource(shaderId, source)  # specify src for the shader
        gl.glCompileShader(shaderId)

        # Error handling 确定编译没问题
        res = int()
        res = gl.glGetShaderiv(shaderId, gl.GL_COMPILE_STATUS)  # iv: int vector
        if res == gl.GL_FALSE:
            length = ctypes.c_uint()
            gl.glGetShaderiv(shaderId, gl.GL_INFO_LOG_LENGTH, length)  # 如果没成功，获取log信息，首先要知道长度
            print(length.value)
            message = gl.glGetShaderInfoLog(shaderId)
            print(f"Fail to compile {repr(shaderType)}:{message.decode()}")
            gl.glDeleteShader(shaderId)
            return 0
        return shaderId


def create_shader(vertexShader, fragmentShader):
    '''
    从string中创建vertexShader和fragmentShader。
    vertexShader：对所有顶点进行的渲染操作
    fragmentShader：对每个像素进行的渲染操作
    '''
    program = gl.glCreateProgram()  # return handle unsigned int,理解为GPU上运行的程序
    # 建立两种shader
    vs = compile_shader(gl.GL_VERTEX_SHADER, vertexShader)
    fs = compile_shader(gl.GL_FRAGMENT_SHADER, fragmentShader)

    # 连接program以及上面的shader
    gl.glAttachShader(program, vs)
    gl.glAttachShader(program, fs)
    gl.glLinkProgram(program)
    gl.glValidateProgram(program)

    # 编译完GPU程序后，可以删除shader源。类似c++编译
    gl.glDeleteShader(vs)
    gl.glDeleteShader(fs)
    return program

class Shader(object):
    def __init__(self,filepath: str):
        self.__filePath = filepath
        self.__locationCache={}
        shaderSource = shader_sparser(filepath) # read shader code from external file
        self.__rendererID = create_shader(shaderSource[0], shaderSource[1]) # create vertex&fragment shader
        gl.glUseProgram(self.__rendererID)

    def __del__(self):
        gl.glDeleteProgram(self.__rendererID)

    def bind(self):
        gl.glUseProgram(self.__rendererID)

    def unbind(self):
        gl.glUseProgram(0)

    def getUniformLocation(self, name:str):
        # Cache location in dict for frequently using
        if name in self.__locationCache.keys():
            return self.__locationCache[name]
        location = gl.glGetUniformLocation(self.__rendererID, name)
        self.__locationCache[name] = location
        return location

    def setUniform4f(self,name:str, v0:float, v1:float, v2:float, v3:float):
        gl.glUniform4f(self.getUniformLocation(name), v0,v1,v2,v3)

    def setUniform3f(self,name:str, v0:float, v1:float, v2:float):
        gl.glUniform3f(self.getUniformLocation(name), v0,v1,v2)

    def setUniform1i(self,name:str, v0:int):
        gl.glUniform1i(self.getUniformLocation(name), v0)

    def setUniform1f(self,name:str, v0:float):
        gl.glUniform1f(self.getUniformLocation(name), v0)

    def setUniformMatrix4fv(self,name:str, v0:np.ndarray):
        gl.glUniformMatrix4fv(self.getUniformLocation(name), 1, gl.GL_TRUE, v0)
