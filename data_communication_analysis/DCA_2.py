# -*- coding: utf-8 -*-
# @ModuleName: DCA_2
# @Function: 内部数据发送子模块
# @Author: Chen Zhongwei
# @Time: 2021/4/28 10:45
from interface.in_interface import in_interface_impl


def send_data(ip, json_data):
    # 通过内部接口将资源信息发送给其它模块
    overall_info = json_data["overall_info"]
    detailed_info = json_data["detailed_info"]
    in_interface_impl().IN_DCA_RSD(ip, overall_info, detailed_info)
    in_interface_impl().IN_DCA_RSA(ip, detailed_info)
    if "smart_data" in json_data:
        smart_data = json_data["smart_data"]
        in_interface_impl().IN_DCA_HDFP(ip, smart_data)
