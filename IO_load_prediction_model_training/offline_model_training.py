# -*- coding: utf-8 -*-
# @ModuleName: offline_model_training
# @Function: 
# @Author: Chen Zhongwei
# @Time: 2021/5/19 16:09

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.metrics import *
from math import sqrt
import pickle


# 获取训练集
def get_train_data(data, batch_size, time_step, train_end, predict_step, train_begin=0):
    batch_index = []
    data_train = data[train_begin:train_end]
    # normalized_train_data = (data_train-np.mean(data_train, axis=0)) / np.std(data_train, axis=0)  # 标准化

    min_value = np.min(data, axis=0)
    max_value = np.max(data, axis=0)
    normalized_train_data = (data_train - min_value) / (max_value - min_value)

    # maxvalue = np.max(data_train, axis=0)
    # normalized_train_data = data_train / maxvalue

    train_x, train_y = [], []   # 训练集
    print('训练集大小:', len(normalized_train_data) - time_step - (predict_step-1))
    for i in range(len(normalized_train_data) - time_step - (predict_step-1)):
       if i % batch_size == 0:
           batch_index.append(i)
       x = normalized_train_data[i:i+time_step]
       y = normalized_train_data[i+time_step+(predict_step-1)]
       train_x.append(x.tolist())
       train_y.append(y.tolist())
    batch_index.append((len(normalized_train_data)-time_step-(predict_step-1)))
    # 返回值: 批序号列表、训练值X、训练值Y
    return batch_index, train_x, train_y


# 获取测试集
def get_test_data(data, time_step, predict_step, test_begin, test_end=-1):
    if test_end == -1:
        data_test = data[test_begin:]
    else:
        data_test = data[test_begin:test_end]

    # mean = np.mean(data, axis=0)
    # std = np.std(data, axis=0)
    # normalized_test_data = (data_test-mean) / std  # 标准化

    min_value = np.min(data, axis=0)
    max_value = np.max(data, axis=0)
    normalized_test_data = (data_test - min_value) / (max_value - min_value)

    # print("mean:", mean, "std:", std)
    # normalized_test_data = data_test / maxvalue
    # size=(len(normalized_test_data)+time_step-1)//time_step
    test_x, test_y = [], []
    print('测试集大小:', len(normalized_test_data)-time_step-(predict_step-1))
    for i in range(len(normalized_test_data)-time_step-(predict_step-1)):
       x = normalized_test_data[i:i+time_step]
       y = normalized_test_data[i+time_step+(predict_step-1)]
       test_x.append(x.tolist())
       test_y.append(y)
    print('get_test_data x', np.array(test_x).shape)
    # print(np.array(test_x))
    print('get_test_data y', np.array(test_y).shape)
    # print(np.array(test_y))
    # 返回值: 最小值、最大值、测试值X、测试值Y
    return min_value, max_value, test_x, test_y


# ——————————————————定义网络——————————————————
def lstm(X, weights, biases, input_size, rnn_unit, keep_prob):
    batch_size = tf.shape(X)[0]
    time_step = tf.shape(X)[1]
    w_in = weights['in']  # tf.Variable(tf.random_uniform([input_size, rnn_unit]))
    b_in = biases['in']  # tf.Variable(tf.constant(0.1, shape=[rnn_unit, ]))

    input = tf.reshape(X, [-1, input_size])  # 需要将tensor转成2维进行计算，计算后的结果作为隐藏层的输入
    input_rnn = tf.matmul(input, w_in) + b_in
    input_rnn = tf.reshape(input_rnn, [-1, time_step, rnn_unit])  # 将tensor转成3维，作为lstm cell的输入
    cell = tf.nn.rnn_cell.BasicLSTMCell(rnn_unit)  # reuse = sign
    init_state = cell.zero_state(batch_size, dtype=tf.float32)
    # output_rnn是记录lstm每个输出节点的结果，final_states是最后一个cell的结果
    output_rnn, final_states = tf.nn.dynamic_rnn(cell, input_rnn, initial_state=init_state, dtype=tf.float32)
    m = output_rnn
    output = tf.reshape(output_rnn, [-1, rnn_unit])  # 作为输出层的输入
    index = tf.range(0, batch_size) * time_step + (time_step - 1)  # 只取最后的输出
    output = tf.gather(output, index)  # 按照index取数据
    mm = output
    w_out = weights['out']  # tf.Variable(tf.random_uniform([rnn_unit, output_size])
    b_out = biases['out']  # tf.Variable(tf.constant(0.1, shape=[output_size, ])
    pred0 = tf.matmul(output, w_out) + b_out
    pred = tf.nn.dropout(pred0, keep_prob)
    return pred, final_states, m, mm


