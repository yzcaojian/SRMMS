import sys
import threading
import time

from PyQt5.QtCore import Qt, QSize, QMutex, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QMainWindow, \
    QMessageBox

from hard_disk_failure_prediction.predict import start_disk_health_prediction
from resource_status_display.mult_disks_info_GUI import MultDisksInfoWidget
from resource_status_display.raid_info_GUI import RAIDInfoWidget
from resource_status_display.configuration_checking import configuration_info

from interface.in_interface import in_interface_impl
from resource_scheduling_allocation.RSA_1 import start_online_model_training
from resource_scheduling_allocation.RSA_2 import start_io_load_prediction
from resource_scheduling_allocation.RSA_3 import sever_disconnection_warning, hard_disk_high_io_warning, hard_disk_failutre_warning
from resource_scheduling_allocation.RSA_4 import resource_scheduling_allocation

from data_communication_analysis.DAC_1 import analyse_data

"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: 主程序
@Time : 2021/4/28 10:48
@Author : cao jian
"""


class MainWidget(QWidget):
    running = True  # 判断程序运行的标志

    def __init__(self):
        super().__init__()

        self.title_widget = QWidget()  # 标题
        self.mult_disks_info_widget = MultDisksInfoWidget(threadLock_drawing)  # 多硬盘架构下监控界面
        self.raid_info_widget = None  # RAID架构下监控界面
        self.whole_layout = QVBoxLayout()

        self.setGeometry(100, 100, 1700, 900)  # 坐标，宽高
        self.setWindowTitle("存储资源监控管理系统")
        self.setObjectName('MultDisksInfoWidget')
        self.setWindowIcon(QIcon('./png/software.png'))  # 设置窗体图标
        self.setStyleSheet("#MultDisksInfoWidget{background-color:#cccccc}")  # 设置背景颜色

        self.initUI()
        # 全局布局
        # whole_layout = QVBoxLayout()
        self.whole_layout.setContentsMargins(0, 0, 0, 10)
        self.whole_layout.addWidget(self.title_widget)
        self.whole_layout.addWidget(self.mult_disks_info_widget)
        self.setLayout(self.whole_layout)
        self.show()

        # 后台线程请求资源
        self.data_request_thread = RequestResourceThread()
        self.data_request_thread.start()

        # 开辟线程进行事务处理
        self.transaction_thread = TransactionProcessingThread()
        self.transaction_thread.start()

    def initUI(self):
        # 标题
        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_label = QLabel('''<font color=black face='黑体' size=8>存储资源监控管理系统<font>''')
        # title_label.setContentsMargins(0, 16, 0, 0)
        title_label.setAlignment(Qt.AlignCenter)  # 文本居中
        switch_button = QPushButton()
        switch_button.setFixedSize(40, 40)
        switch_button_icon = QIcon('./png/switch.png')
        switch_button.setIcon(switch_button_icon)
        switch_button.setIconSize(QSize(35, 35))
        # switch_button.setContentsMargins(0, 30, 0, 0)
        switch_button.setStyleSheet("QPushButton{background-color:#cccccc; border: none} "
                                    "QPushButton:pressed{background-color:#aaaaaa}")
        # 将文本和切换按钮共同居中
        title = QHBoxLayout()
        title_w = QWidget()
        title.addWidget(title_label, alignment=Qt.AlignRight)
        title.addWidget(switch_button, alignment=Qt.AlignLeft)
        title_w.setLayout(title)
        title_layout.addWidget(title_w, alignment=Qt.AlignCenter)
        title_widget.setLayout(title_layout)

        switch_button.clicked.connect(lambda: self.switch_UI())

        self.title_widget = title_widget

    def switch_UI(self):
        if self.whole_layout.itemAt(1).widget() == self.mult_disks_info_widget:
            for i in range(1, self.mult_disks_info_widget.tab_widget.count()):
                self.mult_disks_info_widget.tab_widget.removeTab(i)  # 清除所有tab页
                for (j, key) in enumerate(self.mult_disks_info_widget.tab_widget.tab_update_thread):
                    if j == i - 1:
                        self.mult_disks_info_widget.tab_widget.tab_update_thread[key].close_thread()
                        break  # 关闭所有tab页刷新线程
            self.mult_disks_info_widget.setParent(None)  # 清除多硬盘监控界面
            # for item in self.mult_disks_info_widget.tab_widget.Tab_list:  # 关闭tab页线程
            #     item.update_thread.close_thread()
            self.mult_disks_info_widget.tab_widget.update_thread.close_thread()  # 关闭总体信息刷新线程
            self.mult_disks_info_widget.update_log_thread.close_thread()  # 关闭日志信息刷新线程
            self.mult_disks_info_widget = None
            self.raid_info_widget = RAIDInfoWidget(threadLock_drawing)
            self.whole_layout.addWidget(self.raid_info_widget)
        else:
            self.raid_info_widget.setParent(None)  # 清除RAID监控界面
            self.raid_info_widget.tab_widget.update_thread.close_thread()  # 关闭RAID主页面信息刷新线程
            self.raid_info_widget = None
            self.mult_disks_info_widget = MultDisksInfoWidget(threadLock_drawing)
            self.whole_layout.addWidget(self.mult_disks_info_widget)

    # 当出现对硬盘故障预警的情况时弹窗告警
    def show_disk_error_warning(self, server_ip, disk_id):
        QMessageBox.warning(self, "警告", "服务器" + server_ip + "上机械硬盘" + disk_id + "预计健康度为R4，剩余寿命在150天以下", QMessageBox.Ok)

    def closeEvent(self, event):
        MainWidget.running = False


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.main_ui = MainWidget()


class RequestResourceThread(QThread):
    def __init__(self):
        super(RequestResourceThread, self).__init__()

    def run(self):
        while MainWidget.running:
            # 获得锁
            threadLock_drawing.lock()
            threadLock.lock()
            print("请求资源获得锁")
            print("请求资源开始:")
            for ip in configuration_info.server_IPs:
                analyse_data(ip)
            print("请求资源结束:")
            # 释放锁
            threadLock.unlock()
            threadLock_drawing.unlock()
            print("请求资源释放锁")
            # QApplication.processEvents()
            self.sleep(1)


class TransactionProcessingThread(QThread):
    def __init__(self):
        super(TransactionProcessingThread, self).__init__()

    def run(self):
        while MainWidget.running:
            # 获得锁
            threadLock.lock()
            print("事务处理获得锁")
            print("事务处理开始:")
            # 线上训练 开辟线程
            start_online_model_training(io_load_input_queue_train, mean_and_std, save_model)

            # IO负载预测 开辟线程
            start_io_load_prediction(io_load_input_queue_predict, io_load_output_queue, mean_and_std, save_model[0],
                                     average_io_load, warning_message_queue)
            # 硬盘故障预测 开辟线程
            # start_disk_health_prediction(smart_dict, health_degree_dict, hard_disk_failure_prediction_list)

            # 检查是否有硬盘故障预警
            failure_list = hard_disk_failutre_warning(hard_disk_failure_prediction_list, warning_message_queue)
            for failure in failure_list:
                main.main_ui.show_disk_error_warning(failure[0], failure[1])
            # 判断服务器失联告警
            sever_disconnection_warning(io_load_input_queue, warning_message_queue)
            # 判断硬盘持续高I/O需求
            hard_disk_high_io_warning(high_io_load_queue, warning_message_queue)

            # 处理异常消息
            resource_scheduling_allocation(disk_detailed_info, warning_message_queue)
            print("事务处理结束:")
            # 释放锁
            threadLock.unlock()
            print("事务处理释放锁")
            # QApplication.processEvents()
            self.sleep(2)


if __name__ == '__main__':
    # 线程锁
    threadLock = QMutex()
    threadLock_drawing = QMutex()
    # 预先请求一次数据
    for ip in configuration_info.server_IPs:
        analyse_data(ip)

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
    # 存放IO的平均值和标准差
    mean_and_std = in_interface_impl.get_mean_and_std()
    # 存放所有硬盘smart数据
    smart_dict = in_interface_impl.get_smart_data_dict()
    # 存放各硬盘预测得到的健康度结果
    health_degree_dict = in_interface_impl.get_health_degree_dict()
    # 存放各硬盘需要预警的硬盘位置信息
    hard_disk_failure_prediction_list = in_interface_impl.get_hard_disk_failure_prediction_list()

    save_model = ['../IO_load_prediction_model_training/model/Financial2/', 'Model']

    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())  # 循环等待界面退出
