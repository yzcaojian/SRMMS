# -*- coding: utf-8 -*-
# @ModuleName: client
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/4/26 16:07

import socket
import json
s = socket.socket()
port = 12345
s.connect(("localhost", port))
print("已连接")

send_data = input("输入发送内容:")
s.send(send_data.encode())
data = ""
while True:
    data_ = s.recv(10).decode()
    if not data_:
        break
    data += data_
print(data)
dic = json.loads(data)
print(dic, type(dic))
# print(dic["overall_info"])
# print(dic["detailed_info"])
# if "smart_data" in dic:
#     print(dic["smart_data"])

print("传输完成...")
s.close()