# ——————————————————训练模型—————————————————
def train_lstm(data, input_size, output_size, lr, train_time, rnn_unit, weights, biases, train_end,
               batch_size, time_step, predict_step, kp, save_model, train_begin=0):
    X = tf.placeholder(tf.float32, shape=[None, time_step, input_size])
    Y = tf.placeholder(tf.float32, shape=[None, output_size])
    keep_prob = tf.placeholder('float')
    batch_index, train_x, train_y = get_train_data(data, batch_size, time_step, train_end, predict_step, train_begin)
    # train_y = np.array(train_y)[:, 1:input_size].tolist()  # 如果输入加上时间维度，这里就需要加上
    print(np.array(train_x).shape)
    print(np.array(train_y).shape)
    pred, _, m, mm = lstm(X, weights, biases, input_size, rnn_unit, keep_prob)
    # 损失函数
    loss = tf.reduce_mean(tf.square(tf.reshape(pred, [-1, output_size]) - tf.reshape(Y, [-1, output_size])))
    train_op = tf.train.AdamOptimizer(lr).minimize(loss)

    saver = tf.train.Saver(max_to_keep=1)

    save_model_path, save_model_name = save_model
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # saver.save(sess, './save/MyModel')
        ckpt = tf.train.get_checkpoint_state(save_model_path)  # checkpoint存在的目录
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)  # 自动恢复model_checkpoint_path保存模型一般是最新
            print("Model restored...")
        else:
            print('No Model')
        loss_list = []
        # 重复训练
        for i in range(train_time):
            for step in range(len(batch_index)-1):
                _, loss_, M, MM = sess.run([train_op, loss, m, mm],
                                           feed_dict={X: train_x[batch_index[step]:batch_index[step + 1]],
                                                      Y: train_y[batch_index[step]:batch_index[step+1]], keep_prob: kp})
            print(i, loss_)
            loss_list.append(loss_)
            if loss_ < 1e-4:
                break
        saver.save(sess, save_model_path + save_model_name)  # 保存模型

        # 预测
        min_value, max_value, test_x, test_y = get_test_data(data, time_step, predict_step, train_end - time_step-(predict_step-1))
        # test_y = np.array(test_y)[:, 1:input_size].tolist()  # 如果输入加上时间维度，这里就需要加上
        test_predict = []
        for step in range(len(test_x)):
            prob = sess.run(pred, feed_dict={X: [test_x[step]], keep_prob: 1})
            predict = prob.reshape((-1))
            test_predict.extend(predict)

        print('test_predict:', np.array(test_predict).shape)
        print('truedata:', np.array(test_y).shape)
        test_predict = np.array(test_predict).reshape(-1, output_size)
        print('test_predict:', test_predict.shape)
        print('test_y:', np.array(test_y).shape)
        test_y = np.array(test_y)
        for i in range(output_size):
            test_y[:, i] = test_y[:, i] * (max_value[i] - min_value[i]) + min_value[i]
            test_predict[:, i] = test_predict[:, i] * (max_value[i] - min_value[i]) + min_value[i]

        for item in test_predict:
            if item[0] < 0:
                item[0] = 0

        # 预测误差
        predict_y = test_predict.reshape(-1, )
        true_y = test_y.reshape(-1, )
        mae = mean_absolute_error(test_y, test_predict)/1024
        mse = mean_squared_error(test_y, test_predict)
        rmse = sqrt(mse)
        r_square = r2_score(test_y, test_predict,multioutput="raw_values")
        r_square1 = r2_score(test_y, test_predict)

        print(('平均绝对误差(mae): %dMB' % mae),
              (mean_absolute_error(test_y, test_predict, multioutput="raw_values") / 1024).astype(np.int))
        aa = test_y.sum() / (len(true_y) * 1024)

        print('实际值的平均值：%dMB' % aa)
        print('误差百分比：%.2f' % (100 * mae/aa)+'%')
        print('均方误差: %d' % mse)
        print('均方根误差: %d' % rmse)
        # print('R_square: %.6f' % r_square)
        print('r2_score:')  # 越接近1表示预测值和实际值越接近
        print(r_square)
        print(r_square1)

        # 画图表示结果
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1)
        ax1.set_xlabel('time/min')
        ax1.set_ylabel('the amount of data/KB')
        ax1.set_title('I/O load prediction')
        x = list(range(len(data)))
        X = list(range(train_end, train_end + len(test_predict)))
        y = [[] for i in range(output_size)]
        Y = [[] for i in range(output_size)]
        for i in range(output_size):
            y[i] = data[:, i]
            Y[i] = test_predict[:, i]
        ax1.plot(x, y[0], color='r', label='real')
        ax1.plot(X, Y[0], color='b', label='predict')
        plt.legend()
        plt.show()

        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1)
        ax1.set_xlabel('iteration')
        ax1.set_ylabel('loss')
        ax1.set_title('I/O load prediction loss')
        x = list(range(len(loss_list)))
        y = loss_list
        ax1.plot(x, y, color='r', label='loss')
        plt.legend()
        plt.show()


