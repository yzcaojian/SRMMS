# -*- coding: utf-8 -*-
# @ModuleName: out_interface
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/4/25 16:55
import socket
import  json

Request_Resources = 0
Send_Instructions = 1
# 资源状态信息接口  服务器->系统
class OUT_SS_SRMMS:
    def function(self, ip_addr):
        pass

# 调度指令分配接口  系统->服务器
class OUT_SRMMS_SS:
    def function(self, ip_addr, instructions):
        pass


class OUT_SS_SRMMS_impl(OUT_SS_SRMMS):
    def function(self, ip_addr):
        # 连接服务器 ip_addr=("localhost",8888)
        client = socket.socket()
        client.connect(ip_addr)
        # 将接收到的数据保存到文件
        filename = ip_addr[0] + ".csv"
        f = open(filename, "wb")
        # 构建json文件
        file_msg = {"action": Request_Resources}
        # 发送json文件
        client.send(bytes(json.dumps(file_msg), encoding="utf-8"))
        while True:
            # 每次接收1024字节 纸质接收完毕
            data = client.recv(1024)
            f.write(data)
            if not data:
                break
        client.close()

        return filename


class OUT_SRMMS_SS_impl(OUT_SRMMS_SS):
    def function(self, ip_addr, instructions):
        # 连接服务器 ip_addr=("localhost",8888)
        client = socket.socket()
        client.connect(ip_addr)
        # 构建json文件
        file_msg = {"action": Send_Instructions, "instructions": instructions}
        # 发送json文件
        client.send(bytes(json.dumps(file_msg), encoding="utf-8"))
        client.close()
