# 定义一个于网页交互的桥 方便交互
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
import json
# 信号连接示例
# from Units.Bridge import *
# 创建WebChannel
# self.channel = QWebChannel()
# self.bridge = Bridge()
# self.channel.registerObject('bridge', self.bridge)
# # 设置WebChannel
# self.web_view.page().setWebChannel(self.channel)
# 加载HTML
# self.web_view.load(QUrl("http://localhost:8888/html/index.html"))
#
# # 连接信号
# self.bridge.button_clicked.connect(self.on_web_button_clicked)

# 首页使用的信号
class Bridge(QObject):
    # 定义一个信号，可以在需要时触发
    button_clicked = pyqtSignal(str)


    @pyqtSlot(str)
    def handle_button_click(self,json_data):
        # 这个方法会被网页的JavaScript调用
        # 解析JSON数据
        data = json.loads(json_data)
        print(f"收到的数据：{data}")
        self.button_clicked.emit(json_data)


# 日志使用
class LogSignals(QObject):
    """
    专门用于日志信号传递的类
    """
    log_signal = pyqtSignal(str)
