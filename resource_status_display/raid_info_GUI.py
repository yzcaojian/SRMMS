from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from resource_status_display.configuration_GUI import ConfigurationWidget
from resource_status_display.tab_GUI import RaidInfoTabWidget


"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: RAID架构下的服务器总体详细信息显示界面
@Time : 2021/5/11 20:38
@Author : cao jian
"""


class RAIDInfoWidget(QWidget):
    def __init__(self, lock):
        super().__init__()
        self.configuration = None  # 配置界面
        self.whole_layout = QVBoxLayout()  # 总体布局
        self.button_widget = QWidget()
        self.lock = lock
        self.tab_widget = RaidInfoTabWidget(lock)  # 定义一个Tab类窗口
        self.initUI()

    def initUI(self):
        # 刷新按钮和配置按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        # 刷新按钮
        update_button = QPushButton()
        update_button.setToolTip('刷新')
        update_button.setFixedSize(30, 30)
        update_button_icon = QIcon()
        update_button_icon.addPixmap(QPixmap('./resources/png/update.png'), QIcon.Normal, QIcon.Off)
        update_button.setIcon(update_button_icon)
        update_button.setIconSize(QSize(25, 25))
        update_button.setStyleSheet("background-color:transparent")
        # 绑定事件
        update_button.clicked.connect(lambda: self.update_(self.lock))
        # 配置按钮
        configuration_button = QPushButton()
        configuration_button.setToolTip('配置')
        configuration_button.setFixedSize(30, 30)
        configuration_button_icon = QIcon()
        configuration_button_icon.addPixmap(QPixmap('./resources/png/configuration.png'), QIcon.Normal, QIcon.Off)
        configuration_button.setIcon(configuration_button_icon)
        configuration_button.setIconSize(QSize(25, 25))
        configuration_button.setStyleSheet("background-color:transparent")
        # 绑定事件
        configuration_button.clicked.connect(lambda: self.show_configuration_GUI())
        # 按钮布局添加按钮部件
        button_layout.addWidget(update_button, alignment=Qt.AlignRight)
        button_layout.addWidget(configuration_button)  # 两个控件中只写一个Alignment就可以紧挨着了
        self.button_widget.setLayout(button_layout)
        self.button_widget.setContentsMargins(0, 0, 10, 0)

        self.whole_layout.addWidget(self.button_widget)
        self.whole_layout.addWidget(self.tab_widget)
        self.setLayout(self.whole_layout)
        self.setWindowOpacity(0.1)

    def update_(self, lock):
        self.tab_widget.setParent(None)
        self.button_widget.setParent(None)
        self.tab_widget.update_thread.close_thread()  # 关闭线程
        self.tab_widget = RaidInfoTabWidget(lock)
        self.button_widget = QWidget()
        self.initUI()

    def show_configuration_GUI(self):
        if not self.configuration:
            self.configuration = ConfigurationWidget(self.lock)
        else:
            if self.configuration.isVisible():
                self.configuration.raise_()
            else:
                self.configuration.show()



