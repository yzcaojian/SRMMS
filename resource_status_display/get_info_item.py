from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout

"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: 配置信息中对单个服务器信息的Item封装
@Time : 2021/4/27 10:29
@Author : cao jian
"""


# 获取单个服务器信息的Item，Item内部包括图标、服务器名称、IP地址
def get_ServerInfo_Item(serverInfo):
    # 读取的数据
    server_name = serverInfo[0]
    server_IP = serverInfo[1]

    # 总体窗口
    server_widget = QWidget()
    # 单个服务器信息的布局
    single_server_layout = QHBoxLayout()

    # 图标
    server_image = QLabel()
    server_image.setFixedSize(50, 50)
    # 对读入图标进行调整，不能简单用resize
    png = QPixmap('./png/server.png').scaled(30, 50)
    server_image.setPixmap(png)

    # 服务器名称
    # 名称信息过长采用省略号代替多余文本内容，并且鼠标悬停可以显示全名
    # name_len表示对服务器名称长度的计算，英文一个字符，中文两个字符为长度计算规则
    name_len = int(len(server_name.encode('utf-8')) - len(server_name)) / 2 + len(server_name)
    server_name_widget = QLabel(server_name) if name_len <= 12 else QLabel(server_name[0:5] + '...')
    server_name_widget.setFixedWidth(150)
    # server_name_widget.setWordWrap(True)
    server_name_widget.setToolTip(server_name)
    server_name_widget.setStyleSheet("font-size:20px; font-color:black; font-family:'黑体'")

    # 服务器IP地址
    server_IP_widget = QLabel(server_IP)
    server_IP_widget.setStyleSheet("font-size:20px; font-color:black; font-family:'黑体'")

    single_server_layout.addWidget(server_image)
    single_server_layout.addWidget(server_name_widget, alignment=Qt.AlignLeft)
    single_server_layout.addWidget(server_IP_widget, alignment=Qt.AlignLeft)

    server_widget.setLayout(single_server_layout)

    return server_widget


# 获取一天的执行状态的Item，Item内部包括日期、该日期下各时间点和其对应的事件内容
def get_execution_state_item(line, IsDate=False):
    if IsDate:
        line_label = QLabel(line)
        line_label.setStyleSheet("height:20px; font-size:20px; font-color:black; font-family:'黑体'")
    else:
        line_label = QLabel(line)
        line_label.setWordWrap(True)  # 设置文本超出限制则换行
        line_label.setAlignment(Qt.AlignTop)
        line_label.setStyleSheet("height:20px; font-size:16px; font-color:black; font-family:'黑体'; text-indent:4px")

    return line_label


# 获取总体信息表的表格item, server_storage_info是ServerInfo的对象
def get_server_storage_info_item(server_storage_info, update_cycle, turn=1):
    # 设置默认字体为宋体，大小设为14，并且加粗(划掉)
    text_font = QFont("黑体", 14)  # , QFont.Bold)

    # 服务器名称
    server_name_layout = QHBoxLayout()
    server_name_widget = QWidget()
    if turn > 0:
        server_image = QLabel()
        server_image.setFixedSize(26, 40)
        png = QPixmap('./png/server.png').scaled(24, 38)
        server_image.setPixmap(png)
    else:
        server_image = QLabel()
        server_image.setFixedSize(26, 40)
        png = QPixmap('./png/no.png').scaled(24, 38)
        server_image.setPixmap(png)
    server_name = QLabel(server_storage_info.serverName)
    server_name.setToolTip(server_storage_info.serverName + ' ' + server_storage_info.serverIP)
    server_name.setFont(text_font)

    server_name_layout.addWidget(server_image)
    server_name_layout.addWidget(server_name, alignment=Qt.AlignLeft)
    server_name_widget.setLayout(server_name_layout)

    # 服务器存储总容量
    server_total_storage = QLabel(str(server_storage_info.totalCapacity) + "GB")
    server_total_storage.setFont(text_font)

    # 服务器已使用容量
    server_occupied_storage = QLabel(str(server_storage_info.occupiedCapacity) + "GB")
    server_occupied_storage.setFont(text_font)

    # 服务器容量使用占用率
    server_storage_occupied_rate = QLabel(server_storage_info.occupiedRate)
    server_storage_occupied_rate.setFont(text_font)

    # 连接状态
    connected_state = QLabel('''<font color=\'#00ff50\'><font>''') if update_cycle < 2 else QLabel('''<font color=red><font>''')
    connected_state.setText(str(update_cycle) + "s")
    connected_state.setFont(text_font)

    return [server_name_widget, server_total_storage, server_occupied_storage, server_storage_occupied_rate, connected_state]


# 获取多硬盘架构下详细信息表的表格item，disk_storage_info是DiskInfo类的对象
def get_disk_storage_info_item(disk_storage_info, turn=1):
    # 设置默认字体为宋体，大小设为14，并且加粗(划掉)
    text_font = QFont("黑体", 14)  # , QFont.Bold)

    # 硬盘标识
    disk_name_layout = QHBoxLayout()
    disk_name_widget = QWidget()
    if turn > 0:
        disk_image = QLabel()
        disk_image.setFixedSize(40, 40)
        png = QPixmap('./png/SSD.png').scaled(38, 38) if disk_storage_info.type == "SSD" else QPixmap(
            './png/HDD.png').scaled(38, 38)
        disk_image.setPixmap(png)
    else:
        disk_image = QLabel()
        disk_image.setFixedSize(40, 40)
        png = QPixmap('./png/no.png').scaled(38, 38)
        disk_image.setPixmap(png)
    disk_name = QLabel(disk_storage_info.diskID)
    disk_name.setToolTip(disk_storage_info.diskID)
    disk_name.setFont(text_font)
    disk_name_layout.addWidget(disk_image)
    disk_name_layout.addWidget(disk_name, alignment=Qt.AlignLeft)
    disk_name_widget.setLayout(disk_name_layout)

    # 硬盘类型
    disk_type = QLabel(disk_storage_info.type)
    disk_type.setFont(text_font)

    # 硬盘状态
    disk_state = QLabel(disk_storage_info.state)
    disk_state.setFont(text_font)

    # 硬盘存储容量
    disk_total_storage = QLabel(str(disk_storage_info.totalCapacity) + "GB")
    disk_total_storage.setFont(text_font)

    # 硬盘已使用容量
    disk_occupied_storage = QLabel(str(disk_storage_info.occupiedCapacity) + "GB")
    disk_occupied_storage.setFont(text_font)

    # 硬盘容量使用占用率
    disk_storage_occupied_rate = QLabel(disk_storage_info.occupiedRate)
    disk_storage_occupied_rate.setFont(text_font)

    return [disk_name_widget, disk_type, disk_state, disk_total_storage, disk_occupied_storage,
            disk_storage_occupied_rate]


# 获得RAID架构下详细信息表的表格item，disk_storage_info是LogicVolumeInfo类的对象
def get_volume_storage_info_item(volume_storage_info):
    # 设置默认字体为黑体，大小设为14，并且加粗(划掉)
    text_font = QFont("黑体", 14)  # , QFont.Bold)

    # 硬盘标识
    volume_name_layout = QHBoxLayout()
    volume_name_widget = QWidget()
    volume_image = QLabel()
    volume_image.setFixedSize(34, 40)
    png = QPixmap('./png/volume.png').scaled(32, 38)
    volume_image.setPixmap(png)
    volume_name = QLabel(volume_storage_info.logicVolumeID)
    volume_name.setToolTip(volume_storage_info.logicVolumeID)
    volume_name.setFont(text_font)
    volume_name_layout.addWidget(volume_image)
    volume_name_layout.addWidget(volume_name, alignment=Qt.AlignLeft)
    volume_name_widget.setLayout(volume_name_layout)

    # 逻辑盘存储容量
    volume_total_storage = QLabel(str(volume_storage_info.totalCapacity) + "GB")
    volume_total_storage.setFont(text_font)

    # 逻辑盘已使用容量
    volume_occupied_storage = QLabel(str(volume_storage_info.occupiedCapacity) + "GB")
    volume_occupied_storage.setFont(text_font)

    # 逻辑盘容量使用占用率
    volume_storage_occupied_rate = QLabel(volume_storage_info.occupiedRate)
    volume_storage_occupied_rate.setFont(text_font)

    # 连接状态， QLabel('''<font color=red>异常<font>''')
    connected_state = QLabel('''<font color=\'#00ff50\'>正常<font>''')
    connected_state.setFont(text_font)

    return [volume_name_widget, volume_total_storage, volume_occupied_storage, volume_storage_occupied_rate, connected_state]


# exception来自告警信息类Warning，内部字段
def get_warning_info_item(exception):
    # 设置默认字体为黑体，大小设为9，并且加粗(划掉)
    text_font = QFont("黑体", 9)  # , QFont.Bold)
    # 异常图标
    slot_image = QLabel()
    slot_image.setFixedSize(40, 40)
    # 红点对应硬盘即将故障与服务器失联两种异常，橙点对应硬盘持续高负载和即将高负载两种异常
    png = QPixmap('./png/warning_red.png').scaled(40, 40) if exception[0] == 1 or exception[0] == 3 else QPixmap(
        './png/warning_orange.png').scaled(40, 40)
    slot_image.setPixmap(png)
    # 异常描述=告警描述=时间+内容
    warning_level = ""
    if exception[0] == 1:
        warning_level = "磁盘故障告警："
    elif exception[0] == 2:
        warning_level = "硬盘高负载高警："
    elif exception[0] == 3:
        warning_level = "服务器失联告警："
    if exception[0] == 4:
        warning_level = "硬盘持续高负载告警："
    index = exception[1].find(' ')
    warning_time = QLabel(exception[1][:index])
    warning_time.setFont(text_font)
    warning_content = QLabel(warning_level + exception[1][index + 1:])
    warning_content.setFont(text_font)
    warning_content.setWordWrap(True)  # 设置文本超出限制则换行
    # 告警时间与内容布局
    warning_layout = QVBoxLayout()
    warning_layout.setContentsMargins(0, 0, 0, 0)
    warning_widget = QWidget()
    warning_layout.addWidget(warning_time)
    warning_layout.addWidget(warning_content)
    warning_widget.setLayout(warning_layout)
    # 异常图标与异常描述的布局
    exception_layout = QHBoxLayout()
    exception_layout.setContentsMargins(0, 0, 0, 0)
    exception_widget = QWidget()
    exception_layout.addWidget(slot_image)
    exception_layout.addWidget(warning_widget, alignment=Qt.AlignLeft)
    exception_widget.setLayout(exception_layout)

    return exception_widget


# log来自调度分配日志信息类Scheduling，内部字段
def get_scheduling_info_item(log):
    # 设置默认字体为黑体，大小设为9
    text_font = QFont("黑体", 9)
    # 调度时间与内容
    index = log.find(' ')
    scheduling_time = QLabel(log[:index])
    scheduling_time.setFont(text_font)
    scheduling_content = QLabel(log) if len(log) < 40 else QLabel(log[:35] + "...")
    scheduling_content.setFont(text_font)
    scheduling_content.setWordWrap(True)  # 设置文本超出限制则换行
    scheduling_content.setContentsMargins(10, 0, 10, 0)
    # 调度时间与内容布局
    scheduling_layout = QVBoxLayout()
    scheduling_layout.addWidget(scheduling_time)
    scheduling_layout.addWidget(scheduling_content)
    scheduling_widget = QWidget()
    scheduling_widget.setLayout(scheduling_layout)

    return scheduling_widget
