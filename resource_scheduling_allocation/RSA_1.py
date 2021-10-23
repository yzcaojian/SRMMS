# -*- coding: utf-8 -*-
# @ModuleName: RSA_1
# @Function: 预测模型训练子模块
# @Author: Chen Zhongwei
# @Time: 2021/5/6 15:53

import tensorflow as tf
import numpy as np
import pandas as pd
from IO_load_prediction_model_training.offline_model_training import lstm
import threading


# 线上模型训练
def online_model_training(io_load_input_queue, mean_and_std, save_model):
    if not io_load_input_queue:  # 输入队列为空，直接返回
        return
    # for ip in io_load_input_queue:
    #     for disk_id in io_load_input_queue[ip]:
    #         if len(io_load_input_queue[ip][disk_id]) % 60 != 0:  # 每小时训练一次
    #             return

    rnn_unit, batch_size, time_step, predict_step = [20, 25, 20, 20]
    save_model_path, save_model_name = save_model
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
    Y = tf.placeholder(tf.float32, shape=[None, 1])
    keep_prob = tf.placeholder('float')
    pred, _, m, mm = lstm(X, weights, biases, 1, rnn_unit, keep_prob)
    lr = 0.001
    # 损失函数
    loss = tf.reduce_mean(tf.square(tf.reshape(pred, [-1, 1]) - tf.reshape(Y, [-1, 1])))
    train_op = tf.train.AdamOptimizer(lr).minimize(loss)

    saver = tf.train.Saver(max_to_keep=1)

    with tf.Session() as sess:
        for ip in io_load_input_queue:
            save_model_path_ip = '../IO_load_prediction_model_training/model/' + ip + '/'
            # 读模型操作比较耗时
            sess.run(tf.global_variables_initializer())
            ckpt = tf.train.get_checkpoint_state(save_model_path_ip)  # checkpoint存在的目录
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)  # 自动恢复model_checkpoint_path保存模型一般是最新
                print("对应的服务器预测模型存在,恢复该模型")
            else:
                ckpt = tf.train.get_checkpoint_state(save_model_path)
                saver.restore(sess, ckpt.model_checkpoint_path)
                print('对应的服务器预测模型不存在,恢复默认模型')

            for disk_id in io_load_input_queue[ip]:
                if len(io_load_input_queue[ip][disk_id]) < 300:  # 小于300不进行训练
                    continue
                data_list = io_load_input_queue[ip][disk_id][:]  # 切片复制
                io_load_input_queue[ip][disk_id].clear()  # 将列表清空
                data_list = np.array(data_list)[:, 0]  # 第二维是时间戳，这里取第一维
                data_list = data_list.reshape(len(data_list), 1)

                # 更改mean和std
                mean, std = np.mean(data_list, axis=0), np.std(data_list, axis=0)
                if mean_and_std:  # 不为空,清空列表
                    mean_and_std.clear()
                mean_and_std.append(mean)
                mean_and_std.append(std)

                # 转化为矩阵
                mean = np.array(mean)
                std = np.array(std)

                normalized_data_list = (data_list - mean) / std  # 标准化

                batch_index = []
                train_x, train_y = [], []  # 训练集
                print('训练集大小:', len(normalized_data_list) - time_step - (predict_step - 1))
                for i in range(len(normalized_data_list) - time_step - (predict_step - 1)):
                    if i % batch_size == 0:
                        batch_index.append(i)
                    x = normalized_data_list[i:i + time_step]
                    y = normalized_data_list[i + time_step + (predict_step - 1)]
                    train_x.append(x.tolist())
                    train_y.append(y.tolist())
                batch_index.append((len(normalized_data_list) - time_step - (predict_step - 1)))

                # 重复训练
                for i in range(3000):
                    for step in range(len(batch_index) - 1):
                        _, loss_, M, MM = sess.run([train_op, loss, m, mm],
                                                   feed_dict={X: train_x[batch_index[step]:batch_index[step + 1]],
                                                              Y: train_y[batch_index[step]:batch_index[step + 1]],
                                                              keep_prob: 1})
                    print(i, loss_)
                # 将模型保存在对应的服务器文件夹中
                saver.save(sess, save_model_path_ip + save_model_name)  # 保存模型


def io_second_to_io_minute(ip, io_load_input_queue, io_load_input_queue_minute):
    for disk_id in io_load_input_queue[ip]:
        if len(io_load_input_queue[ip][disk_id]) < 60:
            continue
        total_io = 0
        total_time = 0
        # 取前面60个数据
        for disk_io, time_stamp in io_load_input_queue[ip][disk_id][:60]:
            total_io += disk_io
            total_time += time_stamp
        if ip not in io_load_input_queue_minute:
            io_load_input_queue_minute[ip] = {}
        if disk_id not in io_load_input_queue_minute[ip]:
            io_load_input_queue_minute[ip][disk_id] = []
        # //整除  时间需要取平均值
        # for i in range(10):
        io_load_input_queue_minute[ip][disk_id].append([round(total_io, 1), total_time // 60])


class OnlineModelTrainingThread(threading.Thread):
    def __init__(self, io_load_input_queue, mean_and_std, save_model):
        threading.Thread.__init__(self)
        self.io_load_input_queue = io_load_input_queue
        self.mean_and_std = mean_and_std
        self.save_model = save_model

    def run(self):
        print("动态训练开始:")
        tf.reset_default_graph()
        online_model_training(self.io_load_input_queue, self.mean_and_std, self.save_model)
        print("动态训练结束:")

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
#     data_list = data[:int(len(data) * 0.9)]
#     io_load_input_queue = {"123.123.1.1": {"czw": []}}
#
#     io_load_input_queue["123.123.1.1"]["czw"] = data_list.tolist()
#     Mean_and_std = [[13304.76842105], [4681.6388205]]
#     for i in range(2):
        # tf.reset_default_graph()
        # thread1 = OnlineModelTrainingThread(io_load_input_queue, Mean_and_std,
        #                                     ['../IO_load_prediction_model_training/model/Financial2/', 'Model'])
        # thread1.start()
        # thread1.join()
#         # online_model_training(io_load_input_queue, Mean_and_std,
#         #                       ['../IO_load_prediction_model_training/model/Financial2/', 'Model'])
#         start_online_model_training(io_load_input_queue, Mean_and_std,
#                                     ['../IO_load_prediction_model_training/model/Financial2/', 'Model'])


