import sys
import asyncio
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, \
    QPushButton, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal, QThread
import json

from units.requestHelper import *
from units.EventHandler import *

class CustomLineEdit(QLineEdit):
    enter_pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.enter_pressed.emit()
        else:
            super().keyPressEvent(event)

class AsyncWorker(QThread):
    def __init__(self, coroutine, callback):
        super().__init__()
        self.coroutine = coroutine
        self.callback = callback

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.coroutine)
        loop.close()
        self.callback(result)

class DebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DebugWindow")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        scroll_area.setWidget(self.chat_display)

        input_layout = QHBoxLayout()

        self.input_box = CustomLineEdit(self)
        self.input_box.setPlaceholderText("请输入消息...")
        input_layout.addWidget(self.input_box)

        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        self.debug_button_layout = QHBoxLayout()
        layout.addLayout(self.debug_button_layout)

        self.input_box.enter_pressed.connect(self.send_message)

        # 加载配置文件并生成按钮
        self.load_config_and_create_buttons()

    def load_config_and_create_buttons(self):
        config_path = 'config.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        for event in config["game_event"]:
            button = QPushButton(f"模拟送{event['trigger']['text']}")
            button.clicked.connect(lambda _, e=event['trigger']['text']: self.run_async_task(self.simulate_event(e)))
            self.debug_button_layout.addWidget(button)

    def send_message(self):
        message = self.input_box.text()
        if message:
            self.chat_display.append(f"你: {message}")
            self.input_box.clear()
            self.run_async_task(self.simulate_ai_response(message))

    def run_async_task(self, coroutine):
        self.worker = AsyncWorker(coroutine, self.on_ai_response)
        self.worker.start()

    def on_ai_response(self, result):
        self.chat_display.append(f"AI: {result}")

    async def simulate_ai_response(self, message):
        print(f"模拟发送消息{message}")
        action = {f'comment': f'{message}'}
        handler.add_to_queue(action)
        return '已添加到队列,正在处理中...'

    async def simulate_event(self, event_name):
        print(f"触发事件: {event_name}")

        action = {f'broadcast': f'感谢小桃子送的1个{event_name}'}
        handler.add_to_queue(action)
        action = {f'gift': f'{event_name}'}
        handler.add_to_queue(action)

        return '已添加到队列,正在处理中...'

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DebugWindow()
    window.show()
    sys.exit(app.exec())