# -*- coding: utf-8 -*-
# @ModuleName: collect_data
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/9/23 15:38
import subprocess
import socket
import json
import time
import _thread


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


# 总容量/已使用容量/占用率/io负载(kB)/运行状态
def get_disk_running_status(disk_dict):
    for disk_id in disk_dict:
        disk_dict[disk_id].append("正常")
    return 0


# 总容量/已使用容量/占用率/io负载(kB)/运行状态/硬盘类型
def get_disk_type(disk_dict):
    (status, output) = subprocess.getstatusoutput("lsblk -d -o name,rota")
    if status == 0:
        list_ = output.split('\n')[1:]
        disk_list = []
        for i in range(len(list_)):
            disk_list.append(list_[i].split())
        for item in range(len(disk_list)):
            disk_id = disk_list[item][0]
            if disk_id in disk_dict:
                if disk_list[item][1] == "1":
                    disk_dict[disk_id].append("HDD")
                else:
                    disk_dict[disk_id].append("SSD")
            else:
                continue
        return 0
    else:
        return -1


# 总容量/已使用容量/占用率/io负载(kB)/故障率/运行状态/硬盘类型/smart数据
def get_smart_data(disk_dict, smart_data_dict):
    for disk_id in disk_dict:
        device_model = smart_data_dict[disk_id][0]
        smartID_list = smart_data_dict[disk_id][1]
        smartData_list = smart_data_dict[disk_id][2]
        disk_dict[disk_id].append([device_model, smartID_list, smartData_list])


def background_smart_data_collection(smart_data_dict):
    flag = True
    filename = "./smart_data.txt"
    try:
        # 读取smart数据文件执行恢复操作
        with open(filename, "r", encoding='utf-8') as f:
            smart_dict = json.load(f)
            time_stamp1 = time.strftime("%Y{y}%m{m}%d{d}", time.localtime(time.time() - 60 * 60 * 24))\
                .format(y='年', m='月', d='日')
            time_stamp2 = time.strftime("%Y{y}%m{m}%d{d}", time.localtime(time.time())).format(y='年', m='月', d='日')
            for disk_id in smart_dict:
                # 最新的数据为前一天或者当天
                if smart_dict[disk_id][3][-1] == time_stamp1 or smart_dict[disk_id][3][-1] == time_stamp2:
                    for disk_id in smart_dict:
                        smart_data_dict[disk_id] = smart_dict[disk_id]
                break
    # 文件不存在
    except IOError:
        print("历史smart数据文件不存在")

    while flag:
        disk_dict_, _ = get_disk_total_capacity()
        now_time = time.time()
        time_stamp = time.strftime("%Y{y}%m{m}%d{d}", time.localtime(now_time)).format(y='年', m='月', d='日')
        for disk_id in disk_dict_:
            device_model, smartID_list, smartData_list = "", [], []
            (status, output) = subprocess.getstatusoutput("smartctl -i /dev/" + disk_id)
            list_ = output.split('\n')[4:]
            device_model = list_[1].split()[-1]

            (status, output) = subprocess.getstatusoutput("smartctl -A /dev/" + disk_id)
            list_ = output.split('\n')[7:-1]
            disk_list = []
            # ID# / ATTRIBUTE_NAME / FLAG / VALUE / WORST / THRESH / TYPE / UPDATED / WHEN_FAILED / RAW_VALUE
            for i in range(len(list_)):
                disk_list.append(list_[i].split())
            for item in range(len(disk_list)):
                smartID_list.append(int(disk_list[item][0]))
                smartData_list.append(int(disk_list[item][9]))

            if disk_id not in smart_data_dict:
                smart_data_dict[disk_id] = [device_model, smartID_list, [smartData_list], [time_stamp]]
            else:
                # 若两个数据的时间戳相等，证明是在同一天
                if smart_data_dict[disk_id][3][-1] != time_stamp:
                    smart_data_dict[disk_id][2].append(smartData_list)
                    smart_data_dict[disk_id][3].appendt(time_stamp)

                    # smart数据最多只保存最新的20个,删去多余的数据
                    if len(smart_data_dict[disk_id][2]) > 20:
                        del smart_data_dict[disk_id][2][0]
                        del smart_data_dict[disk_id][3][0]

        # 删除可能因更换硬盘而存在的无效disk_id
        for disk_id in smart_data_dict:
            if disk_id not in disk_dict_:
                del smart_data_dict[disk_id]

        # 将smart数据写入文件中
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(smart_data_dict, f)

        # 每小时只收集一次数据
        time.sleep(60 * 60)


