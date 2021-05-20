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
from PyQt5.QtWidgets import QLCDNumber, QSlider # 数字显示，滑动条
from PyQt5.QtWidgets import QDialog,QInputDialog,QFileDialog # 从用户处获得数据dialog
from PyQt5.QtGui import QIcon # 设定图标
from PyQt5.QtGui import QFont # 设定显示字体
from PyQt5.QtGui import QPixmap # 用于显示图片（配合QLabel）
from PyQt5.QtCore import QPoint # 二维点
from PyQt5.QtCore import Qt # 常量，不同放置ToolBar的区域 e.g. RightToolBarArea
from PyQt5.QtCore import QTimer # 计时器

class MyWindow(QMainWindow):
    def __init__(self,parent):
        super().__init__(parent)
        label1 = QLabel('This is a label',self)
        label1.move(15,10)
        self.statusBar().showMessage('Ready') # 在状态栏中显示信息
        self.setGeometry(200, 200, 500, 500)


def makeNewWindow(self,name,position):
    newWindowButton = QPushButton(name, self)
    newWindowButton.move(*position)
    newWindow = MyWindow(self)
    newWindowButton.clicked.connect(newWindow.show)

