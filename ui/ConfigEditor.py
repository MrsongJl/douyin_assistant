import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QComboBox, QScrollArea, QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

DEFAULT_CONFIG = {
    "config_name": "全局配置",
    "game_event": [{
        "name": "触发比心动作",
        "trigger": {
            "type": 1,
            "text": "小心心"
        },
        "action": {
            "type": 4,
            "config": {
                "method": "post",
                "url": "http://localhost:8888/executeCommand",
                "payload": {
                    "command": "event",
                    "content": "比心"
                }
            }
        }
    }, {
        "name": "触发转身动作",
        "trigger": {
            "type": 1,
            "text": "棒棒糖"
        },
        "action": {
            "type": 4,
            "config": {
                "method": "post",
                "url": "http://localhost:8888/executeCommand",
                "payload": {
                    "command": "event",
                    "content": "转个身"
                }
            }
        }
    }, {
        "name": "触发卖萌动作",
        "trigger": {
            "type": 1,
            "text": "大啤酒"
        },
        "action": {
            "type": 4,
            "config": {
                "method": "post",
                "url": "http://localhost:8888/executeCommand",
                "payload": {
                    "command": "event",
                    "content": "卖萌打招呼"
                }
            }
        }
    }]
}


class FlatStyle:
    """扁平化样式类"""
    MAIN_COLOR = "#2196F3"  # Material Blue
    SECONDARY_COLOR = "#64B5F6"  # Lighter Blue
    BACKGROUND_COLOR = "#FFFFFF"  # White
    TEXT_COLOR = "#333333"  # Dark Gray
    BORDER_RADIUS = "4px"

    @staticmethod
    def get_stylesheet():
        return """
            QMainWindow {
                background-color: #F5F5F5;
            }

            QGroupBox {
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                margin-top: 12px;
                background-color: white;
                padding: 15px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #424242;
            }

            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                selection-background-color: #2196F3;
                height: 24px;
            }

            QLineEdit:focus {
                border: 2px solid #2196F3;
            }

            QComboBox {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                height: 24px;
            }

            QComboBox:drop-down {
                border: none;
                padding: 0px 5px;
            }

            QComboBox:down-arrow {
                image: none;
                border-left: 2px solid #606060;
                border-bottom: 2px solid #606060;
                width: 8px;
                height: 8px;
                transform: rotate(-45deg);
            }

            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
                height: 24px;
            }

            QPushButton:hover {
                background-color: #1976D2;
            }

            QPushButton:pressed {
                background-color: #0D47A1;
            }

            QPushButton[text="删除事件"] {
                background-color: #F44336;
            }

            QPushButton[text="删除事件"]:hover {
                background-color: #D32F2F;
            }

            QScrollArea {
                border: none;
                background-color: transparent;
            }

            QLabel {
                color: #424242;
                padding: 5px;
            }

            QMessageBox {
                background-color: white;
            }

            QMessageBox QPushButton {
                min-width: 60px;
                min-height: 23px;
            }
        """


class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        # 忽略滚轮事件
        event.ignore()


class ConfigEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("礼物配置")
        self.setMinimumSize(800, 600)
        # 设置应用图标
        app_icon = QIcon("./assets/imgs/TikTok-logo-CMYK-Stacked-black.png")  # 替换为你的图标文件路径
        self.setWindowIcon(app_icon)

        # 应用扁平化样式
        self.setStyleSheet(FlatStyle.get_stylesheet())

        # 设置字体
        app = QApplication.instance()
        app.setFont(QFont("Microsoft YaHei UI", 9))

        # 主控件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 带有样式化容器的配置名称部分
        config_container = QGroupBox("基础配置")
        config_layout = QHBoxLayout(config_container)
        config_label = QLabel("配置名称:")
        self.config_name_edit = QLineEdit()
        config_layout.addWidget(config_label)
        config_layout.addWidget(self.config_name_edit)
        main_layout.addWidget(config_container)

        # 事件标签
        events_label = QLabel("事件列表")
        events_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #424242;")
        main_layout.addWidget(events_label)

        # 游戏事件滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.events_widget = QWidget()
        self.events_layout = QVBoxLayout(self.events_widget)
        self.events_layout.setSpacing(10)
        scroll.setWidget(self.events_widget)
        main_layout.addWidget(scroll)

        # 布局按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        add_button = QPushButton("添加事件")
        save_button = QPushButton("保存配置")
        restore_button = QPushButton("恢复默认")

        button_layout.addStretch()

        button_layout.addWidget(restore_button)
        button_layout.addWidget(add_button)
        button_layout.addWidget(save_button)

        add_button.clicked.connect(self.add_event_group)
        save_button.clicked.connect(self.save_config)
        restore_button.clicked.connect(self.restore_default_config)

        main_layout.addLayout(button_layout)

        # 序列化配置
        self.initialize_config()

    def restore_default_config(self):
        """恢复默认配置"""
        reply = QMessageBox.question(self, '恢复默认', '确定要恢复默认配置吗？这将丢失所有当前配置。',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.load_config(DEFAULT_CONFIG)
            QMessageBox.information(self, "成功", "已恢复默认配置")

    def initialize_config(self):
        """首次加载时 默认配置"""
        config_path = 'default_config.json'

        try:
            # 验证是否存在
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                # 不存在 使用默认
                config = DEFAULT_CONFIG
                # Save default configuration
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)

            # 加载配置到UI
            self.load_config(config)

        except Exception as e:
            QMessageBox.warning(self, "初始化警告", f"加载配置文件时出错: {str(e)}\n将使用默认配置。")
            self.load_config(DEFAULT_CONFIG)

    def initialize_config(self):
        """首次加载时 默认配置"""
        config_path = 'config.json'

        try:
            # 验证是否存在
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                # 不存在 使用默认
                config = DEFAULT_CONFIG
                # Save default configuration
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)

            # 加载配置到UI
            self.load_config(config)

        except Exception as e:
            QMessageBox.warning(self, "初始化警告", f"加载配置文件时出错: {str(e)}\n将使用默认配置。")
            self.load_config(DEFAULT_CONFIG)

    def load_config(self, config):
        """加载配置映射组件"""
        # 清除 events_layout的所有控件
        while self.events_layout.count():
            item = self.events_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Set config name
        self.config_name_edit.setText(config["config_name"])

        # Add each event
        for event in config["game_event"]:
            self.add_event_group(event)

    # 创建游戏事件内容
    def create_event_group(self, event_data=None):
        group = QGroupBox("游戏事件")
        layout = QVBoxLayout()

        # Name
        name_layout = QHBoxLayout()
        name_label = QLabel("事件名称:")
        name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)

        # Trigger
        trigger_layout = QHBoxLayout()
        trigger_label = QLabel("触发类型:")
        trigger_type = QComboBox()
        trigger_type.addItem("礼物触发", 1)

        trigger_text_label = QLabel("触发文本（礼物名）:")
        trigger_text = QLineEdit()
        trigger_layout.addWidget(trigger_label)
        trigger_layout.addWidget(trigger_type)
        trigger_layout.addWidget(trigger_text_label)
        trigger_layout.addWidget(trigger_text)
        layout.addLayout(trigger_layout)

        # Action
        action_layout = QHBoxLayout()
        action_label = QLabel("动作类型:")
        action_type = NoWheelComboBox()
        action_type.addItem("接口触发", 4)
        action_layout.addWidget(action_label)
        action_layout.addWidget(action_type)
        layout.addLayout(action_layout)

        # Command
        command_layout = QHBoxLayout()
        command_label = QLabel("命令类型:")
        command_type = NoWheelComboBox()
        command_type.addItems(["event"])
        command_layout.addWidget(command_label)
        command_layout.addWidget(command_type)
        layout.addLayout(command_layout)

        # Content
        content_layout = QHBoxLayout()
        content_label = QLabel("动作内容:")
        content_type = NoWheelComboBox()
        content_type.addItems(["比心", "转个身", "卖萌打招呼", "biubiu", "我来了", "比耶"])
        content_layout.addWidget(content_label)
        content_layout.addWidget(content_type)
        layout.addLayout(content_layout)

        # Delete button
        delete_button = QPushButton("删除事件")
        delete_button.clicked.connect(lambda: self.delete_event_group(group))
        layout.addWidget(delete_button)

        group.setLayout(layout)

        # 填写数据
        if event_data:
            name_edit.setText(event_data["name"])
            # trigger_type.setCurrentIndex(event_data["trigger"]["type"])
            trigger_type_index = trigger_type.findData(event_data["trigger"]["type"])
            trigger_type.setCurrentIndex(trigger_type_index)

            trigger_text.setText(event_data["trigger"]["text"])
            # action_type.setCurrentIndex(event_data["action"]["type"])
            action_type_index = action_type.findData(event_data["action"]["type"])
            action_type.setCurrentIndex(action_type_index)

            if "config" in event_data["action"]:
                command_type.setCurrentText(event_data["action"]["config"]["payload"]["command"])
                content_type.setCurrentText(event_data["action"]["config"]["payload"]["content"])

        return group, {
            "name_edit": name_edit,
            "trigger_type": trigger_type,
            "trigger_text": trigger_text,
            "action_type": action_type,
            "command_type": command_type,
            "content_type": content_type
        }

    # 添加游戏事件
    def add_event_group(self, event_data=None):
        group, _ = self.create_event_group(event_data)
        self.events_layout.addWidget(group)

    # 删除事件分组
    def delete_event_group(self, group):
        group.deleteLater()

    # 全局保存
    def save_config(self):
        config = {
            "config_name": self.config_name_edit.text(),
            "game_event": []
        }

        for i in range(self.events_layout.count()):
            group = self.events_layout.itemAt(i).widget()
            if not isinstance(group, QGroupBox):
                continue

            layout = group.layout()

            # 部件中提取内容
            name = layout.itemAt(0).layout().itemAt(1).widget().text()
            # trigger_type = layout.itemAt(1).layout().itemAt(1).widget().currentIndex()
            trigger_type = layout.itemAt(1).layout().itemAt(1).widget().currentData()
            trigger_text = layout.itemAt(1).layout().itemAt(3).widget().text()
            # action_type = layout.itemAt(2).layout().itemAt(1).widget().currentIndex()
            action_type = layout.itemAt(2).layout().itemAt(1).widget().currentData()
            command = layout.itemAt(3).layout().itemAt(1).widget().currentText()
            content = layout.itemAt(4).layout().itemAt(1).widget().currentText()

            event = {
                "name": name,
                "trigger": {
                    "type": trigger_type,
                    "text": trigger_text
                },
                "action": {
                    "type": action_type,
                    "config": {
                        "method": "post",
                        "url": "http://localhost:8888/executeCommand",
                        "payload": {
                            "command": command,
                            "content": content
                        }
                    }
                }
            }

            config["game_event"].append(event)

        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "成功", "配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")


def main():
    app = QApplication(sys.argv)

    # 设置应用程序级别的调色板
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#F5F5F5"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#424242"))
    app.setPalette(palette)

    window = ConfigEditor()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
