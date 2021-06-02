# -*- coding: utf-8 -*-
# @ModuleName: in_interface
# @Function: out_interface
# @Author: Chen Zhongwei
# @Time: 2021/4/25 16:55

from data_communication_analysis.DAC_1 import send_instructions
from resource_status_display.log_exception_with_suggestions import Warning, warning_list
from resource_status_display.servers_and_disks_info import TwoDiskInfo, DiskInfo, LogicVolumeInfo, ServerInfo


class in_interface:
    # 服务器硬盘和I/O负载信息接口  数据通信解析模块->资源调度分配模块
    def IN_DCA_RSA(self, ip, detailed_info):
        pass

    # 调度分配指令接口  资源调度分配模块->数据通信解析模块
    def IN_RSA_DCA(self, ip, instructions):
        pass

    # 资源信息接口  数据通信解析模块->资源状态显示模块
    def IN_DCA_RSD(self, ip, server_info, detailed_info, two_disk_info=None):
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
    def IN_RSA_RSD(self, warning):
        pass

    # 硬盘故障预警接口  硬盘故障预测模块->资源状态显示模块
    def IN_HDW(self, ip, disk_id, disk_warning):
        pass

    # I/O高负载预警接口  资源调度分配模块->资源状态显示模块
    def IN_IOW(self, ip, disk_id, io_warning):
        pass


class in_interface_impl(in_interface):
    # 存放总体信息 供资源状态显示模块使用
    server_info_dict = {}
    two_disk_info_dict = {}
    two_disk_io_dict = {}  # 两类硬盘实时I/O负载信息
    two_disk_io_dict_past = {}  # 两类硬盘历史I/O负载信息
    # 存放详细信息 供资源状态显示模块使用
    detailed_info_dict = {}
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
    # allocation_instruction_log_list = []
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

    # server_info = [totalCapacity, occupiedCapacity, occupiedRate]
    # or server_info = [totalCapacity, occupiedCapacity, occupiedRate, totalIOPS]
    # detailed_info = [[diskID, type, state, totalCapacity, occupiedCapacity, occupiedRate, diskIO], …]
    # or detailed_info = [[logicVolumeID, totalCapacity, occupiedCapacity, occupiedRate], …]
    # two_disk_info = [occupiedRate, hddCounts, sddCounts, hddTotalCapacity, ssdTotalCapacity,
    # hddOccupiedCapacity, ssdOccupiedCapacity, hddOccupiedRate, sddOccupiedRate, hddErrorRate,
    # ssdErrorRate, hddIOPS, ssdIOPS]
    def IN_DCA_RSD(self, ip, server_info, detailed_info, two_disk_info=None):
        # 将总体信息和详细信息添加到列表中
        in_interface_impl.server_info_dict[ip] = server_info

        in_interface_impl.detailed_info_dict[ip] = detailed_info

        if two_disk_info is not None:
            in_interface_impl.two_disk_info_dict[ip] = two_disk_info

    def get_server_overall_info(self, tag):
        server_info = []
        if tag == 0:  # 多硬盘架构
            for ip in in_interface_impl.server_info_dict:
                if len(in_interface_impl.server_info_dict[ip]) == 3:
                    server_info.append(ServerInfo(ip, in_interface_impl.server_info_dict[ip][0],
                                                  in_interface_impl.server_info_dict[ip][1],
                                                  in_interface_impl.server_info_dict[ip][2]))
        else:  # RAID架构
            for ip in in_interface_impl.server_info_dict:
                if len(in_interface_impl.server_info_dict[ip]) == 3:
                    server_info.append(ServerInfo(ip, in_interface_impl.server_info_dict[ip][0],
                                                  in_interface_impl.server_info_dict[ip][1],
                                                  in_interface_impl.server_info_dict[ip][2]))
        return server_info

    def get_two_disk_info(self, ip):
        two_disk_info = in_interface_impl.two_disk_info_dict[ip]
        two_disk_io = two_disk_info[10:]  # two_disk_io =  [hddIOPS, ssdIOPS]

        if ip not in in_interface_impl.two_disk_io_dict:
            in_interface_impl.two_disk_io_dict[ip] = {"hdd": [], "ssd": []}
        in_interface_impl.two_disk_io_dict[ip]["hdd"].append(two_disk_io[0])
        in_interface_impl.two_disk_io_dict[ip]["ssd"].append(two_disk_io[1])

        return TwoDiskInfo(two_disk_info)

    def get_two_disk_io_info(self, ip):
        # 最多保存600个数据
        if len(in_interface_impl.two_disk_io_dict[ip]["hdd"]) >= 600:
            if ip not in in_interface_impl.two_disk_io_dict_past:
                in_interface_impl.two_disk_io_dict_past[ip] = {"hdd": [], "ssd": []}
            # 将多的数据添加到历史数据中
            in_interface_impl.two_disk_io_dict_past[ip]["hdd"].append(in_interface_impl.two_disk_io_dict[ip]["hdd"][0])
            in_interface_impl.two_disk_io_dict_past[ip]["ssd"].append(in_interface_impl.two_disk_io_dict[ip]["ssd"][0])
            # 删除第一个数据
            in_interface_impl.two_disk_io_dict[ip]["hdd"] = in_interface_impl.two_disk_io_dict[ip]["hdd"][1:]
            in_interface_impl.two_disk_io_dict[ip]["ssd"] = in_interface_impl.two_disk_io_dict[ip]["ssd"][1:]
            # 历史数据最多保存3小时
            if len(in_interface_impl.two_disk_io_dict_past[ip]["hdd"]) >= 3 * 60 * 60:
                in_interface_impl.two_disk_io_dict_past[ip]["hdd"] = in_interface_impl.two_disk_io_dict_past[ip]["hdd"][1:]
                in_interface_impl.two_disk_io_dict_past[ip]["ssd"] = in_interface_impl.two_disk_io_dict_past[ip]["ssd"][1:]

    def get_hdd_disk_io_info(self, ip):
        return in_interface_impl.two_disk_io_dict[ip]["hdd"]

    def get_ssd_disk_io_info(self, ip):
        return in_interface_impl.two_disk_io_dict[ip]["ssd"]

    def get_server_detailed_info(self, ip, tag):
        # 获取server_ip对应的服务器详细信息
        detailed_info = in_interface_impl.detailed_info_dict[ip]
        server_detailed_info = []
        if tag == 0:  # 硬盘详细信息
            for disk in detailed_info:
                server_detailed_info.append(DiskInfo(disk))
        else:  # 逻辑卷详细信息
            for volume in detailed_info:
                server_detailed_info.append(LogicVolumeInfo(volume))
        return server_detailed_info

    # def getData_resource_info(self, ip):  # 获取资源信息(总体信息和详细信息)
    #
    #     server_info = in_interface_impl.server_info_dict[ip]
    #     detailed_info = in_interface_impl.detailed_info_dict[ip]
    #     if ip not in in_interface_impl.two_info_dict:
    #         two_disk_info = None
    #     else:
    #         two_disk_info = in_interface_impl.two_info_dict[ip]
    #
    #     return server_info, detailed_info, two_disk_info

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

    def IN_RSA_RSD(self, warning):
        # 将告警信息添加到列表中
        warning_list.add_new_warning(warning)
        # in_interface_impl.allocation_instruction_log_list.append([ip, disk_id, instructions])

    # def getData_allocation_instruction_log(self):  # 获取分配指令日志信息
    #     list1 = in_interface_impl.allocation_instruction_log_list
    #     in_interface_impl.allocation_instruction_log_list = []
    #     return list1

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


