import time

from PyQt5.QtCore import QThread, pyqtSignal
import threading

"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: 后台线程，用于刷新数据
@Time : 2021/5/15 15:44
@Author : cao jian
"""


class UpdateMDDataThread(QThread):
    """更新数据类"""
    update_data = pyqtSignal()  # pyqt5 支持python3的str，没有Qstring

    def __init__(self, lock):
        super(UpdateMDDataThread, self).__init__()
        self.lock = lock

    def run(self):
        while True:
            self.lock.lock()
            # print("更新多硬盘架构前端数据")
            self.update_data.emit()  # 发射信号
            self.lock.unlock()
            self.sleep(1)  # 推迟执行一秒钟


class UpdateRAIDDataThread(QThread):
    """更新数据类"""
    update_data = pyqtSignal()  # pyqt5 支持python3的str，没有Qstring

    def __init__(self, lock):
        super(UpdateRAIDDataThread, self).__init__()
        self.lock = lock

    def run(self):
        while True:
            self.lock.lock()
            # print("更新RAID架构前端数据")
            self.update_data.emit()  # 发射信号
            self.lock.unlock()
            self.sleep(1)  # 推迟执行一秒钟
