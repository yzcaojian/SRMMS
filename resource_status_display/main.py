import sys
import _thread
import time

from PyQt5.QtCore import Qt, QSize, QMutex, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QMainWindow, QMessageBox
from pyecharts.globals import CurrentConfig
from resource_status_display.mult_disks_info_GUI import MultDisksInfoWidget
from resource_status_display.raid_info_GUI import RAIDInfoWidget
from resource_status_display.configuration_checking import configuration_info
from interface.in_interface import in_interface_impl
from resource_scheduling_allocation.RSA_1 import OnlineModelTrainingThread
from resource_scheduling_allocation.RSA_2 import IoLoadPredictionThread
from resource_scheduling_allocation.RSA_3 import sever_disconnection_warning, hard_disk_high_io_warning, hard_disk_failutre_warning
from resource_scheduling_allocation.RSA_4 import resource_scheduling_allocation
from hard_disk_failure_prediction.predict import DiskHealthPredictionThread
from data_communication_analysis.DAC_1 import analyse_data

"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: 主程序
@Time : 2021/4/28 10:48
@Author : cao jian
"""
CurrentConfig.ONLINE_HOST = "../js/"  # 配置使用本地js文件

# I/O负载输入队列
io_load_input_queue = in_interface_impl.get_io_load_input_queue()
io_load_input_queue_predict = in_interface_impl.get_io_load_input_queue_predict()  # 预测用
io_load_input_queue_train = in_interface_impl.get_io_load_input_queue_train()  # 训练用
# I/O负载输出队列
io_load_output_queue = in_interface_impl.get_io_load_output_queue()
# 高负载队列
high_io_load_queue = in_interface_impl.get_high_io_load_queue()
# 记录平均I/O负载  average_io_load[ip][diskID]:[count, averageIO]
average_io_load = in_interface_impl.get_average_io_load()
# 异常消息列表  [异常ID, 事件发生事件, 服务器IP, 硬盘标识,...]
warning_message_queue = in_interface_impl.get_warning_message_queue()
# disk_detailed_info为字典  格式为{IP:{diskID:[type, state, totalCapacity, occupiedCapacity, occupiedRate}}
disk_detailed_info = in_interface_impl.get_disk_detailed_info()
# 存放所有硬盘smart数据
smart_dict = in_interface_impl.get_smart_data_dict()
# 存放各硬盘预测得到的健康度结果
health_degree_dict = in_interface_impl.get_health_degree_dict()
# 存放各硬盘需要预警的硬盘位置信息
hard_disk_failure_prediction_list = in_interface_impl.get_hard_disk_failure_prediction_list()

save_model = ['./resources/IO_load_prediction_model_training/model/default_model/', 'Model']


class MainWidget(QWidget):
    running = True  # 判断程序运行的标志

    def __init__(self):
        super().__init__()

        self.mult_disks_info_widget = MultDisksInfoWidget(threadLock_drawing, threadLock_log)  # 多硬盘架构下监控界面
        self.raid_info_widget = None  # RAID架构下监控界面
        self.whole_layout = QVBoxLayout()

        # # 窗口标题栏设置相关参数
        self.restorePos = None
        self.restoreSize = None
        self.startMovePos = None

        self.setGeometry(100, 100, 1700, 900)  # 坐标，宽高
        self._padding = 5  # 设置边界宽度为5
        self.setObjectName('detailedInfoWidget')
        self.setWindowFlags(Qt.FramelessWindowHint)  # 隐藏主窗口标题栏
        # self.setWindowTitle("存储资源监控管理系统")
        self.setWindowIcon(QIcon('./resources/png/software.png'))  # 设置窗体图标
        # self.setStyleSheet("#detailedInfoWidget{background-color:#0c1949}")  # 设置背景颜色
        # 背景图片设置
        # palette = QPalette()
        # pix = QPixmap("./resources/png/background.png")
        # pix = pix.scaled(self.width(), self.height())
        # palette.setBrush(QPalette.Background, QBrush(pix))
        # self.setPalette(palette)

        self.initUI()

        # 后台线程请求资源
        self.data_request_thread = RequestResourceThread()
        self.data_request_thread.start()

        # 开辟线程进行事务处理
        self.transaction_thread = TransactionProcessingThread()
        self.transaction_thread.start()

    def initUI(self):
        # 设置鼠标跟踪判断扳机默认值
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False

        # 按钮高度
        BUTTON_HEIGHT = 20
        # 按钮宽度
        BUTTON_WIDTH = 20
        # 标题栏高度
        TITLE_HEIGHT = 20

        # 自定义标题栏
        navigator_widget = QWidget()
        navigator_widget.setObjectName("navigator")
        navigator_widget.setFixedHeight(BUTTON_HEIGHT + 10)
        navigator_layout = QHBoxLayout()

        buttonIcon = QPushButton()
        buttonIcon.setObjectName("ButtonIcon")
        buttonIcon.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        # navigatorContent = QLabel("存储资源监控管理系统")
        # navigatorContent.setFixedHeight(TITLE_HEIGHT)
        # navigatorContent.setObjectName("title")
        self.buttonMin = QPushButton()
        self.buttonMin.setFixedSize(QSize(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.buttonMin.setObjectName("ButtonMin")
        self.buttonMin.clicked.connect(self.ButtonMinSlot)
        self.buttonMin.setContentsMargins(0, 0, 30, 0)
        self.buttonMax = QPushButton()
        self.buttonMax.setFixedSize(QSize(BUTTON_WIDTH - 2, BUTTON_HEIGHT - 2))
        self.buttonMax.setObjectName("ButtonMax")
        self.buttonMax.clicked.connect(self.ButtonMaxSlot)
        self.buttonRestore = QPushButton()
        self.buttonRestore.setFixedSize(QSize(BUTTON_WIDTH - 2, BUTTON_HEIGHT - 2))
        self.buttonRestore.setObjectName("ButtonRestore")
        self.buttonRestore.clicked.connect(self.ButtonRestoreSlot)
        self.buttonRestore.setVisible(False)
        self.buttonClose = QPushButton()
        self.buttonClose.setFixedSize(QSize(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.buttonClose.setObjectName("ButtonClose")
        self.buttonClose.clicked.connect(self.ButtonCloseSlot)
        self.setStyleSheet("#detailedInfoWidget{background-color:#0c1949}"
                           # "QLabel#title{color: white}"
                           "QPushButton#ButtonIcon{border-image:url(./resources/png/software.png)}"
                           "QPushButton#ButtonMin{border-image:url(./resources/png/min.png)}"
                           "QPushButton#ButtonMin:hover{background-color: gray}"
                           "QPushButton#ButtonMax{border-image:url(./resources/png/max.png)}"
                           "QPushButton#ButtonMax:hover{background-color: gray}"
                           "QPushButton#ButtonRestore{border-image:url(./resources/png/restore.png)}"
                           "QPushButton#ButtonRestore:hover{background-color: gray}"
                           "QPushButton#ButtonClose{border-image:url(./resources/png/close.png)}"
                           "QPushButton#ButtonClose:hover{background-color: red}")
        # 占位窗口
        placeholder_1 = QWidget()
        placeholder_2 = QWidget()
        placeholder_1.setFixedWidth(20)
        placeholder_2.setFixedWidth(20)
        navigator_layout.addWidget(buttonIcon)
        navigator_layout.addWidget(QWidget())
        navigator_layout.addWidget(self.buttonMin)
        navigator_layout.addWidget(placeholder_1)
        navigator_layout.addWidget(self.buttonMax)
        navigator_layout.addWidget(self.buttonRestore)
        navigator_layout.addWidget(placeholder_2)
        navigator_layout.addWidget(self.buttonClose)
        navigator_widget.setLayout(navigator_layout)

        # 标题
        title_widget = QWidget()
        title_widget.setObjectName("title")
        title_layout = QHBoxLayout()

        title_label = QLabel('''<font color=white face='黑体' size=8>存储资源监控管理系统<font>''')
        # title_label.setContentsMargins(0, 16, 0, 0)
        title_label.setAlignment(Qt.AlignCenter)  # 文本居中
        switch_button = QPushButton()
        switch_button.setFixedSize(34, 34)
        switch_button_icon = QIcon('./resources/png/switch.png')
        switch_button.setIcon(switch_button_icon)
        switch_button.setIconSize(QSize(30, 30))
        # switch_button.setContentsMargins(0, 30, 0, 0)
        switch_button.setStyleSheet("QPushButton{background-color: transparent; border: none} "
                                    "QPushButton:pressed{background-color: transparent}")

        self.title_branch = QLabel('''<font color=white face='黑体' size=6>（多硬盘架构）<font>''')

        # 切换按钮与架构文字信息布局
        branch = QHBoxLayout()
        branch_widget = QWidget()
        branch.addWidget(self.title_branch, alignment=Qt.AlignRight | Qt.AlignTop)
        branch.addWidget(switch_button, alignment=Qt.AlignLeft | Qt.AlignTop)
        branch_widget.setLayout(branch)

        title_layout.addWidget(title_label, alignment=Qt.AlignRight | Qt.AlignVCenter)
        title_layout.addWidget(branch_widget, alignment=Qt.AlignLeft | Qt.AlignTop)
        title_widget.setLayout(title_layout)
        title_widget.setStyleSheet("#title{border: 1px solid #0c1949; border-top-color: #7efaff}")
        # title_widget.setFixedHeight(80)

        switch_button.clicked.connect(lambda: self.switch_UI())

        # 全局布局
        self.whole_layout = QVBoxLayout()
        self.whole_layout.setContentsMargins(0, 0, 0, 0)
        self.whole_layout.addWidget(navigator_widget)
        self.whole_layout.addWidget(title_widget)
        self.whole_layout.addWidget(self.mult_disks_info_widget)

        self.setLayout(self.whole_layout)
        self.show()

    def switch_UI(self):
        if self.whole_layout.itemAt(2).widget() == self.mult_disks_info_widget:
            self.title_branch.setText('''<font color=white face='黑体' size=6>（RAID架构）<font>''')
            self.mult_disks_info_widget.setParent(None)  # 清除多硬盘监控界面
            if self.mult_disks_info_widget.configuration:
                self.mult_disks_info_widget.configuration.close()  # 清除多硬盘架构打开的配置界面
            if self.mult_disks_info_widget.tab_widget.server_history_io:
                self.mult_disks_info_widget.tab_widget.server_history_io.close()  # 清除多硬盘架构主界面打开的io历史信息图
            for item in self.mult_disks_info_widget.tab_widget.Tab_list:  # 关闭tab页线程
                item.update_thread.close_thread()
                if item.disk_history_io:
                    item.disk_history_io.close()  # 清除每个tab页打开的io历史信息图
            self.mult_disks_info_widget.update_log_thread.close_thread()
            self.mult_disks_info_widget.tab_widget.update_thread.close_thread()  # 关闭总体信息线程
            self.mult_disks_info_widget = None
            self.raid_info_widget = RAIDInfoWidget(threadLock_drawing)
            # self.raid_info_widget.setAttribute(Qt.WA_TranslucentBackground)
            self.whole_layout.addWidget(self.raid_info_widget)
        else:
            self.title_branch.setText('''<font color=white face='黑体' size=6>（多硬盘架构）<font>''')
            self.raid_info_widget.setParent(None)  # 清除RAID监控界面
            if self.raid_info_widget.configuration:
                self.raid_info_widget.configuration.close()  # 清除RAID架构打开的配置界面
            if self.raid_info_widget.tab_widget.server_history_io:
                self.raid_info_widget.tab_widget.server_history_io.close()  # 清除RAID架构界面打开的io历史信息图
            self.raid_info_widget.tab_widget.update_thread.close_thread()  # 关闭总体信息线程
            self.raid_info_widget = None
            self.mult_disks_info_widget = MultDisksInfoWidget(threadLock_drawing, threadLock_log)
            self.whole_layout.addWidget(self.mult_disks_info_widget)

    # def closeEvent(self, event):
    #     reply = QMessageBox.question(self, '提醒', '你确认要退出程序吗？', QMessageBox.Yes, QMessageBox.No)
    #     if reply == QMessageBox.Yes:
    #         MainWidget.running = False
    #         event.accept()
    #         sys.exit(0)
    #     else:
    #         event.ignore()
    def ButtonMaxSlot(self):
        self.showMaximized()
        self.buttonMax.setVisible(False)
        self.buttonRestore.setVisible(True)

    def ButtonMinSlot(self):
        self.showMinimized()

    def ButtonRestoreSlot(self):
        if self.isMaximized():
            self.showNormal()
            self.buttonMax.setVisible(True)
            self.buttonRestore.setVisible(False)
        else:
            self.showMaximized()
            self.buttonMax.setVisible(False)
            self.buttonRestore.setVisible(True)

    def ButtonCloseSlot(self):
        reply = QMessageBox.question(self, '提醒', '你确认要退出程序吗？', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            MainWidget.running = False
            self.close()
            sys.exit(0)

    def mouseDoubleClickEvent(self, event):
        self.ButtonRestoreSlot()

    def mousePressEvent(self, event):
        self.isPressed = True
        self.startMovePos = event.globalPos()

    def mouseMoveEvent(self, QMouseEvent):
        if self.isPressed:
            movePoint = QMouseEvent.globalPos() - self.startMovePos
            widgetPos = self.pos()
            self.startMovePos = QMouseEvent.globalPos()
            self.move(widgetPos.x() + movePoint.x(), widgetPos.y() + movePoint.y())

    def mouseReleaseEvent(self, QMouseEvent):
        self.isPressed = False



class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.main_ui = MainWidget()


class ProbeIPThread(QThread):
    def __init__(self):
        super(ProbeIPThread, self).__init__()

    def run(self):
        # 后台线程进行ip自发现
        in_interface_impl.background_get_ip(MainWidget.running, threadLock_drawing, threadLock_transaction)


class RequestResourceThread(QThread):
    def __init__(self):
        super(RequestResourceThread, self).__init__()

    def run(self):
        while MainWidget.running:
            # 获得锁
            threadLock_drawing.lock()
            threadLock_transaction.lock()
            print("请求资源获得锁")

            in_interface_impl.check_server_ip_dict()
            configuration_info.server_IPs, configuration_info.server_names, configuration_info.server_types = \
                in_interface_impl.get_server_ip_dict()

            print("请求资源开始:")
            for ip in configuration_info.server_IPs:
                in_interface_impl.request_time[ip] = time.time()
                _thread.start_new_thread(analyse_data, (ip, threadLock_resource))
            print("请求资源结束:")
            # 释放锁
            time.sleep(0.5)  # 保持锁0.5秒 便于刷新数据
            threadLock_transaction.unlock()
            threadLock_drawing.unlock()
            print("请求资源释放锁")
            # QApplication.processEvents()
            time.sleep(0.5)  # 推迟执行0.5秒


class TransactionProcessingThread(QThread):
    def __init__(self):
        super(TransactionProcessingThread, self).__init__()

    def run(self):
        while MainWidget.running:
            # 获得锁
            threadLock_transaction.lock()
            threadLock_log.lock()
            print("事务处理获得锁")
            print("事务处理开始:")

            # 动态训练、负载预测、硬盘故障预测
            start_prediction_training_thread()
            # 检查是否有硬盘故障预警
            hard_disk_failutre_warning(hard_disk_failure_prediction_list, warning_message_queue)
            # 判断服务器失联告警
            sever_disconnection_warning(io_load_input_queue, warning_message_queue)
            # 判断硬盘持续高I/O需求
            hard_disk_high_io_warning(high_io_load_queue, warning_message_queue)

            # 处理异常消息
            resource_scheduling_allocation(disk_detailed_info, warning_message_queue)
            print("事务处理结束:")
            # 释放锁
            time.sleep(0.1)  # 保持锁0.1秒 便于刷新数据
            threadLock_log.unlock()
            threadLock_transaction.unlock()
            print("事务处理释放锁")
            # QApplication.processEvents()
            time.sleep(1.9)  # 推迟执行1.9秒


class PredictionTrainingThread:

    online_training_thread = OnlineModelTrainingThread(io_load_input_queue_train, save_model)
    io_load_prediction_thread = IoLoadPredictionThread(io_load_input_queue_predict, io_load_output_queue, save_model[0],
                                                       average_io_load, warning_message_queue)
    hard_disk_failure_prediction_thread = DiskHealthPredictionThread(smart_dict, health_degree_dict,
                                                                     hard_disk_failure_prediction_list)


def start_prediction_training_thread():
    if not PredictionTrainingThread.online_training_thread.is_alive():  # 动态训练线程结束
        PredictionTrainingThread.online_training_thread = OnlineModelTrainingThread(io_load_input_queue_train,
                                                                                    save_model)
        PredictionTrainingThread.online_training_thread.start()
    if not PredictionTrainingThread.io_load_prediction_thread.is_alive():  # 负载预测线程结束
        PredictionTrainingThread.io_load_prediction_thread = \
            IoLoadPredictionThread(io_load_input_queue_predict, io_load_output_queue, save_model[0], average_io_load,
                                   warning_message_queue)
        PredictionTrainingThread.io_load_prediction_thread.start()
    if not PredictionTrainingThread.hard_disk_failure_prediction_thread.is_alive():  # 硬盘故障预测线程结束
        PredictionTrainingThread.hard_disk_failure_prediction_thread = \
            DiskHealthPredictionThread(smart_dict, health_degree_dict, hard_disk_failure_prediction_list)
        PredictionTrainingThread.hard_disk_failure_prediction_thread.start()


# 线程锁
threadLock_transaction = QMutex()
threadLock_drawing = QMutex()
threadLock_log = QMutex()
threadLock_resource = QMutex()


def start():
    app = QApplication(sys.argv)
    main = MainWindow()

    # IP自发现
    check_ip_thread = ProbeIPThread()
    check_ip_thread.start()
    # # 预先请求一次数据
    # for ip in configuration_info.server_IPs:
    #     _thread.start_new_thread(analyse_data, (ip, threadLock_resource))
    # 运行三个线程
    PredictionTrainingThread.online_training_thread.start()
    PredictionTrainingThread.io_load_prediction_thread.start()
    PredictionTrainingThread.hard_disk_failure_prediction_thread.start()

    sys.exit(app.exec_())  # 循环等待界面退出
