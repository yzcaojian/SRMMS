# -*- coding: utf-8 -*-
# @ModuleName: main
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/5/19 16:17

import pandas as pd
import tensorflow as tf
import time
from IO_load_prediction_model_training.offline_model_training import train_lstm, io_load_prediction

if __name__ == "__main__":
    input_size = 1  # 输入维度
    output_size = 1  # 输出维度
    rnn_unit = 20  # 隐藏层节点
    # lr = 0.00000001  # 学习率
    lr = 0.001
    batch_size = 25  # 每次训练的一个批次的大小
    time_step = 20  # 前time_step步来预测下一步
    predict_step = 20  # 预测predict_step分钟后的负载
    kp = 1  # dropout保留节点的比例
    smooth = 1  # 为1则在时间维度上平滑数据
    train_time = 0  # 所有数据的训练轮次
    filename = './data/Financial2_minutes.csv'
    save_model_path = './model/default_model/'  # checkpoint存在的目录
    save_model_name = 'Model'  # saver.save(sess, './save/MyModel') 保存模型

    f = open(filename)
    df = pd.read_csv(f)  # 读入数据
    data = df.values
    data = data[:][:, 1]  # 第一维为时间数据，这里取第二维
    data = data.reshape(len(data), 1)
    # data = data.astype(np.int)
    # train_end = int(len(data) * 0.9)
    train_end = 40
    train_begin = 0
    pred_begin = 40
    pred_end = (len(data))

    if smooth == 1:  # 平滑数据
        newdata = data
        for i in range(2, len(data) - 2):
            for j in range(0, 1):
                newdata[i][j] = (data[i - 2][j] + data[i - 1][j] + data[i][j] + data[i + 1][j] + data[i + 2][j]) / 5
        data = newdata

    # ——————————————————定义神经网络变量——————————————————
    # 输入层、输出层权重、偏置

    # random_normal
    # random_uniform
    # truncated_normal
    init_orthogonal = tf.orthogonal_initializer(gain=1.0, seed=None, dtype=tf.float32)
    init_glorot_uniform = tf.glorot_uniform_initializer()
    init_glorot_normal = tf.glorot_normal_initializer()

    weights = {
        # 'in': tf.get_variable('in', shape=[input_size, rnn_unit], initializer=init_glorot_normal),
        # 'out': tf.get_variable('out', shape=[rnn_unit, output_size], initializer=init_glorot_normal)
        'in': tf.Variable(tf.random_uniform([input_size, rnn_unit])),  # maxval=0.125
        'out': tf.Variable(tf.random_uniform([rnn_unit, output_size]))
    }

    biases = {
        'in': tf.Variable(tf.constant(0.1, shape=[rnn_unit, ])),
        'out': tf.Variable(tf.constant(0.1, shape=[output_size, ]))
    }
    t0 = time.time()
    # train_lstm(data, input_size, output_size, lr, train_time, rnn_unit,
    #            weights, biases, train_end, batch_size, time_step, predict_step, kp,
    #            [save_model_path, save_model_name], train_begin)
    # tf.reset_default_graph()
    io_load_prediction(data, input_size, output_size, rnn_unit, weights, biases, time_step, predict_step, save_model_path, pred_begin, pred_end)
    t1 = time.time()
    print("时间:%.4fs" % (t1 - t0))
