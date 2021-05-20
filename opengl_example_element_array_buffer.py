import random
import sys
import time

import numpy as np
import OpenGL.GL as gl
from PyQt5.QtWidgets import QApplication,QMainWindow,QWidget,QOpenGLWidget
from PyQt5.QtWidgets import QToolTip, QPushButton # 提示框，按钮
from PyQt5.QtWidgets import QLCDNumber, QSlider # 数字显示，滑动条
from PyQt5.QtWidgets import QLabel # 文字标签
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog,QInputDialog,QFileDialog # 从用户处获得数据dialog
from PyQt5.QtWidgets import QGridLayout # 最基本布局类型，将界面分为网格状
from PyQt5.QtCore import Qt # 常量，不同放置ToolBar的区域 e.g. RightToolBarArea
from PyQt5.QtGui import QOpenGLWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal

import Qt5Utility # Utility widget for qt5

from openGL.VertexBuffer import VertexBuffer  # self defined vertex buffer wrapper
from openGL.IndexBuffer import IndexBuffer    # self defined index buffer wrapper
from openGL.VertexArrayLayout import VertexArrayLayout # self defined structure of vertex buffer
from openGL.VertexArray import VertexArray    # self defined vertex array object
from openGL.Shader import Shader              # self defined shader generator
from openGL.Renderer import Renderer          # self defined renderer
from openGL.Renderer import GLClearError,GLCheckError # for debugging,but python has this function
from pybullet_engine import MyWorld
                                                      # default, so don't need actually
from openGL.Texture import Texture           # self defined image texture class
import openGL.Utility as Utility



'''
API：
https://docs.gl/
中文教程：
https://learnopengl-cn.readthedocs.io/zh/latest/01%20Getting%20started/05%20Shaders/
shader 语言：
https://www.jianshu.com/p/1c23ce604e4e 
'''

def unbind(*argc):
    for i in argc:
        i.unbind()

class T():
    def __init__(self,va,vi,proj,view,model):
        self.vertexBuffer = VertexBuffer(va)
        self.vertexBufferLayout = VertexArrayLayout()
        self.vertexArray = VertexArray()
        self.indexBuffer = IndexBuffer(vi)
        self.arrayGroup = []
        self.shader = Shader('resource/shader_simple.shader')
        self.setColor(random.random(),random.random(),random.random())
        self.shader.setUniform3f("u_LightPose", *(-5000.0, -4000.0, 550.0))
        self.shader.setUniform3f("u_LightColor",*(255/255., 241/255., 224/255.))
        self.shader.setUniform1f("u_Ambient",0.4)
        self.proj = proj
        self.view = view
        self.model = model
        self.compile(self.__getMVP())

    def setColor(self, r: float=76/255.,g:float=168/255.,b:float=224/255.,a:float=1.0):
        self.shader.setUniform4f("u_Color", *(r,g,b,a))

    def __getMVP(self):
        return self.proj.dot(self.view).dot(self.model)

    def compile(self, mvp):
        self.vertexBufferLayout.push(gl.GL_FLOAT, 3)  # here draw 3D vertex position, so (float, 3)
        self.vertexBufferLayout.push(gl.GL_FLOAT, 3)  # here draw 3D vertex normal, so (float, 3)
        self.vertexArray.addBuffer(self.vertexBuffer, self.vertexBufferLayout)  # add buffer and its structure
        self.arrayGroup.append((self.vertexArray, self.indexBuffer))
        self.shader.setUniformMatrix4fv("u_MVP", mvp)
        self.shader.setUniformMatrix4fv("u_Model",self.model)

    def show(self, renderer,model=None,view=None):
        for va, vi in self.arrayGroup:
            if type(model)!=type(None):
                self.shader.bind()
                self.model = model
                self.shader.setUniformMatrix4fv("u_MVP", self.__getMVP())
                self.shader.setUniformMatrix4fv("u_Model", self.model)
            if type(view)!=type(None):
                self.shader.bind()
                self.view = view
                self.shader.setUniformMatrix4fv("u_MVP", self.__getMVP())
                self.shader.setUniformMatrix4fv("u_Model", self.model)
            renderer.draw(va, vi, self.shader, None)

class Ts():
    def __init__(self,data, index,proj,view,model):
        self.group = []
        self.color = [random.random()*0.4+0.2,random.random()*0.4+0.2,random.random()*0.3+0.6]
        for d,i in zip(data,index):
            self.group.append((T(d,i,proj,view,model)))
            self.group[-1].setColor(*self.color)

    def show(self,renderer,pose=None,view=None):
        for i in self.group:
            i.show(renderer,pose,view)

