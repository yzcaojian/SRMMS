# -*- coding: utf-8 -*-
# @ModuleName: out_interface
# @Function: out_interface
# @Author: Chen Zhongwei
# @Time: 2021/4/25 16:55
import random
import socket
import json

Request_Resources = 0
Send_Instructions = 1


class out_interface:
    # 资源状态信息接口  服务器->系统
    @classmethod
    def OUT_SS_SRMMS(cls, ip_addr):
        pass

    # 调度指令分配接口  系统->服务器
    @classmethod
    def OUT_SRMMS_SS(cls, ip_addr, instructions):
        pass


class out_interface_impl(out_interface):
    # 端口号
    port = 12345
    index = 0

    @classmethod
    def OUT_SS_SRMMS(cls, ip):
        # 连接服务器
        client = socket.socket()
        ip_addr = (ip, cls.port)
        client.connect(ip_addr)
        if cls.index % (60 * 60 * 24) == 0:  # 请求数据(包含smart数据)
            client.send(bytes("请求数据1", encoding="utf-8"))
        else:  # 请求数据(不包含smart数据)
            client.send(bytes("请求数据2", encoding="utf-8"))
        cls.index = (cls.index + 1) % (60 * 60 * 24)
        data = client.recv(10240).decode()

        client.close()

        # 将接收到的数据返回
        return data

    @classmethod
    def OUT_SRMMS_SS(cls, ip, instructions):
        # 连接服务器
        client = socket.socket()
        ip_addr = (ip, cls.port)
        client.connect(ip_addr)
        message = "接收指令" + '/' + instructions
        client.send(bytes(message, encoding="utf-8"))

        client.close()

    @classmethod
    def OUT_SS_SRMMS_(cls, ip):
        # 读取文件模拟数据
        filename = 'D:/test_SRMMS/' + ip + '_' + str(random.randint(0, 6)) + '.txt'
        with open(filename, "r", encoding='utf-8') as f:
            dataps = f.read()

            data = dataps
            # print(type(data))
            # print(data["overall_info"])

        return data



