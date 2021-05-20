import ctypes
import logging
import sys
from enum import Enum

import numpy as np
import OpenGL.GL as gl
from PyQt5.QtWidgets import QApplication,QMainWindow,QWidget,QOpenGLWidget
from PyQt5.QtGui import QOpenGLWindow

'''
API：
https://docs.gl/
中文教程：
https://learnopengl-cn.readthedocs.io/zh/latest/01%20Getting%20started/05%20Shaders/
shader 语言：
https://www.jianshu.com/p/1c23ce604e4e 
'''

class MinimalGLWidget(QOpenGLWidget):
    def __init__(self, *argc):
        super().__init__(*argc)
        self.setMinimumSize(640, 480)
    
    def _shaderSparser(self,filepath):
        '''
        read shader from file path
        output: str[vertex, fragment]
        '''
        shaderType = Enum('shader',('Vertex','Fragment'))
        currentType = shaderType.Vertex
        source = ['','']
        with open(filepath,'r') as f:
            for line in f.readlines(): 
                if '#shader' in line:
                    if 'Vertex' in  line:
                        currentType = shaderType.Vertex
                    else:
                        currentType = shaderType.Fragment
                else:
                    source[currentType.value-1] += line
        return source
                
    def _compileShader(self, shaderType, source):
        '''
        由于两种shader的生成代码类似，因此代码复用。
        '''
        shaderId = gl.glCreateShader(shaderType) # build the shader
        gl.glShaderSource(shaderId,source) # specify src for the shader
        gl.glCompileShader(shaderId)
        
        # Error handling 确定编译没问题
        res = int()
        res=gl.glGetShaderiv(shaderId,gl.GL_COMPILE_STATUS) # iv: int vector
        if res == gl.GL_FALSE:
            length = ctypes.c_uint()
            gl.glGetShaderiv(shaderId,gl.GL_INFO_LOG_LENGTH,length) #如果没成功，获取log信息，首先要知道长度
            print(length.value)
            message = gl.glGetShaderInfoLog(shaderId)
            print(f"Fail to compile {repr(shaderType)}:{message.decode()}")
            gl.glDeleteShader(shaderId)
            return 0
        return shaderId
        
    def _createShader(self,vertexShader, fragmentShader):
        '''
        从string中创建vertexShader和fragmentShader。 
        vertexShader：对所有顶点进行的渲染操作
        fragmentShader：对每个像素进行的渲染操作
        '''
        program = gl.glCreateProgram() # return handle unsigned int,理解为GPU上运行的程序
        #建立两种shader
        vs = self._compileShader(gl.GL_VERTEX_SHADER,vertexShader)
        fs = self._compileShader(gl.GL_FRAGMENT_SHADER,fragmentShader)
        
        #连接program以及上面的shader
        gl.glAttachShader(program,vs)
        gl.glAttachShader(program,fs)
        gl.glLinkProgram(program)
        gl.glValidateProgram(program)
        
        # 编译完GPU程序后，可以删除shader源。类似c++编译
        gl.glDeleteShader(vs)
        gl.glDeleteShader(fs)
        return program
    
    def initializeGL(self):
        # Build data
        data = [-0.5, -0.5,
                 0.0,  0.5,
                 0.5, -0.5]
        data = np.array(data, dtype=np.float32).reshape(3,2)
        # Request a buffer slot from GPU
        buffer = gl.glGenBuffers(1)
        # Make this buffer the default one
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
        # Upload CPU data to GPU buffer
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_STATIC_DRAW)
        
        gl.glEnableVertexAttribArray(0)
        stride = data.strides[0]
        offset = ctypes.c_void_p(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, stride, offset)
        
        # 加入shader
        shaderSource = self._shaderSparser('resource/shader.shader')
        shader = self._createShader(shaderSource[0], shaderSource[1])
        gl.glUseProgram(shader)
        
    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT) 
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setGeometry(0,0,640,480)
        self.glWidget = MinimalGLWidget(self)
        self.show()
        
        
def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
    
    
    
    
    
    # in vec4 position 表示这是输入，layout(location = 0) 使用了特殊关键词表明输入的位置为attrib 0。 
    # out vec4 blabla 表示这是输出
    vertex_code = '''
    #version 330 core
    layout(location = 0) in vec4 position;
    void main()
    {
        gl_Position  = position;
    }
    '''
    # 也可以用attribute表明位置，更方便代码中使用glGetAttribLocation选择位置
    '''
    attribute vec2 position;
    void main()
    {
      gl_Position = vec4(position, 0.0, 1.0);
    }
    '''

    fragment_code = '''
    #version 330 core
    out vec4 color;
    void main()
    {
      color = vec4(1.0, 0.0, 0.0, 1.0);
    }
    '''