

"""
-*- coding: utf-8 -*- 
@Project: SRMMS
@Description: 监控应用需求期间可能产生的四种异常
@Time : 2021/5/31 15:04
@Author : cao jian
"""


class ServerError:
    def __init__(self, errorId, timeslot, serverName, diskId):
        self.errorId = errorId
        self.timeslot = timeslot
        self.serverName = serverName
        self.diskId = diskId


class DiskFailureError(ServerError):
    def __init__(self, errorId, timeslot, serverName, diskId, healthDegree):
        super().__init__(errorId, timeslot, serverName, diskId)
        self.healthDegree = healthDegree


class DiskHighLevelIOError(ServerError):
    def __init__(self, errorId, timeslot, serverName, diskId, IOPeak):
        super().__init__(errorId, timeslot, serverName, diskId)
        self.IOPeak = IOPeak


class ServerLostError(ServerError):
    def __init__(self, errorId, timeslot, serverName, diskId):
        super().__init__(errorId, timeslot, serverName, diskId)


class DiskIOHighOccupiedError(ServerError):
    def __init__(self, errorId, timeslot, serverName, diskId, IOAverage):
        super().__init__(errorId, timeslot, serverName, diskId)
        self.IOAverage = IOAverage


