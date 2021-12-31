from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QTabBar, QLabel, QPushButton, \
    QSplitter, QTableWidget, QAbstractItemView, QHeaderView, QComboBox
from pyecharts.charts import Bar, Line
from pyecharts.commons.utils import JsCode
from pyecharts import options as opts

from interface.in_interface import in_interface_impl
from resource_status_display.backward_thread import UpdateMDDataThread, UpdateRAIDDataThread, UpdateTabDataThread
from resource_status_display.history_io_display import HistoryIO
from resource_status_display.get_info_item import get_server_storage_info_item, get_volume_storage_info_item
from resource_status_display.detailed_info_tab import DetailedInfoTab
from resource_status_display.configuration_checking import configuration_info

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
        # self.selected_disk_id = []  # 选中的硬盘ID，每个tab页对应一个列表元素[server_ip, disk_id]，默认是每个服务器第一个
        self.Tab_list = []
        self.lock = lock
        self.exception_dict = in_interface_impl.get_exception_dict()  # 异常信号收集
        self.server_overall_info = in_interface_impl.get_server_overall_info(0)  # 多硬盘架构下服务器总体信息列表
        # 选中的服务器IP地址，默认是总体信息表中第一个serverIP
        self.selected_server_ip = "" if len(self.server_overall_info) == 0 else self.server_overall_info[0].serverIP
        # 选中服务器两类硬盘容量、I/O负载、数量、故障率信息列表
        self.two_disk_info = in_interface_impl.get_two_disk_info(self.selected_server_ip)
        self.server_detailed_info = {}  # 根据不同服务器IP地址查询的详细信息，类型应为列表的列表。每个元素为DiskInfo
        self.update_thread = UpdateMDDataThread(lock)  # 后台线程，每秒钟更新数据
        self.initUI()
        self.update_thread.start()

    def initUI(self):
        self.addTab(self.overall_info_tab, "总体信息")  # 初始情况下没有详细页
        self.setTabsClosable(True)  # 设置tab页可以关闭，添加关闭按钮
        # self.setMovable(True)  # 设置可以拖动
        self.tabCloseRequested.connect(self.tabClose)  # 绑定tab页关闭事件
        self.currentChanged.connect(self.tabChange)  # tab页改变时停止对折叠页面的刷新，减少资源消耗和降低卡顿
        self.tabBar().setTabButton(0, QTabBar.RightSide, None)  # 设置总体信息页不能被关闭

        # 总体信息的tab页
        # 服务器总体信息表和容量、故障率柱状图的布局
        # 服务器总体信息表
        server_title = QLabel('''<font color=#def6fe face='黑体' size=5>服务器总体信息<font>''')
        server_title.setAlignment(Qt.AlignCenter)
        server_title.setStyleSheet("background-color:rgb(12, 25, 73);width:100px")
        server_storage_table_widget = QWidget()  # 总体信息页面的总体信息表格窗口
        server_storage_table = QTableWidget(len(self.server_overall_info), 5)
        server_storage_table.setHorizontalHeaderLabels(['服务器名称', '存储总容量', '已使用容量', '存储占用率', '数据延迟'])  # 设置表头
        server_storage_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color:#007580; font:14pt SimHei; color:white}")  # 设置表头样式
        server_storage_table.setStyleSheet("QTableView::item:selected{background-color: #1687A7}"  # 设置行选中样式
                                           "QTableWidget{color:white; background-color:rgb(12, 25, 73);}")
        server_storage_table.horizontalHeader().setHighlightSections(False)  # 设置表头不会因为点击表格而变色
        server_storage_table.verticalHeader().setVisible(False)  # 设置隐藏列表号
        server_storage_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置选中单位为行，而不是单元格
        server_storage_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置禁止编辑
        server_storage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 设置表宽度自适应性扩展
        server_storage_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 设置表根据内容调整第一列宽
        # server_storage_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 将竖直的滑动条隐藏，避免遮挡内容
        server_storage_table.doubleClicked.connect(  # 双击新增详细信息界面
            lambda: self.add_detailed_tab(
                self.server_overall_info[server_storage_table.selectedRanges()[0].topRow()].serverIP, self.lock))
        # 单击对当前页面进行刷新，图表绘制函数重新执行
        server_storage_table.clicked.connect(lambda: self.set_selected_server_ip(server_storage_table.selectedRanges()))
        server_storage_table.clicked.connect(lambda: draw_two_disk_storage_bar())
        server_storage_table.clicked.connect(lambda: draw_two_disk_error_rate_bar())
        server_storage_table.clicked.connect(lambda: set_ssd_io_line())
        server_storage_table.clicked.connect(lambda: set_hdd_io_line())

        server_storage_table_layout = QVBoxLayout()
        server_storage_table_layout.addWidget(server_title, alignment=Qt.AlignLeft)
        server_storage_table_layout.addWidget(server_storage_table)
        server_storage_table_widget.setLayout(server_storage_table_layout)
        server_storage_table_widget.setMinimumSize(self.width() // 3, self.height() // 3)

        # 定义内部函数事件，初始化或者是到刷新周期后，从server_storage_info_list中取数据放入server_storage_table中去
        def show_server_storage_list():
            if self.selected_server_ip not in configuration_info.server_IPs:
                self.selected_server_ip = "" if len(self.server_overall_info) == 0 else self.server_overall_info[
                    0].serverIP
            global line
            self.server_overall_info = in_interface_impl.get_server_overall_info(0)
            server_storage_info_list = self.server_overall_info
            server_storage_table.setRowCount(len(self.server_overall_info))  # 设置表格行数
            for i, single_server_info in enumerate(server_storage_info_list):
                server_storage_table.setRowHeight(i, 60)
                update_cycle = in_interface_impl.get_update_cycle(single_server_info.serverIP)
                # 添加单元格信息
                if single_server_info.serverIP not in self.exception_dict:
                    line = get_server_storage_info_item(single_server_info, update_cycle)
                else:  # 还有服务器图标闪烁
                    self.exception_dict[single_server_info.serverIP][0] = - \
                        self.exception_dict[single_server_info.serverIP][0]
                    line = get_server_storage_info_item(single_server_info, update_cycle,
                                                        self.exception_dict[single_server_info.serverIP][0])

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
        server_storage_table.selectRow(0)  # 设置默认选中第一行

        # 两类硬盘容量与故障率柱状图
        bar_layout = QHBoxLayout()
        bar_widget = QWidget()

        # HDD和SSD容量信息表
        first_bar_widget = QWebEngineView()
        second_bar_widget = QWebEngineView()

        def draw_two_disk_storage_bar():
            two_disk_list = in_interface_impl.get_two_disk_info(self.selected_server_ip)
            if not two_disk_list:
                return
            # clearLayout(bar_layout)  # 清除之前的布局
            hdd_all = round(two_disk_list.hddTotalCapacity / 1024, 2)
            hdd_used = round(two_disk_list.hddOccupiedCapacity / 1024, 2)
            hdd_occ = round(float(two_disk_list.hddOccupiedRate[:-1]), 2)
            ssd_all = round(two_disk_list.ssdTotalCapacity / 1024, 2)
            ssd_used = round(two_disk_list.ssdOccupiedCapacity / 1024, 2)
            ssd_occ = round(float(two_disk_list.ssdOccupiedRate[:-1]), 2)
            used = [{"value": hdd_used, "percent": hdd_occ},
                    {"value": ssd_used, "percent": ssd_occ}]
            left = [{"value": hdd_all - hdd_used, "percent": 100 - hdd_occ},
                    {"value": ssd_all - ssd_used, "percent": 100 - ssd_occ}]

            bar_width = str(bar_widget.width() // 2 - 30) + "px"
            bar_height = str(bar_widget.height() - 20) + "px"

            bar = (Bar(init_opts=opts.InitOpts(bg_color='#0c1949', width=bar_width, height=bar_height,
                                               animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，, 去掉加载动画
                   .add_xaxis(["HDD", "SSD"])
                   .add_yaxis("剩余容量", left, stack="stack1", category_gap="20%", bar_width="40%", color='rgb(188, 228, 193)')
                   .add_yaxis("已使用容量", used, stack="stack1", category_gap="20%", bar_width="40%", color='rgb(244, 97, 113)')
                   .set_global_opts(
                        legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='white')),
                        yaxis_opts=opts.AxisOpts(name="容量\n单位TB", axistick_opts=opts.AxisTickOpts(is_inside=True),
                                                 name_textstyle_opts=opts.TextStyleOpts(color='white', ),
                                                 axislabel_opts=opts.LabelOpts(color='auto'),
                                                 axisline_opts=opts.AxisLineOpts(
                                                     linestyle_opts=opts.LineStyleOpts(is_show=True, color='white'))),
                        xaxis_opts=opts.AxisOpts(name="", type_='category', axistick_opts=opts.AxisTickOpts(is_inside=True),
                                                 name_textstyle_opts=opts.TextStyleOpts(color='white', ),
                                                 axislabel_opts=opts.LabelOpts(color='auto'),
                                                 axisline_opts=opts.AxisLineOpts(
                                                     linestyle_opts=opts.LineStyleOpts(is_show=True, color='white'))))
                   .set_series_opts(
                        label_opts=opts.LabelOpts(
                            position="insideLeft",
                            color='white',
                            formatter=JsCode("function(x) {return Number(x.data.value).toFixed(2) + 'TB'"
                                             "+ ' ' + Number(x.data.percent).toFixed(2) + '%';}"))
                    ).render("./resources/html/first.html"))

            first_bar_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars,
                                                     False)  # 将滑动条隐藏，避免遮挡内容
            first_bar_widget.resize(bar_widget.width() // 2 - 14, bar_widget.height())
            # 打开本地html文件
            first_bar_widget.load(QUrl("file:///./resources/html/first.html"))

        bar_layout.addWidget(first_bar_widget, alignment=Qt.AlignCenter)

        def draw_two_disk_error_rate_bar():
            two_disk_list = in_interface_impl.get_two_disk_info(self.selected_server_ip)
            if not two_disk_list:
                return

            hdd_rate = two_disk_list.hddErrorRate * 100
            ssd_rate = two_disk_list.ssdErrorRate * 100
            bar_width = str(bar_widget.width() // 2 - 30) + "px"
            bar_height = str(bar_widget.height() - 20) + "px"

            bar = (Bar(
                init_opts=opts.InitOpts(bg_color='#0c1949', width=bar_width, height=bar_height,
                                        animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                   .add_xaxis(["HDD", "SSD"])
                   .add_yaxis("", [hdd_rate, ssd_rate], category_gap="20%", bar_width="40%", color='rgb(244, 97, 113)')
                   .set_global_opts(
                yaxis_opts=opts.AxisOpts(name="故障率/%", axistick_opts=opts.AxisTickOpts(is_inside=True),
                                         name_textstyle_opts=opts.TextStyleOpts(color='white', ),
                                         axislabel_opts=opts.LabelOpts(color='auto'),
                                         axisline_opts=opts.AxisLineOpts(
                                             linestyle_opts=opts.LineStyleOpts(is_show=True, color='white'))),
                xaxis_opts=opts.AxisOpts(name="", axistick_opts=opts.AxisTickOpts(is_inside=True),
                                         name_textstyle_opts=opts.TextStyleOpts(color='white', ),
                                         axislabel_opts=opts.LabelOpts(color='auto'),
                                         axisline_opts=opts.AxisLineOpts(
                                             linestyle_opts=opts.LineStyleOpts(is_show=True, color='white'))),
                tooltip_opts=opts.TooltipOpts(
                    formatter=JsCode("function(x){return '故障率：' + parseFloat(x.data).toFixed() + '%';}")))
                   .set_series_opts(
                label_opts=opts.LabelOpts(
                    position="right",
                    color='white',
                    formatter=JsCode("function(x){return parseFloat(x.data).toFixed() + '%';}"))  # 考虑用元组更改x.data的值
            ).render("./resources/html/second.html"))

            second_bar_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars,
                                                      False)  # 将滑动条隐藏，避免遮挡内容
            second_bar_widget.resize(bar_widget.width() // 2 - 14, bar_widget.height())
            # first_bar_widget.resize(self.size().width() / 3, self.size().height() / 2 - 40)
            # 打开本地html文件
            second_bar_widget.load(QUrl("file:///./resources/html/second.html"))

        bar_layout.addWidget(second_bar_widget, alignment=Qt.AlignCenter)

        draw_two_disk_storage_bar()
        draw_two_disk_error_rate_bar()

        bar_widget.setLayout(bar_layout)

        # I/O负载信息布局
        disks_io_widget = QWidget()
        disks_io_layout = QVBoxLayout()
        disks_io_left_layout = QVBoxLayout()
        disks_io_right_layout = QVBoxLayout()
        # disks_io_left_layout.addWidget(QLabel())  # 占位
        # disks_io_right_layout.addWidget(QLabel())

        # 定义label提示信息
        tip_label = QLabel('''<font color=white face='黑体' size=4>注：设置显示SSD/HDD的实时总I/O负载信息的时间范围：<font>''')
        tip_label.setContentsMargins(40, 0, 0, 0)
        # 定义左右选择下拉框选
        comb = QComboBox()
        comb.setFixedSize(70, 20)
        comb.addItems(["7分钟", "6分钟", "5分钟", "4分钟", "3分钟"])
        comb.setStyleSheet("QComboBox{height:20px; width:20px; font-size:16px;}")
        comb.setCurrentIndex(7 - in_interface_impl.get_two_disk_io_show_time())
        # 绑定事件，通过下拉框选择限制输入框的编辑
        comb.currentIndexChanged.connect(lambda: comboBoxSelection(comb.currentIndex()))
        # 定义hdd和ssd数量label
        text = "监控硬盘分类：" + "SSD数量：" + str(self.two_disk_info.ssdCounts) if self.two_disk_info else ""
        text += "、HDD数量：" + str(self.two_disk_info.hddCounts) if self.two_disk_info else ""
        text_label = QLabel(text)
        text_label.setStyleSheet("height:20px; font-size:20px; font-family:黑体; background-color:transparent; color:white")

        tip_layout = QHBoxLayout()
        tip_layout.addWidget(tip_label, alignment=Qt.AlignRight)
        tip_layout.addWidget(comb, alignment=Qt.AlignLeft)
        tip_layout.addWidget(text_label, alignment=Qt.AlignRight)

        # 绑定事件，通过下拉框选择限制输入框的编辑
        def comboBoxSelection(index):
            #  取7 - index内分钟的数据
            in_interface_impl.change_two_disk_io_show_time(7 - index, self.lock)

        # 两个负载图各自的button
        left_button = QPushButton("查看历史信息")
        left_button.setFixedSize(130, 30)
        left_button.setStyleSheet('''QPushButton{background-color:white; font-size:20px; font-family:SimHei; 
                                border-width:2px; border-style:solid; border-color:#7efaff; border-radius:12px}
                                QPushButton:pressed{background-color:#71dfe7}''')
        right_button = QPushButton("查看历史信息")
        right_button.setFixedSize(130, 30)
        right_button.setStyleSheet('''QPushButton{background-color:white; font-size:20px; font-family:SimHei; 
                                border-width:2px; border-style:solid; border-color:#7efaff; border-radius:12px}
                                QPushButton:pressed{background-color:#71dfe7}''')
        # 绑定I/O负载历史信息弹窗事件
        left_button.clicked.connect(lambda: self.show_history_io_line(1))
        right_button.clicked.connect(lambda: self.show_history_io_line(2))

        # 左边I/O负载图
        first_line_widget = QWebEngineView()

        def draw_ssd_io_line():
            if not self.selected_server_ip:
                return

            # 用于设置窗口宽高度，目前是设置固定高度
            disks_io_width = str(disks_io_widget.width() // 2 - 40) + "px"
            disks_io_height = str(disks_io_widget.height() - 100) + "px"

            y_data, x_data = in_interface_impl.get_ssd_disk_io_info(self.selected_server_ip)

            line = (Line(init_opts=opts.InitOpts(bg_color='#0c1949', width=disks_io_width, height=disks_io_height,
                                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                    .add_xaxis(xaxis_data=x_data)
                    .add_yaxis(
                series_name="SSD 实时I/O负载",
                y_axis=y_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                itemstyle_opts=opts.ItemStyleOpts(color='#FF4C29'),
                label_opts=opts.LabelOpts(is_show=False), )
                    .set_global_opts(
                legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='white')),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross",
                                              background_color="rgb(12, 25, 73)", ),
                yaxis_opts=opts.AxisOpts(
                    name="IOPS/KB",
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                    name_textstyle_opts=opts.TextStyleOpts(color='white', ),
                    axislabel_opts=opts.LabelOpts(color='auto'),
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(is_show=True, color='#6166B3',)
                    )),
                xaxis_opts=opts.AxisOpts(
                    name="时间",
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_inside=True),
                    boundary_gap=False,
                    name_textstyle_opts=opts.TextStyleOpts(color='white', ),
                    axislabel_opts=opts.LabelOpts(color='auto'),
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(is_show=True, color='#6166B3',)
                    )))
                    .render("./resources/html/ssd_io.html"))

            # 打开本地html文件
            first_line_widget.load(QUrl("file:///./resources/html/ssd_io.html"))

            first_line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars,
                                                      False)  # 将滑动条隐藏，避免遮挡内容
            first_line_widget.resize(disks_io_widget.width() // 2 - 20, disks_io_widget.height() - 80)
            # first_line_widget.resize(self.size().width() / 2, self.size().height() / 2 - 40)
            disks_io_left_layout.addWidget(first_line_widget, alignment=Qt.AlignLeft | Qt.AlignTop)
            disks_io_left_layout.addWidget(left_button, alignment=Qt.AlignBottom | Qt.AlignCenter)

        def set_ssd_io_line():
            if not self.selected_server_ip:
                return
            # 用于设置窗口宽高度，目前是设置固定高度
            # 后期有高度设置不平衡的问题直接改这里，改为overall_tab宽高度一半少一点
            disks_io_width = str(disks_io_widget.width() // 2 - 40) + "px"
            disks_io_height = str(disks_io_widget.height() - 100) + "px"

            # 获取得到指定IP地址的SSD的IOPS信息
            y_data, x_data = in_interface_impl.get_ssd_disk_io_info(self.selected_server_ip)

            line = (Line(init_opts=opts.InitOpts(bg_color='#0c1949', width=disks_io_width, height=disks_io_height,
                                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                    .add_xaxis(xaxis_data=x_data)
                    .add_yaxis(
                series_name="SSD 实时I/O负载",
                y_axis=y_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                itemstyle_opts=opts.ItemStyleOpts(color='#FF4C29'),
                label_opts=opts.LabelOpts(is_show=False), )
                    .set_global_opts(
                legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='white')),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross",
                                              background_color="rgb(12, 25, 73)", ),
                yaxis_opts=opts.AxisOpts(
                    name="IOPS/KB",
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
                    .render("./resources/html/ssd_io.html"))

            # first_line_widget = QWebEngineView()
            first_line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars,
                                                      False)  # 将滑动条隐藏，避免遮挡内容
            first_line_widget.resize(disks_io_widget.width() // 2 - 20, disks_io_widget.height() - 80)  # 高度设置小一点可以跟贴近底部
            # 打开本地html文件
            first_line_widget.load(QUrl("file:///./resources/html/ssd_io.html"))

        # 右边I/O负载图
        second_line_widget = QWebEngineView()

        def draw_hdd_io_line():
            if not self.selected_server_ip:
                return

            disks_io_width = str(disks_io_widget.width() // 2 - 40) + "px"
            disks_io_height = str(disks_io_widget.height() - 100) + "px"

            # 获取得到指定IP地址的HDD的IOPS信息
            y_data, x_data = in_interface_impl.get_hdd_disk_io_info(self.selected_server_ip)

            line = (Line(init_opts=opts.InitOpts(bg_color='#0c1949', width=disks_io_width, height=disks_io_height,
                                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                    .add_xaxis(xaxis_data=x_data)
                    .add_yaxis(
                series_name="HDD 实时I/O负载",
                y_axis=y_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                itemstyle_opts=opts.ItemStyleOpts(color='#FF4C29'),
                label_opts=opts.LabelOpts(is_show=False), )
                    .set_global_opts(
                legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='white')),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross",
                                              background_color="rgb(12, 25, 73)", ),
                yaxis_opts=opts.AxisOpts(
                    name="IOPS/KB",
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
                    .render("./resources/html/hdd_io.html"))

            # second_line_widget = QWebEngineView()
            second_line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars,
                                                       False)  # 将滑动条隐藏，避免遮挡内容
            second_line_widget.resize(disks_io_widget.width() // 2 - 20, disks_io_widget.height() - 80)
            # 打开本地html文件
            second_line_widget.load(QUrl("file:///./resources/html/hdd_io.html"))
            disks_io_right_layout.addWidget(second_line_widget, alignment=Qt.AlignLeft | Qt.AlignTop)
            disks_io_right_layout.addWidget(right_button, alignment=Qt.AlignBottom | Qt.AlignCenter)

        def set_hdd_io_line():
            if not self.selected_server_ip:
                return

            disks_io_width = str(disks_io_widget.width() // 2 - 40) + "px"
            disks_io_height = str(disks_io_widget.height() - 100) + "px"

            # 获取得到指定IP地址的HDD的IOPS信息
            y_data, x_data = in_interface_impl.get_hdd_disk_io_info(self.selected_server_ip)

            line = (Line(init_opts=opts.InitOpts(bg_color='#0c1949', width=disks_io_width, height=disks_io_height,
                                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                    .add_xaxis(xaxis_data=x_data)
                    .add_yaxis(
                series_name="HDD 实时I/O负载",
                y_axis=y_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                itemstyle_opts=opts.ItemStyleOpts(color='#FF4C29'),
                label_opts=opts.LabelOpts(is_show=False), )
                    .set_global_opts(
                legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='white')),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross",
                                              background_color="rgb(12, 25, 73)", ),
                yaxis_opts=opts.AxisOpts(
                    name="IOPS/KB",
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
                    .render("./resources/html/hdd_io.html"))

            # 将滑动条隐藏，避免遮挡内容
            second_line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
            second_line_widget.resize(disks_io_widget.width() // 2 - 20, disks_io_widget.height() - 80)
            # first_line_widget.resize(self.width() / 2 - 20, self.height() / 2 - 40)
            # 打开本地html文件
            second_line_widget.load(QUrl("file:///./resources/html/hdd_io.html"))

        draw_ssd_io_line()
        draw_hdd_io_line()

        two_io_disk_layout = QHBoxLayout()
        two_io_disk_layout.addLayout(disks_io_left_layout)
        two_io_disk_layout.addLayout(disks_io_right_layout)
        disks_io_layout.addLayout(tip_layout)
        disks_io_layout.addLayout(two_io_disk_layout)
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

        splitter = QSplitter(Qt.Vertical)
        # 设置分割线的样式，宽度为3，颜色为黑色
        splitter.setStyleSheet("QSplitter::handle {background-color: #7efaff} QSplitter{background: rgb(12, 25, 73); "
                               "border-width:1px; border-color:#7efaff; border-style:solid}")
        splitter.setHandleWidth(2)
        splitter.addWidget(server_storage_info_widget)
        splitter.addWidget(server_io_info_widget)

        whole1_layout.addWidget(splitter)

        self.overall_info_tab.setLayout(whole1_layout)
        # self.Tab_list.append(self.overall_info_tab)

        # 定时刷新
        self.update_thread.update_data.connect(lambda: show_server_storage_list())
        self.update_thread.update_data.connect(lambda: draw_two_disk_storage_bar())
        self.update_thread.update_data.connect(lambda: draw_two_disk_error_rate_bar())
        self.update_thread.update_data.connect(lambda: set_hdd_io_line())
        self.update_thread.update_data.connect(lambda: set_ssd_io_line())

    def add_detailed_tab(self, server_selected_ip, lock):
        detailed_tab = DetailedInfoTab(server_selected_ip, lock)
        self.Tab_list.append(detailed_tab)
        # 全局布局
        self.addTab(detailed_tab.detailed_tab, "详细信息(" + server_selected_ip + ")")
        self.setCurrentIndex(self.count() - 1)
        # self.tabBar().setToolTip(self.tabBar().tabText(self.count() - 1))

    def tabClose(self, index):  # 定义关闭tab页事件, index表示第几个tab页，总体信息页是0
        self.removeTab(index)
        self.Tab_list[index - 1].update_thread.close_thread()  # 关闭线程
        self.Tab_list.pop(index - 1)

    def tabChange(self):
        print("change tab page")
        if not self.Tab_list[self.currentIndex() - 1].update_thread.isRunning():
            self.Tab_list[self.currentIndex() - 1].update_thread = UpdateTabDataThread(self.lock)  # 新建后台线程
            self.Tab_list[self.currentIndex() - 1].bind_thread()  # 绑定数据请求函数
            self.Tab_list[self.currentIndex() - 1].update_thread.start()  # 新线程启动
        for i in range(1, self.count()):
            if i != self.currentIndex() and self.Tab_list[i - 1].update_thread.isRunning():
                self.Tab_list[i - 1].update_thread.close_thread()  # 关闭线程

    def set_selected_server_ip(self, server_selected):
        self.selected_server_ip = self.server_overall_info[server_selected[0].topRow()].serverIP  # 获取到选中的serverIP
        # print("selected:", self.selected_server_ip)

    # 查看历史I/O负载信息
    def show_history_io_line(self, level):
        self.server_history_io = HistoryIO(self.selected_server_ip, "", level)
        self.server_history_io.show()


class RaidInfoTabWidget(QTabWidget):
    def __init__(self, lock):
        super().__init__()
        self.overall_info_tab = QWidget()
        self.server_overall_info = in_interface_impl.get_server_overall_info(1)  # 服务器总体信息列表
        # 选中的服务器IP地址，默认是第一个
        self.selected_server_ip = "" if len(self.server_overall_info) == 0 else self.server_overall_info[0].serverIP
        # 根据不同服务器IP地址查询的详细信息，类型应为列表的列表。每个元素为LogicVolumeInfo
        self.server_detailed_info = in_interface_impl.get_server_detailed_info(self.selected_server_ip, 1)
        self.lock = lock
        self.update_thread = UpdateRAIDDataThread(self.lock)  # 后台线程，每秒钟更新数据局
        self.initUI()

    def initUI(self):
        # 服务器总体信息表
        server_title = QLabel('''<font color=#def6fe weight=bold face='黑体' size=5>服务器总体信息<font>''')
        server_title.setStyleSheet("background-color:rgb(12, 25, 73); width:100px")
        server_storage_table_widget = QWidget()  # 总体信息表格窗口
        server_storage_table = QTableWidget(len(self.server_overall_info), 5)
        server_storage_table.setHorizontalHeaderLabels(['服务器名称', '存储总容量', '已使用容量', '存储占用率', '数据延迟'])  # 设置表头
        server_storage_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color:#007580; font:14pt SimHei; color:white}")  # 设置表头样式
        server_storage_table.setStyleSheet("QTableView::item:selected{background-color: #1687A7}"  # 设置行选中样式
                                           "QTableWidget{color:white; background-color:rgb(12, 25, 73);}")  # gridline-color: #7efaff
        server_storage_table.horizontalHeader().setHighlightSections(False)  # 设置表头不会因为点击表格而变色
        server_storage_table.verticalHeader().setVisible(False)  # 设置隐藏列表号
        server_storage_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置选中单位为行，而不是单元格
        server_storage_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置禁止编辑
        server_storage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 设置表宽度自适应性扩展
        server_storage_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 设置表根据内容调整列宽
        # server_storage_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 将竖直的滑动条隐藏，避免遮挡内容
        server_storage_table.clicked.connect(lambda: self.set_selected_server_ip(server_storage_table.selectedRanges()))
        server_storage_table.clicked.connect(lambda: show_volume_storage_list())
        server_storage_table.clicked.connect(lambda: set_server_io_line())  # 单击改变总体信息I/O负载图

        server_storage_table_layout = QVBoxLayout()
        server_storage_table_layout.addWidget(server_title, alignment=Qt.AlignLeft)
        server_storage_table_layout.addWidget(server_storage_table)
        server_storage_table_widget.setLayout(server_storage_table_layout)

        # 定义内部函数事件，初始化或者是到刷新周期后，从server_storage_info_list中取数据放入server_storage_table中去
        def show_server_storage_list():
            if self.selected_server_ip not in configuration_info.server_IPs:
                self.selected_server_ip = "" if len(self.server_overall_info) == 0 else self.server_overall_info[
                    0].serverIP
            self.server_overall_info = in_interface_impl.get_server_overall_info(1)
            server_storage_info_list = self.server_overall_info
            server_storage_table.setRowCount(len(self.server_overall_info))  # 设置表格行数
            for i, single_server_info in enumerate(server_storage_info_list):
                server_storage_table.setRowHeight(i, 60)
                update_cycle = in_interface_impl.get_update_cycle(single_server_info.serverIP)
                # 添加单元格信息
                line = get_server_storage_info_item(single_server_info, update_cycle)
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
        server_storage_table.selectRow(0)  # 设置默认选中第一行

        # 服务器详细信息表
        volume_title = QLabel('''<font color=#def6fe weight=bold face='黑体' size=5>服务器详细信息<font>''')
        volume_title.setStyleSheet("background-color:rgb(12, 25, 73); width:100px")
        volume_storage_table_widget = QWidget()  # 详细信息表格窗口
        volume_storage_table = QTableWidget(len(self.server_overall_info), 4)
        volume_storage_table.setHorizontalHeaderLabels(['逻辑卷标识', '存储总容量', '已使用容量', '存储占用率'])  # 设置表头
        volume_storage_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color:#007580; font:14pt SimHei; color:white;}")  # 设置表头样式
        volume_storage_table.setStyleSheet("QTableView::item:selected{background-color: rgb(12, 25, 73)}"  # 设置行选中样式
                                           "QTableWidget{color:white; background-color:rgb(12, 25, 73);}")  # gridline-color: #7efaff
        volume_storage_table.horizontalHeader().setHighlightSections(False)  # 设置表头不会因为点击表格而变色
        volume_storage_table.verticalHeader().setVisible(False)  # 设置隐藏列表号
        volume_storage_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置选中单位为行，而不是单元格
        volume_storage_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置禁止编辑
        volume_storage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 设置表宽度自适应性扩展
        volume_storage_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 设置表根据内容调整列宽
        # volume_storage_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 将竖直的滑动条隐藏，避免遮挡内容

        volume_storage_table_layout = QVBoxLayout()
        volume_storage_table_layout.addWidget(volume_title, alignment=Qt.AlignLeft)
        volume_storage_table_layout.addWidget(volume_storage_table)
        volume_storage_table_widget.setLayout(volume_storage_table_layout)

        # 定义内部函数事件，初始化或者是到刷新周期后，从volume_storage_info_list中取数据放入volume_storage_table中去
        def show_volume_storage_list():
            volume_storage_info_list = in_interface_impl.get_server_detailed_info(self.selected_server_ip,
                                                                                  1)  # 刷新的情况下直接用当前serverIP
            volume_storage_table.setRowCount(len(volume_storage_info_list))  # 设置表格行数
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

        show_volume_storage_list()

        # 总体信息表和详细信息表布局
        table_widget = QWidget()
        table_layout = QHBoxLayout()
        table_layout.addWidget(server_storage_table_widget)
        table_layout.addWidget(volume_storage_table_widget)
        table_widget.setLayout(table_layout)

        # 总体I/O负载信息图
        # 试验阶段
        comb = QComboBox()
        comb.setFixedSize(70, 20)
        comb.addItems(["7分钟", "6分钟", "5分钟", "4分钟", "3分钟"])
        comb.setStyleSheet("QComboBox{height:20px; width:20px; font-size:16px;}")
        comb.setCurrentIndex(7 - in_interface_impl.get_RAID_io_show_time())
        # 绑定事件，通过下拉框选择限制输入框的编辑
        comb.currentIndexChanged.connect(lambda: comboBoxSelection(comb.currentIndex()))

        def comboBoxSelection(index):
            #  取7 - index内分钟的数据
            in_interface_impl.change_RAID_io_show_time(7 - index, self.lock)

        # 负载图注释label
        tip_label = QLabel('''<font color=white face='黑体' size=4>注：设置显示服务器的实时总I/O负载信息的范围：<font>''')
        tip_layout = QHBoxLayout()
        tip_layout.addWidget(tip_label, alignment=Qt.AlignRight)
        tip_layout.addWidget(comb, alignment=Qt.AlignLeft)
        tip_widget = QWidget()
        tip_widget.setLayout(tip_layout)
        # 负载图的button
        io_button = QPushButton("历史信息")
        io_button.setFixedSize(100, 30)
        io_button.setStyleSheet('''QPushButton{background-color:white; font-size:20px; font-family:SimHei; 
                                               border-width:2px; border-style:solid; border-color:#7efaff; border-radius:12px}
                                               QPushButton:pressed{background-color:#71dfe7}''')
        io_button.clicked.connect(lambda: self.show_history_io_line())  # 绑定历史I/O负载图弹出事件
        # I/O负载图
        server_io_widget = QWidget()
        server_io_layout = QVBoxLayout()
        server_io_layout.addWidget(tip_widget, alignment=Qt.AlignLeft)
        line_widget = QWebEngineView()

        def draw_server_io_line():
            if not self.selected_server_ip:
                return

            line_widget.setHtml('''<!DOCTYPE html>
                                <html lang="en">
                                <head>
                                    <meta charset="UTF-8">
                                    <title>1</title>
                                </head>
                                <body bgcolor="#0c1949">
                                </body>
                                </html>''')

            line_widget.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)  # 将滑动条隐藏，避免遮挡内容
            # line_widget.setFixedSize(server_io_widget.width() - 20, server_io_widget.height() - 100)
            line_widget.resize(self.width(), self.height() // 2 - 80)
            # 打开本地html文件
            line_widget.load(QUrl("file:///./resource_status_display/html/server_io.html"))
            server_io_layout.addWidget(line_widget, alignment=Qt.AlignLeft)  #, alignment=Qt.AlignTop | Qt.AlignLeft)
            server_io_layout.addWidget(io_button, alignment=Qt.AlignBottom | Qt.AlignCenter)

        def set_server_io_line():
            if not self.selected_server_ip:
                return

            # 根据屏幕大小来确定I/O负载图的比例
            io_width = str(server_io_widget.width() - 50) + "px"
            io_height = str(server_io_widget.height() - 80) + "px"

            # 在刷新期间有个逐步调整布局的过程，需要两轮刷新才会适应最终布局大小，在这期间显示空白，初始布局默认是(640, 480)
            if line_widget.width() == 640:
                line_widget.resize(server_io_widget.width() - 50, server_io_widget.height() - 60)
                line_widget.setHtml('''<!DOCTYPE html>
                                    <html lang="en">
                                    <head>
                                        <meta charset="UTF-8">
                                        <title>1</title>
                                    </head>
                                    <body bgcolor="#0c1949">
                                    </body>
                                    </html>''')
                return

            y_data, x_data = in_interface_impl.get_RAID_overall_io_info(self.selected_server_ip)
            line = (Line(init_opts=opts.InitOpts(bg_color='#0c1949', width=io_width, height=io_height,
                                                 animation_opts=opts.AnimationOpts(animation=False)))  # 设置宽高度，去掉加载动画
                    .add_xaxis(xaxis_data=x_data)
                    .add_yaxis(
                series_name="",
                y_axis=y_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                itemstyle_opts=opts.ItemStyleOpts(color='#FF4C29'),
                label_opts=opts.LabelOpts(is_show=False), )
                    .set_global_opts(
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross", background_color="rgb(12, 25, 73)",),
                title_opts=opts.TitleOpts(title="服务器 实时I/O负载",
                                          pos_right="center",
                                          title_textstyle_opts=opts.TextStyleOpts(color="rgb(222,246,254)",
                                                                                  font_weight="bold")),
                yaxis_opts=opts.AxisOpts(
                    name="IOPS/KB",
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True, is_inside=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                    name_textstyle_opts=opts.TextStyleOpts(
                        color='white',),
                    axislabel_opts=opts.LabelOpts(
                        color='auto'),
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(
                            is_show=True,
                            color='#6166B3',
                        )
                    )),
                xaxis_opts=opts.AxisOpts(
                    name="时间",
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_inside=True),
                    boundary_gap=False,
                    name_textstyle_opts=opts.TextStyleOpts(
                        color='white',
                        background_color='black'),
                    axislabel_opts=opts.LabelOpts(
                        color='#auto'),
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(
                            is_show=True,
                            color='#544179',
                        )
                    )))
                    .set_series_opts(label_opts=opts.LabelOpts(is_show=False)).render("./resources/html/raid_server_io.html"))

            line_widget.resize(server_io_widget.width() - 50, server_io_widget.height() - 60)
            # 打开本地html文件
            line_widget.load(QUrl("file:///./resources/html/raid_server_io.html"))

        draw_server_io_line()

        server_io_widget.setLayout(server_io_layout)

        splitter = QSplitter(Qt.Vertical)  # 两张表和I/O负载图的窗口
        # 设置分割线的样式，宽度为3，颜色为#7efaff
        splitter.setStyleSheet("QSplitter::handle {background-color: #7efaff} QSplitter{background: rgb(12, 25, 73); "
                               "border-width:1px; border-color:#7efaff; border-style:solid}")
        splitter.setHandleWidth(2)

        splitter.addWidget(table_widget)
        splitter.addWidget(server_io_widget)
        # table_widget.setAttribute(Qt.WA_TranslucentBackground)
        # server_io_widget.setAttribute(Qt.WA_TranslucentBackground)
        splitter.setSizes([50000, 70000])

        # 全局布局
        whole_layout = QVBoxLayout()
        whole_layout.setContentsMargins(0, 0, 0, 0)

        whole_layout.addWidget(splitter)
        self.setLayout(whole_layout)

        # 定时刷新
        self.update_thread.update_data.connect(lambda: show_server_storage_list())
        self.update_thread.update_data.connect(lambda: show_volume_storage_list())
        self.update_thread.update_data.connect(lambda: set_server_io_line())
        self.update_thread.start()

    def set_selected_server_ip(self, server_selected):
        self.selected_server_ip = self.server_overall_info[server_selected[0].topRow()].serverIP  # 获取到选中的serverIP

    def show_history_io_line(self):
        self.server_history_io = HistoryIO(self.selected_server_ip, "", 3)
        self.server_history_io.show()
