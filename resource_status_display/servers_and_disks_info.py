from resource_status_display.configuration_checking import configuration_info

"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: 关于服务器总体信息的类，包括容量信息；两类硬盘的信息；故障率信息；I/O负载信息。关于服务器详细信息的类，包括容量信息；健康度信息。
@Time : 2021/5/4 20:04
@Author : cao jian
"""


class ServerInfo:
    def __init__(self, serverIP, totalCapacity, occupiedCapacity, occupiedRate):
        super().__init__()
        self.serverName = configuration_info.IPtoName(serverIP)
        self.serverIP = serverIP
        self.totalCapacity = totalCapacity
        self.occupiedCapacity = occupiedCapacity
        self.occupiedRate = occupiedRate


class ServerInfoList:
    def __init__(self):
        super().__init__()
        # self.server_info_list = []
        self.server_info_list = [ServerInfo("192.168.1.1", "50TB", "20TB", "40.0%"),
                                 ServerInfo("192.168.1.2", "40TB", "20TB", "50.0%"),
                                 ServerInfo("192.168.1.3", "80TB", "10TB", "12.5%"),
                                 ServerInfo("192.168.20.1", "80TB", "20TB", "25.0%"),
                                 ServerInfo("192.168.225.230", "10TB", "3TB", "33.3%")]

    def update_info(self, new_list):
        # list每个元素是一个包含ServerInfo除名称外所有字段信息的列表
        self.server_info_list = []  # 先清空
        for single in new_list:
            self.server_info_list.append(ServerInfo(single[0], single[1], single[2], single[3]))


class TwoDiskInfo:
    def __init__(self, info_list):
        super().__init__()
        self.hddCounts = info_list[0]
        self.ssdCounts = info_list[1]
        self.hddTotalCapacity = info_list[2]
        self.ssdTotalCapacity = info_list[3]
        self.hddOccupiedCapacity = info_list[4]
        self.ssdOccupiedCapacity = info_list[5]
        self.hddOccupiedRate = info_list[6]
        self.ssdOccupiedRate = info_list[7]
        self.hddErrorRate = info_list[8]
        self.ssdErrorRate = info_list[9]
        self.hddIOPS = info_list[10]
        self.ssdIOPS = info_list[11]


class TwoDiskInfoList:
    def __init__(self):
        super().__init__()
        # self.server_info_list = []
        self.two_disk_info_list = [
            TwoDiskInfo([20, 10, 500.0, 300.0, 140.0, 100.0, 0.28, 0.33, 0.03, 0.01, 2580, 2683]),
            TwoDiskInfo([15, 8, 420.0, 240.0, 140.0, 80.0, 0.33, 0.33, 0.03, 0, 2980, 2173])]

    def update_info(self, new_list):
        # list每个元素是一个包含所有初始化TwoDiskInfo对象字段信息的列表
        self.two_disk_info_list = []  # 先清空
        for single in new_list:
            self.two_disk_info_list.append(TwoDiskInfo(single))


class DiskInfo:
    def __init__(self, diskID, type, state, totalCapacity, occupiedCapacity, occupiedRate, healthDegree):
        super().__init__()
        self.diskID = diskID
        self.type = type
        self.state = state
        self.totalCapacity = totalCapacity
        self.occupiedCapacity = occupiedCapacity
        self.occupiedRate = occupiedRate
        self.healthDegree = healthDegree


class LogicVolumeInfo:
    def __init__(self, logicVolumeID, totalCapacity, occupiedCapacity, occupiedRate):
        super().__init__()
        self.logicVolumeID = logicVolumeID
        self.totalCapacity = totalCapacity
        self.occupiedCapacity = occupiedCapacity
        self.occupiedRate = occupiedRate


def get_server_detailed_info(server_ip, tag):
    # 获取server_ip对应的服务器详细信息
    if tag == 0:  # 硬盘详细信息
        return [DiskInfo("hdd-01", "HDD", "正常", "1TB", "0.3TB", "30%", 6),
                DiskInfo("hdd-02", "HDD", "正常", "1TB", "0.2TB", "20%", 6),
                DiskInfo("hdd-03", "HDD", "正常", "0.9TB", "0.3TB", "33%", 6),
                DiskInfo("hdd-04", "HDD", "正常", "2TB", "0.5TB", "25%", 5),
                DiskInfo("ssd-01", "SSD", "正常", "4TB", "1.2TB", "30%", 4),
                DiskInfo("ssd-01", "SSD", "正常", "8TB", "3TB", "37.5%", 1)]
    else:  # 逻辑卷详细信息
        return [LogicVolumeInfo("ssd-vol-01", "1TB", "0.3TB", "30%"), LogicVolumeInfo("ssd-vol-02", "4TB", "0.7TB", "17.5%"),
                LogicVolumeInfo("ssd-vol-03", "2TB", "0.34TB", "17%"), LogicVolumeInfo("hdd-vol-01", "2TB", "0.7TB", "35%"),
                LogicVolumeInfo("hdd-vol-01", "3TB", "0.52TB", "17.3%"), LogicVolumeInfo("mix-01", "10TB", "7.2TB", "72%")]


# 通过update_info函数进行周期性地刷新
server_storage_info_list = ServerInfoList()
two_disk_info_list = TwoDiskInfoList()
