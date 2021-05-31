# -*- coding: utf-8 -*-
# @ModuleName: in_interface
# @Function: out_interface
# @Author: Chen Zhongwei
# @Time: 2021/4/25 16:55

from data_communication_analysis.DAC_1 import send_instructions

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
    def IN_HDFP_RSD(self, ip, disk_id, health_degree):
        pass

    # 硬盘故障预测处理接口  硬盘故障预测模块->资源调度分配模块
    def IN_HDFP_RSA(self, ip, disk_id, failure_info):
        pass

    # I/O负载预测接口  资源调度分配模块->资源状态显示模块
    def IN_LP_RSD(self, ip, disk_id, io_pred):
        pass

    # 分配指令日志信息接口  资源调度分配模块->资源状态显示模块
    def IN_RSA_RSD(self, ip, disk_id, instruction):
        pass

    # 硬盘故障预警接口  硬盘故障预测模块->资源状态显示模块
    def IN_HDW(self, ip, disk_id, disk_warning):
        pass

    # I/O高负载预警接口  资源调度分配模块->资源状态显示模块
    def IN_IOW(self, ip, disk_id, io_warning):
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
    # 存放健康度信息
    health_degree_list = []
    # 存放硬盘故障预测处理信息
    hard_disk_failure_prediction_list = []
    # 存放I/O负载预测信息
    io_load_prediction_list = []
    # 存放分配指令日志信息
    allocation_instruction_log_list = []
    # 存放硬盘故障预警信息
    hard_disk_failure_warning_list = []
    # 存放I/O高负载预警信息
    io_load_warning_list = []

    def IN_DCA_RSA(self, ip, detailed_info):
        # 将详细信息添加到列表中
        in_interface_impl.detailed_info_list_RSA.append([ip, detailed_info])

    def getData_disk_io(self):  # 获取服务器硬盘和I/O负载信息(详细信息)
        list1 = in_interface_impl.detailed_info_list_RSA
        in_interface_impl.detailed_info_list_RSA = []
        return list1

    def IN_RSA_DCA(self, ip, instructions):
        # 调用数据通信解析模块模块函数
        send_instructions(ip, instructions)

    def IN_DCA_RSD(self, ip, overall_info, detailed_info):
        # 将总体信息和详细信息添加到列表中
        in_interface_impl.overall_info_list.append([ip, overall_info])
        in_interface_impl.detailed_info_list.append([ip, detailed_info])

    def getData_resource_info(self):  # 获取资源信息(总体信息和详细信息)
        list1 = in_interface_impl.overall_info_list
        in_interface_impl.overall_info_list = []
        list2 = in_interface_impl.detailed_info_list
        in_interface_impl.detailed_info_list = []
        return list1, list2

    def IN_DCA_HDFP(self, ip, smart_data):
        # 将smart数据添加到列表中
        in_interface_impl.smart_data_list.append([ip, smart_data])

    def getData_smart_info(self):  # 获取smart信息
        list1 = in_interface_impl.smart_data_list
        in_interface_impl.smart_data_list = []
        return list1

    def IN_HDFP_RSD(self, ip, disk_id, health_degree):
        # 将健康度信息添加到列表中
        in_interface_impl.health_degree_list.append([ip, disk_id, health_degree])

    def getData_health_degree(self):  # 获取健康度信息
        list1 = in_interface_impl.health_degree_list
        in_interface_impl.health_degree_list = []
        return list1

    def IN_HDFP_RSA(self, ip, disk_id, failure_info):
        # 将硬盘故障预测处理信息添加到列表中
        in_interface_impl.hard_disk_failure_prediction_list.append([ip, disk_id, failure_info])

    def getData_hard_disk_failure_prediction(self):  # 获取硬盘故障预测处理信息
        list1 = in_interface_impl.hard_disk_failure_prediction_list
        in_interface_impl.hard_disk_failure_prediction_list = []
        return list1

    def IN_LP_RSD(self, ip, disk_id, io_pred):
        # 将I/O负载预测信息添加到列表中
        in_interface_impl.io_load_prediction_list.append([ip, disk_id, io_pred])

    def getData_io_load_prediction(self):  # 获取I/O负载预测信息
        list1 = in_interface_impl.io_load_prediction_list
        in_interface_impl.io_load_prediction_list = []
        return list1

    def IN_RSA_RSD(self, ip, disk_id, instructions):
        # 将分配指令日志信息添加到列表中
        in_interface_impl.allocation_instruction_log_list.append([ip, disk_id, instructions])

    def getData_allocation_instruction_log(self):  # 获取分配指令日志信息
        list1 = in_interface_impl.allocation_instruction_log_list
        in_interface_impl.allocation_instruction_log_list = []
        return list1

    def IN_HDW(self, ip, disk_id, disk_warning):
        # 将硬盘故障预警信息添加到列表中
        in_interface_impl.hard_disk_failure_warning_list.append([ip, disk_id, disk_warning])

    def getData_hard_disk_failure_warning(self):  # 获取硬盘故障预警信息
        list1 = in_interface_impl.hard_disk_failure_warning_list
        in_interface_impl.hard_disk_failure_warning_list = []
        return list1

    def IN_IOW(self, ip, disk_id, io_warning):
        # 将I/O高负载预警信息添加到列表中
        in_interface_impl.io_load_warning_list.append([ip, disk_id, io_warning])

    def getData_io_load_warning(self):  # 获取I/O高负载预警信息
        list1 = in_interface_impl.io_load_warning_list
        in_interface_impl.io_load_warning_list = []
        return list1


