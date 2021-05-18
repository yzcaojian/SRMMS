from sklearn.linear_model import Ridge
from sklearn.svm import LinearSVC, SVC
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import RFECV, RFE
import numpy as np
from pandas import read_csv

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 采用递归特征消除（RFE）方法进行特征值筛选，选择9个最重要的SMART属性作为特征
@Time : 2021/1/31 16:53
@Author : cao jian
"""

# smart = read_csv('ST4000DM000_v2.csv', header=0)  # header值表示以第几行作为列标题，没有标题则用None
# title = np.array(smart.columns)[2:]  # 取表头
# smart = np.array(smart)  # 取数据
# smart = smart[1:, :]
reader = read_csv('HGST HMS5C4040ALE640_v1.csv', header=0)
title = np.array(reader.columns)[2:]  # 取表头
smart = np.load('HGST HMS5C4040ALE640_data_v1.npy')
label = np.load('HGST HMS5C4040ALE640_label_v1.npy')
# smart = np.load('REF_data.npy')
# label = np.load('REF_label.npy')
print(smart.shape)
feature = smart  # 以全部的数据量作为特征
print(feature.shape)
print(label.shape)

regr = RandomForestRegressor(n_estimators=50, max_depth=14)  # 设置50棵树，树最大深度为14
rfe = RFE(estimator=regr, n_features_to_select=9, step=1)  # estimator是评估器
rfe = rfe.fit(feature, label)
# svc = SVC(kernel="linear", C=1)
# rfe = RFE(estimator=svc, n_features_to_select=9, step=1)
# rfe.fit(feature, label)

print("N_features %s" % rfe.n_features_)  # 保留的特征数
print("Support is %s" % rfe.support_)  # 是否保留
print("Ranking %s" % rfe.ranking_)  # 保留重要程度排名
# print('importance' % rfe.feature_importances_)  # 重要度

# 根据选择的属性，一做打印显示哪些SMART属性值被选择，二决定从data中要删除的列标号
left_col = []
del_col = []
for (support, feature, i) in zip(rfe.support_, title, range(len(title))):
    if support:
        left_col.append(i)
        print(feature, end=' ')
# smart_2_raw smart_3_raw smart_4_raw smart_9_raw smart_12_raw smart_192_raw smart_193_raw smart_196_raw smart_197_raw
# print("Grid Scores %s" % rfe.grid_scores_)  # 交叉验证的分数，grid_scores_[i] 第i个特征子集的CV分数

for i in range(len(title)):
    if i not in left_col:
        del_col.append(i)
smart = np.delete(smart, del_col, axis=1)
print('\n', smart.shape)
np.save('HGST HMS5C4040ALE640_data_v2.npy', smart)
