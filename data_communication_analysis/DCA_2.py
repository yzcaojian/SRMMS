# -*- coding: utf-8 -*-
# @ModuleName: DCA_2
# @Function: 内部数据发送子模块
# @Author: Chen Zhongwei
# @Time: 2021/4/28 10:45
import time
from interface.in_interface import in_interface_impl


def send_data(ip, dict_data):  # 多硬盘架构
    # 通过内部接口将资源信息发送给其它模块
    overall_info = dict_data["overall_info"]
    detailed_info = dict_data["detailed_info"]

    in_interface_impl.IN_DCA_RSA(ip, detailed_info)

    if "smart_data" in dict_data:
        smart_data = dict_data["smart_data"]
        in_interface_impl.IN_DCA_HDFP(ip, smart_data)
    if "io_load_data" in dict_data:
        io_load_data = dict_data["io_load_data"]
        in_interface_impl.set_io_load_input_queue_train(ip, io_load_data)


def send_data_RSD(ip, server_info, detailed_info, two_disk_info=None):
    # 通过内部接口将资源信息发送给其它模块
    in_interface_impl.server_ip_dict[ip][2] = time.time()
    if two_disk_info is None:
        in_interface_impl.IN_DCA_RSD(ip, server_info, detailed_info)
    else:
        in_interface_impl.IN_DCA_RSD(ip, server_info, detailed_info, two_disk_info)



