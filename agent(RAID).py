# -*- coding: utf-8 -*-
# @ModuleName: collect_data
# @Function:
# @Author: Chen Zhongwei
# @Time: 2021/9/23 15:38
import subprocess
import socket
import json


# 获取硬盘总容量以及逻辑分区从属关系
def get_disk_total_capacity():
    disk_dict = {}
    part_dict = {}
    (status, output) = subprocess.getstatusoutput("lsblk -l")

    if status == 0:
        list_ = output.split('\n')[1:]
        disk_list = []
        for i in range(len(list_)):
            disk_list.append(list_[i].split())

        # NAME/MAJ:MIN/RM/SIZE/RO/TYPE/MOUNTPOINT
        for item in range(len(disk_list)):
            if disk_list[item][5].lower() == "disk":
                disk_dict[disk_list[item][0]] = []

                # 将硬盘容量单位都换算为GB
                temp = disk_list[item][3]
                capacity = float(temp[:-1])
                if temp[-1].lower() == "t":
                    capacity = round(capacity * 1024, 2)
                elif temp[-1].lower() == "g":
                    capacity = round(capacity, 2)
                elif temp[-1].lower() == "m":
                    capacity = round(capacity / 1024, 2)
                else:
                    capacity = round(capacity / 1024 / 1204, 2)
                disk_dict[disk_list[item][0]].append(capacity)

            elif disk_list[item][5].lower() == "part":
                i = item - 1
                while i >= 0:
                    if disk_list[i][5].lower() == "disk":
                        part_dict[disk_list[item][0]] = disk_list[i][0]
                        break
                    else:
                        i -= 1
            else:
                continue

        return disk_dict, part_dict

    else:
        return None, None


# 总容量/已使用容量
def get_disk_used_capacity(disk_dict, part_dict):
    (status, output) = subprocess.getstatusoutput("df")

    if status == 0:
        list_ = output.split('\n')[1:]
        disk_list = []
        for i in range(len(list_)):
            disk_list.append(list_[i].split())

        # 总容量/已使用容量
        for disk_id in disk_dict:
            disk_dict[disk_id].append(0)

        # Filesystem/1K-blocks/Used/Available/Use%/Mounted on
        for item in range(len(disk_list)):
            disk_id = disk_list[item][0].split('/')[-1]
            # 该disk是单个物理盘
            if disk_id in disk_dict:
                disk_dict[disk_id][1] += round(float(disk_list[item][2]) / 1024 / 1024, 2)
            # 该disk是某个物理盘上的分区
            elif disk_id in part_dict:
                disk_dict[part_dict[disk_id]][1] += round(float(disk_list[item][2]) / 1024 / 1024, 2)
            else:
                continue
        # 总容量/已使用容量/占用率
        for disk_id in disk_dict:
            total = disk_dict[disk_id][0]
            used = disk_dict[disk_id][1]
            disk_dict[disk_id].append(str(round(used / total * 100, 2)) + '%')
        return 0

    else:
        return -1


# 总容量/已使用容量/占用率/io负载(kB)
def get_disk_io(disk_dict):
    (status, output) = subprocess.getstatusoutput("iostat -d")

    if status == 0:
        list_ = output.split('\n')[3:-2]
        disk_list = []
        for i in range(len(list_)):
            disk_list.append(list_[i].split())

        # 总容量/已使用容量/占用率/io负载(kB)
        for disk_id in disk_dict:
            disk_dict[disk_id].append(0)

        # Device / tps / kB_read/s / kB_wrtn/s / kB_dscd/s / kB_read / kB_wrtn / kB_dscd
        for item in range(len(disk_list)):
            disk_id = disk_list[item][0]
            if disk_id in disk_dict:
                kB_read = float(disk_list[item][2])
                kB_wrtn = float(disk_list[item][3])
                # 保留一位小数
                disk_dict[disk_id][3] = round(kB_read + kB_wrtn, 1)
            else:
                continue
        return 0

    else:
        return -1


def integrate_data():
    # 获取总容量
    disk_dict, part_dict = get_disk_total_capacity()
    # 获取已使用容量和占用率
    get_disk_used_capacity(disk_dict, part_dict)
    # 获得io负载
    get_disk_io(disk_dict)

    total_capacity, total_used, total_io = 0, 0, 0
    detailed_info = []

    # 总容量 / 已使用容量 / 占用率 / io负载(kB)
    for disk_id in disk_dict:
        total_capacity += disk_dict[disk_id][0]
        total_used += disk_dict[disk_id][1]
        total_io += disk_dict[disk_id][3]

        detailed_info.append([disk_id, disk_dict[disk_id][0], disk_dict[disk_id][1], disk_dict[disk_id][2]])

    # 总体占用率
    occupied_rate = str(round(total_used / total_capacity * 100, 2)) + '%'

    # 单位为GB,保留两位小数
    total_capacity = round(total_capacity, 2)
    total_used = round(total_used, 2)

    # I/O负载数据保留一位小数
    total_io = round(total_io, 1)

    overall_info = [total_capacity, total_used, occupied_rate, total_io]

    dic = {"overall_info": overall_info, "detailed_info": detailed_info}
    return dic


port = 12345
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('10.17.19.124', port))
loop_flag = True
while loop_flag:
    s.listen(1)
    sock, addr = s.accept()
    print("连接已经建立")

    info = sock.recv(1024).decode().split('/')
    if info[0] == "请求数据1" or info[0] == "请求数据2":  # 包含smart数据
        dic = integrate_data()
        string = json.dumps(dic)
        byte = bytes(string, encoding="utf-8")
        sock.send(byte)
    # elif info[0] == "接收指令":
    #     instructions = info[1]
    #     file = open('./instructions.txt', 'a+')
    #     file.writelines(instructions + "\n")
    #     file.close()

    sock.close()
    print("连接已经断开")
s.close()
