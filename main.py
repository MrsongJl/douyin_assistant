import sys
import threading
from typing import Optional
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import QThread, pyqtSignal
import socket
import requests
from contextlib import closing
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uuid
import aiofiles
import asyncio
# 全局配置
from units.config import *
from units.qwen import *
from units.AppManager import *
from edge_tts import Communicate

# 初始化语音
import edge_tts

VOICE = "zh-CN-XiaoyiNeural"  # 晓依，女性，声音较为温柔
SRT_FILE = "test.srt"


# 全局连接管理器
# 管理WebSocket连接
class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.video_list: List[str] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting: {e}")


manager = ConnectionManager()


# 创建一个临时目录
temp_dir = 'temp'
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
    print(f"Temporary directory created: {temp_dir}")


# 生成器 单次对话
class CommandRequest(BaseModel):
    command: str
    content: str


class UvicornServer(uvicorn.Server):
    """自定义 Uvicorn 服务器类，添加了停止功能"""

    def install_signal_handlers(self):
        pass


class FastAPIThread(QThread):
    server_started = pyqtSignal()
    server_stopped = pyqtSignal()

    def __init__(self, port=8888):
        super().__init__()
        self.app = FastAPI()
        self.port = port
        self.server = None
        self.should_exit = False
        self.setup_routes()

        # 配置CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        self.app.mount("/html", StaticFiles(directory="html", html=True), name="html")
        self.app.mount("/assets", StaticFiles(directory="assets"), name="assets")
        self.app.mount("/temp", StaticFiles(directory="temp"), name="temp")

        @self.app.get("/")
        def read_root():
            return {"Hello": "World"}

        @self.app.get("/shutdown")
        def shutdown():
            self.stop()
            return {"status": "shutting down"}

        # 指令
        @self.app.post("/executeCommand")
        async def executeCommand(request: CommandRequest):
            """
            指令执行
            :param request:
            :return:
            """
            print(f"开始执行指令:{request.command}")
            if request.command == "chat":
                # 对话
                # 每次都更细下秘钥及设定的人设
                qwen_client = QwenClient(sys_prompt=read_sys_prompt(), api_key=read_qwen_api_key())
                response = await qwen_client.chat(request.content)
                print(response)
                # 合成
                random_filename = f"{uuid.uuid4()}.mp3"
                file_path = os.path.join(temp_dir, random_filename)

                communicate = edge_tts.Communicate(response, VOICE)
                async with aiofiles.open(file_path, "wb") as file:
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            await file.write(chunk["data"])
                win_path = file_path.replace("\\", "/")
                local_path = f"/{win_path}"
                await queue_manager.add_audio(local_path)
                return {"code": 200, "msg": response}
            elif request.command == "generate":
                try:
                    # 调试对话使用
                    random_filename = f"{uuid.uuid4()}.mp3"
                    file_path = os.path.join(temp_dir, random_filename)

                    communicate = edge_tts.Communicate(request.content, VOICE)
                    async with aiofiles.open(file_path, "wb") as file:
                        async for chunk in communicate.stream():
                            if chunk["type"] == "audio":
                                await file.write(chunk["data"])
                    win_path = file_path.replace("\\", "/")
                    # win_path="temp/4c6cc6c6-547d-4fbf-97fe-c67cc35e4600.mp3"
                    local_path = f"/{win_path}"
                    await queue_manager.add_audio(local_path)
                    return {"code": 200, "msg": f"已合成语音{win_path}"}
                except Exception as e:
                    logger.info(str(e))
                    if "Invalid response status" in str(e):
                        return {"code": 503, "msg": "服务暂时不可用，请稍后重试"}
                    else:
                        return {"code": 500, "msg": f"合成语音时发生错误: {str(e)}"}

            elif request.command == "event":
                # 事件
                await queue_manager.add_event(request.content)
                return {"code": 200, "msg": "已执行"}
            else:
                return {"code": 500, "msg": "不支持的指令！"}

        # websocket 链接
        # 音频流发送端点
        @self.app.websocket("/ws/audio")
        async def websocket_endpoint(websocket: WebSocket):
            await manager.connect(websocket)
            try:
                # 初始时发送当前视频列表和当前选中视频
                await websocket.send_json({
                    "type": "init",
                    "data": "WebSocket 响应成功！"
                })

                while True:
                    # 每隔1秒检查队列
                    await asyncio.sleep(2)
                    # print(websocket.client_state)
                    if not websocket.client_state == WebSocketState.CONNECTED:
                        # print("Client disconnected")
                        break
                    event = await queue_manager.get_event()
                    if event:
                        await websocket.send_json({
                            "type": "event",
                            "data": event
                        })
                        continue

                    # 从队列获取音频文件路径
                    audio_file_path = await queue_manager.get_audio()
                    if audio_file_path is None:
                        await websocket.send_json({
                            "type": "heart",
                            "data": "ok"
                        })
                        continue  # 如果没有新的音频文件，继续等待

                    await websocket.send_json({
                        "type": "audio",
                        "data": audio_file_path
                    })

                    # print(f"开始发送文件: {audio_file_path}")


            except WebSocketDisconnect as e:
                manager.disconnect(websocket)
                print("Client disconnected")
                print(f"Client disconnected: {e.code} - {e.reason}")

    def run(self):
        config = uvicorn.Config(
            app=self.app,
            host="0.0.0.0",
            port=self.port,
            loop="asyncio",
            log_config=None  # 必须为空 否则与 pyinstaller冲突
        )
        self.server = uvicorn.Server(config=config)
        # 禁用服务器的默认信号处理
        self.server.install_signal_handlers = lambda: None

        self.server_started.emit()
        self.server.run()

    def stop(self):
        """停止服务器的方法"""
        if self.server:
            self.server.should_exit = True
            self.server_stopped.emit()