def io_load_prediction(data, input_size, output_size, rnn_unit, weights, biases,
                       time_step, predict_step, save_model_path, pred_begin, pred_end):
    X = tf.placeholder(tf.float32, shape=[None, time_step, input_size])
    keep_prob = tf.placeholder('float')
    pred, _, m, mm = lstm(X, weights, biases, input_size, rnn_unit, keep_prob)

    saver = tf.train.Saver(max_to_keep=1)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        # saver.save(sess, './save/MyModel')
        ckpt = tf.train.get_checkpoint_state(save_model_path)  # checkpoint存在的目录
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)  # 自动恢复model_checkpoint_path保存模型一般是最新
            print("Model restored...")
        else:
            print('No Model')

        # 预测
        min_value, max_value, test_x, test_y = get_test_data(data, time_step,
                                                            predict_step, pred_begin - time_step-(predict_step-1), pred_end)
        # test_y = np.array(test_y)[:, 1:input_size].tolist()  # 如果输入加上时间维度，这里就需要加上
        test_predict = []
        # print(test_x)
        for step in range(len(test_x)):
            prob = sess.run(pred, feed_dict={X: [test_x[step]], keep_prob: 1})
            predict = prob.reshape((-1))
            # print("predict:", predict)
            test_predict.extend(predict)

        print('test_predict:', np.array(test_predict).shape)
        print('truedata:', np.array(test_y).shape)
        test_predict = np.array(test_predict).reshape(-1, output_size)
        print('test_predict:', test_predict.shape)
        print('test_y:', np.array(test_y).shape)

        test_y = np.array(test_y)
        for i in range(output_size):
            test_y[:, i] = test_y[:, i] * (max_value[i] - min_value[i]) + min_value[i]
            test_predict[:, i] = test_predict[:, i] * (max_value[i] - min_value[i]) + min_value[i]

        for item in test_predict:
            if item[0] < 0:
                item[0] = 0

        # 预测误差
        true_y = test_y.reshape(-1, )
        mae = mean_absolute_error(test_y, test_predict) / 1024
        mse = mean_squared_error(test_y, test_predict)
        rmse = sqrt(mse)
        r_square = r2_score(test_y, test_predict, multioutput="raw_values")
        r_square1 = r2_score(test_y, test_predict)

        print(('平均绝对误差(mae): %dMB' % mae),
              (mean_absolute_error(test_y, test_predict, multioutput="raw_values") / 1024).astype(np.int))
        aa = test_y.sum() / (len(true_y) * 1024)

        print('实际值的平均值：%dMB' % aa)
        print('误差百分比：%.2f' % (100 * mae / aa) + '%')
        print('均方误差: %d' % mse)
        print('均方根误差: %d' % rmse)
        # print('R_square: %.6f' % r_square)
        print('r2_score:')  # 越接近1表示预测值和实际值越接近
        print(r_square)
        print(r_square1)

        # 画图表示结果
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1)
        ax1.set_xlabel('time/min')
        ax1.set_ylabel('the amount of data/KB')
        ax1.set_title('I/O load prediction')
        x = list(range(len(data)))
        X = list(range(pred_begin, pred_begin + len(test_predict)))
        y = [[] for i in range(output_size)]
        Y = [[] for i in range(output_size)]
        for i in range(output_size):
            y[i] = data[:, i]
            Y[i] = test_predict[:, i]
        ax1.plot(x, y[0], color='r', label='real')
        ax1.plot(X, Y[0], color='b', label='predict')
        plt.legend()
        plt.show()

