# -*- coding: utf-8 -*-
# @ModuleName: RSA_3
# @Function: 监控应用需求子模块
# @Author: Chen Zhongwei
# @Time: 2021/5/6 15:56
import time
from resource_scheduling_allocation.errors import ServerLostError, DiskIOHighOccupiedError, DiskFailureError
from resource_status_display.configuration_checking import configuration_info


# 监控应用需求_服务器失联告警
def sever_disconnection_warning(io_load_queue, warning_message_queue):
    if not io_load_queue:
        return
    for ip in io_load_queue:
        # 根据ip选择对应服务器的io负载队列
        disk_io_data = io_load_queue[ip]
        # 取出输入队列中最新入队的元素
        for diskID in disk_io_data:
            io_data = disk_io_data[diskID][-1]
            # 获得插入该数据的时间戳  每个时间戳都以自从1970年1月1日午夜（历元）经过了多长时间来表示,单位为秒
            time_stamp = io_data[-1]
            now_time = time.time()
            # 间隔超过十分钟  视作服务器失联
            if now_time - time_stamp > 600:
                errorID = 3
                # 服务器失联异常消息[03, 事件发生时间, 服务器名称, 硬盘标识]
                warning_message_queue.append(ServerLostError(errorID, now_time, configuration_info.IPtoName(ip), diskID))
            break


# 筛选高IO负载数据
def filtering_io_data(ip, io_data, average_io_load, high_io_load_queue):
    # io_data:[diskID, diskIO, timestamp]
    # 若该服务器不在此字典中
    if ip not in average_io_load:
        average_io_load[ip] = {}
    diskID, diskIO, timestamp = io_data
    # average_io_load[ip][diskID]:[count, averageIO]
    # 若该硬盘不在此字典中
    if diskID not in average_io_load[ip]:
        average_io_load[ip][diskID] = [0, 0]
    count, averageIO = average_io_load[ip][diskID]
    # 如果统计数目过多 将统计个数减少到1000
    if count >= 10000:
        count = 1000
    averageIO = (count * averageIO) + diskIO / (count + 1)
    average_io_load[ip][diskID] = [count + 1, averageIO]

    # 高于平均负载的1.2倍或者高于10w视作高负载
    if diskIO > averageIO * 1.2 or diskIO >= 100000:
        # 若该服务器不在此字典中
        if ip not in high_io_load_queue:
            high_io_load_queue[ip] = {}
        # 若该硬盘不在此字典中
        if diskID not in high_io_load_queue[ip]:
            high_io_load_queue[ip][diskID] = []
        # 将高负载硬盘数据加入到高负载队列中
        high_io_load_queue[ip][diskID].append([diskIO, timestamp])


# 监控应用需求_硬盘持续高I/O需求
def hard_disk_high_io_warning(high_io_load_queue, warning_message_queue):
    for serverIP in high_io_load_queue:
        for diskID in high_io_load_queue[serverIP]:
            # 取出该硬盘最新插入的数据
            io_data = high_io_load_queue[serverIP][diskID][-1]
            time_stamp = io_data[-1]
            now_time = time.time()
            # 间隔超过十分钟,将该列表清空
            if now_time - time_stamp > 600:
                high_io_load_queue[serverIP][diskID] = []
                continue
            # 高负载队列数据超过20个,最新插入的数据的时间间隔小于一分钟,视作该硬盘持续高IO负载
            if len(high_io_load_queue[serverIP][diskID]) > 20 and now_time - time_stamp < 60:
                sum = 0
                for item in high_io_load_queue[serverIP][diskID]:
                    sum += item[0]
                average_io = sum / len(high_io_load_queue[serverIP][diskID])
                errorID = 4
                # 硬盘持续高IO异常消息[04, 事件发生时间, 服务器IP, 硬盘标识, 持续期间平均IO负载]
                warning_message_queue.append(DiskIOHighOccupiedError(errorID, now_time, configuration_info.IPtoName(serverIP), diskID, average_io))


def hard_disk_failutre_warning(hard_disk_failure_prediction_list, warning_message_queue):
    # 如果列表不为空
    if hard_disk_failure_prediction_list:
        ip, disk_id, failure_info = hard_disk_failure_prediction_list
        health_degree, timestamp = failure_info
        errorID = 1
        warning_message_queue.append(DiskFailureError(errorID, timestamp, configuration_info.IPtoName(ip), disk_id, health_degree))
