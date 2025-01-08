# -*- coding: utf-8 -*-
# 设置窗口
import sys
import requests
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QLabel, QPlainTextEdit,
                             QPushButton, QMessageBox, QToolButton, QHBoxLayout)
from PyQt6.QtCore import QRegularExpression,Qt
from PyQt6.QtGui import QPixmap, QFont, QAction, QColor, QPainter, QPainterPath, QIcon,QTextCharFormat,QSyntaxHighlighter
import yaml
import json



class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # 关键字高亮
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(136, 19, 145))  # 紫色
        keywords = ["true", "false", "null"]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # 字符串高亮
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(42, 161, 152))  # 青色
        pattern = QRegularExpression("\".*\"")
        self.highlighting_rules.append((pattern, string_format))

        # 数字高亮
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(211, 54, 130))  # 粉红色
        pattern = QRegularExpression("\\b\\d+\\b")
        self.highlighting_rules.append((pattern, number_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

# 设置窗口
class SettingWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.config_file = 'config.yaml'  # 系统配置
        self.json_config_file = 'config.json'  # 事件配置
        self.sys_prompt = 'sys_prompt.txt'  # 虚拟人设

        self.initUI()
        self.load_initial_values()

    def initUI(self):
        # 设置窗口标题和尺寸
        self.setWindowTitle('一些配置')
        self.setGeometry(0, 0, 800, 800)
        self.setFixedSize(800, 600)
        # 创建垂直布局
        layout = QVBoxLayout()

        # 第一行 - API Key 输入框
        api_key_label = QLabel('通义千问 API KEY:', self)
        api_key_label.setStyleSheet("""
                  QLabel {
                      color: #2c3e50;
                      font-size: 14px;
                      font-weight: bold;
                      margin-bottom: 5px;
                  }
              """)
        layout.addWidget(api_key_label)
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setPlaceholderText('请输入您的 API KEY')
        layout.addWidget(self.api_key_input)

        # # 第二行 - JSON 礼物对应文本框
        # json_gifts_layout = QHBoxLayout()  # 新建水平布局用于放置标签和按钮
        # json_gifts_label = QLabel('系统设置及礼物对照（JSON）:', self)
        # json_gifts_label.setStyleSheet("""
        #            QLabel {
        #                color: #2c3e50;
        #                font-size: 14px;
        #                font-weight: bold;
        #            }
        #        """)
        #
        # json_gifts_layout.addWidget(json_gifts_label)

        # # 添加重置按钮
        # reset_button = QToolButton(self)
        # reset_button.setIcon(QIcon('assets/imgs/reset_icon.png'))  # 确保你有一个名为 reset_icon.png 的图标文件
        # reset_button.setToolTip('恢复默认 JSON')
        # reset_button.setStyleSheet("""
        #           QToolButton {
        #               border: none;
        #               padding: 5px;
        #               border-radius: 4px;
        #               background-color: transparent;
        #           }
        #           QToolButton:hover {
        #               background-color: #e0e0e0;
        #           }
        #       """)
        #
        # reset_button.clicked.connect(self.reset_json_editor)
        # json_gifts_layout.addWidget(reset_button)
        #
        # layout.addLayout(json_gifts_layout)  # 将水平布局添加到主布局中

        # self.json_gifts_editor = QPlainTextEdit(self)
        # self.json_gifts_editor.setPlaceholderText('请输入或修改礼物对应的 JSON 内容')
        # self.json_gifts_editor.setFont(QFont('微软雅黑', 10))  # 设置等宽字体方便阅读 JSON
        #
        # # 设置语法高亮
        # self.json_gifts_editor.highlighter = JsonHighlighter(self.json_gifts_editor.document())
        #
        #
        # layout.addWidget(self.json_gifts_editor)

        # 第三行 - 人设文本框
        knowledge_base_label = QLabel('AI 人设（最多 2000 字）:', self)
        knowledge_base_label.setStyleSheet("""
                   QLabel {
                       color: #2c3e50;
                       font-size: 14px;
                       font-weight: bold;
                       margin-top: 10px;
                   }
               """)
        layout.addWidget(knowledge_base_label)
        self.sys_prompt_editor = QTextEdit(self)
        self.sys_prompt_editor.setPlaceholderText(
            '在此处输入"人设与回复逻辑"内容，最多 2000 字,示例：你是一个热情的主播，正在直播间与观众互动。')
        self.sys_prompt_editor.textChanged.connect(self.limit_text_length)
        layout.addWidget(self.sys_prompt_editor)

        # 添加保存按钮
        save_button = QPushButton('保存配置', self)
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)

        # 设置扁平化样式
        self.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                }
                QLineEdit, QPlainTextEdit, QTextEdit, QPushButton {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 5px;
                    background-color: #fff;
                }
                QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QPushButton:hover {
                    border-color: #007BFF;
                }
                   QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
            QPlainTextEdit, QTextEdit {
                min-height: 150px;
            }
            """)

        # 应用布局
        self.setLayout(layout)

    # 恢复到初始配置
#     def reset_json_editor(self):
#         # 定义默认的 JSON 内容
#         default_json = '''{
#     "config_name": "全局配置|右侧刷新按钮可以恢复设置",
#     "game_event": [{
#         "name": "触发比心动作",
#         "trigger": {
#             "type": 1,
#             "text": "小心心"
#         },
#         "action": {
#             "type": 4,
#             "config": {
#                 "method": "post",
#                 "url": "http://localhost:8888/executeCommand",
#                 "payload": {
#                     "command": "event",
#                     "content": "比心"
#                 }
#             }
#         }
#     }, {
#         "name": "触发转身动作",
#         "trigger": {
#             "type": 1,
#             "text": "棒棒糖"
#         },
#         "action": {
#             "type": 4,
#             "config": {
#                 "method": "post",
#                 "url": "http://localhost:8888/executeCommand",
#                 "payload": {
#                     "command": "event",
#                     "content": "转个身"
#                 }
#             }
#         }
#     }, {
#         "name": "触发卖萌动作",
#         "trigger": {
#             "type": 1,
#             "text": "大啤酒"
#         },
#         "action": {
#             "type": 4,
#             "config": {
#                 "method": "post",
#                 "url": "http://localhost:8888/executeCommand",
#                 "payload": {
#                     "command": "event",
#                     "content": "卖萌打招呼"
#                 }
#             }
#         }
#     }]
# }'''
#         self.json_gifts_editor.setPlainText(default_json)

    def load_initial_values(self):
        # 加载 API Key
        with open(self.config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            self.api_key_input.setText(config.get('qwen_api_key', ''))

        # 加载 JSON 配置
        # try:
        #     with open(self.json_config_file, 'r', encoding='utf-8') as file:
        #         json_data = json.load(file)
        #         self.json_gifts_editor.setPlainText(json.dumps(json_data, indent=4, ensure_ascii=False))
        # except FileNotFoundError:
        #     pass  # 如果文件不存在，则保持默认值

        # 加载知识库内容
        try:
            with open(self.sys_prompt, 'r', encoding='utf-8') as file:
                self.sys_prompt_editor.setPlainText(file.read())
        except FileNotFoundError:
            pass  # 如果文件不存在，则保持默认值

    def save_changes(self):
        try:
            # 保存 API Key
            with open(self.config_file, 'w') as file:
                yaml.dump({'qwen_api_key': self.api_key_input.text()}, file, default_flow_style=False)

            # # 保存 JSON 配置
            # json_data = json.loads(self.json_gifts_editor.toPlainText())
            # with open(self.json_config_file, 'w', encoding='utf-8') as file:
            #     json.dump(json_data, file, indent=4, ensure_ascii=False)

            # 保存人设内容
            with open(self.sys_prompt, 'w', encoding='utf-8') as file:
                file.write(self.sys_prompt_editor.toPlainText())

            # 显示保存成功的消息框
            QMessageBox.information(self, '保存成功', '所有更改已成功保存！')

        except json.JSONDecodeError:
            # 如果 JSON 格式不正确，显示错误消息框
            QMessageBox.critical(self, '保存失败', 'JSON 数据格式不正确，无法保存。请检查您的输入。')
        except Exception as e:
            # 捕获其他可能的异常，并显示相应的错误消息框
            QMessageBox.critical(self, '保存失败', f'发生了一个错误: {str(e)}')

    def limit_text_length(self):
        # 限制知识库文本框的内容长度不超过 2000 字
        text = self.sys_prompt_editor.toPlainText()
        if len(text) > 2000:
            self.sys_prompt_editor.setText(text[:2000])
            cursor = self.sys_prompt_editor.textCursor()
            cursor.setPosition(2000)
            self.sys_prompt_editor.setTextCursor(cursor)


def main():
    app = QApplication(sys.argv)
    ex = SettingWindow()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
