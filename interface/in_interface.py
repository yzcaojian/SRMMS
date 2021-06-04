# -*- coding: utf-8 -*-
# @ModuleName: in_interface
# @Function: out_interface
# @Author: Chen Zhongwei
# @Time: 2021/4/25 16:55

from resource_status_display.log_exception_with_suggestions import Warning, warning_list
from resource_status_display.servers_and_disks_info import TwoDiskInfo, DiskInfo, LogicVolumeInfo, ServerInfo
import time
import numpy as np


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
    RAID_io_info_dict = {}  # RAID架构下实时IO负载信息
    RAID_io_info_dict_past = {}  # RAID架构下历史IO负载信息
    two_disk_info_dict = {}  # 两类硬盘总体信息
    two_disk_io_dict = {}  # 两类硬盘实时I/O负载信息
    two_disk_io_dict_past = {}  # 两类硬盘历史I/O负载信息
    # 存放详细信息 供资源状态显示模块使用
    detailed_info_dict = {}
    # 存放详细信息 供资源调度分配模块使用
    detailed_info_list_RSA = []
    # # 存放来自资源调度分配模块的指令
    # instructions_list = []
    # 存放smart数据
    smart_data_dict = {}
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
        from data_communication_analysis.DAC_1 import send_instructions
        # 调用数据通信解析模块的函数发送指令
        send_instructions(ip, instructions)

    # def getData_instructions(self):
    #     list1 = in_interface_impl.instructions_list
    #     in_interface_impl.instructions_list = []
    #     return list1

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

        now_time = time.strftime("%H:%M:%S", time.localtime(time.time()))
        if len(server_info) == 4:  # RAID架构下的数据
            if ip not in in_interface_impl.RAID_io_info_dict:
                in_interface_impl.RAID_io_info_dict[ip] = []
            RAID_io = server_info[-1]
            in_interface_impl.RAID_io_info_dict[ip].append([RAID_io, now_time])
        elif two_disk_info is not None:
            in_interface_impl.two_disk_info_dict[ip] = two_disk_info

            two_disk_io = two_disk_info[10:]  # two_disk_io =  [hddIOPS, ssdIOPS]

            if ip not in in_interface_impl.two_disk_io_dict:
                in_interface_impl.two_disk_io_dict[ip] = {"hdd": [], "ssd": []}
            in_interface_impl.two_disk_io_dict[ip]["hdd"].append([two_disk_io[0], now_time])
            in_interface_impl.two_disk_io_dict[ip]["ssd"].append([two_disk_io[1], now_time])

    def get_RAID_overall_io_info(self, ip):
        # 最多保存600个数据
        if len(in_interface_impl.RAID_io_info_dict[ip]) >= 600:
            if ip not in in_interface_impl.RAID_io_info_dict_past:
                in_interface_impl.RAID_io_info_dict_past[ip] = []
            # 将多的数据添加到历史数据中
            in_interface_impl.RAID_io_info_dict_past[ip].append(in_interface_impl.RAID_io_info_dict[ip][0])
            # 删除第一个数据
            in_interface_impl.RAID_io_info_dict[ip] = in_interface_impl.RAID_io_info_dict[ip][1:]
            # 历史数据最多保存3小时
            if len(in_interface_impl.RAID_io_info_dict_past[ip]) >= 3 * 60 * 60:
                in_interface_impl.RAID_io_info_dict_past[ip] = in_interface_impl.RAID_io_info_dict_past[ip][1:]

        RAID_io_info_list = in_interface_impl.RAID_io_info_dict[ip]
        arr = np.array(RAID_io_info_list)
        RAID_io_list = arr[:, 0].tolist()
        time_list = arr[:, 1].tolist()

        return RAID_io_list, time_list

    def get_RAID_overall_io_info_past(self, ip, time_begin, time_end):
        # 将时间字符串转化为时间元组
        begin = time.strptime(time_begin, "%H:%M")
        end = time.strptime(time_end, "%H:%M")
        base = in_interface_impl.RAID_io_info_dict_past[ip][0][1]  # 第一个数据的时间
        base = time.strptime(base, "%H:%M:%S")
        # 时间元组初始化为2000年1月1日
        begin_tuple = (2000, 1, 1) + begin[3:]
        end_tuple = (2000, 1, 1) + end[3:]
        base_tuple = (2000, 1, 1) + base[3:]
        # 将时间元组转化为浮点数
        begin_time = time.mktime(begin_tuple)
        end_time = time.mktime(end_tuple)
        base = time.mktime(base_tuple)

        start = int(begin_time - base) if (begin_time - base) > 0 else 0
        end = int(end_time - base)
        # 截取从start到end的数据
        RAID_io_past = in_interface_impl.RAID_io_info_dict_past[ip][start:end+1]
        arr = np.array(RAID_io_past)
        RAID_io_past_list = arr[:, 0].tolist()
        time_list = arr[:, 1].tolist()

        return RAID_io_past_list, time_list

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
                if len(in_interface_impl.server_info_dict[ip]) == 4:
                    server_info.append(ServerInfo(ip, in_interface_impl.server_info_dict[ip][0],
                                                  in_interface_impl.server_info_dict[ip][1],
                                                  in_interface_impl.server_info_dict[ip][2]))

        return server_info

    def get_two_disk_info(self, ip):
        two_disk_info = in_interface_impl.two_disk_info_dict[ip]

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

        return in_interface_impl.two_disk_io_dict[ip]["hdd"], in_interface_impl.two_disk_io_dict[ip]["ssd"]

    def get_hdd_disk_io_info(self, ip):
        hdd_disk_list, _ = self.get_two_disk_io_info(ip)
        arr = np.array(hdd_disk_list)
        hdd_io_list = arr[:, 0].tolist()
        time_list = arr[:, 1].tolist()
        return hdd_io_list, time_list

    def get_hdd_disk_io_info_past(self, ip, time_begin, time_end):
        # 将时间字符串转化为时间元组
        begin = time.strptime(time_begin, "%H:%M")
        end = time.strptime(time_end, "%H:%M")
        base = in_interface_impl.two_disk_io_dict_past[ip]["hdd"][0][1]  # 第一个数据的时间
        base = time.strptime(base, "%H:%M:%S")
        # 时间元组初始化为2000年1月1日
        begin_tuple = (2000, 1, 1) + begin[3:]
        end_tuple = (2000, 1, 1) + end[3:]
        base_tuple = (2000, 1, 1) + base[3:]
        # 将时间元组转化为浮点数
        begin_time = time.mktime(begin_tuple)
        end_time = time.mktime(end_tuple)
        base = time.mktime(base_tuple)

        start = int(begin_time - base) if (begin_time - base) > 0 else 0
        end = int(end_time - base)
        # 截取从start到end的数据
        hdd_io_past = in_interface_impl.two_disk_io_dict_past[ip]["hdd"][start:end + 1]
        arr = np.array(hdd_io_past)
        hdd_io_list = arr[:, 0].tolist()
        time_list = arr[:, 1].tolist()

        return hdd_io_list, time_list

    def get_ssd_disk_io_info(self, ip):
        _, ssd_disk_list = self.get_two_disk_io_info(ip)
        arr = np.array(ssd_disk_list)
        ssd_io_list = arr[:, 0].tolist()
        time_list = arr[:, 1].tolist()
        return ssd_io_list, time_list

    def get_ssd_disk_io_info_past(self, ip, time_begin, time_end):
        # 将时间字符串转化为时间元组
        begin = time.strptime(time_begin, "%H:%M")
        end = time.strptime(time_end, "%H:%M")
        base = in_interface_impl.two_disk_io_dict_past[ip]["ssd"][0][1]  # 第一个数据的时间
        base = time.strptime(base, "%H:%M:%S")
        # 时间元组初始化为2000年1月1日
        begin_tuple = (2000, 1, 1) + begin[3:]
        end_tuple = (2000, 1, 1) + end[3:]
        base_tuple = (2000, 1, 1) + base[3:]
        # 将时间元组转化为浮点数
        begin_time = time.mktime(begin_tuple)
        end_time = time.mktime(end_tuple)
        base = time.mktime(base_tuple)

        start = int(begin_time - base) if (begin_time - base) > 0 else 0
        end = int(end_time - base)
        # 截取从start到end的数据
        ssd_io_past = in_interface_impl.two_disk_io_dict_past[ip]["ssd"][start:end + 1]
        arr = np.array(ssd_io_past)
        ssd_io_list = arr[:, 0].tolist()
        time_list = arr[:, 1].tolist()

        return ssd_io_list, time_list

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
        # 优化，判断型号，如果不在可以预测的型号范围内，不接收数据
        if ip not in in_interface_impl.smart_data_dict:
            in_interface_impl.smart_data_dict[ip] = smart_data
        # 将新的smart数据添加到字典中，至少保证采集20天的历史数据才能预测
        else:
            # 只需要保留20天的历史smart数据即可，多余进行删除
            if len(in_interface_impl.smart_data_dict[ip][0][2]) >= 20:
                for old in in_interface_impl.smart_data_dict[ip]:
                    old[2] = old[2][1:]
            # 这里需要保证硬盘按照disk_id排列顺序一致
            for (old, new) in (in_interface_impl.smart_data_dict[ip], smart_data):
                old[2].append(new[2])

    def get_smart_info(self, ip, disk_id):  # 获取smart信息
        for disk in in_interface_impl.smart_data_dict[ip]:
            # disk格式为[[diskID, model, smartID, smartData],[...]...]
            if disk_id == disk[0] and len(disk[2] > 19):
                return disk[2]
        return []

    def IN_HDFP_RSD(self, ip, disk_id, health_degree):
        # 将健康度信息添加到列表中
        in_interface_impl.health_degree_list.append([ip, disk_id, health_degree])

    def get_health_degree(self):  # 获取健康度信息
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


# if __name__ == "__main__":
#     begin = time.strptime("20:10", "%H:%M")
#     begin = (2000, 1) + begin[2:]
#     begin = time.mktime(begin)
#     # end = time.mktime(time.strptime("20:20", "%H:%M"))
#     print(begin)
