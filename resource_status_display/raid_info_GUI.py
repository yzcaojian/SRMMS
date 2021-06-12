from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QAbstractItemView, \
    QHeaderView, QSplitter
from pyecharts import options as opts
from pyecharts.charts import Line

from interface.in_interface import in_interface_impl
from resource_status_display.configuration_GUI import ConfigurationWidget
from resource_status_display.get_info_item import get_server_storage_info_item, get_volume_storage_info_item
from resource_status_display.backward_thread import UpdateRAIDDataThread
from resource_status_display.history_io_display import HistoryIO
# from resource_status_display.servers_and_disks_info import get_server_detailed_info, server_storage_info_list

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
        self.server_overall_info = in_interface_impl.get_server_overall_info(1)  # 服务器总体信息列表
        self.selected_server_ip = "" if len(self.server_overall_info) == 0 else self.server_overall_info[0].serverIP  # 选中的服务器IP地址，默认是第一个
        self.server_detailed_info = in_interface_impl.get_server_detailed_info(self.selected_server_ip, 1)  # 根据不同服务器IP地址查询的详细信息，类型应为列表的列表。每个元素为LogicVolumeInfo
        self.graph_widget = QWidget()  # 两张表和I/O负载图的窗口
        self.update_thread = UpdateRAIDDataThread(lock)  # 后台线程，每秒钟更新数据局
        self.initUI()
        self.update_thread.start()

    def initUI(self):
        # 刷新按钮和配置按钮布局
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        # 刷新按钮
        update_button = QPushButton()
        update_button.setToolTip('刷新')
        update_button.setFixedSize(30, 30)
        update_button_icon = QIcon()
        update_button_icon.addPixmap(QPixmap('./png/update.png'), QIcon.Normal, QIcon.Off)
        update_button.setIcon(update_button_icon)
        update_button.setIconSize(QSize(25, 25))
        update_button.setStyleSheet("background-color:#cccccc")
        # 绑定事件
        update_button.clicked.connect(lambda: self.update_())
        # 配置按钮
        configuration_button = QPushButton()
        configuration_button.setToolTip('配置')
        configuration_button.setFixedSize(30, 30)
        configuration_button_icon = QIcon()
        configuration_button_icon.addPixmap(QPixmap('./png/configuration.png'), QIcon.Normal, QIcon.Off)
        configuration_button.setIcon(configuration_button_icon)
        configuration_button.setIconSize(QSize(25, 25))
        configuration_button.setStyleSheet("background-color:#cccccc")
        # 绑定事件
        configuration_button.clicked.connect(lambda: self.show_configuration_GUI())
        # 按钮布局添加按钮部件
        button_layout.addWidget(update_button, alignment=Qt.AlignRight)
        button_layout.addWidget(configuration_button)  # 两个控件中只写一个Alignment就可以紧挨着了
        button_widget.setLayout(button_layout)
        button_widget.setContentsMargins(0, 0, 10, 0)

        # 总体信息表和详细信息表和I/O负载图布局
        graph_layout = QVBoxLayout()

        # 服务器总体信息表
        server_title = QLabel('''<font color=black face='黑体' size=5>服务器总体信息<font>''')
        server_title.setAlignment(Qt.AlignCenter)
        server_title.setStyleSheet("background-color:#dddddd;width:100px")
        server_storage_table_widget = QWidget()  # 总体信息表格窗口
        server_storage_table = QTableWidget(len(self.server_overall_info), 4)
        server_storage_table.setHorizontalHeaderLabels(['服务器名称', '存储总容量', '已使用容量', '存储占用率'])  # 设置表头
        server_storage_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color:rgb(155, 194, 200); font:14pt SimHei; color:black}")  # 设置表头样式
        server_storage_table.setStyleSheet("QTableView::item:selected{background-color: #daeefe}")  # 设置行选中样式
        server_storage_table.horizontalHeader().setHighlightSections(False)  # 设置表头不会因为点击表格而变色
        server_storage_table.verticalHeader().setVisible(False)  # 设置隐藏列表号
        server_storage_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置选中单位为行，而不是单元格
        server_storage_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置禁止编辑
        server_storage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 设置表宽度自适应性扩展
        # server_storage_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 将竖直的滑动条隐藏，避免遮挡内容
        server_storage_table.clicked.connect(lambda: self.set_selected_server_ip(server_storage_table.selectedRanges()))
        server_storage_table.clicked.connect(lambda: show_volume_storage_list(server_storage_table.selectedRanges(), False))
        server_storage_table.clicked.connect(lambda: set_server_io_line(server_storage_table.selectedRanges(), False))  # 单击改变总体信息I/O负载图
        # server_storage_table.clicked.connect(lambda: printSize())

        server_storage_table_layout = QVBoxLayout()
        server_storage_table_layout.addWidget(server_title)
        server_storage_table_layout.addWidget(server_storage_table)
        server_storage_table_widget.setLayout(server_storage_table_layout)

        # 定义内部函数事件，初始化或者是到刷新周期后，从server_storage_info_list中取数据放入server_storage_table中去
        def show_server_storage_list(server_storage_info_list):
            # server_storage_table.clear()  # 清空刷新前的所有项
            for i, single_server_info in enumerate(server_storage_info_list):
                server_storage_table.setRowHeight(i, 60)
                # 添加单元格信息
                line = get_server_storage_info_item(single_server_info)
                for j, cell in enumerate(line):
                    if j == 0:
                        server_storage_table.setCellWidget(i, j, cell)
                        continue
                    cell_widget = QWidget()
                    cell_layout = QHBoxLayout()
                    cell_layout.setContentsMargins(0, 0, 0, 0)
                    cell_layout.addWidget(cell, alignment=Qt.AlignCenter)
                    cell_widget.setLayout(cell_layout)
                    server_storage_table.setCellWidget(i, j, cell_widget)

        show_server_storage_list(self.server_overall_info)

        # 服务器详细信息表
        volume_title = QLabel('''<font color=black face='黑体' size=5>服务器详细信息<font>''')
        volume_title.setAlignment(Qt.AlignCenter)
        volume_title.setStyleSheet("background-color:#dddddd;width:100px")
        volume_storage_table_widget = QWidget()  # 详细信息表格窗口
        volume_storage_table = QTableWidget(len(self.server_overall_info), 4)
        volume_storage_table.setHorizontalHeaderLabels(['逻辑卷标识', '存储总容量', '已使用容量', '存储占用率'])  # 设置表头
        volume_storage_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color:rgb(155, 194, 200); font:14pt SimHei; color:black}")  # 设置表头样式
        volume_storage_table.setStyleSheet("QTableView::item:selected{background-color: #daeefe}")  # 设置行选中样式
        volume_storage_table.horizontalHeader().setHighlightSections(False)  # 设置表头不会因为点击表格而变色
        volume_storage_table.verticalHeader().setVisible(False)  # 设置隐藏列表号
        volume_storage_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置选中单位为行，而不是单元格
        volume_storage_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置禁止编辑
        volume_storage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 设置表宽度自适应性扩展
        # volume_storage_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 将竖直的滑动条隐藏，避免遮挡内容

        volume_storage_table_layout = QVBoxLayout()
        volume_storage_table_layout.addWidget(volume_title)
        volume_storage_table_layout.addWidget(volume_storage_table)
        volume_storage_table_widget.setLayout(volume_storage_table_layout)

        # 定义内部函数事件，初始化或者是到刷新周期后，从volume_storage_info_list中取数据放入volume_storage_table中去
        def show_volume_storage_list(server_selected, IsUpdate):
            # server_storage_table.clear()  # 清空刷新前的所有项
            # server_selected是获取的选择表格某行的范围信息
            # volume_storage_info_list = []
            if IsUpdate:
                volume_storage_info_list = in_interface_impl.get_server_detailed_info(self.selected_server_ip, 1)  # 刷新的情况下直接用当前serverIP
            else:
                if server_selected is None:
                    print('默认选中第一个server')
                    volume_storage_info_list = self.server_detailed_info
                else:
                    print(self.server_overall_info[server_selected[0].topRow()].serverIP)  # 获取到选中的serverIP，生成详细信息界面
                    volume_storage_info_list = in_interface_impl.get_server_detailed_info(self.selected_server_ip, 1)
            for i, single_volume_info in enumerate(volume_storage_info_list):
                volume_storage_table.setRowHeight(i, 60)
                # 添加单元格信息
                line = get_volume_storage_info_item(single_volume_info)
                for j, cell in enumerate(line):
                    if j == 0:
                        volume_storage_table.setCellWidget(i, j, cell)
                        continue
                    cell_widget = QWidget()
                    cell_layout = QHBoxLayout()
                    cell_layout.setContentsMargins(0, 0, 0, 0)
                    cell_layout.addWidget(cell, alignment=Qt.AlignCenter)
                    cell_widget.setLayout(cell_layout)
                    volume_storage_table.setCellWidget(i, j, cell_widget)

        show_volume_storage_list(None, False)

        # 总体信息表和详细信息表布局
        table_widget = QWidget()
        table_layout = QHBoxLayout()
        table_layout.addWidget(server_storage_table_widget)
        table_layout.addWidget(volume_storage_table_widget)
        table_widget.setLayout(table_layout)

        # 总体I/O负载信息图
        # 负载图的button
        io_button = QPushButton("历史信息")
        io_button.setFixedSize(100, 30)
        io_button.setStyleSheet('''QPushButton{background-color:white; font-size:20px; font-family:SimHei; 
                                        border-width:2px; border-style:solid; border-color:black; border-radius:12px}
                                        QPushButton:pressed{background-color:#bbbbbb}''')
        io_button.clicked.connect(lambda: self.show_history_io_line())  # 绑定历史I/O负载图弹出事件
        # I/O负载图
        server_io_widget = QWidget()
        server_io_layout = QVBoxLayout()
        line_widget = QWebEngineView()

        def draw_server_io_line():
            # clearLayout(disks_io_right_layout)
            # io_width = str(line_widget.size().width() - 20) + "px"
            # io_height = str(line_widget.size().height() - 20) + "px"
            # 根据屏幕大小来确定I/O负载图的比例
            io_width = str(self.size().width() - 50) + "px"
            io_height = str(self.size().height() / 2 - 100) + "px"

            # x_data = ["12:00", "12:01", "12:02", "12:03", "12:04", "12:05", "12:06", "12:07", "12:08", "12:09",
            # "12:10", "12:11", "12:12", "12:13", "12:14", "12:15", "12:16", "12:17", "12:18", "12:19", "12:20",
            # "12:21", "12:22", "12:23", "12:24", "12:25", "12:26", "12:27", "12:28", "12:29", "12:30", "12:31",
            # "12:32", "12:33", "12:34", "12:35", "12:36", "12:37", "12:38", "12:39", "12:40", "12:41", "12:42",
            # "12:43", "12:44", "12:45", "12:46", "12:47", "12:48", "12:49", "12:50", "12:51", "12:52", "12:53",
            # "12:54"] y_data = [820, 652, 701, 934, 1190, 1330, 1340, 1433, 1672, 1630, 1725, 1720, 1691, 1530,
            # 1284, 1063, 851, 720, 630, 980, 954, 947, 1231, 1241, 1382, 1320, 1230, 1128, 1261, 1439, 1496, 1587,
            # 1780, 1820, 1100, 1021, 665, 598, 430, 348, 489, 576, 761, 862, 966, 874, 964, 1123, 1287, 1399, 1465,
            # 1411, 1511, 1004, 856]
            y_data, x_data = in_interface_impl.get_RAID_overall_io_info(self.selected_server_ip)

            line = (Line(init_opts=opts.InitOpts(bg_color='#ffffff', width=io_width, height=io_height,
                                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                    .add_xaxis(xaxis_data=x_data)
                    .add_yaxis(
                series_name="服务器 实时I/O负载",
                y_axis=y_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False), )
                    .set_global_opts(
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    name="IOPS/KB",
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True), ),
                xaxis_opts=opts.AxisOpts(
                    name="时间",
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_inside=True),
                    boundary_gap=False))
                    .render("./html/server_io.html"))

            # line_widget = QWebEngineView()
            line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)  # 将滑动条隐藏，避免遮挡内容
            # line_widget.setFixedSize(server_io_widget.size().width() - 20, server_io_widget.size().height() - 100)
            line_widget.resize(self.size().width() - 50, self.size().height() / 2 - 80)
            # 打开本地html文件
            line_widget.load(QUrl("file:///./html/server_io.html"))
            server_io_layout.addWidget(line_widget, alignment=Qt.AlignLeft | Qt.AlignBottom)
            server_io_layout.addWidget(io_button, alignment=Qt.AlignBottom | Qt.AlignCenter)
            # io_button.setContentsMargins(400, 0, 0, 0)

        def set_server_io_line(server_selected, IsUpdate):
            # server_selected是获取的选择表格某行的范围信息
            if IsUpdate:
                print("update raid server per second...")
                pass  # 刷新的情况下直接用当前serverIP得到I/O负载数据
            else:
                if server_selected is None:
                    print('默认选中第一个server')
                else:
                    print(self.server_overall_info[server_selected[0].topRow()].serverIP)  # 获取到选中的serverIP，生成总体I/O负载图

            # 根据屏幕大小来确定I/O负载图的比例
            io_width = str(self.size().width() - 50) + "px"
            io_height = str(self.size().height() / 2 - 100) + "px"

            y_data, x_data = in_interface_impl.get_RAID_overall_io_info(self.selected_server_ip)

            line = (Line(init_opts=opts.InitOpts(bg_color='#ffffff', width=io_width, height=io_height,
                                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                    .add_xaxis(xaxis_data=x_data)
                    .add_yaxis(
                series_name="HDD 实时I/O负载",
                y_axis=y_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False), )
                    .set_global_opts(
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    name="IOPS/KB",
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True), ),
                xaxis_opts=opts.AxisOpts(
                    name="时间",
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_inside=True),
                    boundary_gap=False))
                    .render("./html/raid_server_io.html"))

            line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)  # 将滑动条隐藏，避免遮挡内容
            # line_widget.setFixedSize(server_io_widget.size().width() - 24, server_io_widget.size().height() - 80)
            line_widget.resize(self.size().width() - 50, self.size().height() / 2 - 80)
            # 打开本地html文件
            line_widget.load(QUrl("file:///./html/raid_server_io.html"))

        draw_server_io_line()

        server_io_widget.setLayout(server_io_layout)
        splitter = QSplitter(Qt.Vertical)
        # 设置分割线的样式，宽度为3，颜色为黑色
        splitter.setStyleSheet("QSplitter::handle { background-color: black } QSplitter{background:white; "
                               "border-width:2px; border-color:black; border-style:solid}")
        splitter.setHandleWidth(3)
        splitter.addWidget(table_widget)
        splitter.addWidget(server_io_widget)
        graph_layout.addWidget(splitter)
        self.graph_widget.setLayout(graph_layout)

        # def printSize():
        #     print("graph_widget", self.graph_widget.size())
        #     print("server_io_widget", server_io_widget.size())
        #     print("server_storage_table", server_storage_table.size())
        #     print("line_widget", line_widget.size())
        # printSize()

        # 全局布局
        whole_layout = QVBoxLayout()
        whole_layout.setContentsMargins(0, 0, 0, 10)
        whole_layout.addWidget(button_widget)
        whole_layout.addWidget(self.graph_widget)
        self.setLayout(whole_layout)

        # 定时刷新
        self.update_thread.update_data.connect(lambda: show_server_storage_list(self.server_overall_info))
        self.update_thread.update_data.connect(lambda: show_volume_storage_list(None, True))
        self.update_thread.update_data.connect(lambda: set_server_io_line(None, True))

    def set_selected_server_ip(self, server_selected):
        self.selected_server_ip = self.server_overall_info[server_selected[0].topRow()].serverIP  # 获取到选中的serverIP

    def update_(self):
        self.graph_widget = QWidget()
        self.initUI()

    def show_configuration_GUI(self):
        self.configuration = ConfigurationWidget()

    def show_history_io_line(self):
        self.server_history_io = HistoryIO(self.selected_server_ip, "", 3)
        self.server_history_io.show()

