# -*- coding: utf-8 -*-
# @ModuleName: main
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/5/10 10:14

import time
from interface.in_interface import in_interface_impl
from resource_scheduling_allocation.RSA_1 import io_second_to_io_minute,online_model_training
from resource_scheduling_allocation.RSA_2 import io_load_prediction
from resource_scheduling_allocation.RSA_3 import sever_disconnection_warning, filtering_io_data, hard_disk_high_io_warning, hard_disk_failutre_warning
from resource_scheduling_allocation.RSA_4 import resource_scheduling_allocation


# I/O负载输入队列
io_load_input_queue = {}
io_load_input_queue_predict = {}  # 预测用
io_load_input_queue_train = {}  # 训练用
# I/O负载输出队列
io_load_output_queue = {}
# 高负载队列
high_io_load_queue = {}
# 记录平均I/O负载  average_io_load[ip][diskID]:[count, averageIO]
average_io_load = {}
# 异常消息列表  [异常ID, 事件发生事件, 服务器IP, 硬盘标识,...]
warning_message_queue = []
# disk_detailed_info为字典  格式为{IP:{diskID:[type, state, totalCapacity, occupiedCapacity, occupiedRate}}
disk_detailed_info = {}
# 存放IO的平均值和标准差
mean_and_std = []

save_model = ['../IO_load_prediction_model_training/model/Financial4/', 'Model']

while True:
    detailed_info_list = in_interface_impl().getData_disk_io()
    for ip, detailed_info in detailed_info_list:
        for disk_id, type, state, total_capacity, occupied_capacity, occupied_rate, disk_io in detailed_info:
            # 将信息添加到详细信息字典中
            if ip not in disk_detailed_info:
                disk_detailed_info = {}
            if disk_id not in disk_detailed_info[ip]:
                disk_detailed_info[ip][disk_id] = []
            disk_detailed_info[ip][disk_id].append([type, state, total_capacity, occupied_capacity, occupied_rate])
            now_time = time.time()
            # I/O负载进入输入队列之前先检测是否高负载
            filtering_io_data(ip, [disk_id, disk_io, now_time], average_io_load, high_io_load_queue)
            # 将I/O负载信息添加到输入队列中
            if ip not in io_load_input_queue:
                io_load_input_queue[ip] = {}
            if disk_id not in io_load_input_queue[ip]:
                io_load_input_queue[ip][disk_id] = []
            io_load_input_queue[ip][disk_id].append([disk_io, now_time])

    # 将以秒为单位的I/O负载数据转化为以分钟为单位的I/O数据
    io_second_to_io_minute(io_load_input_queue, io_load_input_queue_predict)
    io_second_to_io_minute(io_load_input_queue, io_load_input_queue_train)

    # 线上训练
    online_model_training(io_load_input_queue_train, mean_and_std, save_model)

    # IO负载预测
    io_load_prediction(io_load_input_queue_predict, io_load_output_queue, mean_and_std, save_model[0],
                       average_io_load, warning_message_queue)

    # 检查是否有硬盘故障预警
    hard_disk_failure_prediction_list = in_interface_impl().getData_hard_disk_failure_prediction()
    hard_disk_failutre_warning(hard_disk_failure_prediction_list, warning_message_queue)
    # 判断服务器失联告警
    sever_disconnection_warning(io_load_input_queue, warning_message_queue)
    # 判断硬盘持续高I/O需求
    hard_disk_high_io_warning(high_io_load_queue, warning_message_queue)

    # 处理异常消息
    resource_scheduling_allocation(disk_detailed_info, warning_message_queue)