def integrate_data(smart_data_dict):
    # 获取总容量
    disk_dict, part_dict = get_disk_total_capacity()
    # 获取已使用容量和占用率
    get_disk_used_capacity(disk_dict, part_dict)
    # 获得io负载
    get_disk_io(disk_dict)
    # 获得故障率和运行状态
    get_disk_running_status(disk_dict)
    # 获得硬盘类型
    get_disk_type(disk_dict)
    # 获得smart数据
    get_smart_data(disk_dict, smart_data_dict)

    total_capacity, used_capacity, hdd_counts, ssd_counts, hdd_total_capacity, ssd_total_capacity, hdd_used_capacity,\
        ssd_used_capacity, hdd_io, ssd_io = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    detailed_info = []
    smart_data = []
    # 总容量 / 已使用容量 / 占用率 / io负载(kB)  / 运行状态 / 硬盘类型 / smart数据
    for disk_id in disk_dict:
        total_capacity += disk_dict[disk_id][0]
        used_capacity += disk_dict[disk_id][1]
        if disk_dict[disk_id][5] == "HDD":
            hdd_counts += 1
            hdd_total_capacity += disk_dict[disk_id][0]
            hdd_used_capacity += disk_dict[disk_id][1]
            hdd_io += disk_dict[disk_id][3]
        else:
            ssd_counts += 1
            ssd_total_capacity += disk_dict[disk_id][0]
            ssd_used_capacity += disk_dict[disk_id][1]
            ssd_io += disk_dict[disk_id][3]

        detailed_info.append([disk_id, disk_dict[disk_id][5], disk_dict[disk_id][4], disk_dict[disk_id][0],
                              disk_dict[disk_id][1], disk_dict[disk_id][2], disk_dict[disk_id][3]])

        # smart数据
        device_model = disk_dict[disk_id][6][0]
        smartID_list = disk_dict[disk_id][6][1]
        smartData_list = disk_dict[disk_id][6][2]

        smart_data.append([disk_id, device_model, smartID_list, smartData_list])

    # 总体占用率
    occupied_rate = str(round(used_capacity / total_capacity * 100, 2)) + '%'
    # hdd占用率
    if hdd_counts == 0:
        hdd_occupied_rate = 0
    else:
        hdd_occupied_rate = str(round(hdd_used_capacity / hdd_total_capacity * 100, 2)) + '%'
    # ssd占用率
    if ssd_counts == 0:
        ssd_occupied_rate = 0
    else:
        ssd_occupied_rate = str(round(ssd_used_capacity / ssd_total_capacity * 100, 2)) + '%'

    hdd_error_rate, ssd_error_rate = 0, 0
    # 单位为GB,保留两位小数
    total_capacity = round(total_capacity, 2)
    used_capacity = round(used_capacity, 2)
    hdd_total_capacity = round(hdd_total_capacity, 2)
    ssd_total_capacity = round(ssd_total_capacity, 2)
    hdd_used_capacity = round(hdd_used_capacity, 2)
    ssd_used_capacity = round(ssd_used_capacity, 2)

    # I/O负载数据保留一位小数
    hdd_io = round(hdd_io, 1)
    ssd_io = round(ssd_io, 1)

    overall_info = [total_capacity, used_capacity, occupied_rate, hdd_counts, ssd_counts, hdd_total_capacity,
                    ssd_total_capacity, hdd_used_capacity, ssd_used_capacity, hdd_occupied_rate, ssd_occupied_rate,
                    hdd_error_rate, ssd_error_rate, hdd_io, ssd_io]

    dic = {"overall_info": overall_info, "detailed_info": detailed_info, "smart_data": smart_data}
    return dic


