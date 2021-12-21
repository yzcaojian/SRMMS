# -*- coding: utf-8 -*-
# @ModuleName: data_table
# @Function:
# @Author: Chen Zhongwei
# @Time: 2021/5/14 13:48
import pandas as pd
import numpy as np

filename = './data/Financial2.spc'
savaname = './data/Financial2.csv'


#  将负载数据以秒为单位进行处理
f = open(filename)
df = pd.read_csv(f)  # 读入数据
data = df.values
data_timestamp = data[:][:, 4]  # 读取列数据
data_iops = data[:][:, 2]
# ASU = data[:][:, 0]
data_timestamp = data_timestamp.astype(np.int)

second = 0
total = 0
data_array = []

for i in range(len(data_timestamp)):
    # if ASU[i] == 0:
    if second == data_timestamp[i]:
        total += data_iops[i]
    else:
        data_array.append([second, total])
        second = data_timestamp[i]
        total = data_iops[i]
data_array = np.array(data_array)
data_timestamp = data_array[:][:, 0]
data_iops = data_array[:][:, 1]

dataFrame = pd.DataFrame({'time': data_timestamp, 'total': data_iops})
dataFrame.to_csv(savaname, index=False, sep=',')

# 将以秒为单位的负载数据转化为以分钟为单位
filename = './data/Financial2.csv'
savaname = './data/Financial2_minutes.csv'
f = open(filename)
df = pd.read_csv(f)  # 读入数据
data = df.values
data_timestamp = data[:][:, 0]  # 读取列数据
data_iops = data[:][:, 1]


minute = 1
total = 0
data_array = []
for i in range(len(data_timestamp)):
    # 以分钟为单位
    if data_timestamp[i] % 60 == 0 and data_timestamp[i] != 0:
        data_array.append([minute, total // 1024])
        minute += 1
        total = data_iops[i]
    else:
        total += data_iops[i]
data_array = np.array(data_array)
data_timestamp = data_array[:][:, 0]
data_iops = data_array[:][:, 1]

dataFrame = pd.DataFrame({'time': data_timestamp, 'total': data_iops})
dataFrame.to_csv(savaname, index=False, sep=',')

