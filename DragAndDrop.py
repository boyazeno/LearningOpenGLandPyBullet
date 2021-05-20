import sys

from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QPushButton, QWidget, QApplication, QMainWindow

# 右键拖拽按钮，进行相加操作

class Button(QPushButton):

    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.buttonValue = 1
        self.setAcceptDrops(True)

    def mouseMoveEvent(self, e):
        # 当鼠标进行拖动动作时，要判断什么时候进行draganddrop动作，比如计算移动的manhatton 距离，或者按下的鼠标
        if e.buttons() != Qt.RightButton:
            return
        # DragandDrop使用MimeData进行双方的数据交流，因此所有需要交换的数据都要存在QMimeData中。
        mimeData = QMimeData()
        mimeData.setText(str(self.buttonValue))
        # 定义Drag操作
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        # 没啥意义
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        # 在决定要执行这个DragandDrop动作的时候exec。后面的Qt.MoveAction表明了发送的信息该谁来删除，共有三种。返回操作后的MimeData。
        dropAction = drag.exec_(Qt.MoveAction)
    
    # 鼠标按下、拖拽鼠标是可区分的。
    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.button() == Qt.LeftButton:
            print('press')
            
    # 在激活drag后可以用来判断这个drag符不符合要求，即提供的信息够不够操作的，够了就accept。
    # https://doc.qt.io/qt-5/qmimedata.html#hasFormat
    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat("text/plain"):
            e.accept() 
            # A widget must accept this event in order to receive 
            # the drag move events that are sent while the drag and 
            # drop action is in progress. The drag enter event is 
            # always immediately followed by a drag move event.
        else:
            ignore()
            
    # 使用Mimedata进行信息交流
    def dropEvent(self, e):
        self.buttonValue += int(e.mimeData().text())
        self.setText(str(self.buttonValue))
        e.accept()

class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.setAcceptDrops(True)

        self.button1 = Button('Button', self)
        self.button1.move(100, 65)
        self.button2 = Button('Button', self)
        self.button2.move(200, 65)
        
        self.setWindowTitle('Click or Move')
        self.setGeometry(300, 300, 550, 450)
        self.show()



def main():
    
    app = QApplication(sys.argv)
    ex = Example()
    app.exec_()


if __name__ == '__main__':
    main()