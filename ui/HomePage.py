# home_page
import os
# 主控台台
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QMessageBox, QMainWindow,
                             QGraphicsDropShadowEffect, QHBoxLayout, QToolButton)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont, QAction, QColor, QPainter, QPainterPath, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer

from units.Bridge import *
from PyQt6.QtWebChannel import QWebChannel
# 日志
from units.logger_config import setup_logger
logger = setup_logger()

# 首页内容
class HomePage(QWidget):
    def __init__(self,main_window=None):
        super().__init__()
        self.main_window = main_window # 主窗体 备用
        # self.setWindowTitle("本地页面查看器")
        # self.resize(800, 600)

        # 设置HTML文件的基础路径
        # self.base_path = "file:///" + os.path.abspath("Html").replace("\\", "/") + "/"
        # logger.info(self.base_path)

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 创建顶部水平布局
        top_layout = QHBoxLayout()

        # # 创建并设置输入框样式
        # self.room_number_input = QLineEdit()
        # self.room_number_input.setPlaceholderText("请输入房间号")
        # self.room_number_input.setMinimumSize(200, 40)
        # self.room_number_input.setFont(QFont("微软雅黑", 12))
        # self.room_number_input.setStyleSheet("""
        #     QLineEdit {
        #         border: 2px solid #ddd;
        #         border-radius: 5px;
        #         padding: 5px 10px;
        #         background: white;
        #     }
        #     QLineEdit:focus {
        #         border: 2px solid #0078d4;
        #     }
        # """)
        # self.room_number_input.returnPressed.connect(self.open_web_view)

        # # 创建并设置按钮样式
        # start_button = QPushButton("绑定房间")
        # start_button.setMinimumSize(120, 40)
        # start_button.setFont(QFont("微软雅黑", 12))
        # start_button.setStyleSheet("""
        #     QPushButton {
        #         background-color: #0078d4;
        #         color: white;
        #         border: none;
        #         border-radius: 5px;
        #         padding: 5px 15px;
        #     }
        #     QPushButton:hover {
        #         background-color: #006cbd;
        #     }
        #     QPushButton:pressed {
        #         background-color: #005ba1;
        #     }
        # """)
        # start_button.clicked.connect(self.open_web_view)

        # 将输入框和按钮添加到顶部布局
        # top_layout.addWidget(self.room_number_input)
        # top_layout.addWidget(start_button)
        # top_layout.addStretch()

        # # 创建并设置日志文本框
        # self.log_text_edit = QTextEdit()
        # self.log_text_edit.setReadOnly(True)
        # self.log_text_edit.setFont(QFont("微软雅黑", 10))
        # self.log_text_edit.setStyleSheet("""
        #     QTextEdit {
        #         border: 1px solid #ddd;
        #         border-radius: 5px;
        #         padding: 5px;
        #         background: #f9f9f9;
        #     }
        # """)
        # self.log_text_edit.hide()

        # 创建web视图组件
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("""
                   QWebEngineView {
                       border: 1px solid #ddd;
                       border-radius: 5px;
                   }
               """)

        # 加载等待框
        self.loading_label = QLabel("Loading...", self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("font-size: 20px; color: blue;")


        # 注册桥
        self.channel = QWebChannel()
        self.bridge = Bridge()
        self.channel.registerObject('bridge', self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        self.web_view.load(QUrl("http://localhost:8888/html/index_cn.html"))

        # 连接信号
        self.bridge.button_clicked.connect(self.on_web_button_clicked)

        # self.get_loacl_setUrl(name="index")
        main_layout.addWidget(self.loading_label) # 把等待框也放到部件中
        self.show_loading(True) # 加载框状态

        self.web_view.loadStarted.connect(self.on_load_started)
        self.web_view.loadFinished.connect(self.on_load_finished)

        main_layout.addWidget(self.web_view)

        # 将布局添加到主布局
        # main_layout.addLayout(top_layout)
        # main_layout.addWidget(self.log_text_edit)
        main_layout.addStretch()

        # 设置主窗口样式
        self.setStyleSheet("""
                  QWidget {
                      background-color: #f0f0f0;
                  }
              """)

        self.setLayout(main_layout)

    def on_load_started(self):
        self.show_loading(True)

    def on_load_finished(self, ok):
        if ok:
            self.show_loading(False)

    def show_loading(self, show):
        self.loading_label.setVisible(show)
        # Optionally, you can also disable the web view while loading
        self.web_view.setEnabled(not show)

    # web 中的按钮点击事件
    def on_web_button_clicked(self, json_data):
        # 实际的PyQt6窗口事件处理
        logger.info("Web按钮被点击了!")
        # 处理从Web页面传来的数据
        data = json.loads(json_data)
        logger.info(f"Home窗体收到的数据：{data}")
        # 切换到弹幕监听页面
        # start_page = StartPage()
        # # 假设从数据中获取房间号
        room_number = data.get('inputValue', 'https://www.tiktok.com/@username/live')  # 根据实际JSON结构调整
        #
        # # 设置房间号到输入框
        # start_page.room_number_input.setText(str(room_number))

        # 切换到页面 并非是打开新窗口
        # 切换到StartPage 主页面使用的堆叠方式
        start_page_index = 1 # start_page
        # 发射信号 触发主窗口切换到StartPage，并传递设置房间号的方法
        self.main_window.switch_to_start_page_signal.emit(start_page_index,room_number)


    def get_loacl_setUrl(self, name):
        file_path = f"{name}.html"
        full_path = os.path.join(os.path.abspath("html"), file_path)
        logger.info(full_path)
        if os.path.exists(full_path):
            url = QUrl.fromLocalFile(full_path)
            self.web_view.setUrl(url)
        else:
            self.show_error(f"找不到文件: {file_path}")

    # 打开一个新的HTMl 界面
    def open_web_view(self):
        room_number = self.room_number_input.text().strip()
        if room_number:
            try:
                # 构建本地HTML文件的完整路径
                file_path = f"{room_number}.html"
                # full_path = os.path.join(os.path.abspath("html"), file_path)
                logger.info(file_path)
                url = f"http://localhost:8000/{file_path}"
                self.web_view.load(QUrl(url))
                # if os.path.exists(full_path):
                #     # url = QUrl.fromLocalFile(full_path)
                #     url=f"http://localhost:8000/{file_path}"
                #     # self.web_view = QWebEngineView()
                #     # self.web_view.setWindowTitle(f"房间 {room_number}")
                #     # self.web_view.resize(1024, 768)
                #     # 加载本地HTML文件
                #     # self.web_view.setUrl(url)
                #     self.web_view.load(QUrl(url))
                # else:
                #     self.show_error(f"找不到文件: {file_path}")
            except Exception as e:
                self.show_error(f"打开文件出错: {str(e)}")
        else:
            self.show_error("请先输入房间号！")

    def show_error(self, message):
        self.log_text_edit.setText(message)
        self.log_text_edit.show()
        QTimer.singleShot(3000, self.log_text_edit.hide)
