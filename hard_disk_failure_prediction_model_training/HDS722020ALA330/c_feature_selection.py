from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import RFECV, RFE
import numpy as np
from pandas import read_csv

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 采用递归特征消除（RFE）方法进行特征值筛选，选择9个最重要的SMART属性作为特征
@Time : 2021/5/24 20:06
@Author : cao jian
"""

reader = read_csv('HDS722020ALA330_v1.csv', header=0)
title = np.array(reader.columns)[2:]  # 取表头
smart = np.load('HDS722020ALA330_data_v1.npy')
label = np.load('HDS722020ALA330_label_v1.npy')
# smart = np.load('feature_selection_data_2.npy')
# label = np.load('feature_selection_label_2.npy')
# true_smart = np.load('HDS722020ALA330_data_2_v1.npy')
feature = smart  # 以全部数据量作为特征进行选择
print(feature.shape)  # (94998, 17)  一级  (2222, 17) 二级
print(label.shape)  # (94998,)

regr = RandomForestRegressor(n_estimators=50, max_depth=14)  # 设置50棵树，树最大深度为14
rfe = RFE(estimator=regr, n_features_to_select=9, step=1)  # estimator是评估器
rfe = rfe.fit(feature, label)

print("N_features %s" % rfe.n_features_)  # 保留的特征数
print("Support is %s" % rfe.support_)  # 是否保留
print("Ranking %s" % rfe.ranking_)  # 保留重要程度排名

# 根据选择的属性，一做打印显示哪些SMART属性值被选择，二决定从data中要删除的列标号
left_col = []
del_col = []
for (support, feature, i) in zip(rfe.support_, title, range(len(title))):
    if support:
        left_col.append(i)
        print(feature, end=' ')
# 一级健康度
# smart_3_raw smart_4_raw smart_5_raw smart_9_raw smart_12_raw smart_192_raw smart_193_raw smart_196_raw smart_197_raw
# 二级健康度
# smart_1_raw smart_3_raw smart_4_raw smart_9_raw smart_192_raw smart_193_raw smart_194_raw smart_196_raw smart_197_raw

for i in range(len(title)):
    if i not in left_col:
        del_col.append(i)
smart = np.delete(smart, del_col, axis=1)
print('\n', smart.shape)
np.save('HDS722020ALA330_data_v2.npy', smart)

# for i in range(len(title)):
#     if i not in left_col:
#         del_col.append(i)
# true_smart = np.delete(true_smart, del_col, axis=1)
# print('\n', true_smart.shape)  # (6024, 9)
# np.save('HDS722020ALA330_data_2_v2.npy', true_smart)
