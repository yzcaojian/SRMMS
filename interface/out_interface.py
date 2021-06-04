# -*- coding: utf-8 -*-
# @ModuleName: out_interface
# @Function: out_interface
# @Author: Chen Zhongwei
# @Time: 2021/4/25 16:55
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
    port = 8888

    @classmethod
    def OUT_SS_SRMMS(cls, ip):
        # 连接服务器 ip_addr=("localhost",8888)
        client = socket.socket()
        ip_addr = (ip, cls.port)
        client.connect(ip_addr)

        # 构建json格式
        file_msg = {"action": Request_Resources}
        # 发送json信息
        client.send(bytes(json.dumps(file_msg), encoding="utf-8"))

        # 首先接收数据的长度
        length = int(client.recv(1024).decode())
        # 接收指定长度的数据 类型为string
        data = client.recv(length).decode()

        client.close()
        # 将接收到的数据返回
        return data

    @classmethod
    def OUT_SRMMS_SS(cls, ip, instructions):
        # 连接服务器 ip_addr=("localhost",8888)
        client = socket.socket()
        ip_addr = (ip, cls.port)
        client.connect(ip_addr)
        # 构建json格式
        file_msg = {"action": Send_Instructions, "instructions": instructions}
        # 发送json信息
        client.send(bytes(json.dumps(file_msg), encoding="utf-8"))
        client.close()

