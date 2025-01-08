# 登录页面
import requests

from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QMessageBox, QMainWindow,
                             QGraphicsDropShadowEffect, QHBoxLayout, QToolButton)
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QFont, QColor, QIcon, QPalette, QGradient
from PyQt6.QtGui import QIcon, QColor, QPixmap
# 全局配置
from units.config import *
from units.AppManager import *
# 日志
from units.logger_config import setup_logger

logger = setup_logger()

from ui.MainWindow import *


# 样式
class StyledLineEdit(QLineEdit):
    def __init__(self, placeholder):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
              QLineEdit {
                  border: 1px solid #e1e1e1;
                  border-radius: 8px;
                  padding: 8px;
                  font-size: 14px;
                  background-color: #f9f9f9;
              }
              QLineEdit:focus {
                  border-color: #3498db;
              }
          """)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
                   QWidget {
                       background-color: #f0f2f5;
                   }
               """)
        self.initUI()

    def initUI(self):
        # 设置窗口为无边框
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle('TikTok 弹幕助手-Login')

        # 设置应用图标
        app_icon = QIcon("./assets/imgs/TikTok-logo-CMYK-Stacked-black.png")  # 替换为你的图标文件路径
        self.setWindowIcon(app_icon)
        # self.setGeometry(100, 100, 400, 500)
        self.setFixedSize(400, 500)

        # 添加鼠标拖动相关的属性 方便拖动页面
        self._dragging = False
        self._drag_position = QPoint()

        # 创建主布局
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建自定义标题栏
        title_bar = QWidget(self)
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(10, 5, 10, 5)

        # 添加关闭按钮
        # 添加关闭按钮到右上角
        close_button = QToolButton()
        close_button.setIcon(QIcon('assets/imgs/close.png'))
        close_button.setIconSize(QSize(20, 20))
        close_button.setStyleSheet("""
            QToolButton {
                border: none;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: #ff4d4f;
                color: white;
            }
        """)
        close_button.clicked.connect(self.close)

        title_bar_layout.addStretch(0)
        title_bar_layout.addWidget(close_button)
        title_bar.setLayout(title_bar_layout)

        # Logo容器
        logo_container = QWidget()
        logo_layout = QVBoxLayout()

        # 添加Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("./assets/imgs/TikTok-logo-CMYK-Stacked-black.png").scaled(
            100, 100,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_layout.addWidget(logo_label)
        logo_container.setLayout(logo_layout)

        # 登录容器
        login_container = QWidget()
        login_container.setStyleSheet("""
                   QWidget {
                       background-color: white;
                       border-radius: 15px;
                   }
               """)

        # 阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        login_container.setGraphicsEffect(shadow)

        # 登录布局
        login_layout = QVBoxLayout()
        login_layout.setSpacing(20)
        login_layout.setContentsMargins(30, 30, 30, 30)

        # 标题
        # title_label = QLabel('登录')
        # title_label.setStyleSheet("""
        #            color: black;
        #            font-size: 24px;
        #            font-weight: bold;
        #        """)
        # title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 用户名输入
        self.username_input = StyledLineEdit('用户名')
        self.username_input.setText("admin")

        # 密码输入
        self.password_input = StyledLineEdit('密码')
        self.password_input.setText("123")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # 登录按钮
        self.login_button = QPushButton('登 录')
        self.login_button.setStyleSheet("""
                   QPushButton {
                       background-color: #3498db;
                       color: white;
                       border: none;
                       border-radius: 10px;
                       padding: 10px;
                       font-size: 16px;
                   }
                   QPushButton:hover {
                       background-color: #2980b9;
                   }
                   QPushButton:pressed {
                       background-color: #21618c;
                   }
               """)
        self.login_button.clicked.connect(self.login)

        # 组装登录布局
        # login_layout.addWidget(title_label)
        login_layout.addWidget(self.username_input)
        login_layout.addWidget(self.password_input)
        login_layout.addWidget(self.login_button)
        login_container.setLayout(login_layout)

        # 组装主布局
        layout.addWidget(title_bar)
        layout.addWidget(logo_container)
        layout.addWidget(login_container)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        # 鼠标按下事件
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            # 记录鼠标相对窗口左上角的位置
            self._drag_position = event.pos()

    def mouseMoveEvent(self, event):
        # 鼠标移动事件
        if self._dragging:
            # 计算窗口新的位置
            self.move(self.mapToGlobal(event.pos() - self._drag_position))

    def mouseReleaseEvent(self, event):
        # 鼠标释放事件
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            # 实际应用中，替换为你的登录接口地址

            correct_username = "admin"
            correct_password = "123"

            if username == correct_username and password == correct_password:
                # 登录成功，打开主窗口
                self.main_window = MainWindow()
                self.main_window.show()
                self.close()
            else:
                logger.info("登录失败")
                QMessageBox.critical(self, '登录失败', '用户名或密码错误')

        except Exception as e:
            logger.info(f"{str(e)}")
            QMessageBox.critical(self, '错误', str(e))
