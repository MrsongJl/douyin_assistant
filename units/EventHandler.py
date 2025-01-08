import threading
from threading import Lock
import time
from queue import Queue
from typing import Callable, Dict, Any
from units.requestHelper import *
import uuid
import edge_tts
import os
import aiofiles
import requests

from units.AppManager import *

# 日志
from units.logger_config import setup_logger

logger = setup_logger()


class ActionLimiter:
    """触发时间保护"""

    def __init__(self, cooldown_time=1):
        self.cooldown_time = cooldown_time
        self.last_trigger_time = 0
        self.lock = Lock()  # 添加线程锁以确保线程安全

    def can_trigger(self):
        with self.lock:
            current_time = time.time()
            time_diff = current_time - self.last_trigger_time
            logger.info(f"current_time: {current_time}, last_trigger_time: {self.last_trigger_time}, diff: {time_diff}")
            if time_diff >= self.cooldown_time:
                self.last_trigger_time = current_time
                return True
            return False




# 映射事件表
ACTION_HANDLERS = {
    0: 'handle_key_action',  # 按键
    1: 'handle_mouse_action',  # 鼠标
    2: 'handle_video_action',  # 播放视频
    4: 'handle_http_api_action'  # 接口触发
}
class EventHandler():
    """事件"""

    def __init__(self):
        self.queue = Queue()
        self.subscribers: Dict[str, Callable[[Any], None]] = {}
        self.config = None

        self.broadcast_limiter = ActionLimiter(cooldown_time=10)  # broadcast 的限制器
        self.gift_limiter = ActionLimiter(cooldown_time=10)  # gift 的限制器
        self.chat_limiter = ActionLimiter(cooldown_time=10)  # 对话的限制器

    def load_config(self, config_json):
        """加载配置文件"""
        self.config = config_json

    # 队列新增
    def add_to_queue(self, data: Dict[str, Any]):
        if self.first_filter_function(data):
            logger.info(f"数据初次检查通过,可以加入队列！{data}")
            self.queue.put(data)

    # 初次验证
    def first_filter_function(self, data: Dict[str, Any]) -> bool:
        """
        1）礼物全部通过
        2）对话保护期
        """
        logger.info(f"即将开始首次入队前检查：{data}")

        if not self.config:
            logger.error("未读取到配置, 开启互动后使用！")
            return False

        # 对话有保护期
        if 'comment' in data:
            if self.chat_limiter.can_trigger():
                return True
            else:
                logger.info(f"交谈冷却中！此次过滤消息为 {data}")
                return False

            # 分别处理 broadcast 和 gift
        if 'broadcast' in data:
            if self.broadcast_limiter.can_trigger():
                return True
            else:
                logger.info(f"播报事件冷却中！此次过滤消息为 {data}")
                return False

        if 'gift' in data:
            if self.gift_limiter.can_trigger():
                return True
            else:
                logger.info(f"礼物事件冷却中！此次过滤消息为 {data}")
                return False

        # 其他情况关闭
        return False

    # 过滤需要的评论及礼物数据
    # 输入 所有评论及礼物
    # 输出 是参与事件的内容 True
    # 输出 不参与的内容 False
    def filter_function(self, data: Dict[str, Any]) -> bool:
        """
               过滤函数,检查数据是否符合配置的触发条件
               返回: (是否匹配, 匹配的事件配置)
               """
        logger.info(f"即将开始第二次检查：{data}")
        if not self.config:
            return False

        # 处理评论类型事件
        if 'comment' in data:
            # 获取当前评论是否在配置文件中有相应定义
            # data['comment'] 为本次消息
            # event = self.get_event_by_trigger(0, data['comment'])
            # if event:
            #     return True
            return True  # 弹幕直接放行
        elif 'broadcast' in data:
            return True  # 播报继续放行

        # 处理礼物类型事件
        elif 'gift' in data:
            # 获取当前礼物是否在配置文件中有相应定义
            # data['gift'] 为本次礼物数据
            event = self.get_event_by_trigger(1, data['gift'])
            if event:
                return True
            else:
                print(f"当前礼物{data['gift']}未对应事件")
                return False

        return False

    # 事件触发
    trigger_mapping = {
        'comment': 0,
        'gift': 1,
        'like': 2,
        # 如果有其他类型的触发器，可以继续添加
    }

    # 根据 触发条件 及内容 查找匹配的动作
    # 输入 trigger_type 0）弹幕 1）礼物 trigger_text 未对应内容 如 666  或礼物 小心心
    # 输出 执行的动作 event {"name":"大哥我错了","trigger":{"type":"0","text":"1"},"action":{"type":"0","config":{"video_name":"2"}}}
    def get_event_by_trigger(self, trigger_type: int, trigger_text: str) -> Dict:
        """根据触发类型和文本查找对应的事件配置"""
        # 弹幕评论直接返回事件
        if trigger_type == 0:
            game_event = {
                "name": "对话",
                "trigger": {
                    "type": 0,
                    "text": trigger_text
                },
                "action": {
                    "type": 4,  # http_api
                    "config": {
                        "method": "post",
                        "url": "http://localhost:8888/executeCommand",
                        "payload": {
                            "command": "chat",
                            "content": trigger_text
                        }
                    }
                }
            }
            return game_event

        if not self.config:
            return None

        for event in self.config["game_event"]:
            if (event["trigger"]["type"] == trigger_type and
                    event["trigger"]["text"] == trigger_text):
                return event
        return None

    # 队列 消费
    # max_iterations 保护的毫秒数 10s
    def process_queue(self, max_iterations: int = 10000):
        logger.info("************检查中*****************")
        # print(".",end="")
        start_time = time.time()
        iterations = 0
        while not self.queue.empty() and iterations < max_iterations:
            logger.info("************开始消费队列*****************")
            data = self.queue.get()
            # data 数值参考 {“comment”:“666”}
            self.handle_event(data)  # 会触发对应动作
            iterations += 1

        # end_time = time.time()
        # # 如果处理时间过短，可以在这里添加一个短暂的延迟
        # if end_time - start_time < 1:  # 假设你希望至少每秒处理一次
        #     time.sleep(1 - (end_time - start_time))
        #

    # 执行事件
    # 事件路由
    def handle_event(self, data: Dict[str, Any]):
        """处理匹配的事件"""
        # 如果是播报 直接返回事件
        if "broadcast" in data:
            asyncio.run(self.handle_broadcast_action(data["broadcast"]))
            return

        # 第二次检查
        if not self.filter_function(data):
            return

        trigger_mapping = {
            'comment': 0,
            'gift': 1,
            'like': 2,
            # 如果有其他类型的触发器，可以继续添加
        }
        # 默认 为点赞
        default_trigger_type = 2
        default_key = 'like'

        for key, trigger_type in trigger_mapping.items():
            if key in data:
                event = self.get_event_by_trigger(trigger_type, data[key])
                break

        # 事件不为空
        if event:
            logger.info(f"本次执行事件为:{event}")
            action = event["action"]
            # 获取处理函数名称，并检查是否在映射中存在
            handler_name = ACTION_HANDLERS.get(action.get("type"))
            if handler_name:
                handler = getattr(self, handler_name, None)
                if handler:
                    config = action.get("config")
                    handler(config)
                else:
                    logger.error(f"找不到处理方法: {handler_name}")
            else:
                logger.info("暂不支持该类型的操作")

    # 目前仅支持httpapi方式触发
    # 执行1 -http—api
    def handle_http_api_action(self, config: Dict):
        """处理按键动作"""
        method = config["method"]
        url = config["url"]
        payload = config["payload"]  # JSON

        logger.info(f"开始执行HTTP请求:{payload}")

        # 执行请求-同步
        if http_api_action(method=method, url=url, payload=payload):
            logger.info(f"执行成功")
        else:
            logger.info("执行失败")

    # 播放执行
    async def handle_broadcast_action(self, content):
        print(f"开始播报：{content}")
        # 调试对话使用
        random_filename = f"{uuid.uuid4()}.mp3"
        file_path = os.path.join('./temp', random_filename)

        communicate = edge_tts.Communicate(content, 'zh-CN-XiaoyiNeural')
        async with aiofiles.open(file_path, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    await file.write(chunk["data"])
        win_path = file_path.replace("\\", "/")
        # win_path="temp/4c6cc6c6-547d-4fbf-97fe-c67cc35e4600.mp3"
        local_path = f"/{win_path}"
        await queue_manager.add_audio(local_path)
        print(f"播报成功...")


# 使用
handler = EventHandler()