def integrate_data_():  # 不带smart数据
    # 获取总容量
    disk_dict, part_dict = get_disk_total_capacity()
    # 获取已使用容量和占用率
    get_disk_used_capacity(disk_dict, part_dict)
    # 获得io负载
    get_disk_io(disk_dict)
    # 获得故障率和运行状态
    get_disk_running_status(disk_dict)
    # 获得硬盘类型
    get_disk_type(disk_dict)

    total_capacity, used_capacity, hdd_counts, ssd_counts, hdd_total_capacity, ssd_total_capacity, hdd_used_capacity,\
        ssd_used_capacity, hdd_io, ssd_io = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    detailed_info = []
    # 总容量 / 已使用容量 / 占用率 / io负载(kB)  / 运行状态 / 硬盘类型 / smart数据
    for disk_id in disk_dict:
        total_capacity += disk_dict[disk_id][0]
        used_capacity += disk_dict[disk_id][1]
        if disk_dict[disk_id][5] == "HDD":
            hdd_counts += 1
            hdd_total_capacity += disk_dict[disk_id][0]
            hdd_used_capacity += disk_dict[disk_id][1]
            hdd_io += disk_dict[disk_id][3]
        else:
            ssd_counts += 1
            ssd_total_capacity += disk_dict[disk_id][0]
            ssd_used_capacity += disk_dict[disk_id][1]
            ssd_io += disk_dict[disk_id][3]

        detailed_info.append([disk_id, disk_dict[disk_id][5], disk_dict[disk_id][4], disk_dict[disk_id][0],
                              disk_dict[disk_id][1], disk_dict[disk_id][2], disk_dict[disk_id][3]])

    # 总体占用率
    occupied_rate = str(round(used_capacity / total_capacity * 100, 2)) + '%'
    # hdd占用率
    if hdd_counts == 0:
        hdd_occupied_rate = 0
    else:
        hdd_occupied_rate = str(round(hdd_used_capacity / hdd_total_capacity * 100, 2)) + '%'
    # ssd占用率
    if ssd_counts == 0:
        ssd_occupied_rate = 0
    else:
        ssd_occupied_rate = str(round(ssd_used_capacity / ssd_total_capacity * 100, 2)) + '%'

    hdd_error_rate, ssd_error_rate = 0, 0
    # 单位为GB,保留两位小数
    total_capacity = round(total_capacity, 2)
    used_capacity = round(used_capacity, 2)
    hdd_total_capacity = round(hdd_total_capacity, 2)
    ssd_total_capacity = round(ssd_total_capacity, 2)
    hdd_used_capacity = round(hdd_used_capacity, 2)
    ssd_used_capacity = round(ssd_used_capacity, 2)

    # I/O负载数据保留一位小数
    hdd_io = round(hdd_io, 1)
    ssd_io = round(ssd_io, 1)

    overall_info = [total_capacity, used_capacity, occupied_rate, hdd_counts, ssd_counts, hdd_total_capacity,
                    ssd_total_capacity, hdd_used_capacity, ssd_used_capacity, hdd_occupied_rate, ssd_occupied_rate,
                    hdd_error_rate, ssd_error_rate, hdd_io, ssd_io]

    dic_ = {"overall_info": overall_info, "detailed_info": detailed_info}
    return dic_


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.1.1.1', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


smart_data_dict = {}

# 后台线程收集smart数据
_thread.start_new_thread(background_smart_data_collection, smart_data_dict)

ip = get_host_ip()
port = 12345
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ip, port))
loop_flag = True
while loop_flag:
    s.listen(1)
    sock, addr = s.accept()
    print("连接已经建立")

    info = sock.recv(1024).decode().split('/')
    if info[0] == "请求数据1":  # 包含smart数据
        dic = integrate_data(smart_data_dict)
        string = json.dumps(dic)
        byte = bytes(string, encoding="utf-8")
        sock.send(byte)
    elif info[0] == "请求数据2":  # 不包含smart数据
        dic = integrate_data_()
        string = json.dumps(dic)
        byte = bytes(string, encoding="utf-8")
        sock.send(byte)
    elif info[0] == "接收指令":
        instructions = info[1]
        file = open('./instructions.txt', 'a+')
        file.writelines(instructions + "\n")
        file.close()

    sock.close()
    print("连接已经断开")
s.close()
