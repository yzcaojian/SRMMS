# -*- coding: utf-8 -*-
# @ModuleName: DAC_1
# @Function: 服务器通信子模块
# @Author: Chen Zhongwei
# @Time: 2021/4/28 10:45
import json
import socket
from interface.out_interface import out_interface_impl
from data_communication_analysis.DCA_2 import send_data, send_data_RSD


def check_ip(ip):
    # 通过外部接口请求资源信息
    try:
        client = socket.socket()
        client.connect((ip, 12345))
        client.send(bytes("请求数据2", encoding="utf-8"))
        data = client.recv(10240).decode()
        client.close()
    # 服务器失联 捕获异常
    except TimeoutError:
        print("连接超时，IP地址不存在")
        return 1
    except ConnectionRefusedError:
        print("拒绝连接，目标服务器未开启代理程序")
        return 2
    except Exception as e:
        print("其它异常类型:" + str(e))
        return 3
    # 连接正常
    else:
        return 4


# 解析各类资源信息
def analyse_data(ip, lock):
    if not ip:
        return
    # 通过外部接口请求资源信息
    try:
        json_data = out_interface_impl.OUT_SS_SRMMS(ip)
    # 服务器失联 捕获异常
    except TimeoutError:
        print("连接超时，IP地址不存在")
        return
    except ConnectionRefusedError:
        print("拒绝连接，目标服务器未开启代理程序")
        return
    except Exception as e:
        print("其它异常类型:" + str(e))
        return
    else:
        # 获得资源锁
        lock.lock()
        # 将json数据以字典形式读取出来
        dict_data = json.loads(json_data)

        overall_info = dict_data["overall_info"]
        detailed_info = dict_data["detailed_info"]
        if len(overall_info) > 5:  # 多硬盘架构
            # totalCapacity, occupiedCapacity, occupiedRate, hddCounts, sddCounts, hddTotalCapacity, ssdTotalCapacity, \
            # hddOccupiedCapacity, ssdOccupiedCapacity, hddOccupiedRate, sddOccupiedRate, hddErrorRate, ssdErrorRate, \
            # hddIOPS, ssdIOPS = overall_info
            # server_info = [totalCapacity, occupiedCapacity, occupiedRate]
            # two_disk_info = [hddCounts, sddCounts, hddTotalCapacity, ssdTotalCapacity, hddOccupiedCapacity,
            #                  ssdOccupiedCapacity, hddOccupiedRate, sddOccupiedRate, hddErrorRate, ssdErrorRate, hddIOPS, ssdIOPS]

            send_data(ip, dict_data)

            server_info = overall_info[0:3]
            two_disk_info = overall_info[3:]

            send_data_RSD(ip, server_info, detailed_info, two_disk_info)
        else:  # RAID架构
            # totalCapacity, occupiedCapacity, occupiedRate, totalIOPS = overall_info
            # server_info = [totalCapacity, occupiedCapacity, occupiedRate, totalIOPS]

            server_info = overall_info

            send_data_RSD(ip, server_info, detailed_info)
        # 释放资源锁
        lock.unlock()


# 发送资源调度分配指令
def send_instructions(ip, instructions):
    # 调用外部接口发送调度指令
    try:
        out_interface_impl.OUT_SRMMS_SS(ip, instructions)
        # 服务器失联 捕获异常
    except TimeoutError:
        print("连接超时，IP地址不存在")
        return
    except ConnectionRefusedError:
        print("拒绝连接，目标服务器未开启代理程序")
        return
    except Exception as e:
        print("其它异常类型:" + str(e))
        return
    else:
        print("成功向服务器" + ip + "发送调度指令")

# name_emb = {'a': '1111', 'b': '2222', 'c': '3333', 'd': '4444'}
# filename = 'file.txt'
# json_data = json.load(open(filename, 'r', encoding="utf-8"))
# if 'e' not in json_data:
#     print(True)
