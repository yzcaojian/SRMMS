# -*- coding: utf-8 -*-
# @ModuleName: server
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/4/26 15:59

import pandas as pd
import numpy as np
import socket

filename = 'read_diff_disb.csv'
f = open(filename).read()
# df = pd.read_csv(f)  # 读入数据
# data = df.values
# data = data[0:][:, 0:2]
# data = data.astype(np.int)

host = socket.gethostname()
port = 12345
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)
sock, addr = s.accept()
print("连接已经建立")
info = sock.recv(1024).decode()
while True:
    if info == "请求数据":
        sock.send(bytes(f, encoding="utf-8"))
        print("发送文件大小完成:", len(f))
        break
    else:
        break
sock.close()
s.close()
