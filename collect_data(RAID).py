# -*- coding: utf-8 -*-
# @ModuleName: collect_data(RAID)
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/9/28 10:39
import psutil
import socket
import json


# 逻辑盘标识/路径
def get_disk_list():
    list_ = psutil.disk_partitions()
    disk_list = []
    for item in list_:
        disk_list.append([item[0], item[1]])
    return disk_list


# 逻辑盘标识/路径/总容量(kB)/已使用容量/占用率
def get_disk_total_and_used_capacity(disk_list):
    for item in disk_list:
        total, used, free, percent = psutil.disk_usage(item[1])
        # 单位统一转化为kB
        item.append(total / 1024)
        item.append(used / 1024)
        item.append(str(round(percent, 2)) + '%')
    return 0


def integrate_data():
    disk_list = get_disk_list()
    get_disk_total_and_used_capacity(disk_list)
    total_capacity, used_capacity = 0, 0
    detailed_info = []
    for item in disk_list:
        total_capacity += item[2]
        used_capacity += item[3]
        detailed_info.append([item[0], item[2], item[3], item[4]])
    # 总体占用率
    occupied_rate = str(round(used_capacity / total_capacity * 100, 2)) + '%'
    read_count, write_count, read_bytes, write_bytes, read_time, write_time = psutil.disk_io_counters()
    # 单位统一为kB
    total_io = (read_bytes + write_bytes) / 1024
    overall_info = [total_capacity, used_capacity, occupied_rate, total_io]

    dic = {"overall_info": overall_info, "detailed_info": detailed_info}
    return dic


port = 12344
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', port))
loop_flag = True
while loop_flag:
    s.listen(1)
    sock, addr = s.accept()
    print("连接已经建立")
    while True:
        info = sock.recv(1024).decode()
        if info == "请求数据":
            dic = integrate_data()
            string = json.dumps(dic)
            byte = bytes(string, encoding="utf-8")
            sock.send(byte)
        elif info == "断开连接":
            break
    sock.close()
s.close()
