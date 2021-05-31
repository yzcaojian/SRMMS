# -*- coding: utf-8 -*-
# @ModuleName: RSA_4
# @Function: 资源调度分配子模块
# @Author: Chen Zhongwei
# @Time: 2021/5/6 15:56

import time
from interface.in_interface import in_interface_impl
from resource_status_display.configuration_checking import configuration_info


# 资源调度分配
# disk_detailed_info为字典  格式为{IP:{diskID:[type, state, totalCapacity, occupiedCapacity, occupiedRate}}
# warning_message_queue为列表  格式为[errorID, timeslot, severIP, diskID,...]


def resource_scheduling_allocation(disk_detailed_info, warning_message_queue):
    for warning_message in warning_message_queue:
        errorID, timeslot, serverName, diskID = warning_message.errorId, warning_message.timeslot, warning_message.serverName, warning_message.diskId
        serverIP = configuration_info.NametoIP(serverName)
        # 硬盘故障预警信息
        if errorID == 1:
            health_degree = warning_message.healthDegree
            now_time = time.time()
            past_minutes = (now_time - timeslot) / 60
            instructions = "位于服务器" + serverName + "的硬盘" + diskID + "在" + past_minutes \
                           + "分钟前预测到即将出现故障，当前健康度为" + health_degree
            # 分配指令日志信息 to资源状态显示模块
            in_interface_impl().IN_RSA_RSD(serverName, diskID, instructions)
            # 发送分配指令 to数据通信解析模块
            in_interface_impl().IN_RSA_DCA(serverIP, instructions)

        # IO高负载预警
        elif errorID == 2:
            io_prediction = warning_message.IOPeak
            now_time = time.time()
            past_minutes = (now_time - timeslot) / 60
            instructions = "位于服务器" + serverName + "的硬盘" + diskID + "在" + past_minutes \
                           + "分钟前预测到即将出现高I/O负载，最大负载量为" + io_prediction
            # 分配指令日志信息 to资源状态显示模块
            in_interface_impl().IN_RSA_RSD(serverName, diskID, instructions)
            # 发送分配指令 to数据通信解析模块
            in_interface_impl().IN_RSA_DCA(serverIP, instructions)

        # 服务器失联告警
        elif errorID == 3:
            now_time = time.time()
            past_minutes = (now_time - timeslot) / 60
            instructions = "由于未知原因，服务器" + serverName + "在" + past_minutes + "分钟前失联"
            # 分配指令日志信息 to资源状态显示模块
            in_interface_impl().IN_RSA_RSD(serverName, -1, instructions)
            # # 发送分配指令 to数据通信解析模块
            # in_interface_impl().IN_RSA_DCA(severIP, instructions)

        # 硬盘持续高IO
        elif errorID == 4:
            io_average = warning_message.IOAverage
            now_time = time.time()
            past_minutes = (now_time - timeslot) / 60
            instructions = "位于服务器" + serverName + "的硬盘" + diskID + "在" + past_minutes + \
                           "分钟前开始处于高I/O状态， I/O负载平均量为" + io_average
            # 分配指令日志信息 to资源状态显示模块
            in_interface_impl().IN_RSA_RSD(serverName, diskID, instructions)
            # 发送分配指令 to数据通信解析模块
            in_interface_impl().IN_RSA_DCA(serverIP, instructions)

    # 处理完所有请求,将异常消息列表清空
    warning_message_queue = []
