# -*- coding: utf-8 -*-
# @ModuleName: DAC_1
# @Function: 服务器通信子模块
# @Author: Chen Zhongwei
# @Time: 2021/4/28 10:45
import json
import os
from interface.out_interface import out_interface_impl
from data_communication_analysis.DCA_2 import send_data


# 解析各类资源信息
def analyse_data(ip):
    # 通过外部接口请求资源信息
    json_data = out_interface_impl().OUT_SS_SRMMS(ip)
    # 将json数据以字典形式读取出来
    dict_data = json.loads(json_data)
    send_data(ip, dict_data)


# 发送资源调度分配指令
def send_instructions(ip, instructions):
    # 调用外部接口发送调度指令
    out_interface_impl().OUT_SRMMS_SS(ip, instructions)


# name_emb = {'a': '1111', 'b': '2222', 'c': '3333', 'd': '4444'}
# filename = 'file.txt'
# json_data = json.load(open(filename, 'r', encoding="utf-8"))
# if 'e' not in json_data:
#     print(True)





