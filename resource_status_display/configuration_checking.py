import socket
from PyQt5.QtWidgets import QMessageBox
"""
-*- coding: utf-8 -*- 
@Project: GUI_beginning
@Description: 执行各种在配置界面需要进行的判断操作
@Time : 2021/4/28 10:53
@Author : cao jian
"""


def check_ip(ip):
    try:
        client = socket.socket()
        client.connect((ip, 12345))
        client.send(bytes("请求数据2", encoding="utf-8"))
        client.recv(10240).decode()
        client.close()
    # 服务器失联 捕获异常
    except TimeoutError:
        print("连接超时，IP地址不存在")
        return 1
    except ConnectionRefusedError:
        print("拒绝连接，目标服务器未开启代理程序")
        return 2
    except Exception as e:
        print("其它异常类型:" + str(e))
        return 3
    # 连接正常
    else:
        return 4

class ConfigurationInfo:
    def __init__(self):
        self.server_names, self.server_IPs = self.readFile()

    def readFile(self):
        file = open('../resource_status_display/txt/configuration.txt', 'r')
        line = file.readline()
        server_names = []
        server_IPs = []
        while line:
            index = line.find(' ')
            last = line.find('\n') if line.find('\n') != -1 else len(line)
            server_names.append(line[:index])
            server_IPs.append(line[index+1:last])
            line = file.readline()
        file.close()
        return server_names, server_IPs

    def writeFile(self, mode, new_line):
        file = open('./txt/configuration.txt', 'a+')
        if mode == 1:  # 添加
            file.write(new_line)
        elif mode == 2:  # 删除
            # 先清空文件再删除
            file.seek(0)
            file.truncate()
            for i in range(len(self.server_names)):
                file.write(self.server_names[i] + ' ' + self.server_IPs[i] + "\n")
        elif mode == 3:  # 修改
            file.seek(0)
            file.truncate()
            for i in range(len(self.server_names)):
                file.write(self.server_names[i] + ' ' + self.server_IPs[i] + "\n")
        file.close()

    def IsNameExist(self, server_name):
        # 通过本地文件对比是否重名
        for name in self.server_names:
            if name == server_name:
                return True
        return False

    def IsIPAddressExist(self, ip_address):
        # 通过本地文件对比是否重名
        for ip in self.server_IPs:
            if ip == ip_address:
                return True
        return False

    def addServer(self, ip_address, server_name):
        if not ip_address or not server_name:
            return "添加失败，输入信息不完整。"
        if self.IsNameExist(server_name):
            return "添加失败，服务器" + server_name + "已存在。"
        if self.IsIPAddressExist(ip_address):
            return "添加失败，服务器" + ip_address + "已存在。"
        # 判断服务器ip是否可监控
        data = check_ip(ip_address)
        if data == 1:
            return "添加失败，连接超时，IP地址" + ip_address + "不可达。"
        elif data == 2:
            return "添加失败，服务器" + ip_address + "未部署代理程序。"
        elif data == 3:
            return "添加失败，由于未知错误，IP地址连接出现问题。"
        self.server_names.append(server_name)
        self.server_IPs.append(ip_address)
        self.writeFile(1, server_name + ' ' + ip_address + "\n")
        return "已成功配置增加新的服务器" + server_name + "。"

    def deleteServer(self, widget, ip_address, server_name):
        # 只会有一个参数传进来，另一个参数为空
        delete_index = 0
        if server_name:
            if not self.IsNameExist(server_name):
                return "删除失败，服务器" + server_name + "不存在。", 0
        else:
            if not self.IsIPAddressExist(ip_address):
                return "删除失败，服务器" + ip_address + "不存在。", 0
        for i in range(len(self.server_IPs)):
            if self.server_names[i] == server_name or self.server_IPs[i] == ip_address:
                delete_index = i
                break
        selection = QMessageBox.information(widget, "注意", "您确定要删除该服务器连接信息吗", QMessageBox.Yes | QMessageBox.No)
        if selection == QMessageBox.Yes:
            # delete_server = self.server_IPs[delete_index]
            self.server_names.remove(self.server_names[delete_index])
            self.server_IPs.remove(self.server_IPs[delete_index])
            self.writeFile(2, '')
            return "已成功删除服务器" + (server_name if server_name != '' else ip_address) + "。", 1
        else:
            return "您已取消删除操作。", 0

    # 修改配置信息，只能通过IP地址修改名称
    def modifyName(self, ip_address, new_name):
        # 读文件找到能否对应一个IP地址等于new_ip，不能的话返回false，能的话对比name不一样可进行更改
        if not ip_address or not new_name:
            return "添加失败，输入信息不完整。"
        temp = ""
        if self.IsIPAddressExist(ip_address):
            for i in range(len(self.server_IPs)):
                if ip_address == self.server_IPs[i]:
                    if not self.IsNameExist(new_name):
                        temp = self.server_names[i]
                        self.server_names[i] = new_name
                        self.writeFile(3, '')
                        break
                    else:
                        return "更改失败，服务器" + new_name + "已存在。"
        else:
            return "更改失败，服务器" + ip_address + "不存在。"
        return "更改成功，服务器" + ip_address + "名称由" + temp + "改变为" + new_name + "。"

    def searchServer(self, ip_address, server_name):
        # 优化实现模糊查询
        # 只会传入一个实际参数，另一个为空
        if ip_address:
            for i in range(len(self.server_IPs)):
                if ip_address == self.server_IPs[i]:
                    return "查询结果如下：" + self.server_names[i] + ' ' + self.server_IPs[i]
        if server_name:
            for i in range(len(self.server_names)):
                if server_name == self.server_names[i]:
                    return "查询结果如下：" + self.server_names[i] + ' ' + self.server_IPs[i]
        return "没有查询结果。"

    # 根据IP地址查找服务器名称
    def IPtoName(self, ip_address):
        for (i, ip) in enumerate(self.server_IPs):
            if ip == ip_address:
                return self.server_names[i]
        return ""

    # 根据服务器名称查找IP地址
    def NametoIP(self, server_name):
        for (i, name) in enumerate(self.server_names):
            if server_name == name:
                return self.server_IPs[i]
        return ""


# 单例模式，应用于整个系统进行IP地址和名称的对应
configuration_info = ConfigurationInfo()

# server1 192.168.1.1
# serevr2 192.168.1.2
# server3 192.168.1.3
# server4 192.168.1.4
# local1 192.168.20.1
# local2 192.168.20.2
# local3 192.168.20.6
# test1 192.168.225.225
# test2 192.168.225.226
