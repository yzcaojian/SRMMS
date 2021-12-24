# -*- coding: utf-8 -*-
# @ModuleName: in_interface
# @Function: out_interface
# @Author: Chen Zhongwei
# @Time: 2021/4/25 16:55

from resource_status_display.log_exception_with_suggestions import Warning, warning_list
from resource_status_display.servers_and_disks_info import TwoDiskInfo, DiskInfo, LogicVolumeInfo, ServerInfo
from hard_disk_failure_prediction.predict import predict_disk_health_state
import time


class in_interface:

    # 服务器硬盘和I/O负载信息接口  数据通信解析模块->资源调度分配模块
    @classmethod
    def IN_DCA_RSA(cls, ip, detailed_info):
        pass

    # 各服务器刷新周期，当前时间 - 数据上次刷新时间
    @classmethod
    def get_update_cycle(cls, ip):
        pass

    # 通过ip、disk_id来显示单个硬盘的实时IO信息
    @classmethod
    def get_io_load_input_queue_display(cls, ip, id):
        pass

    # 通过ip、disk_id以及起止时间来显示硬盘的历史IO信息
    @classmethod
    def get_io_load_input_queue_display_past(cls, ip, disk_id, time_begin, time_end):
        pass

    # 通过ip、disk_id来显示单个硬盘的实时IO预测信息
    @classmethod
    def get_io_load_output_queue_display(cls, ip, id):
        pass

    # 通过ip、disk_id以及起止时间来显示硬盘的历史IO预测信息
    @classmethod
    def get_io_load_output_queue_display_past(cls, ip, disk_id, time_begin, time_end):
        pass

    # 获得I/O负载队列 用于监控失联告警
    @classmethod
    def get_io_load_input_queue(cls):
        pass

    # 获得IO负载输入队列 for predict
    @classmethod
    def get_io_load_input_queue_predict(cls):
        pass

    # 接收服务器处传来的供训练用的I/O负载数据
    @classmethod
    def set_io_load_input_queue_train(cls, ip, io_load_data):
        pass

    # 获得IO负载输入队列 for train
    @classmethod
    def get_io_load_input_queue_train(cls):
        pass

    # 获得IO负载输出队列 给前端显示
    @classmethod
    def get_io_load_output_queue(cls):
        pass

    # 获得IO高负载队列
    @classmethod
    def get_high_io_load_queue(cls):
        pass

    # 获得平均IO负载队列(判断是否高IO负载)
    @classmethod
    def get_average_io_load(cls):
        pass

    # 获得硬盘详细信息字典 格式为{IP:{diskID:[type, state, totalCapacity, occupiedCapacity, occupiedRate}}
    @classmethod
    def get_disk_detailed_info(cls):
        pass

    # 获得告警消息队列
    @classmethod
    def get_warning_message_queue(cls):
        pass

    # 调度分配指令接口  资源调度分配模块->数据通信解析模块
    @classmethod
    def IN_RSA_DCA(cls, ip, instructions):
        pass

    # 资源信息接口  数据通信解析模块->资源状态显示模块
    @classmethod
    def IN_DCA_RSD(cls, ip, server_info, detailed_info, two_disk_info=None):
        pass

    # 获得RAID架构下总体IO信息
    @classmethod
    def get_RAID_overall_io_info(cls, ip):
        pass

    # 获得RAID架构下总体IO信息(历史)
    @classmethod
    def get_RAID_overall_io_info_past(cls, ip, time_begin, time_end):
        pass

    # 获得服务器的总体信息
    @classmethod
    def get_server_overall_info(cls, tag):
        pass

    # 根据ip,获得两类硬盘的总体信息
    @classmethod
    def get_two_disk_info(cls, ip):
        pass

    # 根据ip,获得两类硬盘的IO信息
    @classmethod
    def get_two_disk_io_info(cls, ip):
        pass

    # 根据ip,获得hdd硬盘的IO信息
    @classmethod
    def get_hdd_disk_io_info(cls, ip):
        pass

    # 根据ip以及起止时间,获得hdd硬盘的历史IO信息
    @classmethod
    def get_hdd_disk_io_info_past(cls, ip, time_begin, time_end):
        pass

    # 根据ip,获得ssd硬盘的IO信息
    @classmethod
    def get_ssd_disk_io_info(cls, ip):
        pass

    # 根据ip以及起止时间,获得ssd硬盘的历史IO信息
    @classmethod
    def get_ssd_disk_io_info_past(cls, ip, time_begin, time_end):
        pass

    # 根据ip获得服务器的详细信息
    @classmethod
    def get_server_detailed_info(cls, ip, tag):
        pass

    # SMART信息接口  数据通信解析模块->硬盘故障预测模块
    @classmethod
    def IN_DCA_HDFP(cls, ip, smart_data):
        pass

    # 硬盘健康度预测接口  硬盘故障预测模块->资源状态显示模块
    @classmethod
    def IN_HDFP_RSD(cls, ip, disk):
        pass

    # 根据ip、disk_id来获得该硬盘的健康度信息
    @classmethod
    def get_health_degree(cls, server_ip, disk_id):
        pass

    # 硬盘健康度下降告警信息 to资源状态显示模块
    @classmethod
    def IN_RSA_RSD(cls, warning):
        pass

    # 硬盘故障预测处理接口  硬盘故障预测模块->资源调度分配模块
    @classmethod
    def IN_HDFP_RSA(cls, ip, disk_id, failure_info):
        pass

    # 获得硬盘故障预警信息
    @classmethod
    def get_hard_disk_failure_prediction(cls):
        pass

    # 关于图标闪烁的两种需求下的预警方式
    @classmethod
    def get_exception_dict(cls):
        pass


