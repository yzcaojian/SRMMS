# -*- coding: utf-8 -*-
# @ModuleName: detailed_info_tab
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/6/15 10:14
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QLabel, QPushButton,\
    QTableWidget, QAbstractItemView, QHeaderView
from pyecharts.charts import Line
from pyecharts import options as opts
from resource_status_display.history_io_display import HistoryIO
from interface.in_interface import in_interface_impl
from resource_status_display.backward_thread import UpdateTabDataThread
from resource_status_display.get_info_item import get_disk_storage_info_item


def clearLayout(layout):
    if layout is not None:
        # print(layout.count())
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()


class DetailedInfoTab(QTabWidget):
    def __init__(self, server_selected_ip, lock):
        super().__init__()
        self.selected_server_ip = server_selected_ip
        self.selected_disk_id = None
        self.update_thread = UpdateTabDataThread(lock)
        self.exception_dict = in_interface_impl.get_exception_dict()
        self.detailed_tab = None
        self.server_detailed_info = None
        self.initUI()
        self.update_thread.start()

    def initUI(self):

        self.server_detailed_info = in_interface_impl.get_server_detailed_info(self.selected_server_ip, 0)
        # 添加详细信息tab页后默认选中第一块硬盘
        if len(self.server_detailed_info) != 0:

            self.selected_disk_id = [self.selected_server_ip, self.server_detailed_info[0].diskID]

        # 详细信息的tab页
        # 服务器详细信息表和硬盘健康度、I/O负载图的布局
        # 服务器详细信息表
        disk_title = QLabel('''<font color=black face='黑体' size=5>服务器详细信息<font>''')
        disk_title.setAlignment(Qt.AlignCenter)
        disk_title.setStyleSheet("background-color:#dddddd;width:100px")
        disk_storage_table = QTableWidget(len(self.server_detailed_info), 6)
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
        disk_storage_table.clicked.connect(lambda: set_disk_io_line())

        disk_storage_table_widget = QWidget()
        disk_storage_table_layout = QVBoxLayout()
        disk_storage_table_layout.addWidget(disk_title)
        disk_storage_table_layout.addWidget(disk_storage_table)
        disk_storage_table_widget.setLayout(disk_storage_table_layout)

        # 定义内部函数事件，初始化或者是到刷新周期后，从disk_storage_info_list中取数据放入disk_storage_table中去
        def show_disks_storage_list():
            global line
            self.server_detailed_info = in_interface_impl.get_server_detailed_info(
                self.selected_disk_id[0], 0)
            disks_storage_info_list = self.server_detailed_info

            disk_storage_table.setRowCount(len(disks_storage_info_list))
            # disk_storage_table.clear()  # 清空刷新前的所有项
            for i, single_disk_info in enumerate(disks_storage_info_list):
                disk_storage_table.setRowHeight(i, 60)
                # 添加单元格信息
                if self.selected_server_ip in self.exception_dict:
                    if single_disk_info.diskID not in self.exception_dict[self.selected_server_ip][1]:  # 还有硬盘图标闪烁
                        line = get_disk_storage_info_item(single_disk_info)
                    else:
                        self.exception_dict[self.selected_server_ip][1][single_disk_info.diskID] = -self.exception_dict[self.selected_server_ip][1][single_disk_info.diskID]
                        line = get_disk_storage_info_item(single_disk_info, self.exception_dict[self.selected_server_ip][1][single_disk_info.diskID])
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
        disk_storage_table.selectRow(0)  # 设置默认选中第一行

        # 健康度条形图和I/O负载信息
        disk_detailed_info_layout = QVBoxLayout()
        disk_detailed_info_widget = QWidget()

        # 健康度条形图，图例
        disk_health_state_layout = QVBoxLayout()

        health_degree_layout = QVBoxLayout()
        heath_title_layout = QHBoxLayout()
        former_item_layout = QHBoxLayout()
        former_text_layout = QHBoxLayout()
        health_degree_item_layout = QHBoxLayout()
        health_degree_text_layout = QHBoxLayout()
        health_degree_title = QLabel("硬盘健康度（图例）")
        health_degree_title.setStyleSheet("font-size:20px; font-color:black; font-family:'黑体'")
        heath_title_layout.addWidget(health_degree_title)
        # 剩余寿命条形图，对应预测结果
        remaining_days_layout = QVBoxLayout()
        days_title_layout = QHBoxLayout()
        remaining_days_item_layout = QHBoxLayout()
        remaining_days_text_layout = QHBoxLayout()
        remaining_days_title = QLabel("硬盘剩余寿命预测")
        remaining_days_title.setContentsMargins(0, 0, 0, 10)
        remaining_days_title.setStyleSheet("font-size:20px; font-color:black; font-family:'黑体'")
        days_title_layout.addWidget(remaining_days_title)

        health_degree_layout.addLayout(heath_title_layout)
        remaining_days_layout.addLayout(days_title_layout)

        def set_health_state():
            degree = in_interface_impl.get_health_degree(self.selected_disk_id[0], self.selected_disk_id[1])
            # degree 0表示无预测结果 1-6表示一级健康度 7-9表示二级健康度
            clearLayout(former_item_layout)
            clearLayout(former_text_layout)
            clearLayout(remaining_days_item_layout)
            clearLayout(remaining_days_text_layout)
            clearLayout(health_degree_item_layout)
            clearLayout(health_degree_text_layout)
            # clearLayout(health_degree_layout)
            if 0 < degree < 7:  # 一级健康度
                color = ['#cf0000', '#ff8303', '#f7ea00', '#fff9b0', '#c6ffc1', '#21bf73']
                days = ['<10', '<30', '<70', '<150', '<310', '>=310']
                for i in range(6):
                    item1 = QLabel()
                    item2 = QLabel()
                    if i == degree - 1:
                        item2.setStyleSheet("background-color:%s" % color[i])
                    else:
                        item2.setStyleSheet("background-color:white")
                    item1.setStyleSheet("background-color:%s" % color[i])
                    text1 = QLabel('R' + str(i + 1) + '(' + days[i] + '天)')
                    text1.setStyleSheet("font-size:20px; font-family:'黑体'")
                    health_degree_item_layout.addWidget(item1)
                    health_degree_text_layout.addWidget(text1, alignment=Qt.AlignCenter)
                    remaining_days_item_layout.addWidget(item2)

                    # 设置布局之间比例划分
                    # 设置第一行和第二行的长度比为3:2
                    disk_health_state_layout.setStretch(0, 3)
                    disk_health_state_layout.setStretch(1, 2)
            elif degree >= 7:  # 二级健康度
                color_1 = ['#cf0000', '#ff8303', '#f7ea00', '#fff9b0', '#c6ffc1', '#21bf73']
                days_1 = ['<10', '<30', '<70', '<150', '<310', '>=310']
                color_2 = ['#cf0000', '#f55c47', '#ff7b54']
                days_2 = ['<2', '<5', '<10']
                for i in range(6):
                    item1 = QLabel()
                    item1.setStyleSheet("background-color:%s" % color_1[i])
                    text1 = QLabel('R' + str(i + 1) + '(' + days_1[i] + '天)')
                    text1.setStyleSheet("font-size:20px; font-family:'黑体'")
                    former_item_layout.addWidget(item1)
                    former_text_layout.addWidget(text1)
                for i in range(6):
                    item2 = QLabel()
                    if i < 3:
                        item2.setStyleSheet("background-color:white")
                        text2 = QLabel()
                    else:
                        item2.setStyleSheet("background-color:%s" % color_2[i - 3])
                        text2 = QLabel('R1-' + str(i + 7) + '(' + days_2[i - 3] + '天)')
                    text2.setStyleSheet("font-size:20px; font-family:'黑体'")
                    health_degree_item_layout.addWidget(item2)
                    health_degree_text_layout.addWidget(text2, alignment=Qt.AlignCenter)
                for i in range(6):
                    item3 = QLabel()
                    if i < degree - 4:
                        if i == 0:
                            item3.setStyleSheet("background-color:%s" % color_1[i])
                        else:
                            item3.setStyleSheet("background-color:white")
                    elif i == degree - 4:
                        item3.setStyleSheet("background-color:%s" % color_2[i - 3])
                    else:
                        item3.setStyleSheet("background-color:white")
                    remaining_days_item_layout.addWidget(item3)

                    # 设置布局之间比例划分
                    disk_health_state_layout.setStretch(0, 5)
                    disk_health_state_layout.setStretch(1, 2)
            else:  # 无法预测健康度
                color = ['#cf0000', '#ff8303', '#f7ea00', '#fff9b0', '#c6ffc1', '#21bf73']
                days = ['<10', '<30', '<70', '<150', '<310', '>=310']
                for i in range(6):
                    item1 = QLabel()
                    item1.setStyleSheet("background-color:%s" % color[i])
                    text1 = QLabel('R' + str(i + 1) + '(' + days[i] + '天)')
                    text1.setStyleSheet("font-size:20px; font-family:'黑体'")
                    health_degree_item_layout.addWidget(item1)
                    health_degree_text_layout.addWidget(text1, alignment=Qt.AlignCenter)
                text2 = QLabel('''<font color=black face='黑体' size=5>该硬盘被监控时间小于20天或者不在所预测的硬盘型号中。<font>''')
                # remaining_days_item_layout.addWidget(item2)  # 没有item
                remaining_days_text_layout.addWidget(text2, alignment=Qt.AlignCenter)

                # 设置布局之间比例划分
                disk_health_state_layout.setStretch(0, 2)
                disk_health_state_layout.setStretch(1, 1)

        set_health_state()
        # 健康度标题、条状图、文字布局
        health_degree_layout.addLayout(former_item_layout)
        health_degree_layout.addLayout(former_text_layout)
        health_degree_layout.addLayout(health_degree_item_layout)
        health_degree_layout.addLayout(health_degree_text_layout)
        remaining_days_layout.addLayout(remaining_days_item_layout)
        remaining_days_layout.addLayout(remaining_days_text_layout)

        # I/O图提示信息
        tip_layout = QVBoxLayout()
        io_title = QLabel("硬盘I/O负载信息")
        io_title.setStyleSheet("font-size:20px; font-color:black; font-family:'黑体'")
        io_title.setContentsMargins(0, 50, 0, 10)
        tip_layout.addWidget(io_title)
        tip_label_1 = QLabel('''<font color=black face='黑体' size=3>注1：默认显示硬盘三小时内的实时和预测I/O负载信息；<font>''')
        tip_label_2 = QLabel('''<font color=black face='黑体' size=3>注2：每个点纵坐标表示该硬盘一分钟内的IO总和。<font>''')
        tip_layout.addWidget(tip_label_1)
        tip_layout.addWidget(tip_label_2)
        tip_label_1.setContentsMargins(20, 0, 0, 0)
        tip_label_2.setContentsMargins(20, 0, 0, 0)

        # 硬盘健康度信息，两个条形图，io注释信息布局
        disk_health_state_layout.addLayout(health_degree_layout)
        disk_health_state_layout.addLayout(remaining_days_layout)

        # 硬盘I/O负载信息，折线
        disk_io_layout = QVBoxLayout()
        disk_io_layout.addLayout(tip_layout)
        line_widget = QWebEngineView()

        # 历史信息的按钮
        io_button = QPushButton("查看历史信息")
        io_button.setFixedSize(130, 30)
        io_button.setStyleSheet('''QPushButton{background-color:white; font-size:20px; font-family:SimHei; 
                                               border-width:2px; border-style:solid; border-color:black; border-radius:12px}
                                               QPushButton:pressed{background-color:#bbbbbb}''')
        io_button.clicked.connect(lambda: self.show_history_io_line(0))  # 绑定事件

        def draw_disk_io_line():
            disk_io_width = str(disk_detailed_info_widget.size().width()) + "px"
            disk_io_height = str(disk_detailed_info_widget.size().height() / 2 - 50) + "px"

            y_data, x_data = in_interface_impl.get_io_load_input_queue_display(self.selected_disk_id[0],
                                                                               self.selected_disk_id[1])
            y_predict_data, _ = in_interface_impl.get_io_load_output_queue_display(self.selected_disk_id[0],
                                                                                   self.selected_disk_id[1])
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
                    name="每分钟IO/KB",
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True)),
                xaxis_opts=opts.AxisOpts(
                    name="时间",
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_inside=True),
                    boundary_gap=False))
                    .render("./html/" + self.selected_disk_id[1] + "_io.html"))  # 各硬盘有单独的IO图

            line_widget.setContentsMargins(0, 20, 0, 0)
            line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)  # 将滑动条隐藏，避免遮挡内容
            line_widget.resize(disk_detailed_info_widget.size().width(), disk_detailed_info_widget.size().height() / 2 - 30)
            # 打开本地html文件
            line_widget.load(QUrl("file:///./html/" + self.selected_disk_id[1] + "_io.html"))
            disk_io_layout.addWidget(line_widget)
            disk_io_layout.addWidget(io_button, alignment=Qt.AlignCenter | Qt.AlignTop)

        def set_disk_io_line():
            disk_io_width = str(self.detailed_tab.size().width() / 2 - 40) + "px"
            disk_io_height = str(disk_detailed_info_widget.size().height() / 2 - 40) + "px"

            y_data, x_data = in_interface_impl.get_io_load_input_queue_display(self.selected_disk_id[0], self.selected_disk_id[1])
            y_predict_data, x_predict_data = in_interface_impl.get_io_load_output_queue_display(
                self.selected_disk_id[0], self.selected_disk_id[1])
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
                        name="每分钟IO/KB",
                        type_="value",
                        axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                        splitline_opts=opts.SplitLineOpts(is_show=True)),
                    xaxis_opts=opts.AxisOpts(
                        name="时间",
                        type_="category",
                        axistick_opts=opts.AxisTickOpts(is_inside=True),
                        boundary_gap=False))
                        .render("./html/" + self.selected_disk_id[1] + "_io.html"))
            else:
                time_list = in_interface_impl.merge_timeline(x_data, x_predict_data)
                y_data_ = y_data + [None] * (len(time_list) - len(y_data))
                y_predict_data_ = [None] * (len(time_list) - len(y_predict_data)) + y_predict_data

                line = (Line(init_opts=opts.InitOpts(bg_color='#ffffff', width=disk_io_width, height=disk_io_height,
                                                     animation_opts=opts.AnimationOpts(
                                                         animation=False)))  # 设置宽高度，去掉加载动画
                        .add_xaxis(xaxis_data=time_list)
                        .add_yaxis(
                    series_name="实时I/O负载",
                    y_axis=y_data_,
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
                        .render("./html/" + self.selected_disk_id[1] + "_io.html"))

            line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)  # 将滑动条隐藏，避免遮挡内容
            line_widget.setFixedSize(self.detailed_tab.size().width() / 2 - 20,
                                     disk_detailed_info_widget.size().height() / 2 - 20)
            # 打开本地html文件
            line_widget.load(QUrl("file:///./html/" + self.selected_disk_id[1] + "_io.html"))

        draw_disk_io_line()

        disk_detailed_info_layout.addLayout(disk_health_state_layout)
        disk_detailed_info_layout.addLayout(disk_io_layout)
        disk_detailed_info_widget.setLayout(disk_detailed_info_layout)

        # 全局布局
        self.detailed_tab = QWidget()
        whole2_layout = QHBoxLayout()
        whole2_layout.setContentsMargins(0, 0, 0, 0)
        whole2_layout.addWidget(disk_storage_table_widget)
        whole2_layout.addWidget(disk_detailed_info_widget)
        self.detailed_tab.setLayout(whole2_layout)

        # 定时刷新
        self.update_thread.update_data.connect(lambda: show_disks_storage_list())
        self.update_thread.update_data.connect(lambda: set_health_state())
        self.update_thread.update_data.connect(lambda: set_disk_io_line())

    def set_selected_disk_id(self, disk_selected):
        # index 表示当前tab页在selected_disk_id列表中对应的索引
        # 如果有异常硬盘图标闪烁，单击后去掉闪烁效果，即对应exception_dict删除

        self.selected_disk_id[1] = self.server_detailed_info[disk_selected[0].topRow()].diskID  # 获取到选中的diskID

        if self.selected_server_ip in self.exception_dict:
            if self.selected_disk_id[1] in self.exception_dict[self.selected_server_ip][1]:
                del self.exception_dict[self.selected_server_ip][1][self.selected_disk_id[1]]

        # 如果对应服务器内无硬盘图标闪烁，则去掉该服务器图标闪烁效果，即对应exception_dict删除
        if self.selected_server_ip in self.exception_dict:
            if not self.exception_dict[self.selected_server_ip][1]:
                del self.exception_dict[self.selected_server_ip]

        # 查看历史I/O负载信息

    def show_history_io_line(self, level):
        self.server_history_io = HistoryIO(self.selected_disk_id[0], self.selected_disk_id[1], level)
        self.server_history_io.show()
