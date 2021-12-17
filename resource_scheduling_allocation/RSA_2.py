# -*- coding: utf-8 -*-
# @ModuleName: RSA_2
# @Function: I/O负载预测子模块
# @Author: Chen Zhongwei
# @Time: 2021/5/6 15:55

import time
import tensorflow as tf
import numpy as np
import threading
import pandas as pd
from IO_load_prediction_model_training.offline_model_training import lstm
from interface.in_interface import in_interface_impl
from resource_status_display.configuration_checking import configuration_info
from resource_status_display.log_exception_with_suggestions import Warning
import matplotlib.pyplot as plt
import json


# I/O负载预测
def io_load_prediction(io_load_input_queue, io_load_output_queue, save_model_path, average_io_load,
                       warning_message_queue):
    if not io_load_input_queue:  # 输入队列为空，直接返回
        return
    rnn_unit, time_step = [20, 20]
    weights = {
        # 'in': tf.get_variable('in', shape=[input_size, rnn_unit], initializer=init_glorot_normal),
        # 'out': tf.get_variable('out', shape=[rnn_unit, output_size], initializer=init_glorot_normal)
        'in': tf.Variable(tf.random_uniform([1, rnn_unit])),  # maxval=0.125 input_size=2
        'out': tf.Variable(tf.random_uniform([rnn_unit, 1]))  # output_size=1
    }

    biases = {
        'in': tf.Variable(tf.constant(0.1, shape=[rnn_unit, ])),
        'out': tf.Variable(tf.constant(0.1, shape=[1, ]))
    }
    X = tf.placeholder(tf.float32, shape=[None, time_step, 1])
    keep_prob = tf.placeholder('float')
    pred, _, m, mm = lstm(X, weights, biases, 1, rnn_unit, keep_prob)
    saver = tf.train.Saver(max_to_keep=1)

    with open("./resources/txt/mean_and_std.txt", "r", encoding='utf-8') as f:
        mean_and_std_dict = json.load(f)

    with tf.Session() as sess:
        for ip in io_load_input_queue:
            for disk_id in io_load_input_queue[ip]:
                if len(io_load_input_queue[ip][disk_id]) < time_step:
                    continue
                else:
                    save_model_path_disk = './resources/IO_load_prediction_model_training/model/' + ip + '/' + disk_id \
                                           + '/'
                    # 读模型操作比较耗时
                    sess.run(tf.global_variables_initializer())
                    ckpt = tf.train.get_checkpoint_state(save_model_path_disk)  # checkpoint存在的目录
                    if ckpt and ckpt.model_checkpoint_path:
                        saver.restore(sess, ckpt.model_checkpoint_path)  # 自动恢复model_checkpoint_path保存模型一般是最新
                        print("对应硬盘的预测模型存在,恢复该模型")
                    else:
                        ckpt = tf.train.get_checkpoint_state(save_model_path)
                        saver.restore(sess, ckpt.model_checkpoint_path)
                        print('对应硬盘的预测模型不存在,恢复默认模型')

                    # 截取前面time_step个数据
                    data_list = io_load_input_queue[ip][disk_id][:time_step]

                    # 去除前面一个数据
                    del io_load_input_queue[ip][disk_id][0:-19]

                    data_list = np.array(data_list)[:, 0]  # 第二维是时间戳，这里取第一维
                    data_list = data_list.reshape(len(data_list), 1)

                    # 若对应的mean和std不存在，则使用默认值
                    if ip not in mean_and_std_dict:
                        mean_and_std_dict[ip] = {}
                    if disk_id not in mean_and_std_dict[ip]:
                        mean_and_std_dict[ip][disk_id] = []
                    if len(mean_and_std_dict[ip][disk_id]) == 0:
                        mean, std = [[13304.76842105], [4681.6388205]]
                    else:
                        mean, std = mean_and_std_dict[ip][disk_id]

                    # 转化为矩阵
                    mean = np.array(mean)
                    std = np.array(std)

                    # 预测
                    normalized_data_list = (data_list - mean) / std  # 标准化
                    # maxvalue = np.max(data_list, axis=0)
                    prob = sess.run(pred, feed_dict={X: [normalized_data_list], keep_prob: 1})
                    # prob是一个1X1的矩阵 取第一个元素
                    predict = prob.reshape((-1))[0]
                    # 将预测值还原 取整数
                    predict = int(predict * std[0] + mean[0])
                    if predict < 0:
                        predict = 0

                    # 将浮点数类型的时间戳转化为时间元组，并按照X时X分的格式转化为字符串
                    now_time = time.time()
                    # 预测的是为20分钟之后的负载值
                    predict_step = 20 * 60
                    local_time = time.strftime("%H:%M", time.localtime(now_time + predict_step))
                    now_time = time.strftime("%Y{y}%m{m}%d{d}%H:%M", time.localtime(now_time)).format(y='年', m='月',
                                                                                                      d='日')
                    # 将预测值添加到输出队列中
                    if ip not in io_load_output_queue:
                        io_load_output_queue[ip] = {}
                    if disk_id not in io_load_output_queue[ip]:
                        io_load_output_queue[ip][disk_id] = []
                    io_load_output_queue[ip][disk_id].append([predict, local_time])

                    _, averageIO = average_io_load[ip][disk_id]

                    filename = "./resources/txt/judgment_criteria_for_high_IO_load.txt"
                    with open(filename, "r", encoding='utf-8') as f:
                        data = f.read().split()
                        maximum_average_IO_times, maximum_IO_threshold = float(data[1]), float(data[3])

                    # 高于平均负载的maximum_IO_threshold倍或者高于60 * maximum_IO_threshold视作高负载
                    if predict > averageIO * maximum_average_IO_times * 60 or predict >= maximum_IO_threshold * 60:
                        errorID = 2
                        warning = Warning(errorID, now_time, configuration_info.IPtoName(ip), disk_id, [local_time, predict])
                        # IO高负载预警异常消息[02, 事件发生时间, 服务器IP, 硬盘标识, 预测IO到达最大负载量]
                        warning_message_queue.append(warning)
                        # 服务器失联告警信息 to资源状态显示模块
                        in_interface_impl.IN_RSA_RSD(warning)
                        # 预警前端图标闪烁
                        if ip not in in_interface_impl.exception_dict:
                            in_interface_impl.exception_dict[ip] = []
                            in_interface_impl.exception_dict[ip].append(1)
                            in_interface_impl.exception_dict[ip].append({disk_id: 1})
                        else:
                            if disk_id not in in_interface_impl.exception_dict[ip][1]:
                                in_interface_impl.exception_dict[ip][1][disk_id] = 1


