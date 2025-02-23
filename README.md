# 🤖 抖音直播虚拟主播助理

一个基于Python的抖音直播虚拟主播助理项目，支持弹幕互动、AI对话、虚拟形象展示等功能。

## ⚠️ 重要提示
不可用于无人直播方式，会被抖音警告，严重可能会被封号，虚拟助理需要与真人、游戏或其他场景 同时出镜！！！

## ✨ 功能介绍

### 1. 📺 抖音直播弹幕监听

### 2. 🎮 互动玩法
互动玩法将在开启互动后生效：

* **聊天:** 调用大模型针对直播间的弹幕进行回复，需要配置AI人设及APIKEY后使用
* **礼物播报:** 将在收到礼物时播放 "感谢xxx送的n个'礼物名'" 并触发内置的动作
* **进入房间播报:** 将在观众进入房间时播报 "欢迎xxx进入直播间"

### 3. 👾 虚拟人显示

* **浏览器方式:** 以便添加OBS浏览器源使用
* **桌面角色方式:** 以便抓取窗口时使用

## 🎉 功能预览

1. 主页面
![主页面](https://raw.githubusercontent.com/MrsongJl/douyin_assistant/main/samples/主页面.png)

2. 监听及互动页面
![监听及互动页面](https://raw.githubusercontent.com/MrsongJl/douyin_assistant/main/samples/监听及互动页面.png)

3. 功能主界面
![功能主界面](https://raw.githubusercontent.com/MrsongJl/douyin_assistant/main/samples/功能主界面.png)

4. 模型显示
![模型显示](https://raw.githubusercontent.com/MrsongJl/douyin_assistant/main/samples/模型显示.png)

5. 直播间效果
![直播间效果](https://raw.githubusercontent.com/MrsongJl/douyin_assistant/main/samples/直播间效果.png)

## 🚀 源码使用
###  ⚠️ 重要提示
需要Window及Python 3.10.0 以上环境

1. 安装虚拟环境
```bash
python -m venv venv
```

2. 激活环境
```bash
venv\Scripts\activate
```

3. 安装包
```bash
pip install -r requirements.txt
```

4. 运行main.py
```bash
python main.py
```

## 📖 软件使用

1. **申请APIKEY**  
   - 目前大模型仅支持通义千问，需先申请一个API KEY。

2. **配置APIKEY**  
   - 将申请好的API KEY放入`config.yaml`文件中，或在软件的“工具-AI配置”中进行设置。

3. **运行调试**  
   - 设置完成后，可使用“运行调试”功能进行直播间布置及其他操作。  
   - 注意：需先开启“互动”功能，否则无法调试。

4. **使用直播间功能**  
   - 完成直播间布置后，输入直播间地址后点击抓取弹幕即可开始使用。


## ⚖️ 免责声明

* 软件主要以科研为目的，禁止用于任何形式的直接或间接的商业用途，包括但不限于付费帮录制、付费定制改版软件、付费分发本软件或本软件的改版、直接以本软件作为付费爬虫课程的案例等
* 禁止非法修改，包括但不限于往软件中植入病毒木马、非法获取用户隐私等
* 禁止非法使用，包括但不限于未经主播本人同意非法录制和上传直播录像、用于非法监控他人、大量录制给抖音服务器造成压力等
* 任何非法修改与非法使用等均与软件作者本人无关，由非法修改者或非法使用者负责

## 🙏 参考的开源项目

* https://github.com/saermart/DouyinLiveWebFetcher
* https://github.com/pixiv/three-vrm
