# -*- coding: utf-8 -*-
# @ModuleName: RSA_1
# @Function: 预测模型训练子模块
# @Author: Chen Zhongwei
# @Time: 2021/5/6 15:53


# 线上模型训练
def online_model_training():
    pass


def io_second_to_io_minute(io_load_input_queue, io_load_input_queue_minute):
    for ip in io_load_input_queue:
        for disk_id in io_load_input_queue[ip]:
            if len(io_load_input_queue[ip][disk_id]) < 60:
                continue
            total_io = 0
            total_time = 0
            # 取前面60个数据
            for disk_io, time_stamp in io_load_input_queue[ip][disk_id][:60]:
                total_io += disk_io
                total_time += time_stamp
            if ip not in io_load_input_queue_minute:
                io_load_input_queue_minute[ip] = {}
            if disk_id not in io_load_input_queue_minute[ip]:
                io_load_input_queue_minute[ip][disk_id] = []
            # //整除  时间需要取平均值
            io_load_input_queue_minute[ip][disk_id].append([total_io, total_time // 60])
            # 将前面60个数据删除
            io_load_input_queue[ip][disk_id] = io_load_input_queue[ip][disk_id][60:]


# list = [1, 2, 3, 4]
# print(list)
# list = list[4:]
# print(list)