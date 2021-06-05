import sys
import time

from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QMainWindow

from resource_status_display.mult_disks_info_GUI import MultDisksInfoWidget
from resource_status_display.raid_info_GUI import RAIDInfoWidget

"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: 主程序
@Time : 2021/4/28 10:48
@Author : cao jian
"""


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.title_widget = QWidget() # 标题
        self.mult_disks_info_widget = MultDisksInfoWidget()  # 多硬盘架构下监控界面
        self.raid_info_widget = RAIDInfoWidget()  # RAID架构下监控界面
        self.whole_layout = QVBoxLayout()

        self.setGeometry(100, 100, 1700, 900)  # 坐标，宽高
        self.setWindowTitle("存储资源监控管理系统")
        self.setObjectName('MultDisksInfoWidget')
        self.setWindowIcon(QIcon('./png/software.png'))  # 设置窗体图标
        self.setStyleSheet("#MultDisksInfoWidget{background-color:#cccccc}")  # 设置背景颜色

        self.initUI("192.168.1.1")
        # 全局布局
        # whole_layout = QVBoxLayout()
        self.whole_layout.setContentsMargins(0, 0, 0, 10)
        self.whole_layout.addWidget(self.title_widget)
        self.whole_layout.addWidget(self.mult_disks_info_widget)
        self.setLayout(self.whole_layout)
        self.show()

    def initUI(self, server_ip):
        print(server_ip)

        # 标题
        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_label = QLabel('''<font color=black face='黑体' size=8>存储资源监控管理系统<font>''')
        # title_label.setContentsMargins(0, 16, 0, 0)
        title_label.setAlignment(Qt.AlignCenter)  # 文本居中
        switch_button = QPushButton()
        switch_button.setFixedSize(40, 40)
        switch_button_icon = QIcon('./png/switch.png')
        switch_button.setIcon(switch_button_icon)
        switch_button.setIconSize(QSize(35, 35))
        # switch_button.setContentsMargins(0, 30, 0, 0)
        switch_button.setStyleSheet("QPushButton{background-color:#cccccc; border: none} "
                                    "QPushButton:pressed{background-color:#aaaaaa}")
        # 将文本和切换按钮共同居中
        title = QHBoxLayout()
        title_w = QWidget()
        title.addWidget(title_label, alignment=Qt.AlignRight)
        title.addWidget(switch_button, alignment=Qt.AlignLeft)
        title_w.setLayout(title)
        title_layout.addWidget(title_w, alignment=Qt.AlignCenter)
        title_widget.setLayout(title_layout)

        switch_button.clicked.connect(lambda: self.switch_UI())

        self.title_widget = title_widget

    def switch_UI(self):
        if self.whole_layout.itemAt(1).widget() == self.mult_disks_info_widget:
            self.mult_disks_info_widget.setParent(None)  # 清除多硬盘监控界面
            self.whole_layout.addWidget(self.raid_info_widget)
        else:
            self.raid_info_widget.setParent(None)  # 清除RAID监控界面
            self.whole_layout.addWidget(self.mult_disks_info_widget)

    # # 当出现对硬盘故障预警的情况时弹窗告警
    # def show_disk_error_warning(self):
    #     QMessageBox.warning(self, "警告", "服务器<‘192.168.1.1’, server1>上机械硬盘<hdd-01>预计健康度为R4，剩余寿命在150天以下", QMessageBox.Ok)


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.main_ui = MainWidget()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())
