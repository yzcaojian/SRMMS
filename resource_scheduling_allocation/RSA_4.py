# -*- coding: utf-8 -*-
# @ModuleName: RSA_4
# @Function: 资源调度分配子模块
# @Author: Chen Zhongwei
# @Time: 2021/5/6 15:56

import time
import _thread
from interface.in_interface import in_interface_impl
from resource_status_display.configuration_checking import configuration_info
from resource_status_display.log_exception_with_suggestions import Warning, Scheduling, scheduling_list


# 资源调度分配
# disk_detailed_info为字典  格式为{IP:{diskID:[type, state, totalCapacity, occupiedCapacity, occupiedRate}}
# warning_message_queue为列表  格式为[errorID, timeslot, severIP, diskID,...]


def resource_scheduling_allocation(disk_detailed_info, warning_message_queue):
    for warning_message in warning_message_queue:
        errorID, timeslot, serverName, diskID = warning_message.errorId, warning_message.timeslot, warning_message.serverName, warning_message.diskId
        if errorID == 3:
            continue
        serverIP = configuration_info.NametoIP(serverName)
        now_time = time.time()
        now_time = time.strftime("%Y{y}%m{m}%d{d}%H:%M", time.localtime(now_time)).format(y='年', m='月', d='日')
        # 生成调度信息，一方面写入调度分配文件，一方面生成调度分配指令
        scheduling = Scheduling(errorID, now_time, serverName, diskID, situation=warning_message.warningContent)
        scheduling_list.add_new_scheduling(scheduling)

        # 发送分配指令 to数据通信解析模块
        _thread.start_new_thread(in_interface_impl.IN_RSA_DCA, (serverIP, scheduling.suggestion))

    # 处理完所有请求,将异常消息列表清空
    warning_message_queue.clear()

        # # 硬盘故障预警信息
        # if errorID == 1:
        #     # past_minutes = (now_time - timeslot) / 60
        #     # instructions = "位于服务器" + serverName + "的硬盘" + diskID + "在" + past_minutes \
        #     #                + "分钟前预测到即将出现故障，当前健康度为" + health_degree
        #     # 发送分配指令 to数据通信解析模块
        #     in_interface_impl.IN_RSA_DCA(serverIP, scheduling.suggestion)
        #
        # # IO高负载预警
        # elif errorID == 2:
        #     # io_prediction = warning_message.IOPeak
        #     now_time = time.time())
        #     # past_minutes = (now_time - timeslot) / 60
        #     # instructions = "位于服务器" + serverName + "的硬盘" + diskID + "在" + past_minutes \
        #     #                + "分钟前预测到即将出现高I/O负载，最大负载量为" + io_prediction
        #     # 分配指令日志信息 to资源状态显示模块
        #     in_interface_impl.IN_RSA_RSD(serverName, diskID, instructions)
        #     # 发送分配指令 to数据通信解析模块
        #     in_interface_impl.IN_RSA_DCA(serverIP, instructions)
        #
        # # 服务器失联告警
        # elif errorID == 3:
        #     now_time = time.time()
        #     past_minutes = (now_time - timeslot) / 60
        #     instructions = "由于未知原因，服务器" + serverName + "在" + past_minutes + "分钟前失联"
        #     # 分配指令日志信息 to资源状态显示模块
        #     in_interface_impl.IN_RSA_RSD(serverName, -1, instructions)
        #     # # 发送分配指令 to数据通信解析模块
        #     # in_interface_impl.IN_RSA_DCA(severIP, instructions)
        #
        # # 硬盘持续高IO
        # elif errorID == 4:
        #     io_average = warning_message.IOAverage
        #     now_time = time.time()
        #     past_minutes = (now_time - timeslot) / 60
        #     instructions = "位于服务器" + serverName + "的硬盘" + diskID + "在" + past_minutes + \
        #                    "分钟前开始处于高I/O状态， I/O负载平均量为" + io_average
        #     # 分配指令日志信息 to资源状态显示模块
        #     in_interface_impl.IN_RSA_RSD(serverName, diskID, instructions)
        #     # 发送分配指令 to数据通信解析模块
        #     in_interface_impl.IN_RSA_DCA(serverIP, instructions)

