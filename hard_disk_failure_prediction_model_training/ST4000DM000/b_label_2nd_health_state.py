import csv
import numpy as np
from sklearn import preprocessing

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 标注二级健康度，并进行特征与标签分开保存，将特征数据归一化
@Time : 2021/5/24 9:59
@Author : cao jian
"""

file = open("ST4000DM000_v1.csv")
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
        hdd.append([int(float(record[j])) for j in range(1, len(record))])

hdd = np.array(hdd)
print(hdd.shape)  # (2159395, 25)
file.close()

j = 0  # 用于记录新的序列号在数组中故障记录的位置
seqlen = [0]  # 用于记录每个序列号的硬盘的记录长度，每个元素代表新的硬盘记录开始行号
for i in range(1, len(hdd)):
    if hdd[i, 0] == 1:  # failure字段是1，hdd[0, 0]一定是1
        seqlen.append(i)
        # if i - j <= 730:
        for k in range(j, i):  # 按距离故障天数划分一级健康度
            days = k - j
            if days >= 11:
                hdd[k, 0] = 10
            elif days >= 6:
                hdd[k, 0] = 9
            elif days >= 3:
                hdd[k, 0] = 8
            elif days >= 0:
                hdd[k, 0] = 7
        j = i  # 更新到下一个序列号的硬盘故障记录
    if i == (len(hdd) - 1):
        for k in range(j, i + 1):  # 按距离故障天数划分一级健康度
            days = k - j
            if days >= 11:
                hdd[k, 0] = 10
            elif days >= 6:
                hdd[k, 0] = 9
            elif days >= 3:
                hdd[k, 0] = 8
            elif days >= 0:
                hdd[k, 0] = 7

del_col = sorted(set(del_col))
print('del', len(del_col))  # 39
# for i in del_col:  # del没问题
#     print(i)
#     print(hdd[i])
# 根据del_col更新seqlen的值，因为删除行造成行号发生变化
for l in range(len(seqlen)):
    minus = 0
    for d in del_col:
        if seqlen[l] > d:  # 前面删除了多少行
            minus += 1
        else:  # 因为两个列表元素都是有序的，所以可以直接break
            break
    seqlen[l] -= minus
seqlen = np.array(seqlen)
print('seqlen:', seqlen.shape)  # (3256,)
for i in seqlen:
    print(i)
# for i in del_col:
#     print(hdd[i])
hdd = np.delete(hdd, del_col, axis=0)

seqlen_u = seqlen
t = len(seqlen) - 1
while t > 0:
    if seqlen[t] - seqlen[t - 1] > 30:
        hdd = np.delete(hdd, range(seqlen[t - 1] + 30, seqlen[t]), axis=0)
        s = len(seqlen_u) - 1
        while s >= t:
            seqlen_u[s] -= (seqlen[t] - seqlen[t - 1] - 30)
            s -= 1
    t = t - 1
print("经过筛选，将三十天以外的数据全部删除", hdd.shape)  # (95538, 25)
print(seqlen_u.shape, seqlen.shape)
seqlen = seqlen_u  # 更新seqlen对每个盘开始位置的的索引

# 中间步骤，为了得到特征选择的数据和特征，需要将10天内的数据单独取出来
# temp = hdd
# t = len(temp) - 1
# while t > 0:
#     if temp[t][0] == 10:
#         temp = np.delete(temp, [t], axis=0)
#     t = t - 1
#
# csv_data = pd.DataFrame(temp)
# csv_data.to_csv('temp_data.csv')
#
# # 对所有SMART数据进行归一化处理
# min_max_scaler = preprocessing.MinMaxScaler()  # 定义一个缩放数据的标量
# smart = temp[:, 1:mlen - 1]
# health_state = temp[:, 0]
#
# smart = min_max_scaler.fit_transform(smart)
# # hdd = np.column_stack((hdd[:, 0], smart))
# print(temp.shape)
#
# np.save("feature_selection_data_2.npy", smart)
# np.save("feature_selection_label_2.npy", health_state)

# 对所有SMART数据进行归一化处理
min_max_scaler = preprocessing.MinMaxScaler()  # 定义一个缩放数据的标量
smart = hdd[:, 1:mlen - 1]
health_state = hdd[:, 0]

# 得到归一化的最大值的和最小值
max_index = smart.argmax(axis=0)
min_index = smart.argmin(axis=0)
for i in range(len(max_index)):
    print("max", smart[max_index[i]][i], "min", smart[min_index[i]][i])

smart = min_max_scaler.fit_transform(smart)
# hdd = np.column_stack((hdd[:, 0], smart))
print(hdd.shape)

np.save("ST4000DM000_data_2_v1.npy", smart)
np.save("ST4000DM000_label_2_v1.npy", health_state)
np.save("seqlen_2.npy", seqlen)
# writer = csv.writer(file2, 'a+', newline='')
# for record in hdd:
#     writer.writerow(record[1:])  # 无需保留序列号

smart = np.load("ST4000DM000_data_2_v1.npy")
health_state = np.load("ST4000DM000_label_2_v1.npy")
print(health_state[0], health_state[1], health_state[2])
print(smart[2])  # 打印测试程序是否正确
# print(hdd)
print(smart.shape)  # (95538, 24)
print(health_state.shape)
