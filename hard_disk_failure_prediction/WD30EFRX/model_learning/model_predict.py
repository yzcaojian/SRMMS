import tensorflow as tf
import numpy as np

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 一级健康度预测
@Time : 2021/5/24 16:19
@Author : cao jian
"""

# Parameters
n_input = 9
n_steps = 20
n_hidden = 128
n_classes = 6
# classes = ["R1", "R2", "R3", "R4", "R5", "R6"]
classes = [1, 2, 3, 4, 5, 6]


def mulitGRU(x):
    # Define weights
    weights = {
        'in': tf.Variable(tf.random_uniform([n_input, n_hidden])),
        'out': tf.Variable(tf.random.normal([n_hidden, n_classes])),
    }
    biases = {
        'in': tf.Variable(tf.random_uniform([n_hidden])),
        'out': tf.Variable(tf.random.normal([n_classes])),
    }

    x = tf.unstack(x, num=n_steps, axis=1)

    # 可以看做3个隐藏层
    stacked_rnn = []
    for i in range(2):
        stacked_rnn.append(tf.contrib.rnn.GRUCell(num_units=n_hidden))

        # 多层RNN的实现 例如cells=[cell1,cell2]，则表示一共有两层，数据经过cell1后还要经过cell2
    grucell = tf.contrib.rnn.MultiRNNCell(cells=stacked_rnn)
    # 静态rnn函数传入的是一个张量list  每一个元素都是一个(batch_size,n_input)大小的张量
    outputs, states = tf.contrib.rnn.static_rnn(cell=grucell, inputs=x, dtype=tf.float32)

    # 输出层
    outputs = outputs[-1]
    output = tf.matmul(outputs, weights['out']) + biases['out']
    return output


def predict_1st(smart_data, smart_id):
    tf.reset_default_graph()
    # 将SAMRT数据按照训练集同样的方式裁剪选择九个特征：1、3、4、9、12、192、193、194、197
    temp = [1, 3, 4, 9, 12, 192, 193, 194, 197]
    index = 0
    delete_col = []
    for i in range(len(smart_id)):
        if index > 8:
            # 将剩余的删除列加入col，剩余的smart_id不会等于temp[index]
            index -= 1
        if smart_id[i] != temp[index]:
            delete_col.append(i)
        else:
            index += 1
    smart_data_ = np.delete(smart_data, delete_col, axis=1)
    if len(smart_data_[0]) != 9:
        return -1
    # 根据提前准备好的训练集中最大最小值进行数据归一化
    smart_data = smart_data_  # 用于二级健康度预测
    smart_data_ = smart_data_[np.newaxis, :, :]
    smart_data_ = smart_data_.astype(np.float32)
    smart_max = [68186, 7025, 86, 40223, 86, 63, 743480, 39, 960]
    smart_min = [0, 0, 1, 6, 1, 0, 0, 14, 0]
    for i in range(len(smart_max)):
        for j in range(smart_data_.shape[1]):
            if smart_data_[0][j][i] >= smart_max[i]:
                smart_data_[0][j][i] = 1
            elif smart_data_[0][j][i] <= smart_min[i]:
                smart_data_[0][j][i] = 0
            else:
                smart_data_[0][j][i] = float((smart_data_[0][j][i] - smart_min[i]) / (smart_max[i] - smart_min[i]))
    # print(smart_data)

    # 数据通过GRU网络计算
    x = tf.compat.v1.placeholder(dtype=tf.float32, shape=[None, 20, 9])
    pred = mulitGRU(x)

    saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(), max_to_keep=15)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # 先加载图和参数变量
        # saver = tf.train.import_meta_graph('./model/hdd_GRU_model.ckpt.meta')  # 不能加这一步
        saver.restore(sess,
                      tf.train.latest_checkpoint('./resources/hard_disk_failure_prediction/WD30EFRX/model_learning/model/'))

        prediction = sess.run(pred, feed_dict={x: smart_data_})
        print(prediction)
        # print(prediction.shape)  # 结果是二维数组
        print(np.max(prediction, axis=1))  # 概率最大的健康度预测结果
        for i in range(len(prediction[0])):
            if prediction[0][i] == np.max(prediction, axis=1):
                return classes[i]


# 预测数据
pre1 = [[68164, 6216, 38, 9280, 38, 9, 28, 26, 0], [68164, 6216, 38, 9304, 38, 9, 28, 26, 0],
        [68164, 6216, 38, 9328, 38, 9, 28, 26, 0],
        [68164, 6216, 38, 9353, 38, 9, 28, 26, 0], [68164, 6216, 38, 9376, 38, 9, 28, 25, 0],
        [68164, 6216, 38, 9400, 38, 9, 28, 25, 0],
        [68164, 6216, 38, 9424, 38, 9, 28, 25, 0], [68164, 6216, 38, 9448, 38, 9, 28, 24, 0],
        [68166, 6216, 38, 9472, 38, 9, 28, 26, 0],
        [68171, 6216, 38, 9496, 38, 9, 28, 24, 0], [68171, 6216, 38, 9520, 38, 9, 28, 24, 0],
        [68178, 6216, 38, 9544, 38, 9, 28, 23, 0],
        [68178, 6216, 38, 9568, 38, 9, 28, 24, 0], [68178, 6216, 38, 9592, 38, 9, 28, 24, 0],
        [68178, 6216, 38, 9616, 38, 9, 28, 24, 0],
        [68180, 6216, 38, 9640, 38, 9, 28, 26, 0], [68180, 6216, 38, 9664, 38, 9, 28, 24, 0],
        [68180, 6216, 38, 9688, 38, 9, 28, 23, 0],
        [68180, 6216, 38, 9712, 38, 9, 28, 25, 0], [68182, 6216, 38, 9736, 38, 9, 28, 26, 0]]  # R1
pre2 = [[38, 6158, 29, 9474, 26, 9, 19, 30, 1], [38, 6158, 29, 9498, 26, 9, 19, 34, 1],
        [38, 6158, 29, 9521, 26, 9, 19, 34, 1],
        [38, 6158, 29, 9546, 26, 9, 19, 32, 1], [38, 6158, 29, 9570, 26, 9, 19, 33, 1],
        [38, 6158, 29, 9594, 26, 9, 19, 33, 1],
        [38, 6158, 29, 9618, 26, 9, 19, 33, 1], [38, 6158, 29, 9642, 26, 9, 19, 33, 1],
        [38, 6158, 29, 9665, 26, 9, 19, 33, 1],
        [38, 6158, 29, 9690, 26, 9, 19, 33, 1], [38, 6158, 29, 9714, 26, 9, 19, 34, 1],
        [38, 6158, 29, 9737, 26, 9, 19, 35, 1],
        [38, 6158, 29, 9762, 26, 9, 19, 35, 1], [38, 6158, 29, 9786, 26, 9, 19, 35, 1],
        [38, 6158, 29, 9809, 26, 9, 19, 35, 1],
        [38, 6158, 29, 9834, 26, 9, 19, 34, 1], [38, 6158, 29, 9858, 26, 9, 19, 35, 1],
        [38, 6158, 29, 9881, 26, 9, 19, 35, 1],
        [38, 6158, 29, 9905, 26, 9, 19, 34, 1], [38, 6158, 29, 9930, 26, 9, 19, 35, 1]]  # R2
pre3 = [[0, 5866, 6, 4851, 6, 2, 302, 22, 0], [0, 5866, 6, 4876, 6, 2, 303, 22, 0],
        [0, 5866, 6, 4899, 6, 2, 304, 22, 0], [0, 5866, 6, 4923, 6, 2, 305, 22, 0],
        [0, 5866, 6, 4948, 6, 2, 306, 23, 0], [0, 5866, 6, 4971, 6, 2, 307, 23, 0],
        [0, 5866, 6, 4995, 6, 2, 308, 23, 0], [0, 5866, 6, 5019, 6, 2, 309, 22, 0],
        [0, 5866, 6, 5043, 6, 2, 310, 22, 0], [0, 5866, 6, 5067, 6, 2, 311, 22, 0],
        [0, 5866, 6, 5091, 6, 2, 312, 22, 0], [0, 5866, 6, 5115, 6, 2, 313, 22, 0],
        [0, 5866, 6, 5139, 6, 2, 314, 23, 0], [0, 5866, 6, 5163, 6, 2, 315, 22, 0],
        [0, 5866, 6, 5186, 6, 2, 316, 23, 0], [0, 5866, 6, 5211, 6, 2, 317, 22, 0],
        [0, 5866, 6, 5235, 6, 2, 318, 22, 0], [0, 5866, 6, 5258, 6, 2, 319, 23, 0],
        [0, 5866, 6, 5283, 6, 2, 320, 22, 0], [0, 5866, 6, 5307, 6, 2, 320, 22, 0]]  # R3
pre4 = [[0, 6091, 26, 11947, 26, 2, 290868, 28, 0], [0, 6091, 26, 11971, 26, 2, 290869, 30, 0],
        [0, 6091, 26, 11995, 26, 2, 290869, 30, 0],
        [0, 6091, 26, 12019, 26, 2, 290870, 30, 0], [0, 6091, 26, 12043, 26, 2, 290870, 30, 0],
        [0, 6091, 26, 12066, 26, 2, 290898, 29, 0],
        [0, 6091, 26, 12091, 26, 2, 290898, 31, 0], [0, 6091, 26, 12115, 26, 2, 290899, 31, 0],
        [0, 6091, 26, 12138, 26, 2, 290901, 31, 0],
        [0, 6091, 26, 12163, 26, 2, 290901, 31, 0], [0, 6091, 26, 12187, 26, 2, 290901, 29, 0],
        [0, 6091, 26, 12210, 26, 2, 290901, 31, 0],
        [0, 6091, 26, 12235, 26, 2, 290902, 31, 0], [0, 6091, 26, 12259, 26, 2, 290902, 31, 0],
        [0, 6091, 26, 12282, 26, 2, 290903, 31, 0],
        [0, 6091, 26, 12306, 26, 2, 290903, 31, 0], [0, 6091, 26, 12331, 26, 2, 290903, 31, 0],
        [0, 6091, 26, 12354, 26, 2, 290903, 31, 0],
        [0, 6091, 26, 12378, 26, 2, 290903, 31, 0], [0, 6091, 26, 12403, 26, 2, 290903, 31, 0]]  # R4
pre5 = [[1, 6116, 56, 34427, 56, 24, 573295, 20, 0], [1, 6116, 56, 34449, 56, 24, 573398, 23, 0],
        [1, 6116, 56, 34474, 56, 24, 573746, 22, 0],
        [1, 6116, 56, 34486, 56, 24, 573783, 22, 0], [1, 6116, 56, 34522, 56, 24, 574182, 21, 0],
        [1, 6116, 56, 34546, 56, 24, 574445, 22, 0],
        [1, 6116, 56, 34569, 56, 24, 574551, 20, 0], [1, 6116, 56, 34602, 56, 24, 574889, 21, 0],
        [1, 6116, 56, 34625, 56, 24, 575053, 21, 0],
        [1, 6116, 56, 34649, 56, 24, 575269, 20, 0], [1, 6116, 56, 34674, 56, 24, 575466, 21, 0],
        [1, 6116, 56, 34697, 56, 24, 575794, 21, 0],
        [1, 6116, 56, 34722, 56, 24, 576089, 20, 0], [1, 6116, 56, 34737, 56, 24, 576216, 21, 0],
        [1, 6116, 56, 34762, 56, 24, 576639, 20, 0],
        [1, 6116, 56, 34785, 56, 24, 576860, 24, 0], [1, 6116, 56, 34809, 56, 24, 577000, 20, 0],
        [1, 6116, 56, 34833, 56, 24, 577110, 21, 0],
        [1, 6116, 56, 34865, 56, 24, 577391, 20, 0], [1, 6116, 56, 34889, 56, 24, 577707, 20, 0]]  # R5
pre6 = [[6, 6158, 40, 32005, 40, 4, 219275, 30, 0], [6, 6158, 40, 32029, 40, 4, 219295, 30, 0],
        [6, 6158, 40, 32053, 40, 4, 219307, 31, 0],
        [6, 6158, 40, 32077, 40, 4, 219322, 31, 0], [6, 6158, 40, 32101, 40, 4, 219344, 30, 0],
        [6, 6158, 40, 32125, 40, 4, 219361, 29, 0],
        [6, 6158, 40, 32149, 40, 4, 219377, 28, 0], [6, 6158, 40, 32173, 40, 4, 219400, 30, 0],
        [6, 6158, 40, 32197, 40, 4, 219417, 30, 0],
        [6, 6158, 40, 32221, 40, 4, 219437, 30, 0], [6, 6158, 40, 32244, 40, 4, 219444, 30, 0],
        [6, 6158, 40, 32269, 40, 4, 219468, 30, 0],
        [6, 6158, 40, 32293, 40, 4, 219486, 30, 0], [6, 6158, 40, 32316, 40, 4, 219539, 30, 0],
        [6, 6158, 40, 32341, 40, 4, 219557, 30, 0],
        [6, 6158, 40, 32365, 40, 4, 219570, 29, 0], [6, 6158, 40, 32388, 40, 4, 219606, 29, 0],
        [6, 6158, 40, 32412, 40, 4, 219618, 29, 0],
        [6, 6158, 40, 32437, 40, 4, 219739, 30, 0], [6, 6158, 40, 32460, 40, 4, 219759, 29, 0]]  # R6

# pre1 = np.array(pre1)
# pre1 = pre1[np.newaxis, :, :]
# predict_1st(pre1, "")
# predict(pre2)
# pre3 = np.array(pre3)
# pre3 = pre3[np.newaxis, :, :]
# predict_1st(pre3, "")
# predict(pre4)
# predict(pre5)
# pre6 = np.array(pre6)
# pre6 = pre6[np.newaxis, :, :]
# predict_1st(pre6, "")

# 1st
# max 68186 min 0
# max 7025 min 0
# max 86 min 1
# max 1967 min 0
# max 124955 min 0
# max 40223 min 6
# max 0 min 0
# max 0 min 0
# max 86 min 1
# max 63 min 0
# max 743480 min 0
# max 39 min 14
# max 1953 min 0
# max 960 min 0
# max 0 min 0
# max 19 min 0
# max 0 min 0
