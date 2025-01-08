import os
import asyncio
from openai import AsyncOpenAI
import platform

from units.config import *

# 每次初始化时都更新下获取的秘钥
DASHSCOPE_API_KEY = qwen_api_key

class QwenClient:
    def __init__(self, api_key=None, sys_prompt='你是一个AI助手！',
                 base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"):

        self.client = AsyncOpenAI(
            api_key=api_key or DASHSCOPE_API_KEY,
            base_url=base_url,
        )
        self.sys_prompt = sys_prompt

    async def chat(self, message, model="qwen-max"):
        try:

            response = await self.client.chat.completions.create(
                messages=[{'role': 'system', 'content': self.sys_prompt},
                          {'role': 'user', 'content': f'{message}'}],
                model=model,
            )
            content = response.choices[0].message.content
            return content

        except Exception as e:
            if "Incorrect API key provided" in str(e):
                return "错误：提供的API密钥不正确，请检查。"
            else:
                return f"发生未知错误：{str(e)}"


# 验证
async def main():
    try:
        qwen_client = QwenClient()
        response = await qwen_client.chat("请回复“大模型访问成功！”")

        print(response)
        return response
    except Exception as e:
        return f"发生未知异常：{str(e)}"

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# asyncio.run(main())
