# -*- coding: utf-8 -*-
# @ModuleName: DAC_1
# @Function: 服务器通信子模块
# @Author: Chen Zhongwei
# @Time: 2021/4/28 10:45
import json
from interface.out_interface import out_interface_impl
from data_communication_analysis.DCA_2 import send_data, send_data_RSD


# 解析各类资源信息
def analyse_data(ip):
    # 通过外部接口请求资源信息
    json_data = out_interface_impl.OUT_SS_SRMMS(ip)
    # 将json数据以字典形式读取出来
    dict_data = json.loads(json_data)

    send_data(ip, dict_data)

    overall_info = dict_data["overall_info"]
    detailed_info = dict_data["detailed_info"]
    if len(overall_info) > 5:  # 多硬盘架构
        # totalCapacity, occupiedCapacity, occupiedRate, hddCounts, sddCounts, hddTotalCapacity, ssdTotalCapacity, \
        # hddOccupiedCapacity, ssdOccupiedCapacity, hddOccupiedRate, sddOccupiedRate, hddErrorRate, ssdErrorRate, \
        # hddIOPS, ssdIOPS = overall_info
        # server_info = [totalCapacity, occupiedCapacity, occupiedRate]
        # two_disk_info = [hddCounts, sddCounts, hddTotalCapacity, ssdTotalCapacity, hddOccupiedCapacity,
        #                  ssdOccupiedCapacity, hddOccupiedRate, sddOccupiedRate, hddErrorRate, ssdErrorRate, hddIOPS, ssdIOPS]

        server_info = overall_info[0:3]
        two_disk_info = overall_info[3:]

        send_data_RSD(ip, server_info, detailed_info, two_disk_info)
    else:  # RAID架构
        # totalCapacity, occupiedCapacity, occupiedRate, totalIOPS = overall_info
        # server_info = [totalCapacity, occupiedCapacity, occupiedRate, totalIOPS]

        server_info = overall_info

        send_data_RSD(ip, server_info, detailed_info)


# 发送资源调度分配指令
def send_instructions(ip, instructions):
    # 调用外部接口发送调度指令
    out_interface_impl.OUT_SRMMS_SS(ip, instructions)

# name_emb = {'a': '1111', 'b': '2222', 'c': '3333', 'd': '4444'}
# filename = 'file.txt'
# json_data = json.load(open(filename, 'r', encoding="utf-8"))
# if 'e' not in json_data:
#     print(True)
