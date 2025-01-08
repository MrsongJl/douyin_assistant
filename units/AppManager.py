import asyncio
# 全局变量
class AppManager:
    _token = None

    @classmethod
    def set_token(cls, token):
        cls._token = token

    @classmethod
    def get_token(cls):
        return cls._token



# 全局队列
class QueueManager:
    def __init__(self):
        self.audio_queue = asyncio.Queue()
        self.event_queue = asyncio.Queue()

    async def add_audio(self, file_path: str):
        await self.audio_queue.put(file_path)

    async def get_audio(self):
        return await self.audio_queue.get() if not self.audio_queue.empty() else None

    async def add_event(self, content: str):
        await self.event_queue.put(content)

    async def get_event(self):
        return await self.event_queue.get() if not self.event_queue.empty() else None


# 创建队列管理器实例 公共
queue_manager = QueueManager()