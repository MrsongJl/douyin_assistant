import requests
import json
import aiohttp
import asyncio


# 同步方式-POST
def send_post_request(url, data):
    """
    发送POST请求到指定的URL，并携带JSON数据。

    :param url: 请求的URL
    :param data: 要发送的JSON数据（字典格式）
    :return: 服务器的响应
    """
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()  # 如果响应状态码不是200，抛出异常
        return response.json()  # 返回响应的JSON数据
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None


# 同步方式-GET
def send_get_request(url, params=None):
    """
    发送GET请求到指定的URL，并携带查询参数。

    :param url: 请求的URL
    :param params: 查询参数（字典格式）
    :return: 服务器的响应
    """
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 如果响应状态码不是200，抛出异常
        return response.json()  # 返回响应的JSON数据
    except requests.exceptions.RequestException as e:
        print(f"GET请求失败: {e}")
        return None


# 异步方式
async def async_send_post_request(url, data):
    """
    发送异步POST请求到指定的URL，并携带JSON数据。

    :param url: 请求的URL
    :param data: 要发送的JSON数据（字典格式）
    :return: 服务器的响应
    """
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(data), headers=headers) as response:
                response.raise_for_status()  # 如果响应状态码不是200，抛出异常
                return await response.json()  # 返回响应的JSON数据
    except aiohttp.ClientError as e:
        print(f"请求失败: {e}")
        return None


# 请求事件
def http_api_action(method, url, payload):
    """
    执行HTTP请求，并考虑冷却时间。

    :param method: HTTP方法（例如 'POST' 或 'GET'）
    :param url: 请求的URL
    :param payload: 要发送的数据（字典格式）
    :return: 如果请求成功且不在冷却中，返回True；否则返回False
    """
    method = method.upper()
    if method == 'POST':
        response = send_post_request(url, payload)
    elif method == 'GET':
        response = send_get_request(url, params=payload)
    else:
        print(f"不支持的HTTP方法: {method}")
        return False

    if response is not None:
        return True
    return False


# 示例使用
if __name__ == "__main__":
    url = "http://localhost:8888/executeCommand"
    data = {
        "command": "event",
        "content": "转个身"
    }

    result = send_post_request(url, data)
    if result:
        print("服务器响应:", result)