class IoLoadPredictionThread(threading.Thread):
    def __init__(self, io_load_input_queue, io_load_output_queue, save_model_path, average_io_load,
                 warning_message_queue):
        threading.Thread.__init__(self)
        self.io_load_input_queue = io_load_input_queue
        self.io_load_output_queue = io_load_output_queue
        self.save_model_path = save_model_path
        self.average_io_load = average_io_load
        self.warning_message_queue = warning_message_queue

    def run(self):
        print("负载预测开始:")
        tf.reset_default_graph()
        io_load_prediction(self.io_load_input_queue, self.io_load_output_queue, self. save_model_path,
                           self.average_io_load, self.warning_message_queue)
        print("负载预测结束:")


# if __name__ == "__main__":
#     f = open('../IO_load_prediction_model_training/data/Financial2_minutes.csv')
#     df = pd.read_csv(f)  # 读入数据
#     data = df.values
#     data = data[:][:, 1]  # 第一维为时间数据，这里取第二维
#     data = data.reshape(len(data), 1)
#     newdata = data
#     for i in range(2, len(data) - 2):
#         for j in range(0, 1):
#             newdata[i][j] = (data[i - 2][j] + data[i - 1][j] + data[i][j] + data[i + 1][j] + data[i + 2][j]) / 5
#     data = newdata
#     data_list = data[100:300]
#     io_load_input_queue = {"123.123.1.1": {"czw": []}}
#     io_load_output_queue = {}
#
#     io_load_input_queue["123.123.1.1"]["czw"] = data_list.tolist()
#
#     while(len(io_load_input_queue["123.123.1.1"]["czw"]) > 19):
#         start_io_load_prediction(io_load_input_queue, io_load_output_queue, [],
#                                  '../IO_load_prediction_model_training/model/Financial2/', {}, [])
#     predict_list = np.array(io_load_output_queue["123.123.1.1"]["czw"])
#
#     # 画图表示结果
#     fig = plt.figure()
#     ax1 = fig.add_subplot(1, 1, 1)
#     ax1.set_xlabel('time/min')
#     ax1.set_ylabel('the amount of data/KB')
#     ax1.set_title('I/O load prediction')
#     x = list(range(len(data)))
#     X = list(range(100, 100 + len(predict_list)))
#     output_size = 1
#     y = [[] for i in range(output_size)]
#     Y = [[] for i in range(output_size)]
#     for i in range(output_size):
#         y[i] = data[:, i]
#         Y[i] = predict_list[:, i]
#     ax1.plot(x, y[0], color='r', label='real')
#     ax1.plot(X, Y[0], color='b', label='predict')
#     plt.legend()
#     plt.show()


# now_time = time.time()
# now_time = time.strftime("%Y{y}%m{m}%d{d} %H:%M", time.localtime(now_time)).format(y='年', m='月', d='日')
# print(now_time)
