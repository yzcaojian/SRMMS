import csv
import numpy as np
from sklearn import preprocessing

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 标注一级健康度，并进行特征与标签分开保存，将特征数据归一化
@Time : 2021/12/3 15:32
@Author : cao jian
"""

file = open("ST8000NM0055_v1.csv")
reader = csv.reader(file)
mlen = len(next(reader))  # 规整的每个记录的长度
del_col = []  # 不规整的记录的行号，以便于后面删除
# 暴力读，将csv文件转化为numpy数组
first_time = True
hdd = []
for i, record in enumerate(reader):
    if len(record) != mlen:
        del_col.append(i)  # 此行SMART数据信息不全，但是根据查看failure字段完整，仍可以用于划分健康度
        # hdd.append([int(float(record[i])) for i in range(1, len(record)) if record[i] != '' else 0])
        temp = []
        for j in range(1, mlen):
            if j >= len(record):
                temp.append(0)  # 对于数据缺失的行先填充零，标注完健康度之后删除
            else:
                temp.append(int(float(record[j])))
        hdd.append(temp)
    else:
        hdd.append([int(float(record[j])) for j in range(1, len(record))])  # 这里已经丢弃了序列号的信息

hdd = np.array(hdd)
print(hdd.shape)  # (390369, 25)
file.close()

j = 0  # 用于记录新的序列号在数组中故障记录的位置
seqlen = [0]  # 用于记录每个序列号的硬盘的记录长度，每个元素代表新的硬盘记录开始行号
for i in range(1, len(hdd)):
    if hdd[i, 0] == 1:  # failure字段是1，hdd[0, 0]一定是1
        seqlen.append(i)
        # if i - j <= 730:
        for k in range(j, i):  # 按距离故障天数划分一级健康度
            days = k - j
            if days >= 310:
                hdd[k, 0] = 6
            elif days >= 150:
                hdd[k, 0] = 5
            elif days >= 70:
                hdd[k, 0] = 4
            elif days >= 30:
                hdd[k, 0] = 3
            elif days >= 10:
                hdd[k, 0] = 2
            elif days >= 0:
                hdd[k, 0] = 1
        j = i  # 更新到下一个序列号的硬盘故障记录

    if i == (len(hdd) - 1):
        for k in range(j, i + 1):  # 按距离故障天数划分一级健康度
            days = k - j
            if days >= 310:
                hdd[k, 0] = 6
            elif days >= 150:
                hdd[k, 0] = 5
            elif days >= 70:
                hdd[k, 0] = 4
            elif days >= 30:
                hdd[k, 0] = 3
            elif days >= 10:
                hdd[k, 0] = 2
            elif days >= 0:
                hdd[k, 0] = 1

print('删除行数', len(del_col))  # 0
# 根据del_col更新seqlen的值，因为删除行造成行号发生变化
for l in range(len(seqlen)):
    minus = 0
    for d in del_col:
        if seqlen[l] > d:  # 前面删除了多少行
            minus += 1
        else:  # 因为两个列表元素都是有序的，所以可以直接break
            break
    seqlen[l] -= minus
# 这里有问题，没有正确更新seqlen
seqlen = np.array(seqlen)
print('序号数量', seqlen.shape)  # (612, )，对应硬盘序列号数量
hdd = np.delete(hdd, del_col, axis=0)

# 对所有SMART数据进行归一化处理
min_max_scaler = preprocessing.MinMaxScaler()  # 定义一个缩放数据的标量
smart = hdd[:, 1:]
health_state = hdd[:, 0]

# 得到归一化的最大值的和最小值
max_index = smart.argmax(axis=0)
min_index = smart.argmin(axis=0)
for i in range(len(max_index)):
    print("max", smart[max_index[i]][i], "min", smart[min_index[i]][i])

smart = min_max_scaler.fit_transform(smart)

np.save("ST8000NM0055_data_v1.npy", smart)
np.save("ST8000NM0055_label_v1.npy", health_state)
np.save("seqlen.npy", seqlen)

smart = np.load("ST8000NM0055_data_v1.npy")
health_state = np.load("ST8000NM0055_label_v1.npy")
print('测试------------------------')
print(health_state[:100, ])
print(smart[:10, ])  # 打印测试程序是否正确
print(smart.shape)
print(health_state.shape)
