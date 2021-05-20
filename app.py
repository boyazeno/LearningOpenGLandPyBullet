import sys
from PyQt5.QtWidgets import QApplication, QWidget # 一切的父类
from PyQt5.QtWidgets import QToolTip, QPushButton # 提示框，按钮
from PyQt5.QtWidgets import QCheckBox, QSlider, QProgressBar, QComboBox, QCalendarWidget # 各种小组件
from PyQt5.QtWidgets import QMessageBox # 跳出提示框
from PyQt5.QtWidgets import QDesktopWidget # 提供用户桌面desktop的信息，如屏幕大小等
from PyQt5.QtWidgets import QMainWindow # 辅助建立状态栏statusBar
from PyQt5.QtWidgets import QAction, qApp # QAction为menubar,toolbar或者定制快捷键的action的类。 qApp 
from PyQt5.QtWidgets import QMenu # 用于目录，可以加入到self.menubar().addMenu()中形成子目录
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QTextEdit,QLineEdit #文本编辑模块
from PyQt5.QtWidgets import QLabel # 文字标签
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QGridLayout # 最基本布局类型，将界面分为网格状
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLCDNumber, QSlider # 数字显示，滑动条
from PyQt5.QtWidgets import QDialog,QInputDialog,QFileDialog # 从用户处获得数据dialog
from PyQt5.QtGui import QIcon # 设定图标
from PyQt5.QtGui import QFont # 设定显示字体
from PyQt5.QtGui import QPixmap # 用于显示图片（配合QLabel）
from PyQt5.QtCore import QPoint # 二维点
from PyQt5.QtCore import Qt # 常量，不同放置ToolBar的区域 e.g. RightToolBarArea
from PyQt5.QtCore import QTimer # 计时器


class MyToolBar(QToolBar):
    '''
    定制了一个工具栏类，唯一区别为在此工具栏上右键会出现自己的contextMenu。
    并且实现了动态删除action的功能。
    '''
    def __init__(self,*argc):
        super().__init__(*argc)
    
    def contextMenuEvent(self,event):
        # 添加右键弹出窗口context menu：
        cmenu = QMenu('Edit', self)
        quitAct = cmenu.addAction("Quit")
        deleteAct = cmenu.addAction("Delete")
        # 调整右侧单击栏出现位置
        action = cmenu.exec_(QPoint(event.globalX(),event.globalY())) # QPoint(event.globalX(),event.globalY()) 等价于self.mapToGlobal(event.pos())
        if action==quitAct:
            qApp.quit()
        elif action==deleteAct:
            if len(self.actions())==0:
                reply = QMessageBox.information(self, 'Message',"No more action", QMessageBox.Ok|QMessageBox.Cancel , QMessageBox.Ok)
            else:
                self.removeAction(self.actions()[-1])
    
class MyWidget1(QWidget):
    '''
    条状按钮分布
    '''
    def __init__(self,*argc,**argv):
        super().__init__(*argc)
        
        getButton = QPushButton("Get")
        deleteButton = QPushButton("Delete")
        
        # bind with slot
        getButton.clicked.connect(argv["callback"])

        hbox = QHBoxLayout()
        hbox.addStretch(0)
        hbox.addWidget(getButton)
        hbox.addWidget(deleteButton)

        vbox = QVBoxLayout()
        vbox.addStretch(0)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        self.setGeometry(200, 200, 200, 200)
        
class MyWidget2(QWidget):
    '''
    网格状按钮分布
    '''
    def __init__(self,*argc):
        super().__init__(*argc)

        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        grid = QGridLayout()
        self.setLayout(grid)
        
        names=['button'+str(i+1) for i in range(9)]
        positions=[(i,j) for i in range(3) for j in range(3)]
        
        for n,p in zip(names,positions):
            if n == "button5":
                continue
            button = QPushButton(n)
            grid.addWidget(button,*p)
        self.setFixedSize(200, 200)
        

class MyWindow(QMainWindow):
    def __init__(self,parent):
        super().__init__(parent)
        label1 = QLabel('This is a label',self)
        label1.move(15,10)
        self.statusBar().showMessage('Ready') # 在状态栏中显示信息
        self.setGeometry(200, 200, 500, 500)
        