# 客户端 开始
from ui.LoginWindow import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("互动虚拟人")
        app_icon = QIcon("./assets/imgs/TikTok-logo-CMYK-Stacked-black.png")  # 替换为你的图标文件路径
        self.setWindowIcon(app_icon)

        self.setup_ui()
        self.api_thread: Optional[FastAPIThread] = None
        self.port = 8888

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 状态标签
        self.status_label = QLabel("服务器状态: 未运行")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # 启动/停止按钮
        self.start_button = QPushButton("启动服务器")
        self.start_button.clicked.connect(self.toggle_server)
        layout.addWidget(self.start_button)
        # 应用扁平化样式
        self.setStyleSheet("""
             QMainWindow {
                 background-color: #f5f5f5;
             }
             QLabel {
                 font-size: 16px;
                 color: #333;
             }
             QPushButton {
                 background-color: #4CAF50;
                 color: white;
                 border: none;
                 padding: 10px 20px;
                 font-size: 16px;
                 border-radius: 5px;
             }
             QPushButton:hover {
                 background-color: #45a049;
             }
             QPushButton:pressed {
                 background-color: #3d8b40;
             }
         """)

    def toggle_server(self):
        if self.api_thread is None or not self.api_thread.isRunning():
            # 启动服务器
            self.api_thread = FastAPIThread(self.port)
            self.api_thread.server_started.connect(self.on_server_started)
            self.api_thread.server_stopped.connect(self.on_server_stopped)
            self.api_thread.start()
            self.start_button.setText("停止服务器")
            self.status_label.setText("服务器状态: 正在启动...")
        else:
            # 通过发送请求来优雅地停止服务器
            try:
                requests.get(f"http://localhost:{self.port}/shutdown")
                self.status_label.setText("服务器状态: 正在停止...")
                self.start_button.setEnabled(False)
            except requests.exceptions.RequestException:
                self.on_server_stopped()

    def open_login_window(self):
        # 创建并显示登录窗口
        self.login_window = LoginWindow()
        self.login_window.show()
        # 隐藏当前的主窗口
        self.hide()

    def on_server_started(self):
        self.status_label.setText("服务器状态: 运行中")
        self.start_button.setEnabled(True)
        self.open_login_window()

    def on_server_stopped(self):
        self.status_label.setText("服务器状态: 已停止")
        self.start_button.setText("启动服务器")
        self.start_button.setEnabled(True)
        if self.api_thread:
            self.api_thread.wait()
            self.api_thread = None

    def closeEvent(self, event):
        if self.api_thread and self.api_thread.isRunning():
            try:
                requests.get(f"http://localhost:{self.port}/shutdown")
                self.api_thread.wait(2000)  # 等待最多2秒
            except requests.exceptions.RequestException:
                pass
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