class MinimalGLWidget(QOpenGLWidget):
    def __init__(self, parent, bulletWorld=None):
        super().__init__(parent)
        self.parent=parent
        self.screenSizeX = 1280.
        self.screenSizeY = 480.
        self.setMinimumSize(self.screenSizeX, self.screenSizeY)
        self.bulletWorld = bulletWorld #MyWorld()
        #self.bulletWorld.move([0.1] * 6)
        self.bulletWorld.step()
        self.flag=False

        self.xRot, self.yRot, self.zRot = 0, 0, 0
        self.xTrans, self.yTrans, self.zTrans = 0, 0, 0
        self.objects={}
        self.collisionObjects={}
        self.chosenObject = None

    def initializeGL(self):
        time.sleep(1)
        gl.glEnable(gl.GL_DEPTH_TEST) # important for not see through the object!!
        self.proj = Utility.matPersp(-1*self.screenSizeX/2,self.screenSizeX/2,-1*self.screenSizeY/2,self.screenSizeY/2,1000.,-1000.)       # set projection mode (rescale the screen)
        view = Utility.matAffine((-np.pi/2,0.,0.),True,0.,1800.,0.)               # set camera view (translation, rotation)                         # set model pose
        self.view = view
        # build renderer for coordinating everything
        self.renderer = Renderer()

        planeVertex = np.array([[-10000., -10000., 0.,0.,0.,1.],
                                [ 10000., -10000., 0.,0.,0.,1.],
                                [-10000.,  10000., 0.,0.,0.,1.],
                                [ 10000.,  10000., 0.,0.,0.,1.]], dtype=np.float32).flatten()
        planeIndex = np.array([0,1,2,2,1,3], dtype=np.int32)
        self.plane = T(planeVertex,planeIndex,self.proj,self.view,Utility.matTranslation())
        self.plane.setColor(0.85,0.8,0.8)
        self.objects={}
        self.loadObject("/home/boya/workspace/RL_pytorch/app/resource/model/meshes/object/box.obj",scale=1000)
        self.loadObject("/home/boya/workspace/RL_pytorch/app/resource/model/meshes/object/box_big.obj", scale=1000)
        self.loadRobot()
        self.parent.initialCollsionObject()

    def loadRobot(self):
        self.objects.clear()
        self.bulletWorld.step()
        for idx, data in self.bulletWorld.shapeDataList.items():
            pose = self.bulletWorld.poses[idx]
            self.objects[idx] = Ts([d[1] for d in data],[d[2] for d in data],self.proj,self.view,pose)

    def loadObject(self, filename, position:tuple=(0.,0.,0.), orientation:tuple=(0.,0.,0.),mess:float=1.0,static:bool=False, scale:float=0.1):
        idx = self.bulletWorld.loadObject(filename,position,orientation,mess,static,scale)
        pose = self.bulletWorld.objectPoseList[idx]
        data = self.bulletWorld.objectDataList[idx]
        print(data[1])
        print(data[2])
        self.collisionObjects[idx] = T(data[1],data[2],self.proj,self.view,pose)
        return idx


    def deleteObject(self,idx):
        print(f"delete {idx}")
        self.bulletWorld.removeObject(idx)
        del self.collisionObjects[idx]

    def paintGL(self):
        self.renderer.clear()
        # 如果前面定义过vao的话，buffer都是直接连接到这个vao的，因此在每次draw时，仅仅需要重新bind要用的vao，和shader就可以了。
        # 如果对每个物体不使用单独vao的话，需要在全局定义一个vao，然后每次都重新bind array buffer\index buffer\shader。具体哪个快不好说。
        self.plane.show(self.renderer,view=self.view)
        if self.flag:
            #print(self.bulletWorld.poses[1])
            #self.bulletWorld.step()
            for idx,object in self.objects.items():
                object.show(self.renderer,self.bulletWorld.poses[idx],self.view)

            #show collsion object
            for idx,object in self.collisionObjects.items():
                object.show(self.renderer,self.bulletWorld.objectPoseList[idx],self.view)
        else:
            self.flag = True
        #GLCheckError()

    def setXRotation(self, angle):
        self.normalizeAngle(angle)

        if angle != self.xRot:
            #self.xRot = angle/20.
            newValue = (angle/-20. * np.pi / 180,0.0, 0.0)
            self.view = self.view.dot(Utility.matRotation(newValue,"xyz"))
            #self.view[0:3,0:3] = Utility.matRotation(newValue, "xyz")[0:3,0:3]
            self.update()

    def setYRotation(self, angle):
        self.normalizeAngle(angle)

        if angle != self.yRot:
            #self.yRot = angle/20.
            newValue = (0.0, angle/-20. * np.pi / 180,0.0)
            self.view = self.view.dot(Utility.matRotation(newValue,"xyz"))
            #self.view[0:3,0:3] = Utility.matRotation(newValue, "xyz")[0:3,0:3]
            self.update()

    def setZRotation(self, angle):
        self.normalizeAngle(angle)

        if angle != self.zRot:
            #self.zRot = angle/20.
            newValue = (0.0, 0.0, angle / -20. * np.pi / 180)
            self.view = self.view.dot(Utility.matRotation(newValue,"xyz"))
            #self.view[0:3,0:3] = Utility.matRotation(newValue,"xyz")[0:3,0:3]
            self.update()

    def setXTranslation(self, distance):
        if distance != self.xTrans:
            #self.xTrans = distance
            self.view = Utility.matTranslation(-1*distance,0.,0.).dot(self.view)
            self.update()

    def setYTranslation(self, distance):
        if distance != self.yTrans:
            #self.yTrans = distance
            self.view = Utility.matTranslation(0.,-1*distance,0.).dot(self.view)
            self.update()

    def setZTranslation(self, distance):
        if distance != self.zTrans:
            #self.zTrans = distance
            self.view = Utility.matTranslation(0.,0.,-1*distance).dot(self.view)
            self.update()

    def wheelEvent(self, event):
        self.lastPos = event.pos()
        deltaAngle = event.angleDelta().y()
        self.setZTranslation(deltaAngle/2.0)
        #print(deltaAngle/2.0)
        self.update()

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.setXRotation(-1*dy)
            self.setYRotation(-1*dx)
        elif event.buttons() & Qt.RightButton:
            self.setXTranslation( - 5*dx)
            self.setYTranslation( 5*dy)
        elif event.buttons() & Qt.MiddleButton:
            self.setZRotation(dy)
            self.setYRotation(-1*dx)

        self.lastPos = event.pos()

    def normalizeAngle(self, angle):
        while (angle < 0):
            angle += 360 * 16

        while (angle > 360 * 16):
            angle -= 360 * 16


