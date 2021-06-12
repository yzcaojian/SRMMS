import time

from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QApplication, QHBoxLayout, QTabBar, QLabel, QPushButton, \
    QSplitter, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QMainWindow, QMessageBox
from pyecharts.charts import Bar, Line
from pyecharts.commons.utils import JsCode
from pyecharts import options as opts

from interface.in_interface import in_interface_impl
from resource_status_display.backward_thread import UpdateMDDataThread
from resource_status_display.get_info_item import get_server_storage_info_item, get_disk_storage_info_item
from resource_status_display.history_io_display import HistoryIO
# from resource_status_display.servers_and_disks_info import server_storage_info_list, two_disk_info_list, \
#     get_server_detailed_info, get_two_disk_info

"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: tab页布局和事件的实现
@Time : 2021/5/11 20:24
@Author : cao jian
"""


# 清除布局
def clearLayout(layout):
    if layout is not None:
        # print(layout.count())
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()


class MultDisksInfoTabWidget(QTabWidget):
    def __init__(self, lock):
        super().__init__()
        self.overall_info_tab = QWidget()  # 定义一个不能关闭的Tab页，表示总体信息显示页，后续可以添加可关闭的详细信息显示页
        self.selected_disk_id = {}  # 选中的硬盘ID，每个tab页对应一个列表元素[server_ip, disk_id]，默认是每个服务器第一个
        self.exception_list = in_interface_impl.get_exception_list()  # 异常信号收集，内部为两个列表，分别是server_ip和turn标志的列表、disk_id和turn标志的列表
        self.server_overall_info = in_interface_impl.get_server_overall_info(0)  # 多硬盘架构下服务器总体信息列表
        self.selected_server_ip = "" if len(self.server_overall_info) == 0 else self.server_overall_info[0].serverIP  # 选中的服务器IP地址，默认是第一个
        self.two_disk_info = in_interface_impl.get_two_disk_info(self.selected_server_ip)  # 选中服务器两类硬盘容量、I/O负载、数量、故障率信息列表
        self.server_detailed_info = {}  # 根据不同服务器IP地址查询的详细信息，类型应为列表的列表。每个元素为DiskInfo
        self.tabCounts = 0
        self.update_thread = UpdateMDDataThread(lock)  # 后台线程，每秒钟更新数据局
        self.initUI()
        self.update_thread.start()

    def initUI(self):
        self.addTab(self.overall_info_tab, "总体信息")  # 初始情况下没有详细页
        self.setTabsClosable(True)  # 设置tab页可以关闭，添加关闭按钮
        # self.setMovable(True)  # 设置可以拖动
        self.tabCloseRequested.connect(self.tabClose)  # 绑定tab页关闭事件
        self.tabBar().setTabButton(0, QTabBar.RightSide, None)  # 设置总体信息页不能被关闭

        # 总体信息的tab页
        # 服务器总体信息表和容量、故障率柱状图的布局
        # 服务器总体信息表
        server_title = QLabel('''<font color=black face='黑体' size=5>服务器总体信息<font>''')
        server_title.setAlignment(Qt.AlignCenter)
        server_title.setStyleSheet("background-color:#dddddd;width:100px")
        server_storage_table_widget = QWidget()  # 总体信息页面的总体信息表格窗口
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
        server_storage_table.doubleClicked.connect(  # 双击新增详细信息界面
            lambda: self.add_detailed_tab(server_storage_table.selectedRanges(), self.tabCounts))
        # server_storage_table.clicked.connect(  # 单击改变总体信息界面
        #     lambda: self.update_server_overall_info(server_storage_table.selectedRanges()))
        server_storage_table.clicked.connect(lambda: self.set_selected_server_ip(server_storage_table.selectedRanges()))
        server_storage_table.clicked.connect(
            lambda: draw_two_disk_storage_bar(server_storage_table.selectedRanges(), False))
        server_storage_table.clicked.connect(
            lambda: draw_two_disk_error_rate_bar(server_storage_table.selectedRanges(), False))
        server_storage_table.clicked.connect(lambda: set_ssd_io_line(server_storage_table.selectedRanges(), False))
        server_storage_table.clicked.connect(lambda: set_hdd_io_line(server_storage_table.selectedRanges(), False))
        # server_storage_table.clicked.connect(self.show_disk_error_warning)
        # server_storage_table.clicked.connect(lambda: printSize())

        server_storage_table_layout = QVBoxLayout()
        server_storage_table_layout.addWidget(server_title)
        server_storage_table_layout.addWidget(server_storage_table)
        server_storage_table_widget.setLayout(server_storage_table_layout)
        server_storage_table_widget.setMinimumSize(self.size().width() / 3, self.size().height() / 3)

        # 定义内部函数事件，初始化或者是到刷新周期后，从server_storage_info_list中取数据放入server_storage_table中去
        def show_server_storage_list():
            global line
            self.server_overall_info = in_interface_impl.get_server_overall_info(0)
            server_storage_info_list = self.server_overall_info
            server_storage_table.setRowCount(len(self.server_overall_info))  # 设置表格行数
            # server_storage_table.clear()  # 清空刷新前的所有项
            for i, single_server_info in enumerate(server_storage_info_list):
                server_storage_table.setRowHeight(i, 60)
                # 添加单元格信息
                if not self.exception_list:  # 还有服务器图标闪烁
                    line = get_server_storage_info_item(single_server_info)
                else:
                    for e in self.exception_list[0]:
                        if single_server_info.serverIP == e[0]:
                            e[1] = 0 - e[1]  # 将标志反转
                            line = get_server_storage_info_item(single_server_info, e[1])
                            break  # 图标闪烁待优化
                        else:
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

        show_server_storage_list()

        # 两类硬盘容量与故障率柱状图
        bar_layout = QHBoxLayout()
        bar_widget = QWidget()

        # HDD和SSD容量信息表
        first_bar_widget = QWebEngineView()
        second_bar_widget = QWebEngineView()

        def draw_two_disk_storage_bar(server_selected, IsUpdate):
            if IsUpdate:
                two_disk_list = in_interface_impl.get_two_disk_info(self.selected_server_ip)  # 刷新的情况下直接用当前selected_server_ip获取两类硬盘容量信息
            else:
                if server_selected is None:
                    print('默认选中第一个server')
                    two_disk_list = self.two_disk_info
                else:
                    print(self.server_overall_info[server_selected[0].topRow()].serverIP)  # 获取到选中的serverIP，生成详细信息界面
                    two_disk_list = in_interface_impl.get_two_disk_info(self.selected_server_ip)
            # two_disk_list = in_interface_impl.get_two_disk_info(self.selected_server_ip)  # 待优化
            # clearLayout(bar_layout)  # 清除之前的布局
            hdd_all = float(two_disk_list.hddTotalCapacity[:-2])
            hdd_used = float(two_disk_list.hddOccupiedCapacity[:-2])
            ssd_all = float(two_disk_list.ssdTotalCapacity[:-2])
            ssd_used = float(two_disk_list.ssdOccupiedCapacity[:-2])
            used = [hdd_used, ssd_used]
            all = [hdd_all - hdd_used, ssd_all - ssd_used]

            bar_width = str(bar_widget.size().width() / 2 - 30) + "px"
            bar_height = str(bar_widget.size().height() - 20) + "px"
            # bar_width = str(self.size().width() / 3) + "px"
            # bar_height = str(self.size().height() / 2 - 60) + "px"

            bar = (Bar(init_opts=opts.InitOpts(bg_color='#ffffff', width=bar_width, height=bar_height,
                                               animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                   .add_xaxis(["HDD", "SSD"], )
                   .add_yaxis("已使用容量", used, stack="stack1", category_gap="20%", bar_width="40%", color='#7eca9c')
                   .add_yaxis("剩余容量", all, stack="stack1", category_gap="20%", bar_width="40%", color='#4d5c6e')
                   .set_global_opts(
                yaxis_opts=opts.AxisOpts(name="容量\n单位TB", axistick_opts=opts.AxisTickOpts(is_inside=True)),
                xaxis_opts=opts.AxisOpts(name="", type_='category', axistick_opts=opts.AxisTickOpts(is_inside=True)))
                   .set_series_opts(
                label_opts=opts.LabelOpts(
                    position="right",
                    formatter=JsCode("function(x){return Number(x.data).toFixed() + 'TB';}"))
            ).render("./html/first.html"))

            first_bar_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars,
                                                     False)  # 将滑动条隐藏，避免遮挡内容
            first_bar_widget.resize(bar_widget.size().width() / 2 - 14, bar_widget.size().height())
            # first_bar_widget.resize(self.size().width() / 3, self.size().height() / 2 - 40)
            # 打开本地html文件
            first_bar_widget.load(QUrl("file:///./html/first.html"))

        bar_layout.addWidget(first_bar_widget, alignment=Qt.AlignCenter)

        def draw_two_disk_error_rate_bar(server_selected, IsUpdate):
            if IsUpdate:
                two_disk_list = in_interface_impl.get_two_disk_info(self.selected_server_ip)  # 刷新的情况下直接用当前selected_server_ip获取两类硬盘容量信息
            else:
                if server_selected is None:
                    print('默认选中第一个server')
                    two_disk_list = self.two_disk_info
                else:
                    print(self.server_overall_info[server_selected[0].topRow()].serverIP)  # 获取到选中的serverIP，生成详细信息界面
                    two_disk_list = in_interface_impl.get_two_disk_info(self.selected_server_ip)

            hdd_rate = two_disk_list.hddErrorRate
            ssd_rate = two_disk_list.ssdErrorRate
            bar_width = str(bar_widget.size().width() / 2 - 30) + "px"
            bar_height = str(bar_widget.size().height() - 20) + "px"
            # bar_width = str(self.size().width() / 3) + "px"
            # bar_height = str(self.size().height() / 2 - 60) + "px"

            bar = (Bar(
                init_opts=opts.InitOpts(bg_color='#ffffff', width=bar_width, height=bar_height,  # rgb(200,200,200,1)
                                        animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                   .add_xaxis(["HDD", "SSD"])
                   .add_yaxis("", [hdd_rate, ssd_rate], category_gap="20%", bar_width="40%", color='#4d5c6e')
                   .set_global_opts(
                yaxis_opts=opts.AxisOpts(name="故障率", axistick_opts=opts.AxisTickOpts(is_inside=True)),
                xaxis_opts=opts.AxisOpts(name="", axistick_opts=opts.AxisTickOpts(is_inside=True)))
                   .set_series_opts(
                label_opts=opts.LabelOpts(
                    position="right",
                    formatter=JsCode("function(x){return Number(x.data * 100).toFixed() + '%';}"))  # 考虑用元组更改x.data的值
            ).render("./html/second.html"))

            second_bar_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars,
                                                      False)  # 将滑动条隐藏，避免遮挡内容
            second_bar_widget.resize(bar_widget.size().width() / 2 - 14, bar_widget.size().height())
            # first_bar_widget.resize(self.size().width() / 3, self.size().height() / 2 - 40)
            # 打开本地html文件
            second_bar_widget.load(QUrl("file:///./html/second.html"))
            # print("self", self.size(), "server_table", server_storage_table_widget.size(), "bar", bar_widget.size())
            # print(first_bar_widget.size(), second_bar_widget.size())

        bar_layout.addWidget(second_bar_widget, alignment=Qt.AlignCenter)

        # def set_two_disk_error_rate_bar(two_disk_list):
        #     hdd_rate = two_disk_list.hddErrorRate
        #     ssd_rate = two_disk_list.ssdErrorRate
        #     bar_width = str(bar_widget.size().width() / 2) + "px"
        #     bar_height = str(bar_widget.size().height()) + "px"
        #
        #     bar = (Bar(
        #         init_opts=opts.InitOpts(bg_color='#ffffff', width=bar_width, height=bar_height,  # rgb(200,200,200,1)
        #                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
        #            .add_xaxis(["HDD", "SSD"])
        #            .add_yaxis("", [hdd_rate, ssd_rate], category_gap="20%", bar_width="40%", color='#4d5c6e')
        #            .set_global_opts(
        #         yaxis_opts=opts.AxisOpts(name="故障率", axistick_opts=opts.AxisTickOpts(is_inside=True)),
        #         xaxis_opts=opts.AxisOpts(name="", axistick_opts=opts.AxisTickOpts(is_inside=True)))
        #            .set_series_opts(
        #         label_opts=opts.LabelOpts(
        #             position="right",
        #             formatter=JsCode("function(x){return Number(x.data * 100).toFixed() + '%';}"))  # 考虑用元组更改x.data的值
        #     ).render("second.html"))
        #
        #     # second_bar_widget = QWebEngineView()
        #     second_bar_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars,
        #                                               False)  # 将滑动条隐藏，避免遮挡内容
        #     second_bar_widget.resize(bar_widget.size().width() / 2, bar_widget.size().height())
        #     # 打开本地html文件
        #     second_bar_widget.load(QUrl("file:///second.html"))
        #     # bar_layout.addWidget(second_bar_widget, alignment=Qt.AlignCenter)

        draw_two_disk_storage_bar(None, False)
        draw_two_disk_error_rate_bar(None, False)

        bar_widget.setLayout(bar_layout)

        # I/O负载信息布局
        disks_io_widget = QWidget()
        disks_io_layout = QHBoxLayout()
        disks_io_left_layout = QVBoxLayout()
        disks_io_right_layout = QVBoxLayout()

        # 两个负载图各自的label和button
        # 改正！！！！！！！！！！！
        left_label = QLabel("SSD数量 " + str(self.two_disk_info.ssdCounts))
        left_label.setStyleSheet("height:20px;font-size:20px; font-family:SimHei; background-color:white")
        # "border-width:1px; border-style:solid; border-color:black")
        left_label.setContentsMargins(0, 0, 50, 0)
        right_label = QLabel("HDD数量 " + str(self.two_disk_info.hddCounts))
        right_label.setStyleSheet("height:20px;font-size:20px; font-family:SimHei; background-color:white")
        # "border-width:1px; border-style:solid; border-color:black")
        right_label.setContentsMargins(0, 0, 50, 0)
        left_button = QPushButton("历史信息")
        left_button.setFixedSize(100, 30)
        left_button.setStyleSheet('''QPushButton{background-color:white; font-size:20px; font-family:SimHei; 
                                border-width:2px; border-style:solid; border-color:black; border-radius:12px}
                                QPushButton:pressed{background-color:#bbbbbb}''')
        right_button = QPushButton("历史信息")
        right_button.setFixedSize(100, 30)
        right_button.setStyleSheet('''QPushButton{background-color:white; font-size:20px; font-family:SimHei; 
                                border-width:2px; border-style:solid; border-color:black; border-radius:12px}
                                QPushButton:pressed{background-color:#bbbbbb}''')
        # 绑定I/O负载历史信息弹窗事件
        left_button.clicked.connect(lambda: self.show_history_io_line(1))
        right_button.clicked.connect(lambda: self.show_history_io_line(2))

        # 左边I/O负载图
        first_line_widget = QWebEngineView()

        def draw_ssd_io_line():
            # 用于设置窗口宽高度，目前是设置固定高度
            disks_io_width = str(disks_io_widget.size().width() / 2 - 40) + "px"
            disks_io_height = str(disks_io_widget.size().height() - 100) + "px"
            # disks_io_width = str(self.size().width() / 2) + "px"
            # disks_io_height = str(self.size().height() / 2 - 60) + "px"

            # x_data = ["12:00", "12:01", "12:02", "12:03", "12:04", "12:05", "12:06", "12:07", "12:08", "12:09",
            # "12:10", "12:11", "12:12", "12:13", "12:14", "12:15", "12:16", "12:17", "12:18", "12:19", "12:20",
            # "12:21", "12:22", "12:23", "12:24", "12:25", "12:26", "12:27", "12:28", "12:29", "12:30", "12:31",
            # "12:32", "12:33", "12:34", "12:35", "12:36", "12:37", "12:38", "12:39", "12:40", "12:41", "12:42",
            # "12:43", "12:44", "12:45", "12:46", "12:47", "12:48", "12:49", "12:50", "12:51", "12:52", "12:53",
            # "12:54"] y_data = [820, 932, 901, 934, 1290, 1330, 1320, 1203, 1422, 1430, 1425, 1320, 1331, 990, 984,
            # 663, 651, 520, 630, 650, 854, 997, 931, 1121, 1302, 1420, 1530, 1520, 1261, 1239, 1196, 1487, 780, 120,
            # 11, 13, 65, 98, 150, 348, 489, 576, 661, 662, 666, 894, 994, 923, 1487, 1499, 1365, 1311, 1211, 1004,
            # 856] 获取得到指定IP地址的SSD的IOPS信息
            y_data, x_data = in_interface_impl.get_ssd_disk_io_info(self.selected_server_ip)

            line = (Line(init_opts=opts.InitOpts(bg_color='#ffffff', width=disks_io_width, height=disks_io_height,
                                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                    .add_xaxis(xaxis_data=x_data)
                    .add_yaxis(
                series_name="SSD 实时I/O负载",
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
                    .render("./html/ssd_io.html"))

            first_line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars,
                                                      False)  # 将滑动条隐藏，避免遮挡内容
            first_line_widget.resize(disks_io_widget.size().width() / 2 - 20,
                                     disks_io_widget.size().height() - 80)  # 高度设置小一点可以跟贴近底部
            # first_line_widget.resize(self.size().width() / 2, self.size().height() / 2 - 40)
            # 打开本地html文件
            first_line_widget.load(QUrl("file:///./html/ssd_io.html"))
            disks_io_left_layout.addWidget(left_label, alignment=Qt.AlignRight | Qt.AlignTop)
            disks_io_left_layout.addWidget(first_line_widget, alignment=Qt.AlignLeft | Qt.AlignTop)
            disks_io_left_layout.addWidget(left_button, alignment=Qt.AlignBottom | Qt.AlignCenter)

        def set_ssd_io_line(server_selected, IsUpdate):
            # server_selected是获取的选择表格某行的范围信息
            if IsUpdate:
                pass  # 刷新的情况下直接用当前serverIP得到I/O负载数据
            else:
                if server_selected is None:
                    print('默认选中第一个server')
                else:
                    print(self.server_overall_info[server_selected[0].topRow()].serverIP)  # 获取到选中的serverIP，得到负载数据

            # 用于设置窗口宽高度，目前是设置固定高度
            # 后期有高度设置不平衡的问题直接改这里，改为overall_tab宽高度一半少一点
            disks_io_width = str(disks_io_widget.size().width() / 2 - 40) + "px"
            disks_io_height = str(disks_io_widget.size().height() - 100) + "px"
            # disks_io_width = str(self.size().width() / 2 - 40) + "px"
            # disks_io_height = str(self.size().height() / 2 - 100) + "px"

            # 获取得到指定IP地址的SSD的IOPS信息
            y_data, x_data = in_interface_impl.get_ssd_disk_io_info(self.selected_server_ip)

            line = (Line(init_opts=opts.InitOpts(bg_color='#ffffff', width=disks_io_width, height=disks_io_height,
                                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                    .add_xaxis(xaxis_data=x_data)
                    .add_yaxis(
                series_name="SSD 实时I/O负载",
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
                    .render("./html/ssd_io.html"))

            # first_line_widget = QWebEngineView()
            first_line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars,
                                                      False)  # 将滑动条隐藏，避免遮挡内容
            first_line_widget.resize(disks_io_widget.size().width() / 2 - 20,
                                     disks_io_widget.size().height() - 80)  # 高度设置小一点可以跟贴近底部
            # first_line_widget.resize(self.size().width() / 2 - 20, self.size().height() / 2 - 80)
            # 打开本地html文件
            first_line_widget.load(QUrl("file:///./html/ssd_io.html"))
            # disks_io_left_layout.addWidget(first_line_widget, alignment=Qt.AlignCenter | Qt.AlignBottom)
            # print(disks_io_left_layout.itemAt(1).widget())
            # print("line-chart----------", disks_io_widget.size(), first_line_widget.size(), second_line_widget.size())

        # 右边I/O负载图
        second_line_widget = QWebEngineView()

        def draw_hdd_io_line():
            # clearLayout(disks_io_right_layout)
            disks_io_width = str(disks_io_widget.size().width() / 2 - 40) + "px"
            disks_io_height = str(disks_io_widget.size().height() - 100) + "px"
            # disks_io_width = str(self.size().width() / 2) + "px"
            # disks_io_height = str(self.size().height() / 2 - 60) + "px"

            # x_data = ["12:00", "12:01", "12:02", "12:03", "12:04", "12:05", "12:06", "12:07", "12:08", "12:09",
            # "12:10", "12:11", "12:12", "12:13", "12:14", "12:15", "12:16", "12:17", "12:18", "12:19", "12:20",
            # "12:21", "12:22", "12:23", "12:24", "12:25", "12:26", "12:27", "12:28", "12:29", "12:30", "12:31",
            # "12:32", "12:33", "12:34", "12:35", "12:36", "12:37", "12:38", "12:39", "12:40", "12:41", "12:42",
            # "12:43", "12:44", "12:45", "12:46", "12:47", "12:48", "12:49", "12:50", "12:51", "12:52", "12:53",
            # "12:54"] y_data = [820, 652, 701, 934, 1190, 1330, 1340, 1433, 1672, 1630, 1725, 1720, 1691, 1530, 984,
            # 663, 651, 520, 630, 980, 954, 947, 1231, 1241, 1382, 1320, 1230, 1128, 1261, 1439, 1496, 1587, 1780,
            # 1820, 1100, 1021, 665, 598, 430, 348, 489, 576, 761, 862, 966, 874, 964, 1123, 1287, 1399, 1465, 1411,
            # 1511, 1004, 856] 获取得到指定IP地址的HDD的IOPS信息 y_data, x_data = in_interface_impl.get_hdd_disk_io_info(
            # self.selected_server_ip)

            # 获取得到指定IP地址的HDD的IOPS信息
            y_data, x_data = in_interface_impl.get_hdd_disk_io_info(self.selected_server_ip)

            line = (Line(init_opts=opts.InitOpts(bg_color='#ffffff', width=disks_io_width, height=disks_io_height,
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
                    .render("./html/hdd_io.html"))

            # second_line_widget = QWebEngineView()
            second_line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars,
                                                       False)  # 将滑动条隐藏，避免遮挡内容
            second_line_widget.resize(disks_io_widget.size().width() / 2 - 20, disks_io_widget.size().height() - 80)
            # first_line_widget.resize(self.size().width() / 2, self.size().height() / 2 - 40)
            # 打开本地html文件
            second_line_widget.load(QUrl("file:///./html/hdd_io.html"))
            disks_io_right_layout.addWidget(right_label, alignment=Qt.AlignRight | Qt.AlignTop)
            disks_io_right_layout.addWidget(second_line_widget, alignment=Qt.AlignLeft | Qt.AlignTop)
            disks_io_right_layout.addWidget(right_button, alignment=Qt.AlignBottom | Qt.AlignCenter)

        def set_hdd_io_line(server_selected, IsUpdate):
            # server_selected是获取的选择表格某行的范围信息
            if IsUpdate:
                print("update server_info per second...")
                pass  # 刷新的情况下直接用当前serverIP得到I/O负载数据
            else:
                if server_selected is None:
                    print('默认选中第一个server')
                else:
                    print(self.server_overall_info[server_selected[0].topRow()].serverIP)  # 获取到选中的serverIP，得到负载数据

            disks_io_width = str(disks_io_widget.size().width() / 2 - 40) + "px"
            disks_io_height = str(disks_io_widget.size().height() - 100) + "px"
            # disks_io_width = str(self.size().width() / 2 - 40) + "px"
            # disks_io_height = str(self.size().height() / 2 - 100) + "px"

            # 获取得到指定IP地址的HDD的IOPS信息
            y_data, x_data = in_interface_impl.get_hdd_disk_io_info(self.selected_server_ip)

            line = (Line(init_opts=opts.InitOpts(bg_color='#ffffff', width=disks_io_width, height=disks_io_height,
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
                    .render("./html/hdd_io.html"))

            # 将滑动条隐藏，避免遮挡内容
            second_line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
            second_line_widget.resize(disks_io_widget.size().width() / 2 - 20, disks_io_widget.size().height() - 80)
            # first_line_widget.resize(self.size().width() / 2 - 20, self.size().height() / 2 - 40)
            # 打开本地html文件
            second_line_widget.load(QUrl("file:///./html/hdd_io.html"))
            # print(disks_io_right_layout.itemAt(1).widget())

        draw_ssd_io_line()
        draw_hdd_io_line()

        disks_io_left_widget = QWidget()
        disks_io_left_widget.setLayout(disks_io_left_layout)
        disks_io_right_widget = QWidget()
        disks_io_right_widget.setLayout(disks_io_right_layout)
        disks_io_layout.addWidget(disks_io_left_widget)
        disks_io_layout.addWidget(disks_io_right_widget)
        disks_io_widget.setLayout(disks_io_layout)

        # 全局布局
        whole1_layout = QVBoxLayout()
        whole1_layout.setContentsMargins(0, 0, 0, 0)
        # 定义可缩放的两个窗口，前者表示总体信息表和两个柱状图的窗口，后者表示折线图绘制的I/O负载信息，splitter表示两个窗口可伸缩
        server_storage_info_widget = QWidget()
        server_storage_info_layout = QHBoxLayout()
        server_storage_info_layout.addWidget(server_storage_table_widget)
        server_storage_info_layout.addWidget(bar_widget, alignment=Qt.AlignRight)
        server_storage_info_widget.setLayout(server_storage_info_layout)

        server_io_info_widget = QWidget()
        server_io_info_layout = QHBoxLayout()
        server_io_info_layout.addWidget(disks_io_widget)
        server_io_info_widget.setLayout(server_io_info_layout)
        # print(server_storage_info_widget.size())
        # print(server_io_info_widget.size())

        splitter = QSplitter(Qt.Vertical)
        # 设置分割线的样式，宽度为3，颜色为黑色
        splitter.setStyleSheet("QSplitter::handle { background-color: black }")
        splitter.setHandleWidth(3)
        splitter.addWidget(server_storage_info_widget)
        splitter.addWidget(server_io_info_widget)

        # def printSize():
        #     print("overall.......")
        #     print("server_storage_info_widget", server_storage_info_widget.size())
        #     print("server_storage_table_widget", server_storage_table_widget.size())
        #     print("bar_widget", bar_widget.size())
        #     print("disk_io_info_widget", server_io_info_widget.size())
        #     print("overall_info_tab", self.overall_info_tab.size())
        #
        # printSize()

        whole1_layout.addWidget(splitter)
        # clearLayout(self.overall_info_tab.layout())
        self.overall_info_tab.setLayout(whole1_layout)

        # 定时刷新
        self.update_thread.update_data.connect(lambda: show_server_storage_list())
        self.update_thread.update_data.connect(lambda: draw_two_disk_storage_bar(None, True))
        self.update_thread.update_data.connect(lambda: draw_two_disk_error_rate_bar(None, True))
        self.update_thread.update_data.connect(lambda: set_hdd_io_line(None, True))
        self.update_thread.update_data.connect(lambda: set_ssd_io_line(None, True))

    def add_detailed_tab(self, server_selected, tabCounts):
        # server_selected是获取的选择表格某行的范围信息
        self.selected_server_ip = self.server_overall_info[server_selected[0].topRow()].serverIP  # 获取到选中的serverIP，生成详细信息界面
        # if self.count() <= len(self.server_detailed_info):  # 对选中硬盘详细信息进行更新
        #     self.server_detailed_info[self.count() - 1] = in_interface_impl.get_server_detailed_info(self.selected_server_ip, 0)
        # else:
        #     self.server_detailed_info.append(in_interface_impl.get_server_detailed_info(self.selected_server_ip, 0))
        self.server_detailed_info[tabCounts] = in_interface_impl.get_server_detailed_info(self.selected_server_ip, 0)
        # 添加详细信息tab页后默认选中第一块硬盘
        if len(self.server_detailed_info) != 0:
            # for selected_disk in self.selected_disk_id:
            #     if self.selected_server_ip == selected_disk[0]:  # 当前选择的服务器已经打开一个tab页
            #         return
            # if self.count() <= len(self.selected_disk_id):  # 对选中硬盘进行更新
            #     self.selected_disk_id[self.count() - 1] = [self.selected_server_ip, self.server_detailed_info[self.count() - 1][0].diskID]
            # else:
            #     self.selected_disk_id.append([self.selected_server_ip, self.server_detailed_info[self.count() - 1][0].diskID])
            self.selected_disk_id[tabCounts] = [self.selected_server_ip, self.server_detailed_info[tabCounts][0].diskID]

        # 如果有异常服务器图标闪烁，双击后去掉闪烁效果，即对应exception_list删除
        if self.exception_list:
            for e in self.exception_list[0]:
                if e[0] == self.selected_server_ip:
                    self.exception_list[0].remove(e)
                    break

        # 详细信息的tab页
        # 服务器详细信息表和硬盘健康度、I/O负载图的布局
        # 服务器详细信息表
        disk_title = QLabel('''<font color=black face='黑体' size=5>服务器详细信息<font>''')
        disk_title.setAlignment(Qt.AlignCenter)
        disk_title.setStyleSheet("background-color:#dddddd;width:100px")
        disk_storage_table = QTableWidget(len(self.server_detailed_info[self.count() - 1]), 6)
        disk_storage_table.setHorizontalHeaderLabels(['硬盘标识', '硬盘类型', '状态', '存储总容量', '已使用容量', '存储占用率'])  # 设置表头
        disk_storage_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color:rgb(155, 194, 200); font:14pt SimHei; color:black}")  # 设置表头样式
        disk_storage_table.setStyleSheet("QTableView::item:selected{background-color: #daeefe}")  # 设置行选中样式
        disk_storage_table.horizontalHeader().setHighlightSections(False)  # 设置表头不会因为点击表格而变色
        disk_storage_table.verticalHeader().setVisible(False)  # 设置隐藏列表号
        disk_storage_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置选中单位为行，而不是单元格
        disk_storage_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置禁止编辑
        disk_storage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 设置表宽度自适应性扩展
        # disk_storage_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 将竖直的滑动条隐藏，避免遮挡内容

        # 绑定事件
        # disk_storage_table.clicked.connect(lambda: printSize())
        disk_storage_table.clicked.connect(lambda: self.set_selected_disk_id(disk_storage_table.selectedRanges()))
        disk_storage_table.clicked.connect(lambda: set_health_state())
        disk_storage_table.clicked.connect(lambda: set_disk_io_line(disk_storage_table.selectedRanges(), False))

        disk_storage_table_widget = QWidget()
        disk_storage_table_layout = QVBoxLayout()
        disk_storage_table_layout.addWidget(disk_title)
        disk_storage_table_layout.addWidget(disk_storage_table)
        disk_storage_table_widget.setLayout(disk_storage_table_layout)

        # 定义内部函数事件，初始化或者是到刷新周期后，从disk_storage_info_list中取数据放入disk_storage_table中去
        def show_disks_storage_list():
            global line
            # if self.currentIndex() == 0 and tabCounts == 0:  # 表示添加详细页时初次调用函数，此时currentIndex是0
            #     print("1-------------")
            #     disks_storage_info_list = self.server_detailed_info[self.count() - 1]
            # else:
            self.server_detailed_info[tabCounts] = in_interface_impl.get_server_detailed_info(self.selected_disk_id[tabCounts][0], 0)
            disks_storage_info_list = self.server_detailed_info[tabCounts]

            disk_storage_table.setRowCount(len(disks_storage_info_list))
            # disk_storage_table.clear()  # 清空刷新前的所有项
            for i, single_disk_info in enumerate(disks_storage_info_list):
                disk_storage_table.setRowHeight(i, 60)
                # 添加单元格信息
                if not self.exception_list:  # 还有硬盘图标闪烁
                    line = get_disk_storage_info_item(single_disk_info)
                else:
                    for e in self.exception_list[1]:
                        if single_disk_info.diskID == e[0]:
                            e[1] = 0 - e[1]  # 将标志反转
                            line = get_disk_storage_info_item(single_disk_info, e[1])
                        else:
                            line = get_disk_storage_info_item(single_disk_info)
                for j, cell in enumerate(line):
                    if j == 0:
                        disk_storage_table.setCellWidget(i, j, cell)
                        continue
                    cell_widget = QWidget()
                    cell_layout = QHBoxLayout()
                    cell_layout.setContentsMargins(0, 0, 0, 0)
                    cell_layout.addWidget(cell, alignment=Qt.AlignCenter)
                    cell_widget.setLayout(cell_layout)
                    disk_storage_table.setCellWidget(i, j, cell_widget)

        show_disks_storage_list()

        # 健康度条形图和I/O负载信息
        disk_detailed_info_layout = QVBoxLayout()
        disk_detailed_info_widget = QWidget()

        # 健康度条形图
        health_degree_layout = QVBoxLayout()
        heath_title_layout = QHBoxLayout()
        health_degree_item_layout = QHBoxLayout()
        health_degree_text_layout = QHBoxLayout()
        health_degree_title = QLabel("硬盘健康度")
        health_degree_title.setStyleSheet("font-size:20px; font-color:black; font-family:'黑体'")
        heath_title_layout.addWidget(health_degree_title)
        # 剩余寿命条形图
        remaining_days_layout = QVBoxLayout()
        days_title_layout = QHBoxLayout()
        remaining_days_item_layout = QHBoxLayout()
        remaining_days_text_layout = QHBoxLayout()
        remaining_days_title = QLabel("硬盘剩余寿命")
        remaining_days_title.setStyleSheet("font-size:20px; font-color:black; font-family:'黑体'")
        days_title_layout.addWidget(remaining_days_title)

        def set_health_state():
            # if self.currentIndex() > len(self.selected_disk_id):
            #     return
            # if self.currentIndex() == 0:  # 表示添加详细页时初次调用函数，此时currenIndex是0
            #     degree = in_interface_impl.get_health_degree(self.selected_disk_id[self.count() - 1][0], self.selected_disk_id[self.count() - 1][1])
            # else:
            degree = in_interface_impl.get_health_degree(self.selected_disk_id[tabCounts][0], self.selected_disk_id[tabCounts][1])
            # degree 0表示无预测结果 1-6表示一级健康度 7-9表示二级健康度
            clearLayout(remaining_days_item_layout)
            clearLayout(remaining_days_text_layout)
            clearLayout(health_degree_item_layout)
            clearLayout(health_degree_text_layout)
            if 0 < degree < 7:  # 一级健康度
                color = ['#cf0000', '#ff8303', '#f7ea00', '#fff9b0', '#c6ffc1', '#21bf73']
                days = ['<10', '<30', '<70', '<150', '<310', '>=310']
                for i in range(6):
                    item1 = QLabel()
                    item2 = QLabel()
                    if i == degree - 1:
                        item1.setStyleSheet(
                            "border-width:2px; border-style:solid; border-color:black; background-color:%s" % color[i])
                        item2.setStyleSheet(
                            "border-width:2px; border-style:solid; border-color:black; background-color:%s" % color[i])
                    else:
                        item1.setStyleSheet("background-color:%s" % color[i])
                        item2.setStyleSheet("background-color:%s" % color[i])
                    text1 = QLabel('R' + str(i + 1))
                    text1.setStyleSheet("font-size:20px; font-family:'黑体'")
                    health_degree_item_layout.addWidget(item1)
                    health_degree_text_layout.addWidget(text1, alignment=Qt.AlignCenter)
                    text2 = QLabel(days[i])
                    text2.setStyleSheet("font-size:20px; font-family:'黑体'")
                    remaining_days_item_layout.addWidget(item2)
                    remaining_days_text_layout.addWidget(text2, alignment=Qt.AlignCenter)
            elif degree >= 7:  # 二级健康度
                color = ['#cf0000', '#f55c47', '#ff7b54']
                days = ['<2', '<5', '<10']
                for i in range(3):
                    item1 = QLabel()
                    item2 = QLabel()
                    if i == degree - 7:
                        item1.setStyleSheet(
                            "border-width:2px; border-style:solid; border-color:black; background-color:%s" % color[i])
                        item2.setStyleSheet(
                            "border-width:2px; border-style:solid; border-color:black; background-color:%s" % color[i])
                    else:
                        item1.setStyleSheet("background-color:%s" % color[i])
                        item2.setStyleSheet("background-color:%s" % color[i])
                    text1 = QLabel('R1-' + str(i + 1))
                    text1.setStyleSheet("font-size:20px; font-family:'黑体'")
                    health_degree_item_layout.addWidget(item1)
                    health_degree_text_layout.addWidget(text1, alignment=Qt.AlignCenter)
                    text2 = QLabel(days[i])
                    text2.setStyleSheet("font-size:20px; font-family:'黑体'")
                    remaining_days_item_layout.addWidget(item2)
                    remaining_days_text_layout.addWidget(text2, alignment=Qt.AlignCenter)
            else:  # 无法预测健康度
                color = ['#cf0000', '#ff8303', '#f7ea00', '#fff9b0', '#c6ffc1', '#21bf73']
                days = ['<10', '<30', '<70', '<150', '<310', '>=310']
                for i in range(6):
                    item1 = QLabel()
                    item1.setStyleSheet("background-color:%s" % color[i])
                    text1 = QLabel('R' + str(i + 1))
                    text1.setStyleSheet("font-size:20px; font-family:'黑体'")
                    health_degree_item_layout.addWidget(item1)
                    health_degree_text_layout.addWidget(text1, alignment=Qt.AlignCenter)
                text2 = QLabel('''<font color=black face='黑体' size=5>该硬盘被监控时间小于20天或者不在所预测的硬盘型号中。<font>''')
                # remaining_days_item_layout.addWidget(item2)  # 没有item
                remaining_days_text_layout.addWidget(text2, alignment=Qt.AlignCenter)

        set_health_state()
        # 健康度标题、条状图、文字布局
        health_degree_layout.addLayout(heath_title_layout)
        health_degree_layout.addLayout(health_degree_item_layout)
        health_degree_layout.addLayout(health_degree_text_layout)
        remaining_days_layout.addLayout(days_title_layout)
        remaining_days_layout.addLayout(remaining_days_item_layout)
        remaining_days_layout.addLayout(remaining_days_text_layout)
        # 硬盘健康度信息，两个条形图布局
        disk_health_state_layout = QVBoxLayout()
        disk_health_state_layout.addLayout(health_degree_layout)
        disk_health_state_layout.addLayout(remaining_days_layout)

        # 硬盘I/O负载信息，折线
        disk_io_layout = QVBoxLayout()
        line_widget = QWebEngineView()

        def draw_disk_io_line():
            disk_io_width = str(disk_detailed_info_widget.size().width()) + "px"
            disk_io_height = str(disk_detailed_info_widget.size().height() - 70) + "px"

            y_data, x_data = in_interface_impl.get_io_load_input_queue_display(self.selected_disk_id[tabCounts][0], self.selected_disk_id[tabCounts][1])
            y_predict_data, _ = in_interface_impl.get_io_load_output_queue_display(self.selected_disk_id[tabCounts][0], self.selected_disk_id[tabCounts][1])
            # 起始一分钟内并没有I/O负载数据
            if not y_data:
                y_data, x_data = [0], ["12:00"]
            if not y_predict_data:
                y_predict_data = [0] * len(y_data)

            line = (Line(init_opts=opts.InitOpts(bg_color='#ffffff', width=disk_io_width, height=disk_io_height,
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
                    name="IOPS/KB",
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True)),
                xaxis_opts=opts.AxisOpts(
                    name="时间",
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_inside=True),
                    boundary_gap=False))
                    .render("./html/" + self.selected_disk_id[tabCounts][1] + "_io.html"))  # 各硬盘有单独的IO图

            line_widget.setContentsMargins(0, 50, 0, 0)
            line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)  # 将滑动条隐藏，避免遮挡内容
            line_widget.setFixedSize(disk_detailed_info_widget.size().width(), disk_detailed_info_widget.size().height())
            # 打开本地html文件
            line_widget.load(QUrl("file:///./html/" + self.selected_disk_id[tabCounts][1] + "_io.html"))
            disk_io_layout.addWidget(line_widget, alignment=Qt.AlignCenter)

        def set_disk_io_line(disk_selected, IsUpdate):
            # if self.currentIndex() > len(self.selected_disk_id):
            #     return
            # disk_selected是获取的选择表格某行的范围信息
            if IsUpdate:
                print("update disk_info per second...")
                pass  # 刷新的情况下直接用当前serverIP得到I/O负载数据
            else:
                if disk_selected is None:
                    print('默认选中第一个disk')
                else:
                    print(self.server_detailed_info[self.currentIndex() - 1][disk_selected[0].topRow()].diskID)  # 获取到选中的diskID，得到负载数据

            disk_io_width = str(detailed_tab.size().width() / 2 - 40) + "px"
            disk_io_height = str(disk_detailed_info_widget.size().height() / 2) + "px"

            y_data, x_data = in_interface_impl.get_io_load_input_queue_display(self.selected_disk_id[tabCounts][0], self.selected_disk_id[tabCounts][1])
            y_predict_data, x_predict_data = in_interface_impl.get_io_load_output_queue_display(self.selected_disk_id[tabCounts][0], self.selected_disk_id[tabCounts][1])
            if not y_data:
                y_data, x_data = [0], ["12:00"]

            if not x_predict_data:
                line = (Line(init_opts=opts.InitOpts(bg_color='#ffffff', width=disk_io_width, height=disk_io_height,
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
                        .render("./html/" + self.selected_disk_id[tabCounts][1] + "_io.html"))
            else:
                if len(y_predict_data) != len(y_data):
                    y_predict_data_ = [None] * (len(y_data) - len(y_predict_data)) + y_predict_data
                    x_predict_data_ = [None] * (len(y_data) - len(y_predict_data)) + x_predict_data
                else:
                    x_predict_data_ = x_predict_data
                    y_predict_data_ = y_predict_data
                line = (Line(init_opts=opts.InitOpts(bg_color='#ffffff', width=disk_io_width, height=disk_io_height,
                                                     animation_opts=opts.AnimationOpts(
                                                         animation=False)))  # 设置宽高度，去掉加载动画
                        .add_xaxis(xaxis_data=x_data)
                        .extend_axis(xaxis_data=x_predict_data_)
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
                        name="IOPS/KB",
                        type_="value",
                        axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                        splitline_opts=opts.SplitLineOpts(is_show=True)),
                    xaxis_opts=opts.AxisOpts(
                        name="时间",
                        type_="category",
                        axistick_opts=opts.AxisTickOpts(is_inside=True),
                        boundary_gap=False))
                        .render("./html/" + self.selected_disk_id[tabCounts][1] + "_io.html"))

            line_widget.setContentsMargins(0, 50, 0, 0)
            line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)  # 将滑动条隐藏，避免遮挡内容
            line_widget.setFixedSize(detailed_tab.size().width() / 2 - 20, disk_detailed_info_widget.size().height() / 2 + 40)
            # 打开本地html文件
            line_widget.load(QUrl("file:///./html/" + self.selected_disk_id[tabCounts][1] + "_io.html"))

        draw_disk_io_line()

        # 历史信息的按钮
        io_button = QPushButton("历史信息")
        io_button.setFixedSize(100, 30)
        io_button.setStyleSheet('''QPushButton{background-color:white; font-size:20px; font-family:SimHei; 
                                        border-width:2px; border-style:solid; border-color:black; border-radius:12px}
                                        QPushButton:pressed{background-color:#bbbbbb}''')
        io_button.clicked.connect(lambda: self.show_history_io_line(0))  # 绑定事件
        disk_io_layout.addWidget(io_button, alignment=Qt.AlignTop | Qt.AlignCenter)

        disk_detailed_info_layout.addLayout(disk_health_state_layout)
        disk_detailed_info_layout.addLayout(disk_io_layout)
        disk_detailed_info_widget.setLayout(disk_detailed_info_layout)

        # 全局布局
        detailed_tab = QWidget()
        whole2_layout = QHBoxLayout()
        whole2_layout.setContentsMargins(0, 0, 0, 0)
        whole2_layout.addWidget(disk_storage_table_widget)
        whole2_layout.addWidget(disk_detailed_info_widget)
        detailed_tab.setLayout(whole2_layout)

        # def printSize():
        #     print("detailed...............")
        #     print("disk_storage_table_widget", disk_storage_table_widget.size())
        #     print("disk_detailed_info_widget", disk_detailed_info_widget.size())
        #     print("detailed_tab", detailed_tab.size())
        #
        # printSize()

        self.addTab(detailed_tab, "详细信息")
        # self.tabCloseRequested.connect(lambda: self.deleteDict(tabCounts))  # 绑定tab页关闭事件
        self.tabCounts += 1
        self.setCurrentIndex(self.count() - 1)

        # 定时刷新
        self.update_thread.update_data.connect(lambda: show_disks_storage_list())
        self.update_thread.update_data.connect(lambda: set_health_state())
        self.update_thread.update_data.connect(lambda: set_disk_io_line(None, True))

    def tabClose(self, index):  # 定义关闭tab页事件, index表示第几个tab页，总体信息页是0
        self.removeTab(index)

        if self.count() == 1:  # 只剩下总体信息页时将count归零
            self.tabCounts = 0
        # self.selected_disk_id.remove(index - 1)
        # del self.selected_disk_id[index - 1]

    def deleteDict(self, tabCounts):  # 删除字典的对应数据
        time.sleep(1)
        self.selected_disk_id.pop(tabCounts)
        self.server_detailed_info.pop(tabCounts)

    def set_selected_server_ip(self, server_selected):
        self.selected_server_ip = self.server_overall_info[server_selected[0].topRow()].serverIP  # 获取到选中的serverIP
        # print("selected:", self.selected_server_ip)

    def set_selected_disk_id(self, disk_selected):
        # index 表示当前tab页在selected_disk_id列表中对应的索引
        # 如果有异常硬盘图标闪烁，单击后去掉闪烁效果，即对应exception_list删除
        if self.exception_list:
            for e in self.exception_list[1]:
                if e[0] == self.selected_disk_id[self.currentIndex() - 1][1]:
                    self.exception_list[1].remove(e)
                    break
        self.selected_disk_id[self.currentIndex() - 1][1] = self.server_detailed_info[self.currentIndex() - 1][disk_selected[0].topRow()].diskID  # 获取到选中的diskID

    # 查看历史I/O负载信息
    def show_history_io_line(self, level):
        self.server_history_io = HistoryIO(self.selected_disk_id[self.currentIndex() - 1][0],
                                           self.selected_disk_id[self.currentIndex() - 1][1], level) if level == 0 \
            else HistoryIO(self.selected_server_ip, "", level)
        self.server_history_io.show()

