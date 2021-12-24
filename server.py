# -*- coding: utf-8 -*-
# @ModuleName: server
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/4/26 15:59

import pandas as pd
import numpy as np
import socket
import json

# filename = 'read_diff_disb.csv'
# f = open(filename).read()
# df = pd.read_csv(f)  # 读入数据
# data = df.values
# data = data[0:][:, 0:2]
# data = data.astype(np.int)

port = 12345
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("localhost", port))
flag = True
while flag:
    s.listen(1)
    sock, addr = s.accept()
    print("连接已经建立")
    dic = {"overall_info": ["2000", "1000", "50%", "5", "4", "1200", "800", "50%", "50%", "0", "0", "100000", "200000"],
           "detailed_info": [["0001", "SSD", "正常", "200", "100", "50%", "40000"]], "smart_data": []}
    string = json.dumps(dic)

    info = sock.recv(1024).decode()
    if info == "请求数据":
        byte = bytes(string, encoding="utf-8")
        sock.send(byte)

    sock.close()
s.close()
