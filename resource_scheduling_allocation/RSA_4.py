# -*- coding: utf-8 -*-
# @ModuleName: RSA_4
# @Function: 资源调度分配子模块
# @Author: Chen Zhongwei
# @Time: 2021/5/6 15:56

import time
from interface.in_interface import in_interface_impl


# 资源调度分配
# disk_detailed_info为字典  格式为{IP:{diskID:[type, state, totalCapacity, occupiedCapacity, occupiedRate}}
# warning_message_queue为列表  格式为[errorID, timeslot, severIP, diskID,...]
def resource_scheduling_allocation(disk_detailed_info, warning_message_queue):
    for warning_message in warning_message_queue:
        errorID, timeslot, severIP, diskID = warning_message[:4]
        # 硬盘故障预警信息
        if errorID == 1:
            health_degree = warning_message[4]
            now_time = time.time()
            past_minutes = (now_time - timeslot) / 60
            instructions = "位于服务器" + severIP + "的硬盘" + diskID + "在" + past_minutes \
                           + "分钟前预测到即将出现故障，当前健康度为" + health_degree
            # 分配指令日志信息 to资源状态显示模块
            in_interface_impl().IN_RSA_RSD(severIP, diskID, instructions)
            # 发送分配指令 to数据通信解析模块
            in_interface_impl().IN_RSA_DCA(severIP, instructions)

        # IO高负载预警
        elif errorID == 2:
            io_prediction = warning_message[4]
            now_time = time.time()
            past_minutes = (now_time - timeslot) / 60
            instructions = "位于服务器" + severIP + "的硬盘" + diskID + "在" + past_minutes \
                           + "分钟前预测到即将出现高I/O负载，最大负载量为" + io_prediction
            # 分配指令日志信息 to资源状态显示模块
            in_interface_impl().IN_RSA_RSD(severIP, diskID, instructions)
            # 发送分配指令 to数据通信解析模块
            in_interface_impl().IN_RSA_DCA(severIP, instructions)

        # 服务器失联告警
        elif errorID == 3:
            now_time = time.time()
            past_minutes = (now_time - timeslot) / 60
            instructions = "由于未知原因，服务器" + severIP + "在" + past_minutes + "分钟前失联"
            # 分配指令日志信息 to资源状态显示模块
            in_interface_impl().IN_RSA_RSD(severIP, -1, instructions)
            # # 发送分配指令 to数据通信解析模块
            # in_interface_impl().IN_RSA_DCA(severIP, instructions)

        # 硬盘持续高IO
        elif errorID == 4:
            now_time = time.time()
            past_minutes = (now_time - timeslot) / 60
            instructions = "位于服务器" + severIP + "的硬盘" + diskID + "在" + past_minutes + "分钟前处于高I/O状态"
            # 分配指令日志信息 to资源状态显示模块
            in_interface_impl().IN_RSA_RSD(severIP, diskID, instructions)
            # 发送分配指令 to数据通信解析模块
            in_interface_impl().IN_RSA_DCA(severIP, instructions)

    # 处理完所有请求,将异常消息列表清空
    warning_message_queue = []
