import yaml
import json


def load_config():
    with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
    return config


# 读取配置文件
config = load_config()

qwen_api_key = config.get("qwen_api_key")


# 读取人设
sys_prompt = "你是一个AI助手!"
with open('sys_prompt.txt', 'r', encoding='utf-8') as file:
    sys_prompt = file.read()

# 读取当前的人设
def read_sys_prompt():
    with open('sys_prompt.txt', 'r', encoding='utf-8') as file:
        return file.read()


# 读取当前的key
def read_qwen_api_key():
    config = load_config()
    return config.get("qwen_api_key")