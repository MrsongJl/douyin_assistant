import sys
from PyQt6.QtCore import Qt, QPoint, QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QPainter,QIcon


class TransparentButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hide()  # 初始隐藏
        self.setText("X")
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 0, 150);
                border: none;
                color: white;
                font-size: 14px;
                width: 20px;
                height: 20px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: red;
            }
        """)


class DragButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hide()  # 初始隐藏
        self.setText("按住这拖动")
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 0, 150);
                border: none;
                color: white;
                font-size: 14px;
                width: 50px;
                height: 20px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: red;
            }
        """)
        self.dragging = False
        self.offset = QPoint()

    def mousePressEvent(self, event):
        """鼠标按下事件 - 开始拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.parent().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口"""
        if self.dragging:
            self.parent().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 结束拖动"""
        self.dragging = False
        self.parent().mouseReleaseEvent(event)


class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口属性
        self.setWindowTitle('桌面角色')
        # 设置应用图标
        app_icon = QIcon("./assets/imgs/TikTok-logo-CMYK-Stacked-black.png")  # 替换为你的图标文件路径
        self.setWindowIcon(app_icon)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建WebView
        self.webview = QWebEngineView(central_widget)
        url = QUrl("http://localhost:8888/html/webview.html")  # 将字符串转换为QUrl对象
        self.webview.setUrl(url)
        self.webview.setStyleSheet("background: transparent;")
        self.webview.page().setBackgroundColor(Qt.GlobalColor.transparent)

        # 创建关闭按钮
        self.close_button = TransparentButton(central_widget)
        self.close_button.clicked.connect(self.close)

        # 创建移动按钮
        self.drag_button = DragButton(central_widget)

        # 设置窗口大小
        self.setGeometry(100, 100, 400, 300)
        self.webview.setGeometry(0, 0, 400, 300)
        # 将窗口移动到屏幕右下角
        self.move_to_bottom_right()

        self.close_button.setGeometry(370, 10, 30, 20)
        self.drag_button.setGeometry(280, 10, 90, 20)

        # 初始化拖动状态
        self.dragging = False
        self.offset = QPoint()

    def move_to_bottom_right(self):
        # 获取屏幕的尺寸
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # 获取窗口的尺寸
        window_width = self.width()
        window_height = self.height()

        # 计算窗口右下角的位置
        x = screen_width - window_width
        y = screen_height - window_height

        # 移动窗口到屏幕右下角
        self.setGeometry(x, y, window_width, window_height)

    def enterEvent(self, event):
        """鼠标进入窗口时显示关闭按钮"""
        self.close_button.show()
        self.drag_button.show()

    def leaveEvent(self, event):
        """鼠标离开窗口时隐藏关闭按钮"""
        if not self.close_button.underMouse():
            self.close_button.hide()
        if not self.drag_button.underMouse():
            self.drag_button.hide()

    def mousePressEvent(self, event):
        """鼠标按下事件 - 开始拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口"""
        if self.dragging:
            self.move(self.mapToGlobal(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 结束拖动"""
        self.dragging = False


def main():
    app = QApplication(sys.argv)
    window = TransparentWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()