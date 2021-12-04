import numpy as np

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 划分一级健康度的数据集
@Time : 2021/12/2 20:10
@Author : cao jian
"""

# 判断天数，不同天数划分不同的步长
smart = np.load('HGST HMS5C4040BLE640_data_v2.npy')
label = np.load('HGST HMS5C4040BLE640_label_v1.npy')
seq_len = np.load('seqlen.npy')

# min_max_scaler = preprocessing.MinMaxScaler()  # 定义一个缩放数据的标量
# smart = min_max_scaler.fit_transform(smart)

print('smart数据格式', smart.shape)
print('label数据格式', label.shape)
hdd = np.column_stack((smart, label))
print('hdd数据格式', hdd.shape)


# 对所有序号的硬盘数据进行裁剪，以合理的步长选择平衡各标签类别下的数据实例
def sliceAll(hdd):
    samples = []  # 以一个时间序列进行拆分样本，None * 20 * 9
    for i in range(1, len(seq_len)):  # 可以不考虑把最后一个故障盘的记录加进去，根据经验它的时间长度肯定小于20
        if i != len(seq_len) - 1:
            samples.append(hdd[seq_len[i - 1]:seq_len[i], :])
        else:
            samples.append(hdd[seq_len[i - 1]:seq_len[i], :])
            samples.append(hdd[seq_len[i]:, :])
    hdd = samples  # np.array(samples) # 将样本增维，不同序列号的硬盘记录分开
    # print(hdd.shape)
    # perDiskStepSlice = np.array([])
    perDiskStepSlice = []
    for d in hdd:  # 通过每个序列号的硬盘记录抽取样本20 * 9
        # print(type(stepSlice(d)))
        # np.row_stack((perDiskStepSlice, stepSlice(d)))
        temp = stepSlice(d)
        if temp:
            perDiskStepSlice.append(stepSlice(d))
        else:
            print("null")
    return perDiskStepSlice


def stepSlice(aDisk, sliceLen=20,  step=1):
    # aDisk表示每个序列号硬盘的所有记录，sliceLen表示RNN序列长度，定为20，step表示步长
    # 分段切片，每个区间取步长1:2:3:4:5:24，一共6个区间，每个区间保证10个输入RNN的序列
    # 针对此model的记录数量，平均每个盘为2100左右记录，可以使用如上的区间步长
    sliceList = []
    # aDisk = np.flip(aDisk, axis=0)  # 颠倒了记录顺序，failure=1的记录在最后一行
    border = aDisk.shape[0]  # 行数
    start = 0  # 开始
    # end = 0  # 结束
    flag = 0  # 计数，每到整十数则更新步长，保证每个区间取平衡又足够的数据
    while start < border:
        if flag % 10 == 0 and flag != 0:
            if step <= 4:
                step += 1
            else:
                step = 24

        end = start + sliceLen
        if end > border:
            break
        # 用相邻的20个记录，并不是非连续的记录，翻转数据，并且让数据的时间流向为从正常到故障
        sliceList.append(np.flip(aDisk[start:end, :], axis=0))
        start = start + step
        flag += 1
    return sliceList  # silceList.tolist()


hdd_n = sliceAll(hdd)  # 此时hdd_n类型较为复杂，[array([[]])...]，需要转化为三维矩阵
hdd = []
for d1 in hdd_n:
    for d2 in d1:
        hdd.append(d2)

hdd = np.array(hdd)
print('所有的样本集', hdd.shape)  # (15826, 20, 10)
smart = hdd[:, :, 0:-1]
label = hdd[:, :, -1]
label = label.astype(np.int32)
print(smart.shape)
print('one-hot编码之前标签数组维度为', label.shape)  # (15826, 20)


# 对标签进行one-hot编码
def one_hot(target):
    n = np.shape(target)[0]
    for i in range(0, n):
        m = int(target[i, 0] - 1)
        target[i, 0] = 0
        if m >= 0:
            target[i, m] = 1
    return target


def buildLabel(label):
    a = np.shape(label)[0]
    b = np.shape(label)[1]
    prezero = np.zeros((a * b, 5))
    # target = np.concatenate((pretarget, prezero), axis=2)
    pretarget = np.reshape(label, (a * b, 1))
    label = np.concatenate((pretarget, prezero), axis=1)
    label = one_hot(label)
    label = np.reshape(label, (a, b, 6))
    label = label[:, -1, :]
    return label


label = buildLabel(label)
print('one-hot编码之后标签数组维度为', label.shape)  # (15826, 6)

# 划分训练集和测试集 9:1
partition = []
i = 0
while i < label.shape[0]:
    partition.append(i)
    i += 10
test_data = smart[::10, :, :]
test_label = label[::10, :]
train_data = np.delete(smart, partition, axis=0)
train_label = np.delete(label, partition, axis=0)

np.save('train_data.npy', train_data)
np.save('train_label.npy', train_label)
np.save('test_data.npy', test_data)
np.save('test_label.npy', test_label)
