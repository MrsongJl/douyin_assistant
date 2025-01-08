from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QMessageBox, QMainWindow,
                             QGraphicsDropShadowEffect, QHBoxLayout, QToolButton, QMenu, QStackedWidget, QTextBrowser)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont, QAction, QColor, QPainter, QPainterPath, QIcon
from urllib.parse import urlparse
import threading
from threading import Lock

from units.config import *
from units.AppManager import *

import re
# 日志
from units.logger_config import setup_logger

logger = setup_logger()

# 弹幕相关
from webfetcher.CustomTikTokLiveClient import *

from units.EventHandler import *


# 开始界面
class StartPage(QWidget):
    def __init__(self):
        super().__init__()
        # 是否开启
        self.is_open = False

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)  # 位置
        main_layout.setSpacing(10)

        # 输入框 位置
        input_section = self._create_input_section()
        main_layout.addLayout(input_section)

        # log 位置
        self.log_text_edit = self._create_log_area()
        main_layout.addWidget(self.log_text_edit, stretch=2)

        self.setLayout(main_layout)

        # 样式
        self._apply_flat_style()

    # 输入框位置 样式
    def _create_input_section(self):
        # 水平布局
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)  # 间距

        # Room Number Input
        self.room_number_input = QLineEdit()
        self.room_number_input.setPlaceholderText("输入你的直播间地址")
        self.room_number_input.setMinimumHeight(40)
        self.room_number_input.returnPressed.connect(self.start_monitoring)

        # 添加一个线程停止标志
        self.stop_client_thread_flag = threading.Event()
        self.client_thread = None
        # 开始监控按钮
        self.start_button = self._create_flat_button(
            "抓取弹幕",
            self.start_monitoring
        )

        # 添加一个线程停止标志
        self.stop_thread_flag = threading.Event()
        # 存放新的线程
        self.interact_thread = None
        # 恶作剧按钮
        self.interact_button = self._create_flat_button(
            "点击开始互动",
            self.toggle_interact
        )

        # 将小部件添加到布局中
        input_layout.addWidget(self.room_number_input, stretch=2)
        input_layout.addWidget(self.start_button)
        input_layout.addWidget(self.interact_button)

        return input_layout

    def _create_log_area(self):
        log_area = QTextBrowser()
        # 设置字体大小和样式
        font = QFont("Segoe UI", 10)
        log_area.setFont(font)

        # 设置背景颜色和文本颜色
        log_area.setStyleSheet("""
QTextBrowser {
    background-color: #EDE7F6;
    color: #4A148C;
    border: 1px solid #B39DDB;
    border-radius: 5px;
    padding: 10px;
}
QScrollBar:vertical {
    background-color: #D1C4E9;
    width: 12px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background-color: #B39DDB;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    background: none;
}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}
        """)

        return log_area

    def _create_flat_button(self, text, on_click):
        button = QPushButton(text)
        button.setMinimumHeight(40)
        button.clicked.connect(on_click)
        button.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
            QPushButton:pressed {
                background-color: #4C566A;
            }
        """)
        return button

    def _apply_flat_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #3B4252;
                color: #ECEFF4;
            }
        """)

    # 开始监听 可以停止
    def start_monitoring(self):
        if self.client_thread is None or not self.client_thread.is_alive():
            print("开始监听")
            # 获取文本验证
            room_name = self.room_number_input.text()
            if not room_name:
                # self.text_display.insert(tk.END, "请输入房间名称!\n")
                self.show_text(f"请输入房间名称!")
                return
            # 可以开始
            self.start_button.setText("Opening...")
            # 改变按钮的颜色
            self.start_button.setStyleSheet("background-color: green; color: white;")
            # self.start_button.setEnabled(False)
            # 创建并启动客户端
            live_id = self.get_douyin_live_id(room_name)
            logger.info(f"本次监听的房间名称为:{live_id}")
            if not live_id:
                self.show_text("请确保输入的是有效的抖音直播链接，格式应为 {https://live.douyin.com/你的房间号}")
                return
            # 初始化 弹幕
            self.client = CustomTikTokLiveClient(live_id=live_id)
            # 连接日志信号到日志显示槽函数
            self.client.log_signals.log_signal.connect(self.show_text)
            # 启动线程
            self.stop_client_thread_flag.clear()  # 清除停止标志
            # 在新线程中运行客户端
            self.client_thread = threading.Thread(target=self._run_client, daemon=True)
            self.client_thread.start()
        else:
            print("停止监听")
            # 停止监听
            self.client.stop()

            # 停止线程
            self.stop_client_thread_flag.set()  # 设置停止标志
            # 等待线程结束（可选）
            if self.client_thread:
                self.client_thread.join(timeout=2)

            # 重置按钮状态
            self.start_button.setText("抓取弹幕")
            self.start_button.setStyleSheet("")
            self.start_button.setEnabled(True)

    # 新线程开启
    def _run_client(self):
        try:
            # 标记开始了
            self.show_text("开始监听弹幕...")
            self.is_open = True
            self.client.start()


        except Exception as e:
            logger.info(f"failed: {e}")
            # 显示错误
            self.show_text(f"抱歉，出错了. {e}\n")
            # 恢复按钮
            self.start_button.setText("抓取弹幕")
            # 改变按钮的颜色
            self.start_button.setStyleSheet("")
            self.start_button.setEnabled(True)

    # 获取房间号
    def get_douyin_live_id(self, url_string):
        try:
            # 解析URL
            if "live.douyin.com/" not in url_string:
                return None
            parsed_url = urlparse(url_string)

            # 获取路径部分并去除开头的斜杠
            path = parsed_url.path.lstrip('/')

            # 假设路径只包含直播间ID，直接返回
            return path if path.isdigit() else None

        except Exception as e:
            print("Invalid URL:", e)
            return None

    def show_text(self, message):
        self.log_text_edit.append(message)
        # 自动滚动到底部
        self.log_text_edit.verticalScrollBar().setValue(self.log_text_edit.verticalScrollBar().maximum())

    # 添加扁平的按钮
    def _create_flat_button(self, text, callback):
        button = QPushButton(text)
        button.setMinimumHeight(40)
        button.clicked.connect(callback)
        return button

    # 扁平的样式
    def _apply_flat_style(self):
        # Flat, modern color palette
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f4;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                border: 1px solid #e1e1e1;
                border-radius: 4px;
                padding: 8px;
                background: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                outline: none;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
            QTextBrowser {
                background-color: white;
                border: 1px solid #e1e1e1;
                border-radius: 4px;
                padding: 10px;
            }
        """)

    def read_config(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    # 切换开启状态
    def toggle_interact(self):
        if self.interact_thread is None or not self.interact_thread.is_alive():
            print("开启互动")
            self.show_text("已开启互动，将持续监听事件进行交互！")
            # 启动线程
            self.stop_thread_flag.clear()  # 清除停止标志
            self.interact_button.setText("STARTING..")
            self.interact_button.setStyleSheet("background-color: green; color: white;")
            # self.interact_button.setEnabled(False)

            # 写入配置
            config = self.read_config('config.json')
            print(config)
            handler.load_config(config_json=config)

            self.interact_thread = threading.Thread(target=self._run_queue, daemon=True)
            self.interact_thread.start()
        else:
            print("停止互动")
            self.show_text("已停止互动！")
            # 停止线程
            self.stop_thread_flag.set()  # 设置停止标志

            # 等待线程结束（可选）
            if self.interact_thread:
                self.interact_thread.join(timeout=2)

            # 重置按钮状态
            self.interact_button.setText("点击开始互动")
            self.interact_button.setStyleSheet("")
            self.interact_button.setEnabled(True)

    def _run_queue(self):
        """一直循环处理队列内容"""
        while not self.stop_thread_flag.is_set():
            handler.process_queue()
            time.sleep(1)
