# -*- coding: utf-8 -*-
# @ModuleName: in_interface
# @Function: out_interface
# @Author: Chen Zhongwei
# @Time: 2021/4/25 16:55

from data_communication_analysis.DAC_1 import DAC_1

class in_interface:
    # 服务器硬盘和I/O负载信息接口  数据通信解析模块->资源调度分配模块
    def IN_DCA_RSA(self, ip, detailed_info):
        pass

    # 调度分配指令接口  资源调度分配模块->数据通信解析模块
    def IN_RSA_DCA(self, ip, instructions):
        pass

    # 资源信息接口  数据通信解析模块->资源状态显示模块
    def IN_DCA_RSD(self, ip, overall_info, detailed_info):
        pass

    # SMART信息接口  数据通信解析模块->硬盘故障预测模块
    def IN_DCA_HDFP(self, ip, smart_data):
        pass

    # 硬盘健康度预测接口  硬盘故障预测模块->资源状态显示模块
    def IN_HDFP_RSD(self):
        pass

    # 硬盘故障预测处理接口  硬盘故障预测模块->资源调度分配模块
    def IN_HDFP_RSA(self):
        pass

    # I/O负载预测接口  资源调度分配模块->资源状态显示模块
    def IN_LP_RSD(self):
        pass

    # 分配指令日志信息接口  资源调度分配模块->资源状态显示模块
    def IN_RSA_RSD(self):
        pass

    # 硬盘故障预警接口  硬盘故障预测模块->资源状态显示模块
    def IN_HDW(self):
        pass

    # I/O高负载预警接口  资源调度分配模块->资源状态显示模块
    def IN_IOW(self):
        pass


class in_interface_impl(in_interface):
    # 存放总体信息 供资源状态显示模块使用
    overall_info_list = []
    # 存放详细信息 供资源状态显示模块使用
    detailed_info_list = []
    # 存放详细信息 供资源调度分配模块使用
    detailed_info_list_RSA = []
    # 存放smart数据
    smart_data_list = []

    def IN_DCA_RSA(self, ip, detailed_info):
        # 将详细信息添加到列表中
        in_interface_impl.detailed_info_list_RSA.append([ip, detailed_info])

    def getData_RSA(self):
        list = in_interface_impl.detailed_info_list_RSA
        in_interface_impl.detailed_info_list_RSA = []
        return list

    def IN_RSA_DCA(self, ip, instructions):
        # 调用数据通信解析模块模块函数
        DAC_1().send_instructions(ip, instructions)

    def IN_DCA_RSD(self, ip, overall_info, detailed_info):
        # 将总体信息和详细信息添加到列表中
        in_interface_impl.overall_info_list.append([ip, overall_info])
        in_interface_impl.detailed_info_list.append([ip, detailed_info])

    def getData_RSD(self):
        list1 = in_interface_impl.overall_info_list
        in_interface_impl.overall_info_list = []
        list2 = in_interface_impl.detailed_info_list
        in_interface_impl.detailed_info_list = []
        return list1, list2

    def IN_DCA_HDFP(self, ip, smart_data):
        # 将smart数据添加到列表中
        in_interface_impl.smart_data_list.append([ip, smart_data])

    def getData_HDFP(self):
        list = in_interface_impl.smart_data_list
        in_interface_impl.smart_data_list = []
        return list

    def IN_HDFP_RSD(self):
        pass

    def IN_HDFP_RSA(self):
        pass

    def IN_LP_RSD(self):
        pass

    def IN_RSA_RSD(self):
        pass

    def IN_HDW(self):
        pass

    def IN_IOW(self):
        pass


