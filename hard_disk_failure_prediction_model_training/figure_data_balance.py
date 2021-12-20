import numpy as np

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 测试标签文件里面各类别的健康度到底有多少，是否平衡
@Time : 2021/12/20 16:40
@Author : cao jian
"""

# label = np.load("./ST4000DM000/ST4000DM000_label_v1.npy")
# train_label = np.load("./ST4000DM000/train_label.npy")
# label = np.load("./WD30EFRX/WD30EFRX_label_v1.npy")
# train_label = np.load("./WD30EFRX/train_label.npy")
# label = np.load("./ST12000NM0007/ST12000NM0007_label_v1.npy")
# train_label = np.load("./ST12000NM0007/train_label.npy")
# label = np.load("./HGST HMS5C4040BLE640/HGST HMS5C4040BLE640_label_v1.npy")
# train_label = np.load("./HGST HMS5C4040BLE640/train_label.npy")
# label = np.load("./ST8000DM002/ST8000DM002_label_v1.npy")
# train_label = np.load("./ST8000DM002/train_label.npy")
# label = np.load("./ST8000NM0055/ST8000NM0055_label_v1.npy")
# train_label = np.load("./ST8000NM0055/train_label.npy")
label = np.load("./TOSHIBA MQ01ABF050/TOSHIBA MQ01ABF050_label_v1.npy")
train_label = np.load("./TOSHIBA MQ01ABF050/train_label.npy")
label_nums = [0, 0, 0, 0, 0, 0]
train_label_nums = [0] * 6
for i in label:
    label_nums[i - 1] += 1

for j in train_label:
    for k in range(len(j)):
        if j[k] == 1:
            train_label_nums[k] += 1

print("原始数据的标签：")
for n in label_nums:
    print(n, '\t')

print("训练数据的标签：")
for n in train_label_nums:
    print(n, '\t')

# ST4000DM000
# 修改后
# 原始数据的标签：
# 32183
# 63348
# 123467
# 235110
# 418272
# 1286976
# 训练数据的标签：
# 26072
# 26042
# 25957
# 25883
# 25235
# 39969

# WD60EFRX
# 修改后
# 原始数据的标签：
# 1577
# 2981
# 5558
# 9859
# 15730
# 23118
# 训练数据的标签：
# 1326
# 1275
# 1571
# 1720
# 1567
# 1423

# HDS722020ALA330
# 修改后
# 原始数据的标签：
# 2020
# 4004
# 7671
# 14671
# 27090
# 39542
# 训练数据的标签：
# 1782
# 1735
# 2204
# 2614
# 2720
# 2642

# ST12000NM0007
# 原始数据的标签：
# 17792
# 34789
# 67282
# 128322
# 227775
# 360478
# 训练数据的标签：
# 15530
# 15315
# 14925
# 14286
# 12651
# 19456

# HGST HMS5C4040BLE640
# 原始数据的标签：
# 2523
# 4843
# 9145
# 16231
# 28227
# 89912
# 训练数据的标签：
# 2173
# 2096
# 2570
# 3028
# 1106
# 3270

# ST8000DM002
# 原始数据的标签：
# 4384
# 8609
# 16686
# 31816
# 58281
# 211881
# 训练数据的标签：
# 3864
# 3809
# 3695
# 3523
# 3601
# 4770

# ST8000NM0055
# 原始数据的标签：
# 6016
# 11770
# 22887
# 43418
# 78564
# 227714
# 训练数据的标签：
# 5271
# 5200
# 5079
# 6259
# 4897
# 6099
