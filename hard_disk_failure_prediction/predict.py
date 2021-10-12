import threading
import time
import numpy as np
"""
-*- coding: utf-8 -*- 
@Project: SRMMS
@Description: 健康度预测
@Time : 2021/6/4 14:55
@Author : cao jian
"""


def predict_disk_health_state(disk):
    # disk格式为[diskID, model, smartID, smartData]
    degree = 0
    if disk[1] == "HDS722020ALA330":
        from hard_disk_failure_prediction.HDS722020ALA330.model_learning.model_predict import predict_1st
        from hard_disk_failure_prediction.HDS722020ALA330.model_learning. model_predict_2 import predict_2nd
        degree = predict_1st(np.array(disk[3]), disk[2])  # smartData, smartID
        if degree == 1:
            degree = predict_2nd(np.array(disk[3]), disk[2])
    elif disk[1] == "HMS5C4040ALE640":
        from hard_disk_failure_prediction.HMS5C4040ALE640.model_learning.model_predict import predict_1st
        from hard_disk_failure_prediction.HMS5C4040ALE640.model_learning. model_predict_2 import predict_2nd
        degree = predict_1st(np.array(disk[3]), disk[2])  # smartData, smartID
        if degree == 1:
            degree = predict_2nd(np.array(disk[3]), disk[2])
    elif disk[1] == "ST4000DM000":
        from hard_disk_failure_prediction.ST4000DM000.model_learning.model_predict import predict_1st
        from hard_disk_failure_prediction.ST4000DM000.model_learning. model_predict_2 import predict_2nd
        degree = predict_1st(np.array(disk[3]), disk[2])  # smartData, smartID
        if degree == 1:
            degree = predict_2nd(np.array(disk[3]), disk[2])
    elif disk[1] == "WD30EFRX":
        from hard_disk_failure_prediction.WD30EFRX.model_learning.model_predict import predict_1st
        from hard_disk_failure_prediction.WD30EFRX.model_learning. model_predict_2 import predict_2nd
        degree = predict_1st(np.array(disk[3]), disk[2])  # smartData, smartID
        if degree == 1:
            degree = predict_2nd(np.array(disk[3]), disk[2])
    return degree


class DiskHealthPredictionThread(threading.Thread):
    def __init__(self, smart_dict, health_degree_dict, hard_disk_failure_prediction_list):
        threading.Thread.__init__(self)
        self.smart_dict = smart_dict
        self.health_degree_dict = health_degree_dict
        self.hard_disk_failure_prediction_list = hard_disk_failure_prediction_list

    def run(self):
        print("硬盘故障预测开始:")
        for ip in self.smart_dict:
            for disk in self.smart_dict[ip]:
                if len(disk[3]) <= 19:  # SMART数据不够预测
                    continue
                else:  # SMART数据足够预测
                    disk_list = disk[:]  # 切片复制
                    disk_list[3] = disk[3][:20]
                    del disk[3][0:-19]  # 只需要保留20天的历史smart数据即可，多余进行删除

                    health_degree = predict_disk_health_state(disk_list)
                    if ip not in self.health_degree_dict:
                        self.health_degree_dict[ip] = {}  # {ip: {disk_id: degree}, ip :{disk_id: degree}}
                    if disk_list[0] not in self.health_degree_dict[ip]:
                        self.health_degree_dict[ip][disk_list[0]] = 6

                    if self.health_degree_dict[ip][disk_list[0]] > health_degree:  # 健康度下降
                        timestamp = time.strftime("%Y{y}%m{m}%d{d} %H:%M", time.localtime(time.time())).\
                            format(y='年', m='月', d='日')
                        self.hard_disk_failure_prediction_list.append([ip, disk_list[0], [health_degree, timestamp]])
                    self.health_degree_dict[ip][disk_list[0]] = health_degree  # disk_id和健康度

        print("硬盘故障预测结束:")

