from PyQt5.QtCore import QUrl, QTime, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView
from PyQt5.QtWidgets import QPushButton, QTimeEdit, QHBoxLayout, QVBoxLayout, QWidget, QLabel
from pyecharts.charts import Line
from pyecharts import options as opts

from interface.in_interface import in_interface_impl

"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: 所有I/O负载历史信息弹窗显示功能窗口
@Time : 2021/5/26 16:03
@Author : cao jian
"""


class HistoryIO(QWidget):
    def __init__(self, server_ip, disk_id, level):
        super().__init__()
        self.server_ip = server_ip
        self.disk_id = disk_id
        time = QTime.currentTime()
        self.time_end = str(time.hour()) + ":" + str(time.minute())
        self.time_start = str(time.hour()) + ":" + str(time.minute())
        self.level = level  # 历史负载信息显示分为显示秒级的和显示分钟级的，0表示服硬盘级以分钟显示，
        # 1表示服务器级SSD总负载以秒显示，2表示服务器级HDD总负载以秒显示，3表示RAID架构服务器总负载以秒显示
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(900, 600)
        self.setWindowTitle("历史I/O负载信息")
        self.setWindowIcon(QIcon('./resource_status_display/png/history_io.png'))  # 设置窗体图标
        # 新建的窗口始终位于当前屏幕的最前面
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # 父类窗口不能点击
        # self.setWindowModality(Qt.ApplicationModal)

        # 总体布局，时间选择与I/O负载图
        server_io_layout = QVBoxLayout()

        # 提示文字信息
        raid_server_tip = QLabel('''<font color=black face='黑体' size=3>注：可选择查看服务器三个小时内的历史总I/O负载信息，横坐标以秒为单位<font>''')
        ssd_server_tip = QLabel('''<font color=black face='黑体' size=3>注：可选择查看服务器三个小时内SSD的历史总I/O负载信息，横坐标以秒为单位<font>''')
        hdd_server_tip = QLabel('''<font color=black face='黑体' size=3>注：可选择查看服务器三个小时内HDD的历史总I/O负载信息，横坐标以秒为单位<font>''')
        disk_tip = QLabel('''<font color=black face='黑体' size=3>注：可选择查看硬盘十二个小时内的历史I/O负载信息，横坐标以分钟为单位<font>''')

        # 时间选择, 并控制时间选择范围最大值和最小值
        time_layout = QHBoxLayout()
        time_widget = QWidget()
        time_start = QTimeEdit(QTime.currentTime())
        time_end = QTimeEdit(QTime.currentTime())
        if self.level == 0:
            time_start.setMaximumTime(QTime.currentTime().addSecs(-60 * 60 * 3))
            time_end.setMaximumTime(QTime.currentTime().addSecs(-60 * 60 * 3))
        else:
            time_start.setMinimumTime(QTime.currentTime().addSecs(-60 * 60 * 3 - 420))
            time_start.setMaximumTime(QTime.currentTime())
            time_end.setMinimumTime(QTime.currentTime().addSecs(-60 * 60 * 3 - 420))
            time_end.setMaximumTime(QTime.currentTime())

        # 时间段选择的改变刷新历史I/O事件
        time_start.timeChanged.connect(self.start_time_changed)
        time_end.timeChanged.connect(self.end_time_changed)

        # 时间选择的提示信息
        tip_image = QLabel()
        tip_image.setFixedSize(20, 20)
        png = QPixmap('./png/tips.png').scaled(18, 18)
        tip_image.setContentsMargins(0, 0, 30, 0)
        tip_image.setPixmap(png)
        tip_image.setToolTip("时间选择有上下界限制；\n时间选择通过点击上下键控制；\n只会显示输入时间范围内存在的数据。")

        # 确认按钮
        io_button = QPushButton("确认")
        io_button.setFixedSize(100, 30)
        io_button.setStyleSheet('''QPushButton{background-color:white; font-size:20px; font-family:SimHei; 
                    border-width:2px; border-style:solid; border-color:black; border-radius:12px} 
                    QPushButton:pressed{background-color:#bbbbbb}''')
        if self.level == 0:
            io_button.clicked.connect(lambda: draw_disk_io_line())  # 绑定历史I/O负载图刷新事件
        else:
            io_button.clicked.connect(lambda: draw_server_io_line())  # 绑定历史I/O负载图刷新事件

        time_layout.addWidget(time_start)
        time_layout.addWidget(time_end)
        time_layout.addWidget(tip_image)
        time_layout.addWidget(io_button)
        time_widget.setLayout(time_layout)

        # I/O负载图
        line_widget = QWebEngineView()

        def draw_server_io_line():
            # 根据当前服务器IP地址和选择的起始时间来查看I/O负载信息
            # self.server_ip, self.time_start, self.time_end
            global x_data, y_data
            if self.level == 1: y_data, x_data = in_interface_impl.get_ssd_disk_io_info_past(self.server_ip, self.time_start, self.time_end)
            elif self.level == 2: y_data, x_data = in_interface_impl.get_hdd_disk_io_info_past(self.server_ip, self.time_start, self.time_end)
            elif self.level == 3: y_data, x_data = in_interface_impl.get_RAID_overall_io_info_past(self.server_ip, self.time_start, self.time_end)
            # 可以稍加判断选择的时间范围不合理问题

            # 根据屏幕大小来确定I/O负载图的比例
            io_width = str(self.size().width() - 20) + "px"
            io_height = str(self.size().height() - 130) + "px"

            if not y_data:
                y_data, x_data = [0], ["12:00"]

            line = (Line(init_opts=opts.InitOpts(bg_color='#ffffff', width=io_width, height=io_height,
                                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                    .add_xaxis(xaxis_data=x_data)
                    .add_yaxis(
                series_name="实时I/O负载",
                y_axis=y_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color='#ce1212'))
                    .set_global_opts(
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    name="IOPS/KB",
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True)),
                xaxis_opts=opts.AxisOpts(
                    name="时间",
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_inside=True),
                    boundary_gap=False))
                    .render("./resource_status_display/html/history_server_io.html"))

            line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)  # 将滑动条隐藏，避免遮挡内容
            line_widget.resize(self.size().width(), self.size().height() - 90)
            # 打开本地html文件
            line_widget.load(QUrl("file:///./resource_status_display/html/history_server_io.html"))

        def draw_disk_io_line():
            # 根据当前服务器IP地址和选择的起始时间来查看I/O负载信息
            # self.server_ip, self.time_start, self.time_end
            # 可以稍加判断选择的时间范围不合理问题

            # 根据屏幕大小来确定I/O负载图的比例
            io_width = str(self.size().width() - 20) + "px"
            io_height = str(self.size().height() - 130) + "px"

            y_data, x_data = in_interface_impl.get_io_load_input_queue_display_past(self.server_ip, self.disk_id, self.time_start, self.time_end)
            y_predict_data, _ = in_interface_impl.get_io_load_output_queue_display_past(self.server_ip, self.disk_id, self.time_start, self.time_end)
            if not y_data:
                y_data, x_data = [0], ["12:00"]
            if len(y_predict_data) != len(y_data):
                y_predict_data_ = [None] * (len(y_data) - len(y_predict_data)) + y_predict_data
            else:
                y_predict_data_ = y_predict_data

            line = (Line(init_opts=opts.InitOpts(bg_color='#ffffff', width=io_width, height=io_height,
                                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                    .add_xaxis(xaxis_data=x_data)
                    .add_yaxis(
                series_name="实时I/O负载",
                y_axis=y_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color='#ce1212'))
                    .add_yaxis(
                series_name="预测I/O负载",
                y_axis=y_predict_data_,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color='#19d3da'))
                    .set_global_opts(
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    name="每分钟IO/KB",
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True)),
                xaxis_opts=opts.AxisOpts(
                    name="时间",
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_inside=True),
                    boundary_gap=False))
                    .render("./resource_status_display/html/history_server_io.html"))

            line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)  # 将滑动条隐藏，避免遮挡内容
            line_widget.resize(self.size().width(), self.size().height() - 90)
            # 打开本地html文件
            line_widget.load(QUrl("file:///./resource_status_display/html/history_server_io.html"))

        if self.level == 0:
            draw_disk_io_line()
        else:
            draw_server_io_line()

        if self.level == 0:
            server_io_layout.addWidget(disk_tip, alignment=Qt.AlignLeft)
        elif self.level == 1:
            server_io_layout.addWidget(ssd_server_tip, alignment=Qt.AlignLeft)
        elif self.level == 2:
            server_io_layout.addWidget(hdd_server_tip, alignment=Qt.AlignLeft)
        else:
            server_io_layout.addWidget(raid_server_tip, alignment=Qt.AlignLeft)

        server_io_layout.addWidget(line_widget, alignment=Qt.AlignCenter)
        server_io_layout.addWidget(time_widget, alignment=Qt.AlignCenter)

        self.setLayout(server_io_layout)

    def start_time_changed(self, time):
        self.time_start = str(time.hour()) + ":" + str(time.minute())
        print("时间下限", str(time.hour()) + ":" + str(time.minute()))

    def end_time_changed(self, time):
        self.time_end = str(time.hour()) + ":" + str(time.minute())
        print("时间上限", str(time.hour()) + ":" + str(time.minute()))
