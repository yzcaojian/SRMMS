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

                # 将硬盘容量单位都换算为KB
                temp = disk_list[item][3]
                capacity = float(temp[:-1])
                if temp[-1].lower() == "t":
                    capacity *= 1024 * 1024 * 1024
                elif temp[-1].lower() == "g":
                    capacity *= 1024 * 1024
                else:
                    capacity *= 1024
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


def get_disk_used_capacity(disk_dict, part_dict):
    (status, output) = subprocess.getstatusoutput("df")

    if status == 0:
        list_ = output.split('\n')[1:]
        disk_list = []
        for i in range(len(list_)):
            disk_list.append(list_[i].split())

        # 总容量/已使用容量
        for disk in disk_dict:
            disk.append(0)

        # Filesystem/1K-blocks/Used/Available/Use%/Mounted on
        for item in range(len(disk_list)):
            disk_id = disk_list[item][0].split('/')[-1]
            # 该disk是单个物理盘
            if disk_id in disk_dict:
                disk_dict[disk_id][1] += float(disk_list[item][2])
            # 该disk是某个物理盘上的分区
            elif disk_id in part_dict:
                disk_dict[part_dict[disk_id]][1] += float(disk_list[item][2])
            else:
                continue
        # 总容量/已使用容量/占用率
        for disk in disk_dict:
            total = disk[0]
            used = disk[1]
            disk.append(used / total)
        return 0

    else:
        return -1


def get_disk_io(disk_dict):
    (status, output) = subprocess.getstatusoutput("iostat -d")

    if status == 0:
        list_ = output.split('\n')[3:-2]
        disk_list = []
        for i in range(len(list_)):
            disk_list.append(list_[i].split())

        # 总容量/已使用容量/占用率/io负载(kB)
        for disk in disk_dict:
            disk.append(0)

        # Device / tps / kB_read/s / kB_wrtn/s / kB_dscd/s / kB_read / kB_wrtn / kB_dscd
        for item in range(len(disk_list)):
            disk_id = disk_list[item][0]
            if disk_id in disk_dict:
                kB_read = float(disk_list[item][5])
                kB_wrtn = float(disk_list[item][6])

                disk_dict[disk_id][3] = kB_read + kB_wrtn
            else:
                continue
        return 0

    else:
        return -1


def get_disk_io(disk_dict):
    pass


while True:
    port = 12344
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', port))
    s.listen(1)
    sock, addr = s.accept()
    print("连接已经建立")
    dic = {"overall_info": ["2000", "1000", "50%", "5", "4", "1200", "800", "50%", "50%", "0", "0", "100000", "200000"],
           "detailed_info": [["0001", "SSD", "正常", "200", "100", "50%", "40000"]], "smart_data": []}
    string = json.dumps(dic)
    while True:
        info = sock.recv(1024).decode()
        if info == "请求数据":
            byte = bytes(string, encoding="utf-8")
            sock.send(byte)
        elif info == "断开连接":
            break
    sock.close()
    s.close()


