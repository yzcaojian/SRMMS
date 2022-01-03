# -*- coding: utf-8 -*-
# @ModuleName: detailed_info_tab
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/6/15 10:14
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QLabel, QPushButton, \
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
        # self.health_state = {}
        self.server_detailed_info = None
        self.bind_thread = self.initUI()  # 用于绑定线程和刷新图表的信号槽的函数
        self.update_thread.start()

    def initUI(self):

        self.server_detailed_info = in_interface_impl.get_server_detailed_info(self.selected_server_ip, 0)
        # 添加详细信息tab页后默认选中第一块硬盘
        if len(self.server_detailed_info) != 0:
            self.selected_disk_id = [self.selected_server_ip, self.server_detailed_info[0].diskID]

        # 详细信息的tab页
        # 服务器详细信息表和硬盘健康度、I/O负载图的布局
        # 服务器详细信息表
        disk_title = QLabel('''<font color=white face='黑体' size=5>服务器详细信息<font>''')
        disk_title.setStyleSheet("background-color:rgb(12, 25, 73);width:100px")
        disk_storage_table = QTableWidget(len(self.server_detailed_info), 6)
        disk_storage_table.setHorizontalHeaderLabels(['硬盘标识', '硬盘类型', '状态', '存储总容量', '已使用容量', '存储占用率'])  # 设置表头
        disk_storage_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color:#007580; font:12pt SimHei; color:white}")  # 设置表头样式
        disk_storage_table.setStyleSheet("QTableWidget{color:white; background-color:rgb(12, 25, 73);}"
                                         "QTableView::item:selected{background: #1687A7}")  # 设置行选中样式
        disk_storage_table.horizontalHeader().setHighlightSections(False)  # 设置表头不会因为点击表格而变色
        disk_storage_table.verticalHeader().setVisible(False)  # 设置隐藏列表号
        disk_storage_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置选中单位为行，而不是单元格
        disk_storage_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置禁止编辑
        disk_storage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 设置表宽度自适应性扩展

        # 绑定事件
        # disk_storage_table.clicked.connect(lambda: printSize())
        disk_storage_table.clicked.connect(lambda: self.set_selected_disk_id(disk_storage_table.selectedRanges()))
        disk_storage_table.clicked.connect(lambda: set_health_state())
        disk_storage_table.clicked.connect(lambda: set_disk_io_line())

        disk_storage_table_widget = QWidget()
        disk_storage_table_layout = QVBoxLayout()
        disk_storage_table_layout.addWidget(disk_title, alignment=Qt.AlignLeft)
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
                        self.exception_dict[self.selected_server_ip][1][single_disk_info.diskID] = - \
                            self.exception_dict[self.selected_server_ip][1][single_disk_info.diskID]
                        line = get_disk_storage_info_item(single_disk_info,
                                                          self.exception_dict[self.selected_server_ip][1][
                                                              single_disk_info.diskID])
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
        health_degree_title.setStyleSheet("font-size:20px; color:white; font-family:'黑体'")
        heath_title_layout.addWidget(health_degree_title)

        # 可预测硬盘的提示信息
        tip_image = QLabel()
        tip_image.setFixedSize(20, 20)
        png = QPixmap('./resources/png/tips.png').scaled(18, 18)
        tip_image.setContentsMargins(0, 0, 30, 0)
        tip_image.setPixmap(png)
        tip_image.setToolTip("可预测硬盘型号：\n希捷 ST4000DM000\n希捷 ST8000DM002\n希捷 ST8000NM0055\n希捷 ST12000NM0007\n日立 "
                             "HDS722020ALA330\n昱科 HGST HMS5C4040ALE640\n昱科 HGST HMS5C4040ALE640\n西部数据 WDC "
                             "WD30EFRX\n东芝 TOSHIBA MQ01ABF050")
        heath_title_layout.addWidget(tip_image, alignment=Qt.AlignRight)

        # 剩余寿命条形图，对应预测结果
        remaining_days_layout = QVBoxLayout()
        days_title_layout = QHBoxLayout()
        remaining_days_item_layout = QHBoxLayout()
        remaining_days_text_layout = QHBoxLayout()
        remaining_days_title = QLabel("硬盘剩余寿命预测")
        remaining_days_title.setContentsMargins(0, 0, 0, 10)
        remaining_days_title.setStyleSheet("font-size:20px; color:white; font-family:'黑体'")
        days_title_layout.addWidget(remaining_days_title)

        health_degree_layout.addLayout(heath_title_layout)
        remaining_days_layout.addLayout(days_title_layout)

        def set_health_state():
            clearLayout(former_item_layout)
            clearLayout(former_text_layout)
            clearLayout(remaining_days_item_layout)
            clearLayout(remaining_days_text_layout)
            clearLayout(health_degree_item_layout)
            clearLayout(health_degree_text_layout)

            # degree说明：1-6表示一级健康度，7-9表示二级健康度，0表示时间数据不够20天，-1表示型号不匹配，-2表示无法获取型号
            degree = -2  # 无法获取硬盘型号
            model = in_interface_impl.get_disk_model(self.selected_disk_id[0], self.selected_disk_id[1])
            if model != "":
                remaining_days_title.setText("硬盘剩余寿命预测（硬盘型号为：" + model + "）")
                if model not in {"ST4000DM000", "ST8000DM002", "ST8000NM0055", "ST12000NM0007", "WD30EFRX",
                                 "HMS5C4040ALE640", "HMS5C4040BLE640", "HDS722020ALA330", "MQ01ABF050"}:
                    degree = -1
                else:
                    degree = in_interface_impl.get_health_degree(self.selected_disk_id[0], self.selected_disk_id[1])
            else:
                remaining_days_title.setText("硬盘剩余寿命预测")

            if 0 < degree < 7:  # 一级健康度
                color = ['#cf0000', '#ff8303', '#f7ea00', '#fff9b0', '#c6ffc1', '#21bf73']
                days = ['<10', '<30', '<70', '<150', '<310', '>=310']
                for i in range(6):
                    item1 = QLabel()
                    item2 = QLabel()
                    if i == degree - 1:
                        item2.setStyleSheet("background-color:%s" % color[i])
                    else:
                        item2.setStyleSheet("background-color:#0c1949")
                    item1.setStyleSheet("background-color:%s" % color[i])
                    text1 = QLabel('R' + str(i + 1) + '(' + days[i] + '天)')
                    text1.setStyleSheet("font-size:20px; font-family:'黑体'; color:white")
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
                    text1.setStyleSheet("font-size:20px; font-family:'黑体'; color:white")
                    former_item_layout.addWidget(item1)
                    former_text_layout.addWidget(text1)
                for i in range(6):
                    item2 = QLabel()
                    if i < 3:
                        item2.setStyleSheet("background-color:#0c1949")
                        text2 = QLabel()
                    else:
                        item2.setStyleSheet("background-color:%s" % color_2[i - 3])
                        text2 = QLabel('R1-' + str(i - 2) + '(' + days_2[i - 3] + '天)')
                    text2.setStyleSheet("font-size:20px; font-family:'黑体'; color:white")
                    health_degree_item_layout.addWidget(item2)
                    health_degree_text_layout.addWidget(text2, alignment=Qt.AlignCenter)
                for i in range(6):
                    item3 = QLabel()
                    if i < degree - 4:
                        if i == 0:
                            item3.setStyleSheet("background-color:%s" % color_1[i])
                        else:
                            item3.setStyleSheet("background-color:#0c1949")
                    elif i == degree - 4:
                        item3.setStyleSheet("background-color:%s" % color_2[i - 3])
                    else:
                        item3.setStyleSheet("background-color:#0c1949")
                    remaining_days_item_layout.addWidget(item3)

                # 设置布局之间比例划分
                disk_health_state_layout.setStretch(0, 5)
                disk_health_state_layout.setStretch(1, 2)
            else:  # 数据采集时间少于20天/硬盘型号不匹配/硬盘型号无法获取
                color = ['#cf0000', '#ff8303', '#f7ea00', '#fff9b0', '#c6ffc1', '#21bf73']
                days = ['<10', '<30', '<70', '<150', '<310', '>=310']
                for i in range(6):
                    item1 = QLabel()
                    item1.setStyleSheet("background-color:%s" % color[i])
                    text1 = QLabel('R' + str(i + 1) + '(' + days[i] + '天)')
                    text1.setStyleSheet("font-size:20px; font-family:'黑体'; color:white")
                    health_degree_item_layout.addWidget(item1)
                    health_degree_text_layout.addWidget(text1, alignment=Qt.AlignCenter)
                current_days = in_interface_impl.get_current_smart_data_len(self.selected_disk_id[0],
                                                                            self.selected_disk_id[1])

                text2 = QLabel()
                text2.setStyleSheet("font-family:'黑体'; font-size: 24px; color:white")
                # text_font = QFont("黑体", 14)
                # text2.setFont(text_font)
                text2.setText("该硬盘被监控时间为" + str(current_days) + "天（小于20天）内，暂时无法进行预测。")
                if degree == -1:
                    text2.setText("该硬盘型号不在所预测的硬盘型号中。")
                elif degree == -2:
                    text2.setText("无法获取该硬盘的型号信息。")
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
        io_title.setStyleSheet("font-size:20px; color:white; font-family:'黑体'")
        io_title.setContentsMargins(0, 30, 0, 10)
        tip_layout.addWidget(io_title)
        tip_label_1 = QLabel('''<font face='黑体' size=3 color='white'>注1：默认显示硬盘三小时内的实时和预测I/O负载信息；<font>''')
        tip_label_2 = QLabel('''<font face='黑体' size=3 color='white'>注2：每个点纵坐标表示该硬盘一分钟内的IO总和。<font>''')
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
        line_widget.page().setBackgroundColor(QColor(12, 25, 73))

        # 历史信息的按钮
        io_button = QPushButton("查看历史信息")
        io_button.setFixedSize(130, 30)
        io_button.setStyleSheet('''QPushButton{background-color:white; font-size:20px; font-family:SimHei; 
                                               border-width:2px; border-style:solid; border-color:#7efaff; border-radius:12px}
                                               QPushButton:pressed{background-color:#71dfe7}''')
        io_button.clicked.connect(lambda: self.show_history_io_line(0))  # 绑定事件

        def draw_disk_io_line():
            disk_io_width = str(disk_detailed_info_widget.width()) + "px"
            disk_io_height = str(disk_detailed_info_widget.height() // 2 - 50) + "px"

            y_data, x_data = in_interface_impl.get_io_load_input_queue_display(self.selected_disk_id[0],
                                                                               self.selected_disk_id[1])
            y_predict_data, _ = in_interface_impl.get_io_load_output_queue_display(self.selected_disk_id[0],
                                                                                   self.selected_disk_id[1])
            # 起始一分钟内并没有I/O负载数据
            if not y_data:
                y_data, x_data = [0], ["12:00"]
            if not y_predict_data:
                y_predict_data = [0] * len(y_data)

            line = (Line(init_opts=opts.InitOpts(bg_color='#0c1949', width=disk_io_width, height=disk_io_height,
                                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                    .add_xaxis(xaxis_data=x_data)
                    .add_yaxis(
                series_name="实时I/O负载",
                y_axis=y_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color='#FF4C29'), )
                    .add_yaxis(
                series_name="预测I/O负载",
                y_axis=y_predict_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color='#2940D3'), )
                    .set_global_opts(
                legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='white')),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross",
                                              background_color="rgb(12, 25, 73)", ),
                yaxis_opts=opts.AxisOpts(
                    name="每分钟IO/KB",
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                    name_textstyle_opts=opts.TextStyleOpts(color='white', ),
                    axislabel_opts=opts.LabelOpts(color='auto'),
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(is_show=True, color='#6166B3', )
                    )),
                xaxis_opts=opts.AxisOpts(
                    name="时间",
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_inside=True),
                    boundary_gap=False,
                    name_textstyle_opts=opts.TextStyleOpts(color='white', ),
                    axislabel_opts=opts.LabelOpts(color='auto'),
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(is_show=True, color='#6166B3', )
                    )))
                    .render("./resources/html/" + self.selected_disk_id[1] + "_io.html"))  # 各硬盘有单独的IO图

            line_widget.setContentsMargins(0, 20, 0, 0)
            line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)  # 将滑动条隐藏，避免遮挡内容
            line_widget.resize(disk_detailed_info_widget.width(),
                               disk_detailed_info_widget.height() // 2 - 30)
            # 打开本地html文件
            line_widget.load(QUrl("file:///./resources/html/" + self.selected_disk_id[1] + "_io.html"))
            disk_io_layout.addWidget(line_widget)
            disk_io_layout.addWidget(io_button, alignment=Qt.AlignCenter | Qt.AlignTop)

        def set_disk_io_line():
            disk_io_width = str(self.detailed_tab.width() // 2 - 60) + "px"
            disk_io_height = str(disk_detailed_info_widget.height() // 2 - 40) + "px"

            y_data, x_data = in_interface_impl.get_io_load_input_queue_display(self.selected_disk_id[0],
                                                                               self.selected_disk_id[1])
            y_predict_data, x_predict_data = in_interface_impl.get_io_load_output_queue_display(
                self.selected_disk_id[0], self.selected_disk_id[1])
            if not y_data:
                y_data, x_data = [0], ["12:00"]

            if not x_predict_data:
                line = (Line(init_opts=opts.InitOpts(bg_color='#0c1949', width=disk_io_width, height=disk_io_height,
                                                     animation_opts=opts.AnimationOpts(
                                                         animation=False)))  # 设置宽高度，去掉加载动画
                        .add_xaxis(xaxis_data=x_data)
                        .add_yaxis(
                    series_name="实时I/O负载",
                    y_axis=y_data,
                    areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                    label_opts=opts.LabelOpts(is_show=False),
                    itemstyle_opts=opts.ItemStyleOpts(color='#FF4C29'))
                        .set_global_opts(
                    legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='white')),
                    tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross",
                                                  background_color="rgb(12, 25, 73)", ),
                    yaxis_opts=opts.AxisOpts(
                        name="每分钟IO/KB",
                        type_="value",
                        axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                        splitline_opts=opts.SplitLineOpts(is_show=True),
                        name_textstyle_opts=opts.TextStyleOpts(color='white', ),
                        axislabel_opts=opts.LabelOpts(color='auto'),
                        axisline_opts=opts.AxisLineOpts(
                            linestyle_opts=opts.LineStyleOpts(is_show=True, color='#6166B3', )
                        )),
                    xaxis_opts=opts.AxisOpts(
                        name="时间",
                        type_="category",
                        axistick_opts=opts.AxisTickOpts(is_inside=True),
                        boundary_gap=False,
                        name_textstyle_opts=opts.TextStyleOpts(color='white', ),
                        axislabel_opts=opts.LabelOpts(color='auto'),
                        axisline_opts=opts.AxisLineOpts(
                            linestyle_opts=opts.LineStyleOpts(is_show=True, color='#6166B3', )
                        )))
                        .render("./resources/html/" + self.selected_disk_id[1] + "_io.html"))
            else:
                time_list = in_interface_impl.merge_timeline(x_data, x_predict_data)
                y_data_ = y_data + [None] * (len(time_list) - len(y_data))
                y_predict_data_ = [None] * (len(time_list) - len(y_predict_data)) + y_predict_data

                line = (Line(init_opts=opts.InitOpts(bg_color='#0c1949', width=disk_io_width, height=disk_io_height,
                                                     animation_opts=opts.AnimationOpts(
                                                         animation=False)))  # 设置宽高度，去掉加载动画
                        .add_xaxis(xaxis_data=time_list)
                        .add_yaxis(
                    series_name="实时I/O负载",
                    y_axis=y_data_,
                    areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                    label_opts=opts.LabelOpts(is_show=False),
                    itemstyle_opts=opts.ItemStyleOpts(color='#FF4C29'))
                        .add_yaxis(
                    series_name="预测I/O负载",
                    y_axis=y_predict_data_,
                    areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                    label_opts=opts.LabelOpts(is_show=False),
                    itemstyle_opts=opts.ItemStyleOpts(color='#2940D3'))
                        .set_global_opts(
                    legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='white')),
                    tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross",
                                                  background_color="rgb(12, 25, 73)", ),
                    yaxis_opts=opts.AxisOpts(
                        name="每分钟IO/KB",
                        type_="value",
                        axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                        splitline_opts=opts.SplitLineOpts(is_show=True),
                        name_textstyle_opts=opts.TextStyleOpts(color='white', ),
                        axislabel_opts=opts.LabelOpts(color='auto'),
                        axisline_opts=opts.AxisLineOpts(
                            linestyle_opts=opts.LineStyleOpts(is_show=True, color='#6166B3', )
                        )),
                    xaxis_opts=opts.AxisOpts(
                        name="时间",
                        type_="category",
                        axistick_opts=opts.AxisTickOpts(is_inside=True),
                        boundary_gap=False,
                        name_textstyle_opts=opts.TextStyleOpts(color='white', ),
                        axislabel_opts=opts.LabelOpts(color='auto'),
                        axisline_opts=opts.AxisLineOpts(
                            linestyle_opts=opts.LineStyleOpts(is_show=True, color='#6166B3', )
                        )))
                        .render("./resources/html/" + self.selected_disk_id[1] + "_io.html"))

            line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)  # 将滑动条隐藏，避免遮挡内容
            line_widget.setFixedSize(self.detailed_tab.width() // 2 - 40,
                                     disk_detailed_info_widget.height() // 2 - 20)
            # 打开本地html文件
            line_widget.load(QUrl("file:///./resources/html/" + self.selected_disk_id[1] + "_io.html"))

        draw_disk_io_line()

        disk_detailed_info_layout.addLayout(disk_health_state_layout)
        disk_detailed_info_layout.addLayout(disk_io_layout)
        disk_detailed_info_widget.setLayout(disk_detailed_info_layout)

        # 全局布局
        self.detailed_tab = QWidget()
        self.detailed_tab.setObjectName("tab")
        self.detailed_tab.setStyleSheet("QWidget#tab{background-color: #0c1949; border:1px solid #7efaff;}")
        whole2_layout = QHBoxLayout()
        whole2_layout.setContentsMargins(0, 0, 0, 0)
        whole2_layout.addWidget(disk_storage_table_widget)
        whole2_layout.addWidget(disk_detailed_info_widget)
        self.detailed_tab.setLayout(whole2_layout)

        # 绑定线程每秒刷新
        def bind_thread():
            self.update_thread.update_data.connect(lambda: show_disks_storage_list())
            self.update_thread.update_data.connect(lambda: set_health_state())
            self.update_thread.update_data.connect(lambda: set_disk_io_line())

        # 定时刷新
        bind_thread()
        return bind_thread

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
