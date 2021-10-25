import locale
import time

"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: 关于调度分配日志信息与告警信息读写文件的类
@Time : 2021/5/3 21:13
@Author : cao jian
"""


class Scheduling:
    schedule_num = 0

    def __init__(self, errorId, timeslot, serverName, diskId, situation):
        self.scheduleId = Scheduling.schedule_num
        Scheduling.schedule_num += 1
        self.timeslot = timeslot
        self.serverName = serverName
        self.diskId = diskId
        self.situation = situation  # situation就是Warning对象中的warningContent属性
        self.suggestion = self.get_suggestion(errorId)
        self.feedback = ""
        self.write_file()

    def get_suggestion(self, errorId):
        if errorId == 1:
            return "减少服务器" + self.serverName + "上标识为" + self.diskId + "的机械硬盘的I/O需求操作，将I/O操作向其他硬盘调度，以延长硬盘寿命。"
        elif errorId == 2:
            return "提前为服务器" + self.serverName + "上标识为" + self.diskId + "的硬盘分配资源，以便快速满足高I/O负载需求。"
        elif errorId == 4:
            return "减少服务器" + self.serverName + "上标识为" + self.diskId + "的硬盘处理任务， 向其他盘均衡调度。"
        return ""

    def write_file(self):
        file = open('./txt/schedule.txt', 'a+')
        file.writelines(self.timeslot + " 系统向服务器" + self.serverName + "发送调度建议，针对\"" +
                        self.situation + "\"的情况，向服务器作出如下调度建议：" + self.suggestion + "\n")
        file.close()


class Warning:
    warning_num = 0

    def __init__(self, errorId, timeslot, serverName, diskId, extra):
        # extra表示在不同异常情况发生时需要传入的额外参数
        # self.warningId = str(errorId) + '_' + str(Warning.warning_num)
        self.errorId = errorId
        self.timeslot = timeslot
        self.serverName = serverName
        self.diskId = diskId
        self.warningContent = self.get_content(extra)  # content要根据其他字段生成
        self.write_file()

    def get_content(self, extra):
        content = self.timeslot + " 服务器" + self.serverName
        if self.errorId == 1:  # 硬盘即将故障的情况：extra为healthState
            if extra > 6:
                health = "R1-" + str(extra - 6)
            else:
                health = "R" + str(extra)
            content += "上标识为" + self.diskId + "的机械硬盘健康度下降为" + health + "。"
        elif self.errorId == 2:  # I/O即将高负载的情况：extra为[time, IOPeak]
            content += "上标识为" + self.diskId + "的机械硬盘预计在" + str(extra[0]) + "出现高负载需求，" + "负载最大量将达到" + str(extra[1]) + "KB。"
        elif self.errorId == 3:
            content += "由于未知原因长时间未响应，处理为失联，并尝试重新连接。"
        elif self.errorId == 4:
            content += "上标识为" + self.diskId + "的硬盘长时间处于高负载环境下，平均I/O负载量为" + str(extra) + "KB。"
        return content

    def write_file(self):
        file = open('./txt/warning.txt', 'a+')
        file.writelines(str(self.errorId) + " " + self.warningContent + "\n")
        file.close()


class SchedulingList:
    def __init__(self):
        super().__init__()
        self.scheduling_list = []
        self.read_file()

    # scheduling是Scheduling类的对象
    def add_new_scheduling(self, scheduling):
        self.scheduling_list.append(scheduling.timeslot + " 系统向服务器" + scheduling.serverName + "发送调度建议，针对\"" +
                                    scheduling.situation + "\"的情况，向服务器作出如下调度建议：" + scheduling.suggestion + "\n")

    def read_file(self):
        file = open('../resource_status_display/txt/schedule.txt', 'r')
        line = file.readline()
        while line:
            self.scheduling_list.append(line)
            line = file.readline()
        file.close()


class WarningList:
    def __init__(self):
        super().__init__()
        self.warning_list = []
        self.read_file()
        # self.warning_list = [[1, "2021年4月25日09:12 服务器server1上标识为disk-01的机械硬盘健康度下降为R4。"],
        #                      [2, "2021年4月25日10:10 服务器server2上标识为disk-03的机械硬盘预计在4月25日10:20出现高负载需求，负载最大量将达到7890KB。"],
        #                      [3, "2021年4月25日12:30 服务器server1长时间未响应，处理为失联，并尝试重新连接。"],
        #                      [4, "2021年4月25日18:36 服务器local4上标识为disk-nvm-02的硬盘长时间处于高负载环境下，平均I/O负载量为8520KB。"]]

    # 调用添加告警信息，在资源调度分配模块产生告警信息时调用，warning是Waning类的对象
    def add_new_warning(self, warning):
        self.warning_list.append([warning.errorId, warning.warningContent + "\n"])

    # 读文件初始化，开始文件为空，之后退出程序再进入程序能读入以前的告警信息
    def read_file(self):
        file = open('../resource_status_display/txt/warning.txt', 'r')
        line = file.readline()
        while line:
            index = line.find(' ')
            self.warning_list.append([int(line[:index]), line[index + 1:]])
            line = file.readline()
        file.close()


# 采用单例模式，在整个系统中只有一个WarningList和LogList对象存在
# 在资源调度分配模块中采用warning_list.add_new_warning()添加新的告警信息
warning_list = WarningList()
# 在资源调度分配模块采用schedule_list.add_new_scheduling()添加新的调度日志信息
scheduling_list = SchedulingList()

# s = Scheduling(1, "2021年4月25日07:01", "server4", "disk-23", warning_list.warning_list[0][1][:-2])
# s1 = Scheduling(1, "2021年4月25日09:26", "server1", "disk-01", warning_list.warning_list[1][1][:-2])
# s2 = Scheduling(2, "2021年4月25日10:11", "server2", "disk-03", warning_list.warning_list[2][1][:-2])
# s3 = Scheduling(4, "2021年4月25日19:36", "local4", "disk-nvm-02", warning_list.warning_list[4][1][:-2])
