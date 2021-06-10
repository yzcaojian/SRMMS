"""
-*- coding: utf-8 -*- 
@Project: SRMMS
@Description: 健康度预测
@Time : 2021/6/4 14:55
@Author : cao jian
"""
import threading
import time


def predict_disk_health_state(disk):
    # disk格式为[diskID, model, smartID, smartData]
    degree = 0
    if disk[1] == "HDS722020ALA330":
        from hard_disk_failure_prediction.HDS722020ALA330.model_learning.model_predict import predict_1st
        from hard_disk_failure_prediction.HDS722020ALA330.model_learning. model_predict_2 import predict_2nd
        degree = predict_1st(disk[3], disk[2])  # smartData, smartID
        if degree == 1:
            degree = predict_2nd(disk[3], disk[2])
    elif disk[1] == "HMS5C4040ALE640":
        from hard_disk_failure_prediction.HMS5C4040ALE640.model_learning.model_predict import predict_1st
        from hard_disk_failure_prediction.HMS5C4040ALE640.model_learning. model_predict_2 import predict_2nd
        degree = predict_1st(disk[3], disk[2])  # smartData, smartID
        if degree == 1:
            degree = predict_2nd(disk[3], disk[2])
    elif disk[1] == "ST4000DM000":
        from hard_disk_failure_prediction.ST4000DM000.model_learning.model_predict import predict_1st
        from hard_disk_failure_prediction.ST4000DM000.model_learning. model_predict_2 import predict_2nd
        degree = predict_1st(disk[3], disk[2])  # smartData, smartID
        if degree == 1:
            degree = predict_2nd(disk[3], disk[2])
    elif disk[1] == "WD30EFRX":
        from hard_disk_failure_prediction.WD30EFRX.model_learning.model_predict import predict_1st
        from hard_disk_failure_prediction.WD30EFRX.model_learning. model_predict_2 import predict_2nd
        degree = predict_1st(disk[3], disk[2])  # smartData, smartID
        if degree == 1:
            degree = predict_2nd(disk[3], disk[2])
    return degree


class DiskHealthPredictionThread(threading.Thread):
    def __init__(self, ip, disk_list, health_degree_dict, hard_disk_failure_prediction_list):
        threading.Thread.__init__(self)
        self.ip = ip
        self.disk_list = disk_list
        self.health_degree_dict = health_degree_dict
        self.hard_disk_failure_prediction_list = hard_disk_failure_prediction_list

    def run(self):
        health_degree = predict_disk_health_state(self.disk_list)
        if self.ip not in self.health_degree_dict:
            self.health_degree_dict[self.ip] = {}  # {ip: {disk_id: degree}, ip :{disk_id: degree}}
        if self.disk_list[0] in self.health_degree_dict[self.ip]:
            if self.health_degree_dict[self.ip][self.disk_list[0]] > health_degree:  # 健康度下降
                timestamp = time.strftime("%Y{y}%m{m}%d{d} %H:%M", time.localtime(time.time())).format(y='年', m='月',
                                                                                                       d='日')
                self.hard_disk_failure_prediction_list.append([self.ip, self.disk_list[0], [health_degree, timestamp]])
        self.health_degree_dict[self.ip][self.disk_list[0]] = health_degree  # disk_id和健康度
        print("硬盘故障预测结束:")


def start_disk_health_prediction(ip, disk_list, health_degree_dict, hard_disk_failure_prediction_list):
    mythread = DiskHealthPredictionThread(ip, disk_list, health_degree_dict, hard_disk_failure_prediction_list)
    mythread.start()
