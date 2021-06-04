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
    io_load_input_queue = {}  # 输入队列 单位为秒
    io_load_input_queue_display = {}  # 前端绘图用
    io_load_input_queue_display_past = {}  # 前端绘图用  历史信息
    io_load_input_queue_predict = {}  # 预测用 单位为分钟
    io_load_input_queue_train = {}  # 训练用 单位为分钟
    io_load_output_queue = {}  # I/O负载输出队列
    io_load_output_queue_past = {}  # I/O负载输出队列  历史信息
    high_io_load_queue = {}  # 高负载队列
    average_io_load = {}  # 记录平均I/O负载  average_io_load[ip][diskID]:[count, averageIO]
    mean_and_std = []  # 存放IO的平均值和标准差
    disk_detailed_info = {}  # disk_detailed_info为字典  格式为{IP:{diskID:[type, state, totalCapacity, occupiedCapacity, occupiedRate}}
    warning_message_queue = []  # 异常消息列表  [异常ID, 事件发生事件, 服务器IP, 硬盘标识,...]

    # 存放smart数据
    smart_data_list = []
    # 存放健康度信息
    health_degree_list = []
    # 存放硬盘故障预测处理信息
    hard_disk_failure_prediction_list = []
    # 存放I/O负载预测信息
    io_load_prediction_list = []
    # # 存放分配指令日志信息
    # allocation_instruction_log_list = []
    # # 存放硬盘故障预警信息
    # hard_disk_failure_warning_list = []
    # # 存放I/O高负载预警信息
    # io_load_warning_list = []

    def IN_DCA_RSA(self, ip, detailed_info):
        from resource_scheduling_allocation.RSA_1 import io_second_to_io_minute
        from resource_scheduling_allocation.RSA_3 import filtering_io_data

        # detailed_info = [disk_id, type, state, total_capacity, occupied_capacity, occupied_rate, disk_io]
        disk_id, disk_io = detailed_info[0], detailed_info[-1]
        # 将信息添加到详细信息字典中
        if ip not in in_interface_impl.disk_detailed_info:
            in_interface_impl.disk_detailed_info[ip] = {}
        # [type, state, total_capacity, occupied_capacity, occupied_rate]
        in_interface_impl.disk_detailed_info[ip][disk_id] = detailed_info[1:6]

        now_time = time.time()
        # I/O负载进入输入队列之前先检测是否高负载
        filtering_io_data(ip, [disk_id, disk_io, now_time], in_interface_impl.average_io_load, in_interface_impl.high_io_load_queue)
        # 将I/O负载信息添加到输入队列中
        if ip not in in_interface_impl.io_load_input_queue:
            in_interface_impl.io_load_input_queue[ip] = {}
        if disk_id not in in_interface_impl.io_load_input_queue[ip]:
            in_interface_impl.io_load_input_queue[ip][disk_id] = []
        in_interface_impl.io_load_input_queue[ip][disk_id].append([disk_io, now_time])

        # 将以秒为单位的I/O负载数据转化为以分钟为单位的I/O数据
        io_second_to_io_minute(in_interface_impl.io_load_input_queue, in_interface_impl.io_load_input_queue_display)
        io_second_to_io_minute(in_interface_impl.io_load_input_queue, in_interface_impl.io_load_input_queue_predict)
        io_second_to_io_minute(in_interface_impl.io_load_input_queue, in_interface_impl.io_load_input_queue_train)

        for ip in in_interface_impl.io_load_input_queue:
            for disk_id in in_interface_impl.io_load_input_queue[ip]:
                if len(in_interface_impl.io_load_input_queue[ip][disk_id]) < 60:
                    continue
                else:
                    # 将前面60个数据删除
                    in_interface_impl.io_load_input_queue[ip][disk_id] = in_interface_impl.io_load_input_queue[ip][disk_id][60:]

    def get_io_load_input_queue_display(self, ip, id):
        for server_ip in in_interface_impl.io_load_input_queue_display:
            for disk_id in in_interface_impl.io_load_input_queue_display[server_ip]:
                # 只保存3小时内的数据
                length = len(in_interface_impl.io_load_input_queue_display[server_ip][disk_id])
                if length > 3 * 60:
                    if server_ip not in in_interface_impl.io_load_input_queue_display_past:
                        in_interface_impl.io_load_input_queue_display_past[server_ip] = {}
                        if disk_id not in in_interface_impl.io_load_input_queue_display_past[server_ip]:
                            in_interface_impl.io_load_input_queue_display_past[server_ip][disk_id] = []
                        # 将多的数据添加到历史数据中
                        for i in range(length - 3 * 60):
                            in_interface_impl.io_load_input_queue_display_past[server_ip][disk_id].append(in_interface_impl.io_load_input_queue_display[server_ip][disk_id][i])
                        # 删除前面的数据
                        in_interface_impl.io_load_input_queue_display[server_ip][disk_id] = in_interface_impl.io_load_input_queue_display[server_ip][disk_id][length - 3 * 60:]
                        # 历史数据最多保存24小时
                        _length = len(in_interface_impl.io_load_input_queue_display_past[server_ip][disk_id])
                        if _length > 24 * 60:
                            in_interface_impl.io_load_input_queue_display_past[server_ip][disk_id] = in_interface_impl.io_load_input_queue_display_past[server_ip][disk_id][_length - 24 * 60:]

        io_load = in_interface_impl.io_load_input_queue_display[ip][id]
        arr = np.array(io_load)
        io_load_list = arr[:, 0].tolist()
        time_list = arr[:, 1].tolist()
        # 转化为时间字符串
        for i in range(len(time_list)):
           time_list[i] = time.strftime("%H:%M", time.localtime(time_list[i]))

        return io_load_list, time_list

    def get_io_load_input_queue_display_past(self, ip, disk_id, time_begin, time_end):
        # 将时间字符串转化为时间元组
        begin = time.strptime(time_begin, "%H:%M")
        end = time.strptime(time_end, "%H:%M")
        base = in_interface_impl.io_load_input_queue_display_past[ip][disk_id][0][1]  # 第一个数据的时间  浮点型

        # 时间元组初始化为2000年1月1日
        begin_tuple = (2000, 1, 1) + begin[3:]
        end_tuple = (2000, 1, 1) + end[3:]

        # 将时间元组转化为浮点数
        begin_time = time.mktime(begin_tuple)
        end_time = time.mktime(end_tuple)

        start = int((begin_time - base) // 60 + 1) if (begin_time - base) > 0 else 0
        end = int((end_time - base) // 60 + 1)
        # 截取从start到end的数据
        io_load_past = in_interface_impl.io_load_input_queue_display_past[ip][disk_id][start:end + 1]
        arr = np.array(io_load_past)
        io_load_past_list = arr[:, 0].tolist()
        time_list = arr[:, 1].tolist()
        # 转化为时间字符串
        for i in range(len(time_list)):
            time_list[i] = time.strftime("%H:%M", time.localtime(time_list[i]))

        return io_load_past_list, time_list

    def get_io_load_output_queue_display(self, ip, id):
        for server_ip in in_interface_impl.io_load_output_queue:
            for disk_id in in_interface_impl.io_load_output_queue[server_ip]:
                # 只保存3小时内的数据
                length = len(in_interface_impl.io_load_output_queue[server_ip][disk_id])
                if length > 3 * 60:
                    if server_ip not in in_interface_impl.io_load_output_queue_past:
                        in_interface_impl.io_load_output_queue_past[server_ip] = {}
                        if disk_id not in in_interface_impl.io_load_output_queue_past[server_ip]:
                            in_interface_impl.io_load_output_queue_past[server_ip][disk_id] = []
                        # 将多的数据添加到历史数据中
                        for i in range(length - 3 * 60):
                            in_interface_impl.io_load_output_queue_past[server_ip][disk_id].append(in_interface_impl.io_load_output_queue[server_ip][disk_id][i])
                        # 删除前面的数据
                        in_interface_impl.io_load_output_queue[server_ip][disk_id] = in_interface_impl.io_load_output_queue[server_ip][disk_id][length - 3 * 60:]
                        # 历史数据最多保存24小时
                        _length = len(in_interface_impl.io_load_output_queue_past[server_ip][disk_id])
                        if _length > 24 * 60:
                            in_interface_impl.io_load_output_queue_past[server_ip][disk_id] = in_interface_impl.io_load_output_queue_past[server_ip][disk_id][_length - 24 * 60:]

        # 输出队列里的时间数据为 %H:%M 的字符串格式
        io_load = in_interface_impl.io_load_output_queue_past[ip][id]
        arr = np.array(io_load)
        io_load_list = arr[:, 0].tolist()
        time_list = arr[:, 1].tolist()

        return io_load_list, time_list

    def get_io_load_output_queue_display_past(self, ip, disk_id, time_begin, time_end):
        # 将时间字符串转化为时间元组
        begin = time.strptime(time_begin, "%H:%M")
        end = time.strptime(time_end, "%H:%M")
        base = in_interface_impl.io_load_output_queue_past[ip][disk_id][0][1]  # 第一个数据的时间
        base = time.strptime(base, "%H:%M")

        # 时间元组初始化为2000年1月1日
        begin_tuple = (2000, 1, 1) + begin[3:]
        end_tuple = (2000, 1, 1) + end[3:]
        base_tuple = (2000, 1, 1) + base[3:]

        # 将时间元组转化为浮点数
        begin_time = time.mktime(begin_tuple)
        end_time = time.mktime(end_tuple)
        base = time.mktime(base_tuple)

        start = int((begin_time - base) // 60) if (begin_time - base) > 0 else 0
        end = int((end_time - base) // 60)
        # 截取从start到end的数据 输出队列里的时间数据为 %H:%M 的字符串格式
        io_load_past = in_interface_impl.io_load_output_queue_past[ip][disk_id][start:end + 1]
        arr = np.array(io_load_past)
        io_load_past_list = arr[:, 0].tolist()
        time_list = arr[:, 1].tolist()

        return io_load_past_list, time_list

    @classmethod
    def get_io_load_input_queue_predict(cls):
        return in_interface_impl.io_load_input_queue_predict

    @classmethod
    def get_io_load_input_queue_train(cls):
        return in_interface_impl.io_load_input_queue_train

    @classmethod
    def get_io_load_output_queue(cls):
        return in_interface_impl.io_load_output_queue

    @classmethod
    def get_high_io_load_queue(cls):
        return in_interface_impl.high_io_load_queue

    @classmethod
    def get_average_io_load(cls):
        return in_interface_impl.average_io_load

    @classmethod
    def get_mean_and_std(cls):
        return in_interface_impl.mean_and_std

    @classmethod
    def get_disk_detailed_info(cls):
        return in_interface_impl.disk_detailed_info

    @classmethod
    def get_warning_message_queue(cls):
        return in_interface_impl.warning_message_queue

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
        for sever_ip in in_interface_impl.RAID_io_info_dict:
            # 最多保存600个数据
            length = len(in_interface_impl.RAID_io_info_dict[sever_ip])
            if length > 600:
                if sever_ip not in in_interface_impl.RAID_io_info_dict_past:
                    in_interface_impl.RAID_io_info_dict_past[sever_ip] = []
                # 将多的数据添加到历史数据中
                for i in range(length - 600):
                    in_interface_impl.RAID_io_info_dict_past[sever_ip].append(in_interface_impl.RAID_io_info_dict[sever_ip][i])
                # 删除前面的数据
                in_interface_impl.RAID_io_info_dict[sever_ip] = in_interface_impl.RAID_io_info_dict[sever_ip][length - 600:]
                # 历史数据最多保存3小时
                _length = len(in_interface_impl.RAID_io_info_dict_past[sever_ip])
                if _length > 3 * 60 * 60:
                    in_interface_impl.RAID_io_info_dict_past[sever_ip] = in_interface_impl.RAID_io_info_dict_past[sever_ip][_length - 3 * 60 * 60:]

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
        for server_ip in in_interface_impl.two_disk_io_dict:
            # 最多保存600个数据
            length = len(in_interface_impl.two_disk_io_dict[server_ip]["hdd"])
            if length > 600:
                if server_ip not in in_interface_impl.two_disk_io_dict_past:
                    in_interface_impl.two_disk_io_dict_past[server_ip] = {"hdd": [], "ssd": []}
                # 将多的数据添加到历史数据中
                for i in range(length - 600):
                    in_interface_impl.two_disk_io_dict_past[server_ip]["hdd"].append(in_interface_impl.two_disk_io_dict[server_ip]["hdd"][i])
                    in_interface_impl.two_disk_io_dict_past[server_ip]["ssd"].append(in_interface_impl.two_disk_io_dict[server_ip]["ssd"][i])
                # 删除前面的数据
                in_interface_impl.two_disk_io_dict[server_ip]["hdd"] = in_interface_impl.two_disk_io_dict[server_ip]["hdd"][length - 600:]
                in_interface_impl.two_disk_io_dict[server_ip]["ssd"] = in_interface_impl.two_disk_io_dict[server_ip]["ssd"][length - 600:]
                # 历史数据最多保存3小时
                _length = len(in_interface_impl.two_disk_io_dict_past[server_ip]["hdd"])
                if _length > 3 * 60 * 60:
                    in_interface_impl.two_disk_io_dict_past[server_ip]["hdd"] = in_interface_impl.two_disk_io_dict_past[server_ip]["hdd"][_length - 3 * 60 * 60:]
                    in_interface_impl.two_disk_io_dict_past[server_ip]["ssd"] = in_interface_impl.two_disk_io_dict_past[server_ip]["ssd"][_length - 3 * 60 * 60:]

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

    # def IN_HDW(self, ip, disk_id, disk_warning):
    #     # 将硬盘故障预警信息添加到列表中
    #     in_interface_impl.hard_disk_failure_warning_list.append([ip, disk_id, disk_warning])
    #
    # def getData_hard_disk_failure_warning(self):  # 获取硬盘故障预警信息
    #     list1 = in_interface_impl.hard_disk_failure_warning_list
    #     in_interface_impl.hard_disk_failure_warning_list = []
    #     return list1
    #
    # def IN_IOW(self, ip, disk_id, io_warning):
    #     # 将I/O高负载预警信息添加到列表中
    #     in_interface_impl.io_load_warning_list.append([ip, disk_id, io_warning])
    #
    # def getData_io_load_warning(self):  # 获取I/O高负载预警信息
    #     list1 = in_interface_impl.io_load_warning_list
    #     in_interface_impl.io_load_warning_list = []
    #     return list1


# if __name__ == "__main__":
#     begin = time.strptime("20:10", "%H:%M")
#     begin = (2000, 1) + begin[2:]
#     begin = time.mktime(begin)
#     # end = time.mktime(time.strptime("20:20", "%H:%M"))
#     print(begin)

