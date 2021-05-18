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

f = open("file.txt", "wb")
while True:
    send_data = input("输入发送内容:")
    if not send_data:
        break
    s.send(send_data.encode())
    while True:
        data = s.recv(1024)
        f.write(data)
        if not data:
            break
print("传输完成...")
s.close()