def list_split(raw_list):
    data_list = []
    time_list = []
    for item in raw_list:
        data_list.append(item[0])
        time_list.append(item[1])
    return data_list, time_list


class in_interface_impl(in_interface):
    # 存放总体信息 供资源状态显示模块使用
    server_info_dict = {}
    RAID_io_info_dict = {}  # RAID架构下实时IO负载信息
    RAID_io_info_dict_past = {}  # RAID架构下历史IO负载信息
    two_disk_info_dict = {}  # 两类硬盘总体信息
    two_disk_io_dict = {}  # 两类硬盘实时I/O负载信息
    two_disk_io_dict_past = {}  # 两类硬盘历史I/O负载信息
    request_time = {}  # 服务器准备请求数据的时间
    update_time = {}  # 服务器请求到数据的时间

    # 存放详细信息 供资源状态显示模块使用
    detailed_info_dict = {}

    # 存放详细信息 供资源调度分配模块使用
    io_load_input_queue = {}  # 输入队列 单位为秒
    io_load_input_queue_display = {}  # 前端绘图用
    io_load_input_queue_display_past = {}  # 前端绘图用  历史信息
    io_load_input_queue_predict = {}  # 预测用 单位为分钟
    io_load_input_queue_train = {}  # 训练用 单位为分钟 直接从服务器处获取
    io_load_output_queue = {}  # I/O负载输出队列
    io_load_output_queue_past = {}  # I/O负载输出队列  历史信息
    high_io_load_queue = {}  # 高负载队列
    average_io_load = {}  # 记录平均I/O负载  average_io_load[ip][diskID]:[count, averageIO]
    disk_detailed_info = {}  # disk_detailed_info为字典  格式为{IP:{diskID:[type, state, totalCapacity, occupiedCapacity, occupiedRate}}
    warning_message_queue = []  # 异常消息列表  [异常ID, 事件发生事件, 服务器IP, 硬盘标识,...]

    two_disk_io_max_amount = 420
    RAID_io_max_amount = 420

    # 存放smart数据
    smart_data_dict = {}
    # 存放健康度信息
    health_degree_dict = {}
    # 存放硬盘故障预测处理信息
    hard_disk_failure_prediction_list = []
    hard_disk_failure_prediction_list_ = []
    # 关于图标闪烁的两种需求下的预警方式
    exception_dict = {}

    @classmethod
    def IN_DCA_RSA(cls, ip, detailed_info_list):
        from resource_scheduling_allocation.RSA_1 import io_second_to_io_minute
        from resource_scheduling_allocation.RSA_3 import filtering_io_data

        # detailed_info = [[disk_id, type, state, total_capacity, occupied_capacity, occupied_rate, disk_io],...]
        for detailed_info in detailed_info_list:
            disk_id, disk_io = detailed_info[0], detailed_info[-1]
            # 将信息添加到详细信息字典中
            if ip not in cls.disk_detailed_info:
                cls.disk_detailed_info[ip] = {}
            # [type, state, total_capacity, occupied_capacity, occupied_rate]
            cls.disk_detailed_info[ip][disk_id] = detailed_info[1:6]

            now_time = time.time()
            # I/O负载进入输入队列之前先检测是否高负载
            filtering_io_data(ip, [disk_id, disk_io, now_time], cls.average_io_load, cls.high_io_load_queue)
            # 将I/O负载信息添加到输入队列中
            if ip not in cls.io_load_input_queue:
                cls.io_load_input_queue[ip] = {}
            if disk_id not in cls.io_load_input_queue[ip]:
                cls.io_load_input_queue[ip][disk_id] = []
            cls.io_load_input_queue[ip][disk_id].append([disk_io, now_time])

        # 将以秒为单位的I/O负载数据转化为以分钟为单位的I/O数据
        io_second_to_io_minute(ip, cls.io_load_input_queue, cls.io_load_input_queue_display)
        io_second_to_io_minute(ip, cls.io_load_input_queue, cls.io_load_input_queue_predict)
        # 检查数据超载
        cls.check_for_data_overload_1(ip)

    @classmethod
    def get_update_cycle(cls, ip):
        if ip in cls.update_time and ip in cls.request_time:
            if cls.update_time[ip] > cls.request_time[ip]:
                return round((time.time() - cls.request_time[ip] - 0.5) + cls.update_time[ip] - cls.request_time[ip], 2)
            else:
                return round(time.time() - cls.update_time[ip], 2)
        else:
            return 0

    @classmethod
    def check_for_data_overload_1(cls, ip):  # 检查输入队列和输出队列数据是否超载
        for disk_id in cls.io_load_input_queue[ip]:
            if len(cls.io_load_input_queue[ip][disk_id]) < 60:
                continue
            else:
                # 将前面60个数据删除
                del cls.io_load_input_queue[ip][disk_id][:60]

        # 检查io_load_input_queue_display里面的数据是否过多
        max_amount = 3 * 60
        if ip in cls.io_load_input_queue_display:
            for disk_id in cls.io_load_input_queue_display[ip]:
                # 只保存3小时内的数据
                length = len(cls.io_load_input_queue_display[ip][disk_id])
                if length > max_amount:
                    if ip not in cls.io_load_input_queue_display_past:
                        cls.io_load_input_queue_display_past[ip] = {}
                    if disk_id not in cls.io_load_input_queue_display_past[ip]:
                        cls.io_load_input_queue_display_past[ip][disk_id] = []
                    # 将多的数据添加到历史数据中
                    for i in range(length - max_amount):
                        cls.io_load_input_queue_display_past[ip][disk_id].append(
                            cls.io_load_input_queue_display[ip][disk_id][i])
                    # 删除前面的数据
                    del cls.io_load_input_queue_display[ip][disk_id][:length - max_amount]  # 3 * 60
                    # 历史数据最多保存24小时
                    _length = len(cls.io_load_input_queue_display_past[ip][disk_id])
                    if _length > 24 * 60:
                        del cls.io_load_input_queue_display_past[ip][disk_id][:_length - 24 * 60]

        # 检查io_load_output_queue里面的数据是否过多
        if ip in cls.io_load_output_queue:
            for disk_id in cls.io_load_output_queue[ip]:
                # 只保存3小时内的数据
                length = len(cls.io_load_output_queue[ip][disk_id])
                if length > (max_amount + 20):
                    if ip not in cls.io_load_output_queue_past:
                        cls.io_load_output_queue_past[ip] = {}
                    if disk_id not in cls.io_load_output_queue_past[ip]:
                        cls.io_load_output_queue_past[ip][disk_id] = []
                    # 将多的数据添加到历史数据中
                    for i in range(length - (max_amount + 20)):
                        cls.io_load_output_queue_past[ip][disk_id].append(cls.io_load_output_queue[ip][disk_id][i])
                    # 删除前面的数据
                    del cls.io_load_output_queue[ip][disk_id][:length - (max_amount + 20)]
                    # 历史数据最多保存24小时
                    _length = len(cls.io_load_output_queue_past[ip][disk_id])
                    if _length > 24 * 60:
                        del cls.io_load_output_queue_past[ip][disk_id][:_length - 24 * 60]

    @classmethod
    def get_io_load_input_queue_display(cls, ip, id):
        if ip not in cls.io_load_input_queue_display or id not in cls.io_load_input_queue_display[ip]:  # 如果为空
            return [], []
        io_load = cls.io_load_input_queue_display[ip][id]
        io_load_list, time_list = list_split(io_load)
        # 转化为时间字符串
        for i in range(len(time_list)):
            time_list[i] = time.strftime("%H:%M", time.localtime(time_list[i]))

        return io_load_list, time_list

    @classmethod
    def get_io_load_input_queue_display_past(cls, ip, disk_id, time_begin, time_end):
        if ip not in cls.io_load_input_queue_display_past or disk_id not in cls.io_load_input_queue_display_past[ip]:  # 如果为空
            return [], []

        # 将时间字符串转化为时间元组
        begin = time.strptime(time_begin, "%H:%M")
        end = time.strptime(time_end, "%H:%M")
        base = time.strftime("%H:%M:%S", time.localtime(cls.io_load_input_queue_display_past[ip][disk_id][0][1]))  # 第一个数据的时间
        base = time.strptime(base, "%H:%M:%S")

        # 时间元组初始化为2000年1月1日
        begin_tuple = (2000, 1, 1) + begin[3:]
        end_tuple = (2000, 1, 1) + end[3:]
        base_tuple = (2000, 1, 1) + base[3:]

        # 将时间元组转化为浮点数
        begin_time = time.mktime(begin_tuple)
        end_time = time.mktime(end_tuple)
        base = time.mktime(base_tuple)

        start = int((begin_time - base) // 60 + 1) if (begin_time - base) > 0 else 0
        end = int((end_time - base) // 60 + 1)
        # 截取从start到end的数据
        io_load_past = cls.io_load_input_queue_display_past[ip][disk_id][start:end + 1]
        if not io_load_past:
            return [], []
        io_load_past_list, time_list = list_split(io_load_past)
        # 转化为时间字符串
        for i in range(len(time_list)):
            time_list[i] = time.strftime("%H:%M", time.localtime(time_list[i]))

        return io_load_past_list, time_list

    @classmethod
    def get_io_load_output_queue_display(cls, ip, id):
        if ip not in cls.io_load_output_queue or id not in cls.io_load_output_queue[ip]:  # 如果为空
            return [], []
        # 输出队列里的时间数据为 %H:%M 的字符串格式
        io_load = cls.io_load_output_queue[ip][id]
        io_load_list, time_list = list_split(io_load)

        return io_load_list, time_list

    @classmethod
    def get_io_load_output_queue_display_past(cls, ip, disk_id, time_begin, time_end):
        if ip not in cls.io_load_output_queue_past or disk_id not in cls.io_load_output_queue_past[ip]:  # 如果为空
            return [], []
        # 将时间字符串转化为时间元组
        begin = time.strptime(time_begin, "%H:%M")
        end = time.strptime(time_end, "%H:%M")
        base = cls.io_load_output_queue_past[ip][disk_id][0][1]  # 第一个数据的时间
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
        io_load_past = cls.io_load_output_queue_past[ip][disk_id][start:end + 1]
        if not io_load_past:
            return [], []
        io_load_past_list, time_list = list_split(io_load_past)

        return io_load_past_list, time_list

    @classmethod
    def get_io_load_input_queue(cls):
        return cls.io_load_input_queue

    @classmethod
    def get_io_load_input_queue_predict(cls):
        return cls.io_load_input_queue_predict

    @classmethod
    def set_io_load_input_queue_train(cls, ip, io_load_data):
        cls.io_load_input_queue_train[ip] = io_load_data

    @classmethod
    def get_io_load_input_queue_train(cls):
        return cls.io_load_input_queue_train

    @classmethod
    def get_io_load_output_queue(cls):
        return cls.io_load_output_queue

    @classmethod
    def get_high_io_load_queue(cls):
        return cls.high_io_load_queue

    @classmethod
    def get_average_io_load(cls):
        return cls.average_io_load

    @classmethod
    def get_disk_detailed_info(cls):
        return cls.disk_detailed_info

    @classmethod
    def get_warning_message_queue(cls):
        return cls.warning_message_queue

    @classmethod
    def get_smart_data_dict(cls):
        return cls.smart_data_dict

    @classmethod
    def get_hard_disk_failure_prediction_list(cls):
        return cls.hard_disk_failure_prediction_list

    @classmethod
    def get_health_degree_dict(cls):
        return cls.health_degree_dict

    @classmethod
    def IN_RSA_DCA(cls, ip, instructions):
        from data_communication_analysis.DAC_1 import send_instructions
        # 调用数据通信解析模块的函数发送指令
        send_instructions(ip, instructions)

    # server_info = [totalCapacity, occupiedCapacity, occupiedRate]
    # or server_info = [totalCapacity, occupiedCapacity, occupiedRate, totalIOPS]
    # detailed_info = [[diskID, type, state, totalCapacity, occupiedCapacity, occupiedRate, diskIO], …]
    # or detailed_info = [[logicVolumeID, totalCapacity, occupiedCapacity, occupiedRate], …]
    # two_disk_info = [occupiedRate, hddCounts, sddCounts, hddTotalCapacity, ssdTotalCapacity,
    # hddOccupiedCapacity, ssdOccupiedCapacity, hddOccupiedRate, sddOccupiedRate, hddErrorRate,
    # ssdErrorRate, hddIOPS, ssdIOPS]
    @classmethod
    def IN_DCA_RSD(cls, ip, server_info, detailed_info, two_disk_info=None):
        # 将总体信息和详细信息添加到列表中
        cls.server_info_dict[ip] = server_info
        cls.detailed_info_dict[ip] = detailed_info

        now_time = time.strftime("%H:%M:%S", time.localtime(time.time()))
        if len(server_info) == 4:  # RAID架构下的数据
            if ip not in cls.RAID_io_info_dict:
                cls.RAID_io_info_dict[ip] = []
            RAID_io = server_info[-1]
            cls.RAID_io_info_dict[ip].append([RAID_io, now_time])
        elif two_disk_info is not None:
            cls.two_disk_info_dict[ip] = two_disk_info

            two_disk_io = two_disk_info[10:]  # two_disk_io =  [hddIOPS, ssdIOPS]

            if ip not in cls.two_disk_io_dict:
                cls.two_disk_io_dict[ip] = {"hdd": [], "ssd": []}
            cls.two_disk_io_dict[ip]["hdd"].append([two_disk_io[0], now_time])
            cls.two_disk_io_dict[ip]["ssd"].append([two_disk_io[1], now_time])
        # 检查数据超载
        cls.check_for_data_overload_2()

        # 刷新ip更新数据时间
        cls.update_time[ip] = time.time()

    @classmethod
    def check_for_data_overload_2(cls):  # 检查RAID架构总体负载和两类硬盘负载是否超载
        max_amount_RAID = cls.RAID_io_max_amount
        max_amount = cls.two_disk_io_max_amount
        for sever_ip in cls.RAID_io_info_dict:  # 检查RAID架构总体负载数据是否超载
            # 最多保存420个数据
            length = len(cls.RAID_io_info_dict[sever_ip])
            if length > max_amount_RAID:
                if sever_ip not in cls.RAID_io_info_dict_past:
                    cls.RAID_io_info_dict_past[sever_ip] = []
                # 将多的数据添加到历史数据中
                for i in range(length - max_amount_RAID):
                    cls.RAID_io_info_dict_past[sever_ip].append(cls.RAID_io_info_dict[sever_ip][i])
                # 删除前面的数据
                del cls.RAID_io_info_dict[sever_ip][:length - max_amount_RAID]
                # 历史数据最多保存3小时
                _length = len(cls.RAID_io_info_dict_past[sever_ip])
                if _length > 3 * 60 * 60:
                    del cls.RAID_io_info_dict_past[sever_ip][:_length - 3 * 60 * 60]

        for server_ip in cls.two_disk_io_dict:  # 检查两类硬盘负载数据是否超载
            # 最多保存420个数据
            length = len(cls.two_disk_io_dict[server_ip]["hdd"])
            if length > max_amount:
                if server_ip not in cls.two_disk_io_dict_past:
                    cls.two_disk_io_dict_past[server_ip] = {"hdd": [], "ssd": []}
                # 将多的数据添加到历史数据中
                for i in range(length - max_amount):
                    cls.two_disk_io_dict_past[server_ip]["hdd"].append(cls.two_disk_io_dict[server_ip]["hdd"][i])
                    cls.two_disk_io_dict_past[server_ip]["ssd"].append(cls.two_disk_io_dict[server_ip]["ssd"][i])
                # 删除前面的数据
                del cls.two_disk_io_dict[server_ip]["hdd"][:length - max_amount]
                del cls.two_disk_io_dict[server_ip]["ssd"][:length - max_amount]
                # 历史数据最多保存3小时
                _length = len(cls.two_disk_io_dict_past[server_ip]["hdd"])
                if _length > 3 * 60 * 60:
                    del cls.two_disk_io_dict_past[server_ip]["hdd"][:_length - 3 * 60 * 60]
                    del cls.two_disk_io_dict_past[server_ip]["ssd"][:_length - 3 * 60 * 60]

    @classmethod
    def get_RAID_overall_io_info(cls, ip):
        if ip not in cls.RAID_io_info_dict:
            return [], []
        RAID_io_info_list = cls.RAID_io_info_dict[ip]
        RAID_io_list, time_list = list_split(RAID_io_info_list)

        return RAID_io_list, time_list

    @classmethod
    def get_RAID_overall_io_info_past(cls, ip, time_begin, time_end):
        if ip not in cls.RAID_io_info_dict_past or not cls.RAID_io_info_dict_past[ip]:  # 如果为空
            return [], []
        # 将时间字符串转化为时间元组
        begin = time.strptime(time_begin, "%H:%M")
        end = time.strptime(time_end, "%H:%M")
        base = cls.RAID_io_info_dict_past[ip][0][1]  # 第一个数据的时间
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
        RAID_io_past = cls.RAID_io_info_dict_past[ip][start:end + 1]
        if not RAID_io_past:
            return [], []
        RAID_io_past_list, time_list = list_split(RAID_io_past)

        return RAID_io_past_list, time_list

    @classmethod
    def get_server_overall_info(cls, tag):
        server_info = []
        if tag == 0:  # 多硬盘架构
            for ip in cls.server_info_dict:
                if len(cls.server_info_dict[ip]) == 3:
                    server_info.append(ServerInfo(ip, cls.server_info_dict[ip][0],
                                                  cls.server_info_dict[ip][1],
                                                  cls.server_info_dict[ip][2]))
        else:  # RAID架构
            for ip in cls.server_info_dict:
                if len(cls.server_info_dict[ip]) == 4:
                    server_info.append(ServerInfo(ip, cls.server_info_dict[ip][0],
                                                  cls.server_info_dict[ip][1],
                                                  cls.server_info_dict[ip][2]))

        return server_info

    @classmethod
    def get_two_disk_info(cls, ip):
        if ip not in cls.two_disk_info_dict:
            return None
        two_disk_info = cls.two_disk_info_dict[ip]
        return TwoDiskInfo(two_disk_info)

    @classmethod
    def get_hdd_disk_io_info(cls, ip):
        if ip not in cls.two_disk_io_dict:
            return [], []
        hdd_disk_list = cls.two_disk_io_dict[ip]["hdd"]
        hdd_io_list, time_list = list_split(hdd_disk_list)

        return hdd_io_list, time_list

    @classmethod
    def get_hdd_disk_io_info_past(cls, ip, time_begin, time_end):
        if ip not in cls.two_disk_io_dict_past or not cls.two_disk_io_dict_past[ip]["hdd"]:  # 如果为空
            return [], []
        # 将时间字符串转化为时间元组
        begin = time.strptime(time_begin, "%H:%M")
        end = time.strptime(time_end, "%H:%M")
        base = cls.two_disk_io_dict_past[ip]["hdd"][0][1]  # 第一个数据的时间
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
        hdd_io_past = cls.two_disk_io_dict_past[ip]["hdd"][start:end + 1]
        if not hdd_io_past:
            return [], []
        hdd_io_list, time_list = list_split(hdd_io_past)

        return hdd_io_list, time_list

    @classmethod
    def get_ssd_disk_io_info(cls, ip):
        if ip not in cls.two_disk_io_dict:
            return [], []
        ssd_disk_list = cls.two_disk_io_dict[ip]["ssd"]
        ssd_io_list, time_list = list_split(ssd_disk_list)

        return ssd_io_list, time_list

    @classmethod
    def get_ssd_disk_io_info_past(cls, ip, time_begin, time_end):
        if ip not in cls.two_disk_io_dict_past or not cls.two_disk_io_dict_past[ip]["ssd"]:  # 如果为空
            return [], []
        # 将时间字符串转化为时间元组
        begin = time.strptime(time_begin, "%H:%M")
        end = time.strptime(time_end, "%H:%M")
        base = cls.two_disk_io_dict_past[ip]["ssd"][0][1]  # 第一个数据的时间
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
        ssd_io_past = cls.two_disk_io_dict_past[ip]["ssd"][start:end + 1]
        if not ssd_io_past:
            return [], []
        ssd_io_list, time_list = list_split(ssd_io_past)

        return ssd_io_list, time_list

    @classmethod
    def get_server_detailed_info(cls, ip, tag):
        if ip not in cls.detailed_info_dict:
            return []
        # 获取server_ip对应的服务器详细信息
        detailed_info = cls.detailed_info_dict[ip]
        server_detailed_info = []
        if tag == 0:  # 硬盘详细信息
            for disk in detailed_info:
                server_detailed_info.append(DiskInfo(disk))
        else:  # 逻辑卷详细信息
            for volume in detailed_info:
                server_detailed_info.append(LogicVolumeInfo(volume))
        return server_detailed_info

    @classmethod
    def IN_DCA_HDFP(cls, ip, smart_data):

        cls.smart_data_dict[ip] = smart_data
        # print(smart_data)
        # 将smart数据添加到列表中
        # 优化，判断型号，如果不在可以预测的型号范围内，不接收数据
        # if ip not in cls.smart_data_dict:
        #     cls.smart_data_dict[ip] = smart_data
        #     # 将原来的一维列表改变为嵌套列表
        #     for daily_data in cls.smart_data_dict[ip]:
        #         daily_data[3] = [daily_data[3]]
        # # 将新的smart数据添加到字典中，至少保证采集20天的历史数据才能预测
        # else:
        #     # # 只需要保留20天的历史smart数据即可，多余进行删除，已在main进行删除
        #     # for old in cls.smart_data_dict[ip]:
        #     #     if len(old[3]) > 19:
        #     #         old[3] = old[3][1:]
        #     # 这里需要保证硬盘按照disk_id排列顺序一致
        #     for old in cls.smart_data_dict[ip]:
        #         for new in smart_data:
        #             if old[0] == new[0]:
        #                 old[3].append(new[3])
        #                 # 每当有新的SMART数据添加进列表时，做一次健康度预测
        #                 # if len(old[3]) > 19:
        #                 #     cls.IN_HDFP_RSD(ip, old)
        #                 break

    @classmethod
    def get_disk_model(cls, ip, disk_id):
        if ip in cls.smart_data_dict:
            for list in cls.smart_data_dict[ip]:
                if list[0] == disk_id:
                    return list[1]
        return ""

    @classmethod
    def get_current_smart_data_len(cls, ip, disk_id):
        if ip in cls.smart_data_dict:
            for disk in cls.smart_data_dict[ip]:
                if disk[0] == disk_id:
                    return len(disk[2])
        return 0

    @classmethod  # 废弃
    def IN_HDFP_RSD(cls, ip, disk):
        # 将健康度信息添加到列表中
        # disk = cls.get_smart_info(ip, disk_id)
        health_degree = predict_disk_health_state(disk)
        if ip not in cls.health_degree_dict:
            cls.health_degree_dict[ip] = {}  # {ip: {disk_id: degree}, ip :{disk_id: degree}}
        if disk[0] in cls.health_degree_dict[ip]:
            if cls.health_degree_dict[ip][disk[0]] > health_degree:  # 健康度下降
                timestamp = time.strftime("%Y{y}%m{m}%d{d} %H:%M", time.localtime(time.time())).format(y='年', m='月',
                                                                                                       d='日')
                cls.hard_disk_failure_prediction_list.append([ip, disk[0], [health_degree, timestamp]])
        cls.health_degree_dict[ip][disk[0]] = health_degree  # disk_id和健康度

    @classmethod
    def get_health_degree(cls, server_ip, disk_id):  # 获取健康度信息
        if server_ip in cls.health_degree_dict and disk_id in cls.health_degree_dict[server_ip]:
            return cls.health_degree_dict[server_ip][disk_id]
        else:
            return 0  # 表示没有对应型号的预测模型

    @classmethod
    def IN_RSA_RSD(cls, warning):
        # 将告警信息添加到列表中
        warning_list.add_new_warning(warning)

    @classmethod
    def IN_HDFP_RSA(cls, ip, disk_id, failure_info):
        # 将硬盘故障预测处理信息添加到列表中
        cls.hard_disk_failure_prediction_list.append([ip, disk_id, failure_info])

    @classmethod
    def get_hard_disk_failure_prediction(cls):  # 获取硬盘故障预警信息
        list1 = cls.hard_disk_failure_prediction_list
        cls.hard_disk_failure_prediction_list = []
        return list1

    @classmethod
    def get_exception_dict(cls):
        return cls.exception_dict

    @classmethod
    def merge_timeline(cls, list1, list2):
        start_time, end_time = list1[0], list2[-1]
        # 转化为浮点数
        start_time = time.mktime((2000, 1, 1) + time.strptime(start_time, "%H:%M")[3:])
        end_time = time.mktime((2000, 1, 1) + time.strptime(end_time, "%H:%M")[3:])
        length = int((end_time - start_time) / 60 + 1)
        time_list = []
        for i in range(length):
            time_list.append(time.strftime("%H:%M", time.localtime(start_time + 60 * i)))

        return time_list

    @classmethod
    def delete_server(cls, ip, lock):
        # 删除前先申请锁
        lock.lock()
        if ip in cls.server_info_dict:
            del cls.server_info_dict[ip]
        if ip in cls.RAID_io_info_dict:
            del cls.RAID_io_info_dict[ip]
        if ip in cls.RAID_io_info_dict_past:
            del cls.RAID_io_info_dict_past[ip]
        if ip in cls.two_disk_io_dict:
            del cls.two_disk_io_dict[ip]
        if ip in cls.two_disk_io_dict_past:
            del cls.two_disk_io_dict_past[ip]
        if ip in cls.detailed_info_dict:
            del cls.detailed_info_dict[ip]
        if ip in cls.io_load_input_queue:
            del cls.io_load_input_queue[ip]
        if ip in cls.io_load_input_queue_display:
            del cls.io_load_input_queue_display[ip]
        if ip in cls.io_load_input_queue_display_past:
            del cls.io_load_input_queue_display_past[ip]
        if ip in cls.io_load_input_queue_predict:
            del cls.io_load_input_queue_predict[ip]
        if ip in cls.io_load_input_queue_train:
            del cls.io_load_input_queue_train[ip]
        if ip in cls.io_load_output_queue:
            del cls.io_load_output_queue[ip]
        if ip in cls.io_load_output_queue_past:
            del cls.io_load_output_queue_past[ip]
        if ip in cls.high_io_load_queue:
            del cls.high_io_load_queue[ip]
        if ip in cls.average_io_load:
            del cls.average_io_load[ip]
        if ip in cls.disk_detailed_info:
            del cls.disk_detailed_info[ip]
        if ip in cls.smart_data_dict:
            del cls.smart_data_dict[ip]
        if ip in cls.health_degree_dict:
            del cls.health_degree_dict[ip]
        if ip in cls.exception_dict:
            del cls.exception_dict[ip]
        if ip in cls.exception_dict:
            del cls.exception_dict[ip]
        if ip in cls.update_time:
            del cls.update_time[ip]
        # 释放锁
        lock.unlock()

    @classmethod
    def get_two_disk_io_show_time(cls):
        return cls.two_disk_io_max_amount // 60

    @classmethod
    def change_two_disk_io_show_time(cls, minute, lock):
        if (cls.two_disk_io_max_amount // 60) == minute:
            return

        # 删除前先申请锁
        lock.lock()
        for ip in cls.two_disk_io_dict:
            current_length = len(cls.two_disk_io_dict[ip]["hdd"])

            # 列表由小变大
            if (cls.two_disk_io_max_amount // 60) < minute:
                # 缺少的数据从历史列表中取回来
                if ip in cls.two_disk_io_dict_past and cls.two_disk_io_dict_past[ip]["hdd"]:
                    cls.two_disk_io_dict[ip]["hdd"] = cls.two_disk_io_dict_past[ip]["hdd"][
                                                      -(minute * 60 - current_length):] + cls.two_disk_io_dict[ip][
                                                          "hdd"]
                    cls.two_disk_io_dict[ip]["ssd"] = cls.two_disk_io_dict_past[ip]["ssd"][
                                                      -(minute * 60 - current_length):] + cls.two_disk_io_dict[ip][
                                                          "ssd"]
                    # 删除取出的数据
                    del cls.two_disk_io_dict_past[ip]["hdd"][-(minute * 60 - current_length):]
                    del cls.two_disk_io_dict_past[ip]["ssd"][-(minute * 60 - current_length):]
            # 列表由大变小
            else:
                # 当前数据对于缩小后的列表已经溢出
                if current_length > minute * 60:
                    # 将多余数据放入历史列表中去
                    for i in range(current_length - minute * 60):
                        if ip not in cls.two_disk_io_dict_past:
                            cls.two_disk_io_dict_past[ip] = {"hdd": [], "ssd": []}
                        cls.two_disk_io_dict_past[ip]["hdd"].append(cls.two_disk_io_dict[ip]["hdd"][i])
                        cls.two_disk_io_dict_past[ip]["ssd"].append(cls.two_disk_io_dict[ip]["ssd"][i])
                    # 删除前面的数据
                    del cls.two_disk_io_dict[ip]["hdd"][:current_length - minute * 60]
                    del cls.two_disk_io_dict[ip]["ssd"][:current_length - minute * 60]

        cls.two_disk_io_max_amount = int(minute * 60)

        # 释放锁
        lock.unlock()

    @classmethod
    def get_RAID_io_show_time(cls):
        return cls.RAID_io_max_amount // 60

    @classmethod
    def change_RAID_io_show_time(cls, minute, lock):
        if (cls.RAID_io_max_amount // 60) == minute:
            return
        
        # 删除前先申请锁
        lock.lock()
        for ip in cls.RAID_io_info_dict:
            current_length = len(cls.RAID_io_info_dict[ip])

            # 列表由小变大
            if (cls.RAID_io_max_amount // 60) < minute:
                # 缺少的数据从历史列表中取回来
                if ip in cls.RAID_io_info_dict_past and cls.RAID_io_info_dict_past[ip]:
                    cls.RAID_io_info_dict[ip] = cls.RAID_io_info_dict_past[ip][
                                                -(minute * 60 - current_length):] + cls.RAID_io_info_dict[ip]
                    # 删除取出的数据
                    del cls.RAID_io_info_dict_past[ip][-(minute * 60 - current_length):]
            # 列表由大变小
            else:
                # 当前数据对于缩小后的列表已经溢出
                if current_length > minute * 60:
                    # 将多余数据放入历史列表中去
                    for i in range(current_length - minute * 60):
                        if ip not in cls.RAID_io_info_dict_past:
                            cls.RAID_io_info_dict_past[ip] = []
                        cls.RAID_io_info_dict_past[ip].append(cls.RAID_io_info_dict[ip][i])
                    # 删除前面的数据
                    del cls.RAID_io_info_dict[ip][:current_length - minute * 60]

        cls.RAID_io_max_amount = int(minute * 60)
        # 释放锁
        lock.unlock()
