"""
-*- coding: utf-8 -*- 
@Project: SRMMS
@Description: 健康度预测
@Time : 2021/6/4 14:55
@Author : cao jian
"""

def predict_disk_health_state(disk):
    # disk格式为[diskID, model, smartID, smartData]
    global degree
    if disk[0] == "HDS722020ALA330":
        from hard_disk_failure_prediction.HDS722020ALA330.model_learning.model_predict import predict_1st
        from hard_disk_failure_prediction.HDS722020ALA330.model_learning. model_predict_2 import predict_2nd
        degree = predict_1st(disk[3], disk[2])  # smartData, smartID
        if degree == 1:
            degree = predict_2nd(disk[3], disk[2])
    elif disk[0] == "HMS5C4040ALE640":
        from hard_disk_failure_prediction.HMS5C4040ALE640.model_learning.model_predict import predict_1st
        from hard_disk_failure_prediction.HMS5C4040ALE640.model_learning. model_predict_2 import predict_2nd
        degree = predict_1st(disk[3], disk[2])  # smartData, smartID
        if degree == 1:
            degree = predict_2nd(disk[3], disk[2])
    elif disk[0] == "ST4000DM000":
        from hard_disk_failure_prediction.ST4000DM000.model_learning.model_predict import predict_1st
        from hard_disk_failure_prediction.ST4000DM000.model_learning. model_predict_2 import predict_2nd
        degree = predict_1st(disk[3], disk[2])  # smartData, smartID
        if degree == 1:
            degree = predict_2nd(disk[3], disk[2])
    elif disk[0] == "WD30EFRX":
        from hard_disk_failure_prediction.WD30EFRX.model_learning.model_predict import predict_1st
        from hard_disk_failure_prediction.WD30EFRX.model_learning. model_predict_2 import predict_2nd
        degree = predict_1st(disk[3], disk[2])  # smartData, smartID
        if degree == 1:
            degree = predict_2nd(disk[3], disk[2])
    return degree
