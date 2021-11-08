import locale
import re
import time

from interface.in_interface import in_interface_impl
from resource_status_display.configuration_checking import configuration_info
from resource_status_display.get_info_item import get_ServerInfo_Item, get_execution_state_item
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QApplication, QMainWindow, QComboBox, \
    QPushButton, QLineEdit, QTextBrowser, QListView, QListWidget, QListWidgetItem, QMessageBox

"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: 系统配置界面
@Time : 2021/4/26 14:55
@Author : cao jian
"""


class ConfigurationWidget(QWidget):

    def __init__(self, lock):
        super().__init__()
        self.lock = lock
        self.edit_state = 0  # 编辑状态，表示对输入框的编辑是都可以编辑还是存在限制，0表示无限制
        self.configuration_info = configuration_info  # 用于操作同步配置文件内容和server_info内容一致
        self.server_info = self.get_server_info()  # 维护服务器IP地址、名称和架构的信息
        self.events_info = []  # 维护所有服务型信息上的操作的历史结果
        self.initUI()

    def initUI(self):
        # self.setGeometry(200, 200, 1000, 500)  # 坐标，宽高
        self.setFixedSize(900, 600)
        self.setWindowTitle("系统配置")
        self.setObjectName('ConfigurationWidget')
        self.setWindowIcon(QIcon('./resource_status_display/png/configuration.png'))  # 设置窗体图标
        # self.setStyleSheet('#ConfigurationWidget{border-image:url(zuanshi.png);}')  # 设置背景图
        self.setStyleSheet("#ConfigurationWidget{background-color:#cccccc}")  # 设置背景颜色
        # 新建的窗口始终位于当前屏幕的最前面
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # 父类窗口不能点击
        # self.setWindowModality(Qt.ApplicationModal)

        # 全局布局
        whole_layout = QVBoxLayout(self)

        # 最顶端的文字：系统配置
        upper_title = QLabel('''<font color=black face='黑体' size=8>系 统 配 置<font>''')
        upper_title.setAlignment(Qt.AlignCenter)  # 文本居中

        # 显示已经连入的存储服务器部分
        # 内部再布局
        middle_layout = QVBoxLayout()
        # 内部标题
        middle_title_layout = QVBoxLayout()
        middle_title = QLabel('''<font color=black face='黑体' size=4>正在监控的存储服务器信息<font>''')
        middle_title.setAlignment(Qt.AlignLeft)  # 文本左对齐
        middle_title_layout.addWidget(middle_title)

        # 内部为一个listWidget，每行呈现两个server-info
        server_list = QListWidget()
        # server_list.setStyleSheet('{text-align:left; display:compact}')

        # 定义内部函数事件，初始化或者是按钮提交后，从server_info中取数据放入server_list中去，刷新服务器显示信息
        def show_server_info_list(server_info):
            server_list.clear()  # 清空刷新前所有项

            # 标头
            server_name = QLabel("服务器名称")
            server_name.setStyleSheet("font-size:20px; font-family:'黑体'; background-color:#eeeeee")
            server_IP = QLabel("IP地址")
            server_IP.setStyleSheet("font-size:20px; font-family:'黑体'; background-color:#eeeeee")
            server_type = QLabel("类型")
            server_type.setStyleSheet("font-size:20px; font-family:'黑体'; background-color:#eeeeee")
            head_layout = QHBoxLayout()
            head_layout.addWidget(server_name, alignment=Qt.AlignCenter)
            head_layout.addWidget(server_IP, alignment=Qt.AlignCenter)
            head_layout.addWidget(server_type, alignment=Qt.AlignCenter)
            head_widget = QWidget()
            head_widget.setLayout(head_layout)
            head_widget.setStyleSheet("background-color:#eeeeee")
            header_item = QListWidgetItem()
            header_item.setFlags(Qt.NoItemFlags)  # 设置条目不可选中不可编辑
            header_item.setSizeHint(QSize(200, 50))
            server_list.addItem(header_item)
            server_list.setItemWidget(header_item, head_widget)

            for (i, server_data) in enumerate(server_info):
                item = QListWidgetItem()
                item.setFlags(Qt.NoItemFlags)  # 设置条目不可选中不可编辑
                item.setSizeHint(QSize(200, 100))
                server_widget = get_ServerInfo_Item(server_data)
                server_list.addItem(item)
                server_list.setItemWidget(item, server_widget)

        show_server_info_list(self.server_info)

        # 加上标题再布局组合成为左边部分所有布局
        middle_layout.addWidget(middle_title)
        middle_layout.addWidget(server_list)
        middle_widget = QWidget()
        middle_widget.setLayout(middle_layout)

        # 显示筛选条件按钮、输入框之类的人机交互的控件，以及输出信息展示框
        down_layout = QVBoxLayout()
        # 第一行布局：下拉框和确认按钮
        condition_layout = QHBoxLayout()
        # 定义下拉框
        comb = QComboBox()
        comb.setFixedSize(120, 40)
        comb.addItems(['增加', '删除', '更改', '查询'])
        comb.setStyleSheet("QComboBox{height:40px; width:60px; font-size:20px}"
                           "QComboBox QAbstractItemView{border:1px solid black; height:160px; font-size:15px}"
                           "QListView::item{background:white; color:black}"
                           "QListView::item:selected{background:#000000; color:white}"
                           "QListView::item:hover{background:#999999; color:white}")
        comb.setView(QListView())
        # 绑定事件，通过下拉框选择限制输入框的编辑
        comb.currentIndexChanged.connect(lambda: comboBoxSelection(comb.currentIndex()))

        # 下拉框在选择查询和删除的条件下改变编辑状态
        def comboBoxSelection(index):
            if index == 1 or index == 3:
                # 只能可编辑某一行，IP地址或者是名称
                self.edit_state = 1
            else:
                self.edit_state = 0
            server_IP_input.setText("")
            server_name_input.setText("")
            server_name_input.setEnabled(True)
            server_IP_input.setEnabled(True)

        # 定义按钮
        button = QPushButton('确认')
        button.setFixedSize(80, 40)
        button.setStyleSheet('''QPushButton{height:40px; width:60px; background-color:white; border-width:2px; 
                                border-style:solid; border-color:black; border-radius:20px; font-size:20px}
                                QPushButton:pressed{background-color:#bbbbbb}''')

        # 下拉框与确认按钮的布局
        condition_layout.addWidget(comb, alignment=Qt.AlignLeft)  # 左对齐方式
        condition_layout.addWidget(button, alignment=Qt.AlignLeft)
        condition_widget = QWidget()
        condition_widget.setLayout(condition_layout)
        condition_widget.setContentsMargins(0, 20, 0, 0)

        # 输入部分的布局
        input_layout = QVBoxLayout()
        input_layout.addWidget(QLabel('''<font color=black face='黑体' size=4>服务器IP地址<font>'''), alignment=Qt.AlignBottom)
        server_IP_input = QLineEdit()
        server_IP_input.setPlaceholderText('请输入服务器IP地址')
        server_IP_input.setFixedSize(300, 30)
        server_IP_input.setStyleSheet("height:30px")
        input_layout.addWidget(server_IP_input)
        input_layout.addWidget(QLabel('''<font color=black face='黑体' size=4>服务器名称<font>'''), alignment=Qt.AlignBottom)
        server_name_input = QLineEdit()
        server_name_input.setPlaceholderText('请输入服务器名称')
        server_name_input.setFixedSize(300, 30)
        server_name_input.setStyleSheet("height:30px")
        input_layout.addWidget(server_name_input)
        input_widget = QWidget()
        input_widget.setLayout(input_layout)
        # 绑定事件，server_IP_input和server_name_input两个输入框在edit_state为1下只能编辑一个
        server_IP_input.textEdited.connect(lambda: set_another_not_edit(server_name_input))
        server_name_input.textEdited.connect(lambda: set_another_not_edit(server_IP_input))
        # 绑定button事件，确认按钮提交用户操作，参数：选择的执行操作：增删改查，输入的数据 IP地址和（或）名称
        button.clicked.connect(
            lambda: self.server_info_op(comb.currentText(), server_name_input.text(), server_IP_input.text()))
        #  绑定刷新服务器信息展示的事件，按照逻辑必须在上一条语句后面
        button.clicked.connect(lambda: show_server_info_list(self.server_info))
        # 绑定刷新操作执行状态展示的事件
        button.clicked.connect(lambda: show_operation_result(self.events_info))

        # server_IP_input.editingFinished.connect(lambda: set_another_edit(server_name_input))
        # server_name_input.editingFinished.connect(lambda: set_another_edit(server_IP_input))

        # 内部函数，在查询和删除的操作下输入一个框时使另一个框不可编辑
        def set_another_not_edit(another_line_edit):
            if self.edit_state == 1:
                another_line_edit.setEnabled(False)

        # 系统配置日志信息，内部为一个listWidget，列表呈现执行状态
        events_list = QListWidget()

        log_widget = QLabel('''<font color=black face='黑体' size=4>系统配置日志信息<font>''')

        # 定义内部函数事件，初始化或者是按钮提交后，从events_info中取数据放入events_list中去，刷新服务器显示信息
        def show_operation_result(event_info):
            events_list.clear()  # 清空刷新前的所有项
            for daily in event_info:
                item = QListWidgetItem()
                item.setFlags(Qt.NoItemFlags)  # 设置条目不可选中不可编辑
                # item.setSizeHint(QSize(400, 100))  # 必须设置Item大小，否则默认很小
                item.setSizeHint(QSize(400, 50))
                # 添加时间条目
                date_widget = get_execution_state_item(daily["date"], True)
                events_list.addItem(item)
                events_list.setItemWidget(item, date_widget)
                for event in daily["events"]:
                    item_t = QListWidgetItem()
                    item_t.setFlags(Qt.NoItemFlags)  # 设置条目不可选中不可编辑
                    item_t.setSizeHint(QSize(400, 40))
                    # 添加时间条目
                    date_widget = get_execution_state_item(event)
                    events_list.addItem(item_t)
                    events_list.setItemWidget(item_t, date_widget)

        show_operation_result(self.events_info)

        # 界面右部分总体布局
        down_layout.addWidget(condition_widget, alignment=Qt.AlignLeft)
        down_layout.addWidget(input_widget)
        down_layout.addWidget(log_widget)
        down_layout.addWidget(events_list)
        down_widget = QWidget()
        down_widget.setLayout(down_layout)

        # 界面左右布局
        content_layout = QHBoxLayout()
        content_layout.addWidget(middle_widget)
        content_layout.addWidget(down_widget)

        # 全局布局
        whole_layout.addWidget(upper_title)
        whole_layout.addLayout(content_layout)

        self.setLayout(whole_layout)
        self.show()

    # 定义事件，选择op（增删改查）后根据输入数据返回执行结果
    def server_info_op(self, op, server_name, server_ip):
        feedback = ""
        if not self.illegal_ip_info(server_ip):
            return ""
        if op == "增加":
            feedback = self.configuration_info.addServer(server_ip, server_name)
        elif op == "删除":
            delete_ip = server_ip if not server_name else configuration_info.NametoIP(server_name)
            feedback, is_delete = self.configuration_info.deleteServer(self, server_ip, server_name)
            if is_delete == 1:
                in_interface_impl.delete_server(delete_ip, self.lock)
        elif op == "更改":
            feedback = self.configuration_info.modifyName(server_ip, server_name)
        elif op == "查询":
            feedback = self.configuration_info.searchServer(server_ip, server_name)
        # print(feedback)
        # 更新当前所保持的服务器信息
        self.server_info = self.get_server_info()
        # 更新所有执行结果，把最新的执行状态结果加上去
        self.set_events_info(feedback)
        return feedback

    # 输入无效的IP地址时弹窗提示警告
    def illegal_ip_info(self, server_ip):
        if server_ip == "": return True
        r = '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(r, server_ip) is None:  # 没有匹配结果返回None
            QMessageBox.warning(self, "警告", "无效的IP地址，请重新输入。")
            return False
        return True

    # 获取服务器信息，包括服务器IP地址、名称和所属架构
    def get_server_info(self):
        server_info = []
        for i in range(len(self.configuration_info.server_IPs)):
            server_info.append([self.configuration_info.server_names[i], self.configuration_info.server_IPs[i], self.configuration_info.server_types[i]])
        return server_info

    # 获取历史执行状态结果列表
    # 考虑时间因素，无返回结果，直接更改内部元素为元组的列表events_info
    def set_events_info(self, new_line):
        # current_time = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')
        locale.setlocale(locale.LC_CTYPE, 'chinese')
        current_time = time.strftime('%Y年%m月%d日 %H:%M')
        index = current_time.find(' ')
        current_date = current_time[:index]
        current_time = current_time[index + 1:]
        last = len(self.events_info)
        if last != 0 and current_date == self.events_info[last - 1]["date"]:
            self.events_info[last - 1]["events"].append(current_time + ' ' + new_line)
        else:
            self.events_info.append({"date": current_date, "events": [current_time + ' ' + new_line]})
