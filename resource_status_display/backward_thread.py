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
    """更新多硬盘架构数据类"""
    update_data = pyqtSignal()  # pyqt5 支持python3的str，没有Qstring

    def __init__(self, lock):
        super(UpdateMDDataThread, self).__init__()
        self.lock = lock
        self.flag = True

    def close_thread(self):
        self.flag = False

    def run(self):
        while self.flag:
            self.lock.lock()
            print("update MD-server data...")
            self.update_data.emit()  # 发射信号
            time.sleep(0.1)  # 保持锁0.1秒 便于刷新数据
            self.lock.unlock()
            time.sleep(0.9)   # 推迟执行0.9秒


class UpdateRAIDDataThread(QThread):
    """更新RAID架构数据类"""
    update_data = pyqtSignal()  # pyqt5 支持python3的str，没有Qstring

    def __init__(self, lock):
        super(UpdateRAIDDataThread, self).__init__()
        self.lock = lock
        self.flag = True

    def close_thread(self):
        self.flag = False

    def run(self):
        while self.flag:
            self.lock.lock()
            print("update RAID-server data...")
            self.update_data.emit()  # 发射信号
            time.sleep(0.1)  # 保持锁0.1秒 便于刷新数据
            self.lock.unlock()
            time.sleep(0.9)  # 推迟执行0.9秒


class UpdateTabDataThread(QThread):
    """更新多硬盘架构下tab页数据类"""
    update_data = pyqtSignal()  # pyqt5 支持python3的str，没有Qstring

    def __init__(self, lock):
        super(UpdateTabDataThread, self).__init__()
        self.lock = lock
        self.flag = True

    def close_thread(self):
        self.flag = False

    def run(self):
        while self.flag:
            self.lock.lock()
            print("update MD-disk data...")
            self.update_data.emit()  # 发射信号
            time.sleep(0.1)  # 保持锁0.1秒 便于刷新数据
            self.lock.unlock()
            time.sleep(0.9)  # 推迟执行0.9秒


class UpdateLogThread(QThread):
    """更新多硬盘架构下日志信息与告警信息数据类"""
    update_data = pyqtSignal()  # pyqt5 支持python3的str，没有Qstring

    def __init__(self, lock):
        super(UpdateLogThread, self).__init__()
        self.lock = lock
        self.flag = True

    def close_thread(self):
        self.flag = False

    def run(self):
        while self.flag:
            self.lock.lock()
            print("update MD-log data...")
            self.update_data.emit()  # 发射信号
            time.sleep(0.1)  # 保持锁0.1秒 便于刷新数据
            self.lock.unlock()
            time.sleep(0.9)  # 推迟执行0.9秒
