from PyQt5.QtCore import QUrl, QTime, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView
from PyQt5.QtWidgets import QPushButton, QTimeEdit, QHBoxLayout, QVBoxLayout, QWidget
from pyecharts.charts import Line
from pyecharts import options as opts

"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: 所有I/O负载历史信息弹窗显示功能窗口
@Time : 2021/5/26 16:03
@Author : cao jian
"""


class HistoryIO(QWidget):
    def __init__(self, server_ip):
        super().__init__()
        self.server_ip = server_ip
        self.time_end = QTime.currentTime()
        self.time_start = self.time_end.addSecs(-60*60)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(900, 600)
        self.setWindowTitle("历史I/O负载信息")
        self.setWindowIcon(QIcon('./png/history_io.png'))  # 设置窗体图标
        # 新建的窗口始终位于当前屏幕的最前面
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # 父类窗口不能点击
        self.setWindowModality(Qt.ApplicationModal)

        # 总体布局，时间选择与I/O负载图
        server_io_layout = QVBoxLayout()

        # 时间选择, 并控制时间选择范围最大值和最小值
        time_layout = QHBoxLayout()
        time_widget = QWidget()
        time_start = QTimeEdit(QTime.currentTime())
        time_start.setMinimumTime(QTime.currentTime().addSecs(-60 * 60 * 3))
        time_start.setMaximumTime(QTime.currentTime().addSecs(-60 * 60))
        time_end = QTimeEdit(QTime.currentTime())
        time_end.setMinimumTime(QTime.currentTime().addSecs(-60 * 60 * 2))
        time_end.setMaximumTime(QTime.currentTime())
        # 时间段选择的改变刷新历史I/O事件
        time_start.timeChanged.connect(self.start_time_changed)
        time_end.timeChanged.connect(self.end_time_changed)

        # 确认按钮
        io_button = QPushButton("确认")
        io_button.setFixedSize(100, 30)
        io_button.setStyleSheet('''QPushButton{background-color:white; font-size:20px; font-family:SimHei; 
                    border-width:2px; border-style:solid; border-color:black; border-radius:12px} 
                    QPushButton:pressed{background-color:#bbbbbb}''')
        io_button.clicked.connect(lambda: draw_server_io_line())  # 绑定历史I/O负载图刷新事件

        time_layout.addWidget(time_start)
        time_layout.addWidget(time_end)
        time_layout.addWidget(io_button)
        time_widget.setLayout(time_layout)

        # I/O负载图
        line_widget = QWebEngineView()

        def draw_server_io_line():
            # 根据当前服务器IP地址和选择的起始时间来查看I/O负载信息
            # self.server_ip, self.time_start, self.time_end
            # 可以稍加判断选择的时间范围不合理问题

            # 根据屏幕大小来确定I/O负载图的比例
            io_width = str(self.size().width() - 20) + "px"
            io_height = str(self.size().height() - 100) + "px"

            x_data = ["12:00", "12:01", "12:02", "12:03", "12:04", "12:05", "12:06", "12:07", "12:08", "12:09", "12:10",
                      "12:11", "12:12", "12:13", "12:14", "12:15", "12:16", "12:17", "12:18", "12:19", "12:20", "12:21",
                      "12:22", "12:23", "12:24", "12:25", "12:26", "12:27", "12:28", "12:29", "12:30", "12:31", "12:32",
                      "12:33", "12:34", "12:35", "12:36", "12:37", "12:38", "12:39", "12:40", "12:41", "12:42", "12:43",
                      "12:44", "12:45", "12:46", "12:47", "12:48", "12:49", "12:50", "12:51", "12:52", "12:53", "12:54"]
            y_data = [820, 652, 701, 934, 1190, 1330, 1340, 1433, 1672, 1630, 1725, 1720, 1691, 1530, 984, 663, 651,
                      520, 630, 980, 954, 947, 1231, 1241, 1382, 1320, 1230, 1128, 1261, 1439, 1496, 1587, 1780, 1820,
                      1100, 1021, 665, 598, 430, 348, 489, 576, 761, 862, 966, 874, 964, 1123, 1287, 1399, 1465, 1411,
                      1511, 1004, 856]
            y_predict_data = [620, 632, 665, 734, 1030, 1190, 1205, 1243, 1341, 1338, 1439, 1585, 1650, 1550, 997, 753,
                              671, 560, 627, 970, 955, 973, 1203, 1210, 1112, 1122, 1128, 1181, 1251, 1339, 1416, 1523,
                              1647, 1708, 1120, 1074, 675, 633, 479, 373, 430, 546, 663, 769, 829, 724, 634, 711, 853,
                              1019, 1155, 1221, 1504, 984, 843]

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
                y_axis=y_predict_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color='#19d3da'))
                    .set_global_opts(
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    name="IOPS",
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True)),
                xaxis_opts=opts.AxisOpts(
                    name="时间",
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_inside=True),
                    boundary_gap=False))
                    .render("./html/history_server_io.html"))

            line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)  # 将滑动条隐藏，避免遮挡内容
            line_widget.resize(self.size().width(), self.size().height() - 70)
            # 打开本地html文件
            line_widget.load(QUrl("file:///./html/history_server_io.html"))

        draw_server_io_line()

        server_io_layout.addWidget(line_widget, alignment=Qt.AlignCenter)
        server_io_layout.addWidget(time_widget, alignment=Qt.AlignCenter)

        self.setLayout(server_io_layout)

    def start_time_changed(self, time):
        self.time_start = str(time.hour()) + ":" + str(time.minute())
        print("时间下限", str(time.hour()) + ":" + str(time.minute()))

    def end_time_changed(self, time):
        self.time_end = str(time.hour()) + ":" + str(time.minute())
        print("时间上限", str(time.hour()) + ":" + str(time.minute()))