class Example(QMainWindow): # 继承于QMainWindow时，可以使用状态栏等功能。

    def __init__(self):
        super().__init__()

        self.initUI()
        

    def initUI(self):
        # no this font on linux
        #QToolTip.setFont(QFont('SansSerif', 10))
        # 设定状态栏
        self.statusBar().showMessage('Ready') # 在状态栏中显示信息。
        # 设定提示信息
        self.setToolTip('This is a <b>Demo</b>')
        
        # 加入标签
        label1 = QLabel('This is a label',self)
        label1.move(15,10)
        
        # 加入按钮
        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())
        btn.clicked.connect(QApplication.instance().quit)
        btn.move(50, 150)
        
        # checkBox
        cb = QCheckBox('Show title', self)
        cb.move(10, 250)
        cb.toggle()
        def func3(*argcs):
            QMessageBox.information(self, 'Message',"Get {} .".format(repr(argcs)), QMessageBox.Ok|QMessageBox.Cancel , QMessageBox.Ok)
        cb.stateChanged.connect(func3)
        
        # toggle button
        redb = QPushButton('Red', self)
        redb.setCheckable(True)
        redb.move(10, 290)
        def func2(*argcs):
            QMessageBox.information(self, 'Message',"Get {} .".format(repr(argcs)), QMessageBox.Ok|QMessageBox.Cancel , QMessageBox.Ok)
        redb.clicked.connect(func2)
        
        # 滑动条
        sld = QSlider(Qt.Horizontal, self)
        #sld.setFocusPolicy(Qt.NoFocus) # 是否允许使用tab键访问
        sld.setGeometry(10, 340, 200, 30)
        sld.setMaximum(200)
        sld.setMinimum(0)
        sld.setTickPosition(QSlider.TicksBelow)
        sld.setTickInterval(50)
        sld.setSingleStep(50) # 只在使用tab选择到slider后，使用键盘方左右按键才有用
        sldl=QLabel(self)
        sldl.move(10,310)
        def func4(value):
            sldl.setText(str(value))
        sld.valueChanged[int].connect(func4)
        
        # 进度条
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(10, 370, 200, 25)
        self.btn = QPushButton('Start', self)
        self.btn.move(10, 400)
        # 定时器到时callback
        def func5(*argc):
            self.timerStep +=1
            self.pbar.setValue(self.timerStep)
            if self.timerStep ==100:
                self.timer.stop()
                self.btn.setText('Finished')
                self.timerStep=0
        self.timer = QTimer(self)
        self.timer.timeout.connect(func5)
        self.timerStep = 0
        # 按钮单击callback
        def func6():
            if self.timer.isActive():
                self.timer.stop()
                self.btn.setText('Start')
            else:
                self.timer.start(100)
                self.btn.setText('Stop')
        self.btn.clicked.connect(func6)
        
        # 添加一个选项栏：
        bombobox = QComboBox(self)
        bombobox.addItem('item1')
        bombobox.addItem('item2')
        bombobox.addItem('item3')
        bombobox.move(200,700)
        bombolabel = QLabel('default',self)
        bombolabel.move(100,700)
        def func7(text):
            bombolabel.setText(text)
            bombolabel.adjustSize()
        bombobox.activated[str].connect(func7)
        
        # 设定目录栏
        # 1。定义一个action
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application') #鼠标指向此按钮时会在状态栏显示此信息
        exitAct.triggered.connect(qApp.quit)
        
        testAct = QAction(QIcon('exit.png'), '&Test', self)  # 符号&代表开头加下划线
        testAct.setShortcut('Ctrl+T') # 快捷键
        testAct.setStatusTip('Test') # 鼠标指向此按钮时会在状态栏显示此信息
        testAct.setCheckable(True) # 是否可勾选，会返回两个状态：True,False见 https://doc.qt.io/qt-5/qaction.html#checkable-prop
        testAct.triggered.connect(self.callback1) #回调函数可以为任意函数
        
        viewStatAct = QAction('View statusbar', self, checkable=True)
        viewStatAct.setStatusTip('View statusbar')
        viewStatAct.setChecked(True)
        viewStatAct.triggered.connect(self.callback2)
        
        # 2。定义menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        editMenu = menubar.addMenu('Edit')
        viewMenu = menubar.addMenu('View')
        fileMenu.addAction(exitAct)
        editMenu.addAction(testAct)
        viewMenu.addAction(viewStatAct)

        
        # 3。添加子menu
        impMenu = QMenu('Import', self)
        impAct = QAction('Import mail', self)
        impMenu.addAction(impAct)
        editMenu.addMenu(impMenu) #可以层层嵌套
        
        # 添加toolbar，即常用选项栏
        self.toolbar = MyToolBar('Exit',self)
        self.toolbar.addAction(exitAct)
        self.toolbar.addAction(viewStatAct)
        self.addToolBar(Qt.RightToolBarArea, self.toolbar) # 使用先建立一个ToolBar，再用addToolBar的形式能够设置初始位置。
        
        # 设定文本编辑模块为中心模块
        self.textEdit = QTextEdit(self)
        self.textEdit.setGeometry(50, 50, 200, 200)
        self.textShow = QTextEdit(self)
        self.textShow.setGeometry(300, 50, 200, 200)
        self.textEdit.textChanged.connect(self.callback3)
        
        # 添加图片： 
        pixmap = QPixmap()
        lbl = QLabel(self)
        lbl.move(50,450)
        def func7():
            # 交互窗口，Dialog
            filename = QFileDialog.getOpenFileName(self,'Open file') #获得文件名，显示文件名
            if filename[0]:
                pixmap.load(filename[0])
                lbl.setPixmap(pixmap)
                lbl.adjustSize()
        imgButton = QPushButton("Open",self)
        imgButton.move(50,450)
        imgButton.clicked.connect(func7)
        
        # 跳出新窗口
        newWindowButton = QPushButton("New",self)
        newWindowButton.move(400,400)
        newWindow = MyWindow(self)
        newWindowButton.clicked.connect(newWindow.show)
        
        # 数字显示以及滑动条
        def func(value):
            l.setText(str(value))
            lcd.display(value)
        lcd = QLCDNumber(self)
        sld = QSlider(Qt.Horizontal, self)
        lcd.move(300,300)
        sld.valueChanged.connect(func)
        l=QLabel(self)
        l.move(260,300)
        sld.move(300,320)
        #self.setCentralWidget(textEdit) # 使用默认GUI布局
        
        # 添加自定义的带有横、纵布局的按钮
        def func1():
            # 交互窗口，Dialog
            #text,ok=QInputDialog.getText(self,'Input Dialog','Enter your name:') #获得参数
            # l.setText(text) # 显示参数
            filename = QFileDialog.getOpenFileName(self,'Open file') #获得文件名，显示文件名
            if filename[0]:
                self.textEdit.setText(''.join(filename))
                with open(filename[0],'r') as f:
                    self.textShow.setText(f.read())
                
        mywidget1 = MyWidget1(self,callback=func1)
        mywidget1.move(50,100)
           
        # 添加自定义的网格按钮
        mywidget2 = MyWidget2(self)
        mywidget2.move(200,400)


        # slide down list
        myComboBox = QComboBox(self)
        myComboBox.addItem("abc")
        myComboBox.addItem("abc")
        myComboBox.addItem("abc")
        
        # 设定应用窗口大小位置
        self.setGeometry(300, 300, 300, 220)
        self.center()
        self.setWindowTitle('Icon')
        self.setWindowIcon(QIcon('icon.png'))

        self.show()
    
    def timerEvent(self, e):
        if self.step >= 100:
            self.timer.stop()
            self.btn.setText('Finished')
            return
        self.step = self.step + 1
        self.pbar.setValue(self.step)
    
    def callback1(self,*argc):
        reply = QMessageBox.information(self, 'Message',"Get {} of argc.".format(repr(argc)), QMessageBox.Ok|QMessageBox.Cancel , QMessageBox.Ok)
    
    def callback2(self, state):
        #toggleMenu, show or not show menu
        if state:
            self.statusBar().show()
        else:
            self.statusBar().hide()
            
    # 所有signal都可以用.connect()连接函数       
    # 一个markdown转换的小例子        
    def callback3(self,*argc):
        t = self.textEdit.toPlainText()
        self.textShow.setMarkdown(t)
    
    # override
    def contextMenuEvent(self,event):
        # 添加右键弹出窗口context menu：
        cmenu = QMenu('Import', self)
        quitAct = cmenu.addAction("Quit")
        # 调整右侧单击栏出现位置
        action = cmenu.exec_(QPoint(event.globalX(),event.globalY())) # QPoint(event.globalX(),event.globalY()) 等价于self.mapToGlobal(event.pos())
        if action==quitAct:
            qApp.quit()
            
    # override, click the close button on the upper right will trigger this, but QApplication.instance().quit不会
    def closeEvent(self,event):
        # see https://doc.qt.io/qt-5/qmessagebox.html [hashtag: StandardButton, Static Public Members]
        reply = QMessageBox.information(self, 'Message',"Are you sure to quit?", QMessageBox.Ok|QMessageBox.Cancel , QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()
            
    # used for centering the window     
    def center(self):
        fake_window = self.frameGeometry() # 获得当前应用程序窗口的几何形状（新建了一个图形，具有和当前应用程序窗口相同的形状类型，尺寸）
        cp = QDesktopWidget().availableGeometry().center() # 获得当前桌面的几何中心
        fake_window.moveCenter(cp) # 移动几何形状到当前桌面的中心，尺寸保持不变
        self.move(fake_window.topLeft())  # 移动应用程序窗口左上点到几何形状的左上点位置（即将当前窗口和fake_window相重合，即centering）

        
def main():

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()
