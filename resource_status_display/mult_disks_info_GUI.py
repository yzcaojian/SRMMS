from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, \
    QMessageBox

from resource_status_display.backward_thread import UpdateLogThread
from resource_status_display.configuration_GUI import ConfigurationWidget
from resource_status_display.get_info_item import get_warning_info_item, get_scheduling_info_item
from resource_status_display.log_exception_with_suggestions import warning_list, scheduling_list
from resource_status_display.tab_GUI import MultDisksInfoTabWidget
from interface.in_interface import in_interface_impl

"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: 多硬盘架构下的服务器总体和详细信息显示界面
@Time : 2021/4/30 15:25
@Author : cao jian
"""


class MultDisksInfoWidget(QWidget):
    def __init__(self, lock, lock_log):
        super().__init__()
        self.configuration = None  # 配置界面
        self.whole_layout = QHBoxLayout()  # 总体布局
        self.lock = lock
        self.lock_log = lock_log
        self.tab_widget = MultDisksInfoTabWidget(lock)  # 定义一个Tab类窗口
        self.text_info_widget = QWidget()  # 定义一个日志信息显示窗口
        self.warning_list = list(reversed(warning_list.warning_list))  # 告警信息列表
        self.scheduling_list = list(reversed(scheduling_list.scheduling_list))  # 调度分配日志信息列表
        self.warning_list_current_len = len(self.warning_list)
        self.scheduling_list_current_len = len(self.scheduling_list)
        self.warning_update = False
        self.scheduling_update = False
        self.disk_failure_message = in_interface_impl.hard_disk_failure_prediction_list_
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)  # 设置窗口始终在前
        self.update_log_thread = UpdateLogThread(self.lock_log)
        self.initUI()

    def initUI(self):
        # 按钮、告警信息和日志信息布局
        text_info_layout = QVBoxLayout()

        # 刷新按钮和配置按钮布局
        button_widget = QWidget()
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
        update_button.setStyleSheet("background-color: rgb(0, 0, 0, 0)")
        # 绑定事件
        update_button.clicked.connect(lambda: self.update_())
        # 配置按钮
        configuration_button = QPushButton()
        configuration_button.setToolTip('配置')
        configuration_button.setFixedSize(30, 30)
        configuration_button_icon = QIcon()
        configuration_button_icon.addPixmap(QPixmap('./resources/png/configuration.png'), QIcon.Normal, QIcon.Off)
        configuration_button.setIcon(configuration_button_icon)
        configuration_button.setIconSize(QSize(25, 25))
        configuration_button.setStyleSheet("background-color: rgb(0, 0, 0, 0)")
        # 绑定事件
        configuration_button.clicked.connect(lambda: self.show_configuration_GUI())
        # 按钮布局添加按钮部件
        button_layout.addWidget(update_button, alignment=Qt.AlignRight)
        button_layout.addWidget(configuration_button)  # 两个控件中只写一个Alignment就可以紧挨着了
        button_widget.setLayout(button_layout)

        # 告警信息
        warning_label = QLabel('''<font color=#def6fe face='黑体' size=5>告警信息<font>''')
        warning_label.setStyleSheet("height:40px;")
        # 告警信息， 以list呈现
        warning_widget = QListWidget()
        warning_widget.setStyleSheet("QListWidget{background-color:transparent; border:1px solid #7efaff;}"
                                     "QListWidget::item:hover{background-color: #839B97}")

        # warning_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 将竖直的滑动条隐藏，避免遮挡内容

        # 定义内部函数事件，初始化或者是有告警信号后，从warning_list中取数据放入warning_widget中去，刷新告警信息
        def show_warning_list(warningList):
            warning_widget.clear()  # 清空刷新前的所有项
            # 判断是否有新产生的告警信息
            if self.warning_update:
                item = QListWidgetItem()
                item.setSizeHint(QSize(280, 50))  # 必须设置Item大小，否则默认很小
                # item.setBackground(QColor(218, 255, 225, 155))

                update_click = QPushButton()
                update_click.setToolTip('刷新')
                update_click.setFixedSize(30, 30)
                update_icon = QIcon()
                update_icon.addPixmap(QPixmap('./resources/png/update.png'))
                update_click.setIcon(update_button_icon)
                update_click.setIconSize(QSize(25, 25))
                update_click.setStyleSheet("background-color:white")
                update_click.clicked.connect(lambda: update_warning())

                update_tip = QLabel("有" + str(len(warning_list.warning_list) - len(self.warning_list)) + "条告警信息更新")
                update_tip.setStyleSheet("font-size:14px; color:red; font-family:'黑体'")

                warning_item_layout = QHBoxLayout()
                warning_item_layout.addWidget(update_click, alignment=Qt.AlignTop)
                warning_item_layout.addWidget(update_tip, alignment=Qt.AlignLeft)
                warning_item = QWidget()
                warning_item.setLayout(warning_item_layout)
                warning_widget.addItem(item)
                warning_widget.setItemWidget(item, warning_item)

            for warning in warningList:
                item = QListWidgetItem()
                # item.setFlags(Qt.NoItemFlags)  # 设置条目不可选中不可编辑
                item.setSizeHint(QSize(260, 120))  # 必须设置Item大小，否则默认很小
                # 添加告警信息条目
                warning_item = get_warning_info_item(warning)
                warning_widget.addItem(item)
                warning_widget.setItemWidget(item, warning_item)

        show_warning_list(self.warning_list)

        # 日志信息
        log_label = QLabel('''<font color=#def6fe face='黑体' size=5>日志信息<font>''')
        log_label.setStyleSheet("height:40px;")
        # 日志信息，以list呈现
        log_widget = QListWidget()
        log_widget.setStyleSheet("QListWidget{background-color:transparent; border:1px solid #7efaff;}"
                                 "QListWidget::item:hover{background-color: #839B97}")
        # log_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 将竖直的滑动条隐藏，避免遮挡内容
        log_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 将水平的滑动条隐藏，避免遮挡内容
        # 定位当前选中的item行，双击显示详细信息
        log_widget.itemDoubleClicked.connect(lambda: self.display_detailed_log_info(log_widget.selectedIndexes()))

        # 定义内部函数事件，初始化或者是有调度信号后，从scheduling_list中取数据放入log_widget中去，刷新调度分配日志信息
        def show_scheduling_list(schedulingList):
            log_widget.clear()  # 清空刷新前的所有项
            # 判断是否有新产生的日志信息
            if self.scheduling_update:
                item = QListWidgetItem()
                item.setSizeHint(QSize(280, 50))  # 必须设置Item大小，否则默认很小
                # item.setBackground(QColor(218, 255, 225, 155))

                update_click = QPushButton()
                update_click.setToolTip('刷新')
                update_click.setFixedSize(30, 30)
                update_icon = QIcon()
                update_icon.addPixmap(QPixmap('./resources/png/update.png'))
                update_click.setIcon(update_button_icon)
                update_click.setIconSize(QSize(25, 25))
                update_click.setStyleSheet("background-color:rbg(0, 0, 0, 0)")
                update_click.clicked.connect(lambda: update_scheduling())

                update_tip = QLabel(
                    "有" + str(len(scheduling_list.scheduling_list) - len(self.scheduling_list)) + "条告警信息更新")
                update_tip.setStyleSheet("font-size:14px; color:red; font-family:'黑体'")

                scheduling_item_layout = QHBoxLayout()
                scheduling_item_layout.addWidget(update_click, alignment=Qt.AlignTop)
                scheduling_item_layout.addWidget(update_tip, alignment=Qt.AlignLeft)
                scheduling_item = QWidget()
                scheduling_item.setLayout(scheduling_item_layout)
                log_widget.addItem(item)
                log_widget.setItemWidget(item, scheduling_item)

            for scheduling in schedulingList:
                item = QListWidgetItem()
                # item.setFlags(Qt.NoItemFlags)  # 设置条目不可选中不可编辑
                item.setSizeHint(QSize(280, 100))  # 必须设置Item大小，否则默认很小
                # 添加告警信息条目
                scheduling_item = get_scheduling_info_item(scheduling)
                log_widget.addItem(item)
                log_widget.setItemWidget(item, scheduling_item)

        show_scheduling_list(self.scheduling_list)

        # 告警信息和日志信息布局管理
        text_info_layout.addWidget(button_widget)
        text_info_layout.addWidget(warning_label)
        text_info_layout.addWidget(warning_widget)
        text_info_layout.addWidget(log_label)
        text_info_layout.addWidget(log_widget)
        text_info_layout.setContentsMargins(0, 0, 0, 0)  # 设置内部窗体上下左右空隙为0，和tab页对齐
        self.text_info_widget.setLayout(text_info_layout)
        self.text_info_widget.setFixedWidth(300)  # 设置了固定长度300
        # print("size", self.size())

        # tab页与按钮和告警日志信息的布局
        self.whole_layout.setContentsMargins(10, 0, 10, 10)
        self.tab_widget.setStyleSheet("QTabWidget:pane{border: 1px solid black; top: -2px; background-color: white}\
                        QTabBar::tab{height:34px; width:250px; margin-right:1px; font-size:20px; border-radius: 4px;}\
                        QTabBar::tab:selected{border:2px solid #7efaff; border-bottom-color:#7efaff; bottom:-2px; border-bottom-width: 4px; background:#0c1949; color:white}\
                        QTabBar::tab:!selected{background:#0c1949; color:white}")  # border:2px solid #5089C6
        self.whole_layout.addWidget(self.tab_widget)
        self.whole_layout.addWidget(self.text_info_widget)
        self.setLayout(self.whole_layout)

        self.update_log_thread.update_data.connect(lambda: update_log())
        self.update_log_thread.update_data.connect(lambda: pop_up_window())
        self.update_log_thread.start()

        def update_log():
            if self.warning_list_current_len != len(warning_list.warning_list):
                self.warning_update = True
                show_warning_list(self.warning_list)
                self.warning_list_current_len = len(warning_list.warning_list)

            if self.scheduling_list_current_len != len(scheduling_list.scheduling_list):
                self.scheduling_update = True
                show_scheduling_list(self.scheduling_list)
                self.scheduling_list_current_len = len(scheduling_list.scheduling_list)

        def update_warning():
            self.warning_update = False
            self.warning_list = list(reversed(warning_list.warning_list))
            show_warning_list(self.warning_list)

        def update_scheduling():
            self.scheduling_update = False
            self.scheduling_list = list(reversed(scheduling_list.scheduling_list))
            show_scheduling_list(self.scheduling_list)

        def pop_up_window():
            # 当出现对硬盘故障预警的情况时弹窗告警
            if len(self.disk_failure_message) != 0:
                server_ip = self.disk_failure_message[0][0]
                disk_id = self.disk_failure_message[0][1]
                health_state = self.disk_failure_message[0][2][0]
                del self.disk_failure_message[0:1]
                liftime = [10, 30, 70, 150, 310, 360, 2, 5, 10]
                QMessageBox.warning(self, "警告", "服务器" + server_ip + "上机械硬盘" + disk_id + "预计健康度为R" +
                                    str(health_state) + "，剩余寿命在" + str(liftime[health_state - 1]) + "天以下",
                                    QMessageBox.Ok)

    def display_detailed_log_info(self, index):
        QMessageBox.information(self, "全部", self.scheduling_list[index[0].row()])

    def update_(self):
        self.tab_widget.setParent(None)
        self.text_info_widget.setParent(None)
        # for key in self.tab_widget.tab_update_thread:
        #     self.tab_widget.tab_update_thread[key].close_thread()

        for item in self.tab_widget.Tab_list:  # 关闭Tab页线程
            item.update_thread.close_thread()
        self.tab_widget.update_thread.close_thread()  # 关闭总体信息的线程
        self.update_log_thread.close_thread()

        self.tab_widget = MultDisksInfoTabWidget(self.lock)
        self.update_log_thread = UpdateLogThread(self.lock_log)
        self.text_info_widget = QWidget()
        self.initUI()

    def show_configuration_GUI(self):
        self.configuration = ConfigurationWidget(self.lock)
