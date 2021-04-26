# -*- coding: utf-8 -*-
# @ModuleName: client
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/4/26 16:07

import socket
s = socket.socket()
host = socket.gethostname()
port = 12345
s.connect((host, port))
print("已连接")
info = ""
while info != "byebye":
    send_data = input("输入发送内容:")
    s.send(send_data.encode())
    if send_data == "byebye":
        break
    info = s.recv(1024).decode()
    print("接收到的内容:" + info)
s.close()