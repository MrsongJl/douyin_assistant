import os

from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QMessageBox, QMainWindow,
                             QGraphicsDropShadowEffect, QHBoxLayout, QToolButton, QMenu, QStackedWidget, QGridLayout,
                             QTextEdit, QDialog, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QUrl, QTimer
from PyQt6.QtGui import QPixmap, QFont, QAction, QColor, QPainter, QPainterPath, QIcon, QScreen
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
# 日志
from units.logger_config import setup_logger

logger = setup_logger()

from units.config import *

from ui.SettingWindow import *
from ui.DebugWindow import *
from ui.TransparentWindow import *
from ui.ConfigEditor import *

# 对话框
class CustomInputDialog(QWidget):
    """
    自定义输入对话框示例
    Example of a custom input dialog
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Input Dialog")
        self.setGeometry(300, 300, 300, 200)

        # 主布局
        layout = QVBoxLayout()

        # 用户名输入
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # 密码输入
        # password_layout = QHBoxLayout()
        # password_label = QLabel("Password:")
        # self.password_input = QLineEdit()
        # self.password_input.setEchoMode(QLineEdit.Password)
        # password_layout.addWidget(password_label)
        # password_layout.addWidget(self.password_input)
        # layout.addLayout(password_layout)

        # 结果标签
        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.setLayout(layout)


# 工具 点击后的窗口
class ToolWindow(QWidget):
    """
     可动态加载不同内容的工具窗口类
     Supports loading web pages, local HTML files, and custom content types
    """

    def __init__(self, content_type='web', content_source=None, window_title="Tool Window",
                 custom_widget: QWidget = None):
        """
               初始化工具窗口

               :param content_type: 内容类型 ('web', 'local_html', 'text', 'custom')
               :param content_source: 内容源 (URL, 文件路径, 文本内容等)
               :param window_title: 窗口标题
        """
        logger.info(f"即将打开Web：{content_source}")
        super().__init__()
        # 设置窗口标题
        self.setWindowTitle(window_title)
        # 设置新窗口logo
        app_icon = QIcon("assets/imgs/TikTok-logo-CMYK-Stacked-black.png")  # 替换为你的图标文件路径
        self.setWindowIcon(app_icon)
        # 设置基础路径 暂时不用
        self.base_path = "file:///" + os.path.abspath("Html").replace("\\", "/") + "/"

        self.custom_widget = custom_widget  # 页面

        # 创建主布局
        main_layout = QVBoxLayout()
        # main_layout.setContentsMargins(20, 20, 20, 20)

        # 获取主屏幕的尺寸
        screen: QScreen = QApplication.primaryScreen()
        screen_size = screen.size()
        if content_type == 'local_html':

            # 计算窗口尺寸为屏幕的50%
            width = int(screen_size.width() * 0.5)
            height = int(screen_size.height() * 0.5)
            self.resize(width, height)


        # 根据内容类型创建不同的内容显示组件
        self.content_widget = self._create_content_widget(content_type, content_source)
        main_layout.addWidget(self.content_widget)

        # 设置布局
        self.setLayout(main_layout)
        # 设置窗口为全屏显示
        # self.showFullScreen()

    def _create_content_widget(self, content_type, content_source):
        """
        根据内容类型创建不同的内容显示组件

        :param content_type: 内容类型
        :param content_source: 内容源
        :return: 内容显示组件
        """
        if content_type == 'web':
            # 在web 设置窗口大小
            # 计算窗口尺寸为屏幕的50%
            return self._create_web_view(content_source)
        elif content_type == 'local_html':
            return self._create_local_html_view(content_source)
        elif content_type == 'text':
            return self._create_text_view(content_source)
        elif content_type == 'custom':
            # 弹出自定义对话框
            return self._create_custom_view()
        else:
            return QLabel("Unsupported content type")

    def _create_web_view(self, url=None):
        """
        创建Web视图

        :param url: 要加载的网页URL
        :return: QWebEngineView
        """
        web_view = QWebEngineView()
        web_view.setStyleSheet("""
            QWebEngineView {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)

        # 如果没有提供URL，则加载默认页面
        load_url = url if url else "http://www.baidu.com"
        web_view.load(QUrl(load_url))

        return web_view

    def _create_local_html_view(self, file_path):
        """
        创建本地HTML文件视图

        :param file_path: 本地HTML文件路径
        :return: QWebEngineView
        """
        web_view = QWebEngineView()
        web_view.setStyleSheet("""
            QWebEngineView {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)

        # 构建完整的本地文件URL
        if file_path:
            local_url = self.base_path + file_path if not file_path.startswith('file:///') else file_path
            web_view.load(QUrl(local_url))

        return web_view

    def _create_text_view(self, text=None):
        """
        创建文本显示视图

        :param text: 要显示的文本内容
        :return: QTextEdit
        """
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        if text:
            text_edit.setText(text)

        return text_edit

    def _create_custom_view(self):
        """
        创建自定义组件视图

        :param custom_widget: 自定义的Qt组件
        :return: 自定义组件或默认标签
        """
        # 创建并显示自定义对话框
        dialog = self.custom_widget
        #  dialog.exec_()  # 模态对话框
        return dialog

    # # 示例1：加载网页
    # web_window = ToolWindow(content_type='web', content_source='https://www.google.com', window_title='Web Page')
    # web_window.show()
    #
    # # 示例2：加载本地HTML
    # local_html_window = ToolWindow(content_type='local_html', content_source='about.html', window_title='Local HTML')
    # local_html_window.show()
    #
    # # 示例3：显示文本
    # text_window = ToolWindow(content_type='text', content_source='Hello, World!', window_title='Text View')
    # text_window.show()


# 工具界面
class AssistantPage(QWidget):
    def __init__(self):
        super().__init__()

        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 添加标题
        # title_label = QLabel("热门工具", self)
        # title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        # main_layout.addWidget(title_label)

        # 创建网格布局用于放置工具按钮
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(20)
        main_layout.addLayout(grid_layout)

        # 示例数据 - 工具列表
        tools = [
            (1, 'assets/imgs/AI配置.png', 'AI配置', '一些系统初始配置。'),
            (2, 'assets/imgs/系统设置.png', '礼物设置', '一些礼物配置。'),
            (3, 'assets/imgs/运行调试', '运行调试', '可在这里调整模拟评论及礼物。。'),
            (4, 'assets/imgs/桌面角色.png', '桌面角色', '可在桌面进行交互的角色'),
            (5, 'assets/imgs/关于我们.png', '关于我们', '关于我们'),

        ]

        # 添加工具到网格布局
        for idx, (id, icon, name, desc) in enumerate(tools):
            button = ToolButton(id, icon, name, desc)
            row = idx // 3
            col = idx % 3
            grid_layout.addWidget(button, row, col)

        # 确保布局填充窗口
        main_layout.addStretch(1)


# 按钮 事件
class ToolButton(QPushButton):
    # toolClicked = pyqtSignal(str)

    def __init__(self, id, icon_path, tool_name, tool_description, *args, **kwargs):
        super().__init__()
        # self.setFixedSize(200, 150)
        self.id = id
        self.tool_name = tool_name
        # self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Icon
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QPixmap(icon_path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                            Qt.TransformationMode.SmoothTransformation))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet('''
                background-color: white;
            ''')

        layout.addWidget(self.icon_label)

        # Name
        self.name_label = QLabel(tool_name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet('''
            background-color: white;

            color: #333;
        ''')
        layout.addWidget(self.name_label)

        # Description
        self.desc_label = QLabel(tool_description)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setStyleSheet('''
                  background-color: white;
                 font-size: 12px; 
                 color: #666;
             ''')
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)

        # Button styling
        self.setStyleSheet('''
              QPushButton {
                  background-color: white;
                  border: none;
                  border-radius: 10px;
                  padding: 10px;
                  transition: background-color 0.3s ease;
              }

          ''')

        # Ensure the button can expand
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.name_label.setObjectName("name_label")
        self.desc_label.setObjectName("desc_label")
        # 连接点击信号
        self.clicked.connect(self.handleClick)  # 绑定信号到槽

    def enterEvent(self, event):
        """鼠标进入时的效果"""
        # logger.info("鼠标进入")
        self.setStyleSheet('''
                    QPushButton {
                        background-color: #d8d8d8;
                        border: none;
                        padding: 10px;
                        transition: background-color 0.3s ease;
                    }
                ''')
        # 非默认样式 只能重新设置
        self.name_label.setStyleSheet('''
                    background-color: #d8d8d8;
                ''')
        self.desc_label.setStyleSheet('''
                        background-color: #d8d8d8;
                    ''')
        self.icon_label.setStyleSheet('''
                        background-color: #d8d8d8;
                    ''')

        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开时的效果"""
        self.setStyleSheet('''
                   QPushButton {
                       background-color: white;
                       border: none;
                       padding: 10px;
                       transition: background-color 0.3s ease;
                   }
               ''')
        self.name_label.setStyleSheet('''
                    background-color: white;
                ''')
        self.desc_label.setStyleSheet('''
                        background-color: white;
                    ''')
        self.icon_label.setStyleSheet('''
                        background-color: white;
                    ''')
        super().leaveEvent(event)

    # 点击后事件
    def handleClick(self):
        """处理点击事件"""
        if self.id == 1:
            # 智能场景
            self.new_window = ToolWindow(content_type='custom', window_title='初始设置', custom_widget=SettingWindow())
            self.new_window.show()
        elif self.id == 2:
            # 礼物对照
            self.configEditor = ConfigEditor()
            self.configEditor.show()

        elif self.id == 3:
            # 调试窗口
            self.new_window = ToolWindow(content_type='custom',
                                         window_title='调试工具', custom_widget=DebugWindow())
            self.new_window.show()

        elif self.id == 4:
            # 桌面
            # self.new_window = ToolWindow(content_type='custom',
            #                              window_title='桌面角色', custom_widget=TransparentWindow())
            # self.new_window.show()
            self.transparent_window = TransparentWindow()
            self.transparent_window.show()

        elif self.id == 5:
            # 关于我们
            self.new_window = ToolWindow(content_type='local_html', window_title='关于我们',
                                         content_source='about.html')
            self.new_window.show()


        else:
            print("没有这个菜单")
