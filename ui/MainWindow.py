# 主控台台
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QMessageBox, QMainWindow,
                             QGraphicsDropShadowEffect, QHBoxLayout, QToolButton, QMenu, QStackedWidget)
from PyQt6.QtCore import Qt, QSize,QPoint
from PyQt6.QtGui import QPixmap, QFont, QAction, QColor, QPainter, QPainterPath, QIcon
from PyQt6.QtCore import pyqtSignal

# 日志
from units.logger_config import setup_logger
logger = setup_logger()

from ui.HomePage import *
from ui.StartPage import *

from ui.AssistantPage import *


class MainWindow(QMainWindow):
    # 设置一个信号 切换页面使用
    switch_to_start_page_signal = pyqtSignal(object, object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("抖音直播-互动虚拟人")
        self.setFixedSize(1200, 600)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        # 设置应用图标
        app_icon = QIcon("assets/imgs/TikTok-logo-CMYK-Stacked-black.png")  # 替换为你的图标文件路径
        self.setWindowIcon(app_icon)
        # 设置左下角状态栏
        self.statusBar()
        self.statusBar().showMessage('登录成功！')

        # 添加鼠标拖动相关的属性
        self._dragging = False
        self._drag_position = QPoint()

        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 创建主布局
        main_layout = QHBoxLayout(main_widget)

        # 创建左侧菜单部件和布局
        left_widget = QWidget()
        left_widget.setFixedWidth(200)
        left_widget.setStyleSheet("background-color: #4D557A;")
        left_layout = QVBoxLayout(left_widget)

        # Add Logo
        # Create a widget to hold the layout
        logo_widget = QWidget()  # Use QWidget instead of QLabel
        logo_layout = QVBoxLayout(logo_widget)  # Set layout directly on the widget
        logo_layout.setContentsMargins(0, 0, 0, 0)  # Remove default margins
        logo_layout.setSpacing(5)  # Add some spacing between image and text

        # If the image is loaded
        logo_pixmap = QPixmap("assets/imgs/TikTok-logo-CMYK-Stacked-white-simplified.png")
        if not logo_pixmap.isNull():
            # Create a pixmap label for the image
            logo_image_label = QLabel()
            logo_image_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
            logo_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Add both image and text to the layout
            logo_layout.addWidget(logo_image_label)
            # logo_layout.addWidget(logo_text_label)

            # Optional: Set widget stylesheet
            logo_widget.setStyleSheet("color: white; padding: 20px;")
        else:
            # If image fails to load, create a label with text
            logo_text_label = QLabel("LOGO")
            logo_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_text_label.setStyleSheet("color: white; padding: 20px;")
            logo_layout.addWidget(logo_text_label)

        # 创建菜单按钮
        home_btn = self.create_menu_button("首 页")
        start_btn = self.create_menu_button("开 始")
        assistant_btn = self.create_menu_button("工 具")
        # 设置按钮字体
        font = QFont(QFont("微软雅黑", 10, QFont.Weight.Bold))
        home_btn.setFont(font)
        start_btn.setFont(font)
        assistant_btn.setFont(font)

        # 添加组件到左侧布局
        left_layout.addWidget(logo_widget)
        left_layout.addWidget(home_btn)
        left_layout.addWidget(start_btn)
        left_layout.addWidget(assistant_btn)
        left_layout.addStretch()
        # 设置布局的对齐方式为居中
        # left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 创建右侧主容器和布局
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_widget.setStyleSheet("background-color: #f0f2f5; ")  # 右侧全部设备灰色
        # 创建顶部用户信息栏
        top_bar = QWidget()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("background-color: #f0f2f5; ")
        top_layout = QHBoxLayout(top_bar)

        # 添加弹簧推动用户信息到右侧
        top_layout.addStretch()

        # 创建用户信息区域
        user_widget = QWidget()
        user_layout = QHBoxLayout(user_widget)
        top_bar.setStyleSheet("background-color: #f0f2f5; ")
        # 用户头像
        avatar_label = CircleAvatarLabel(30)
        avatar_label.setImage("assets/imgs/avatar.png")  # 设置默认头像图片

        # 用户名
        username_label = QLabel("小助手")
        username_label.setStyleSheet("""
            color: #333333; 
            font-size: 14px;
            font-weight: 500;
            margin-left: 10px;
            margin-right: 5px;
        """)

        # 下拉箭头按钮
        dropdown_btn = QToolButton()
        # dropdown_btn.setText("▼")
        dropdown_btn.setStyleSheet("""
            QToolButton {
                border: none;
                color: #666666;
                padding: 5px;
            }
            QToolButton::menu-indicator {
                image: url(path/to/dropdown_icon.png); 
                width: 12px;
                height: 12px;
            }
        """)
        dropdown_btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)  # 添加这一行

        # 创建下拉菜单
        menu = QMenu(dropdown_btn)
        menu.setStyleSheet("QMenu::item { color: black; }")  # 设置菜单项的文本颜色为黑色

        logout_action = QAction("关闭", menu)
        logout_action.triggered.connect(self.close)
        menu.addAction(logout_action)

        # 创建最小化动作
        minimize_action = QAction("最小化", menu)
        minimize_action.triggered.connect(self.showMinimized)  # 最小化窗口
        menu.addAction(minimize_action)

        dropdown_btn.setMenu(menu)

        # 设置布局
        user_layout.addWidget(avatar_label)
        user_layout.addWidget(username_label)
        user_layout.addWidget(dropdown_btn)
        user_layout.setContentsMargins(10, 0, 10, 0)
        user_layout.setSpacing(5)  # 添加组件间的间距

        # 将用户信息添加到顶部栏
        top_layout.addWidget(user_widget)

        # 创建右侧内容区域
        self.content_stack = QStackedWidget()

        # 创建各个页面的内容
        # home_page = QWidget()
        home_page = HomePage(main_window=self)
        # home_layout = QVBoxLayout(home_page)
        # home_layout.addWidget(QLabel("首页内容"))

        self.start_page = StartPage()  #

        assistant_page = AssistantPage()
        # assistant_layout = QVBoxLayout(assistant_page)
        # assistant_layout.addWidget(QLabel("主播助手内容"))

        # 将页面添加到堆叠窗口
        self.content_stack.addWidget(home_page)
        self.content_stack.addWidget(self.start_page)
        self.content_stack.addWidget(assistant_page)

        # 连接按钮信号
        # home_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        # start_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
        # assistant_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))
        home_btn.clicked.connect(lambda:self.on_button_clicked(0))
        start_btn.clicked.connect(lambda:self.on_button_clicked(1))
        assistant_btn.clicked.connect(lambda:self.on_button_clicked(2))

        # 连接信号到处理方法
        self.switch_to_start_page_signal.connect(self.switch_to_start_page)

        # 将顶部栏和内容区域添加到右侧布局
        right_layout.addWidget(top_bar)
        right_layout.addWidget(self.content_stack)

        # 将左侧菜单和右侧内容添加到主布局
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        # 设置主布局的边距
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.current_button = None  # 用于保存当前选中的按钮

    def closeEvent(self, event):
        print("监听到关闭,正在关闭所有窗口...")
        # 终止整个应用程序
        QApplication.quit()
        event.accept()

    # 创建菜单按钮
    def create_menu_button(self, text):
        button = QPushButton(text)
        button.setFont(QFont("Arial", 12))
        button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                text-align: centent;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)
        return button

    # 菜单 点击
    def on_button_clicked(self,index=0):
        logger.info(index)
        self.content_stack.setCurrentIndex(index)
        #
        button = self.sender()
        # 如果当前有选中的按钮，重置其样式
        if self.current_button:
            self.current_button.setStyleSheet("""
                       QPushButton {
                           color: white;
                           background-color: transparent;
                           border: none;
                           text-align: center;
                           padding: 10px 20px;
                       }
                       QPushButton:hover {
                           background-color: #34495e;
                       }
                       QPushButton:pressed {
                           background-color: #2980b9;
                       }
                   """)

        # 更新当前选中的按钮
        self.current_button = button
        # 设置当前选中按钮的样式
        button.setStyleSheet("""
                   QPushButton {
                       color: white;
                       background-color: #2980b9;
                       border: none;
                       text-align: center;
                       padding: 10px 20px;
                   }
                   QPushButton:hover {
                       background-color: #34495e;
                   }
                   QPushButton:pressed {
                       background-color: #2980b9;
                   }
               """)


    # 切换页面使用
    def switch_to_start_page(self, page_index=0, input_value=None):
        # 切换到StartPage
        self.content_stack.setCurrentIndex(page_index)
        # 传值
        self.start_page.room_number_input.setText(str(input_value))

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


# 设置头像圆形
class CircleAvatarLabel(QLabel):
    def __init__(self, size=40):
        super().__init__()
        self.size = size
        self.setFixedSize(size, size)

    def setImage(self, image_path):
        # 加载图片
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # 创建圆形图片
            rounded_pixmap = QPixmap(self.size, self.size)
            rounded_pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(rounded_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 创建圆形路径
            path = QPainterPath()
            path.addEllipse(0, 0, self.size, self.size)
            painter.setClipPath(path)

            # 缩放原始图片并绘制
            scaled_pixmap = pixmap.scaled(self.size, self.size,
                                          Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                          Qt.TransformationMode.SmoothTransformation)

            # 计算居中位置
            x = (self.size - scaled_pixmap.width()) // 2
            y = (self.size - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()

            self.setPixmap(rounded_pixmap)
        else:
            self.setText("头像")
            self.setStyleSheet("""
                    background-color: #eee;
                    border-radius: {}px;
                    """.format(self.size // 2))
