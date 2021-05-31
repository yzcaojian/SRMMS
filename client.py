# -*- coding: utf-8 -*-
# @ModuleName: client
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/4/26 16:07

import socket
import json
s = socket.socket()
host = socket.gethostname()
port = 12345
s.connect((host, port))
print("已连接")

while True:
    send_data = input("输入发送内容:")
    if not send_data:
        break
    s.send(send_data.encode())
    string = ""

    length = int(s.recv(100).decode())
    data = s.recv(length)
    print(data, type(data))
    string += data.decode()
    print(string, length)
    dic = json.loads(string)
    print(dic, type(dic))
    print(dic["overall_info"])
    print(dic["detailed_info"])

print("传输完成...")
s.close()