class MySlider(QWidget):
    '''
    网格状按钮分布
    '''
    def __init__(self, *argc):
        super().__init__(*argc)
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.a = 0.0
        self.b = 0.0
        self.c = 0.0
        grid = QGridLayout()
        self.setLayout(grid)
        names = ["x","y","z","a","b","c"]
        positions = [i for i in range(6)]
        for n, p in zip(names, positions):
            sld = QSlider(Qt.Horizontal, self)
            if n in ["a","b","c"]:
                sld.setMaximum(314000.)
                sld.setMinimum(-314000.)
            else:
                sld.setMaximum(100.)
                sld.setMinimum(-100.)
            sld.setTickInterval(0.05)
            sld.setSingleStep(0.05)
            l = QLabel(self)
            l.setText(n+":")
            sld.valueChanged[int].connect(self.changeVal(n))
            grid.addWidget(sld, p, 1)
            grid.addWidget(l, p, 0)
        self.setFixedSize(200, 200)

    def changeVal(self,attri):
        def myFunc(val):
            self.__dict__[attri] = val/100000.
            print(self.__dict__[attri])
        return myFunc


class Example(QMainWindow):
    def __init__(self,bulletWorld):
        super().__init__()
        self.bulletWorld = bulletWorld
        self.initUI()

    def initUI(self):
        self.screenSizeX = 1280
        self.screenSizeY = 480
        self.setGeometry(0,0,self.screenSizeX,self.screenSizeY+300)

        self.glWidget = MinimalGLWidget(self, bulletWorld=self.bulletWorld)

        self.btn = QPushButton('Start', self)
        self.btn.setToolTip('This controls the <b>status of GUI</b>')
        self.btn.resize(self.btn.sizeHint())
        self.btn.clicked.connect(self.callbackButton)
        self.btn.move(100, self.screenSizeY+50)

        self.btn1 = QPushButton('Reverse', self)
        self.btn1.setToolTip('This controls the <b>direction of rotation</b>')
        self.btn1.resize(self.btn1.sizeHint())
        self.btn1.clicked.connect(self.callbackButton1)
        self.btn1.move(100, self.screenSizeY + 90)
        self.flagButton1 = False

        self.sld = QSlider(Qt.Horizontal, self)
        # sld.setFocusPolicy(Qt.NoFocus) # 是否允许使用tab键访问
        self.sld.setGeometry(100, self.screenSizeY+20, 100, 20)
        self.sld.setMaximum(200)
        self.sld.setMinimum(1)
        self.sld.setTickPosition(QSlider.TicksBelow)
        self.sld.setTickInterval(20)
        self.sld.setSingleStep(20)  # 只在使用tab选择到slider后，使用键盘方左右按键才有用
        self.sldl = QLabel(self)
        self.sldl.move(240, self.screenSizeY+10)
        l=QLabel(self)
        l.move(0, self.screenSizeY+10)
        l.setText("Speed:")
        self.sld.valueChanged[int].connect(self.callbackSlider)
        self.speed = 10


        lbl = QLabel(self)
        lbl.move(250, self.screenSizeY + 90)
        def callbackChooseButton():
            if self.timer.isActive():
                self.callbackButton()
            # 交互窗口，Dialog
            filename = QFileDialog.getOpenFileName(self, 'Open file')  # 获得文件名，显示文件名
            if filename[0]:
                lbl.setText("Opened: "+filename[0])
                lbl.adjustSize()
                self.timer1.stop()
                self.bulletWorld.init()#(filename[0])
                self.glWidget.loadRobot()
                self.timer1.start(20)
        imgButton = QPushButton("Choose Robots", self)
        imgButton.move(180, self.screenSizeY + 90)
        imgButton.clicked.connect(callbackChooseButton)
        imgButton.adjustSize()

        ############
        self.bombobox = QComboBox(self)
        self.bombobox.move(350, self.screenSizeY + 130)
        self.bombolabel = QLabel('default', self)
        self.bombolabel.move(380, self.screenSizeY + 130)
        def func7(text):
            self.bulletWorld.chosenObject = int(text)
        self.bombobox.activated[str].connect(func7)

        self.sliders = MySlider(self)
        self.sliders.move(450,self.screenSizeY + 120)


        self.btn2 = QPushButton('Load object', self)
        self.btn2.setToolTip('Load object into scene')
        self.btn2.resize(self.btn2.sizeHint())

        self.btn2.clicked.connect(self.callbackLoadObjectButton)
        self.btn2.move(350, self.screenSizeY + 160)

        def callbackDeleteObjectButton():
            print(f"Remove {self.bombobox.currentText()}")
            self.glWidget.deleteObject(int(self.bombobox.currentText()))
            self.bombobox.removeItem(self.bombobox.currentIndex())

        self.btn3 = QPushButton('Delete object', self)
        self.btn3.setToolTip('Delete object from scene')
        self.btn3.resize(self.btn3.sizeHint())

        self.btn3.clicked.connect(callbackDeleteObjectButton)
        self.btn3.move(350, self.screenSizeY + 190)

        def callbackMovePosition():
            if self.timer.isActive():
                self.callbackButton()
            idx = int(self.bombobox.currentText())
            self.bulletWorld.setObjectPose(idx,(self.sliders.x,self.sliders.y,self.sliders.z),(self.sliders.a,self.sliders.b,self.sliders.c))
            self.glWidget.update()

        self.btn4 = QPushButton('Move object', self)
        self.btn4.setToolTip('Move object to this position')
        self.btn4.resize(self.btn4.sizeHint())

        self.btn4.clicked.connect(callbackMovePosition)
        self.btn4.move(350, self.screenSizeY + 220)

        ############
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.bulletWorld.step)
        #self.timer.start(self.speed)
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.glWidget.update)
        self.timer1.start(20)
        self.show()

    def initialCollsionObject(self):
        for idx,data in self.bulletWorld.objectDataList.items():
            self.bombobox.addItem(f"{idx}")

    def callbackLoadObjectButton(self):
        if self.timer.isActive():
            self.callbackButton()
        self.timer1.stop()
        # 交互窗口，Dialog
        filename = QFileDialog.getOpenFileName(self, 'Open file')  # 获得文件名，显示文件名
        if filename[0]:
            idx = self.glWidget.loadObject(filename[0], scale=100)
            self.bombobox.addItem(f"{idx}")
        self.timer1.start(20)

    def callbackButton1(self):
        if self.flagButton1:
            self.bulletWorld.move([ 0., 0.,0.5,  0., 0., 0.])
        else:
            self.bulletWorld.move([ 0., 0.,-1*0.5, 0., 0., 0.])
        self.flagButton1 = not self.flagButton1


    def callbackButton(self):
        if self.timer.isActive():
            print("Timer is active, try to stop it")
            self.timer.stop()
            print(f"Timer is now {self.timer.isActive()}")
            self.btn.setText("Resume")
        else:
            self.timer.start(self.speed)
            self.btn.setText("Stop")

    def callbackSlider(self, value):
            self.sldl.setText(str(value))
            self.speed = value
            self.timer.stop()
            self.btn.setText("Resume")

        
def main():
    bulletWorld = MyWorld(1000)
    bulletWorld.move([0.,0.3,0.,0.3,0.,0.])
    app = QApplication(sys.argv)
    ex = Example(bulletWorld)
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