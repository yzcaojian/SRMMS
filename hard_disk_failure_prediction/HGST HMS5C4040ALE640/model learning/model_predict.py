import tensorflow as tf
import numpy as np

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 一级健康度预测
@Time : 2021/4/1 21:14
@Author : cao jian
"""

# Parameters
n_input = 9
n_steps = 20
n_hidden = 128
n_classes = 6
classes = ["R1", "R2", "R3", "R4", "R5", "R6"]

# Define weights
weights = {
    'in': tf.Variable(tf.random_uniform([n_input, n_hidden])),
    'out': tf.Variable(tf.random.normal([n_hidden, n_classes])),
}
biases = {
    'in': tf.Variable(tf.random_uniform([n_hidden])),
    'out': tf.Variable(tf.random.normal([n_classes])),
}


def mulitGRU(x):
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


def predict_1st(smart_data):
    # 将SAMRT数据按照训练集同样的方式裁剪选择九个特征：2、3、4、9、12、192、193、196、197
    # 根据提前准备好的训练集中最大最小值进行数据归一化
    smart_data = smart_data.astype(np.float32)
    smart_max = [268, 572, 27, 52228, 27, 9035, 9035, 3585, 38624]
    smart_min = [0, 0, 1, 0, 1, 1, 1, 0, 0]
    for i in range(len(smart_max)):
        for j in range(smart_data.shape[1]):
            if smart_data[0][j][i] >= smart_max[i]:
                smart_data[0][j][i] = 1
            elif smart_data[0][j][i] <= smart_min[i]:
                smart_data[0][j][i] = 0
            else:
                smart_data[0][j][i] = float((smart_data[0][j][i] - smart_min[i]) / (smart_max[i] - smart_min[i]))
    print(smart_data)

    # 数据通过GRU网络计算
    x = tf.compat.v1.placeholder(dtype=tf.float32, shape=[None, 20, 9])
    pred = mulitGRU(x)

    saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(), max_to_keep=15)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # 先加载图和参数变量
        # saver = tf.train.import_meta_graph('./model/hdd_GRU_model.ckpt.meta')  # 不能加这一步
        saver.restore(sess, tf.train.latest_checkpoint('./model/'))

        prediction = sess.run(pred, feed_dict={x: smart_data})
        print(prediction)
        # print(prediction.shape)  # 结果是二维数组
        print(np.max(prediction, axis=1))  # 概率最大的健康度预测结果
        for i in range(len(prediction[0])):
            if prediction[0][i] == np.max(prediction, axis=1):
                print(classes[i])


# 预测数据
pre1 = [[102, 538, 15, 33795, 13, 484, 484, 0, 0], [102, 538, 15, 33819, 13, 484, 484, 0, 0], [102, 538, 15, 33843, 13, 485, 485, 0, 0],
        [102, 538, 15, 33867, 13, 486, 486, 0, 0], [102, 538, 15, 33891, 13, 486, 486, 0, 0], [102, 538, 15, 33914, 13, 487, 487, 0, 0],
        [102, 538, 15, 33938, 13, 488, 488, 0, 0], [102, 538, 15, 33963, 13, 489, 489, 0, 0], [102, 538, 15, 33987, 13, 490, 490, 0, 0],
        [102, 538, 15, 34011, 13, 490, 490, 0, 0], [102, 538, 15, 34035, 13, 490, 490, 0, 0], [102, 538, 15, 34059, 13, 490, 490, 0, 0],
        [102, 538, 15, 34083, 13, 490, 490, 0, 0], [102, 538, 15, 34107, 13, 490, 490, 0, 0], [102, 538, 15, 34131, 13, 491, 491, 0, 0],
        [102, 538, 15, 34155, 13, 492, 492, 0, 0], [102, 538, 15, 34180, 13, 492, 492, 0, 0], [102, 538, 15, 34204, 13, 493, 493, 0, 0],
        [102, 538, 15, 34228, 13, 493, 493, 0, 0], [102, 538, 15, 34252, 13, 494, 494, 0, 0]]  # R1
pre2 = [[104, 569, 13, 17886, 13, 220, 220, 0, 0], [104, 569, 13, 17910, 13, 220, 220, 0, 0], [104, 569, 13, 17935, 13, 220, 220, 0, 0],
        [104, 569, 13, 17958, 13, 221, 221, 0, 0], [104, 569, 13, 17982, 13, 221, 221, 0, 0], [104, 569, 13, 18007, 13, 221, 221, 0, 0],
        [104, 569, 13, 18030, 13, 222, 222, 0, 0], [104, 569, 13, 18054, 13, 222, 222, 0, 0], [104, 569, 13, 18078, 13, 223, 223, 0, 0],
        [104, 569, 13, 18103, 13, 223, 223, 0, 0], [104, 569, 13, 18126, 13, 223, 223, 0, 0], [104, 569, 13, 18150, 13, 224, 224, 0, 0],
        [104, 569, 13, 18175, 13, 225, 225, 0, 0], [104, 569, 13, 18198, 13, 225, 225, 0, 0], [104, 569, 13, 18222, 13, 226, 226, 0, 0],
        [104, 569, 13, 18246, 13, 227, 227, 0, 0], [104, 569, 13, 18270, 13, 227, 227, 0, 0], [104, 569, 13, 18294, 13, 227, 227, 0, 0],
        [104, 569, 13, 18318, 13, 227, 227, 0, 0], [104, 569, 13, 18343, 13, 227, 227, 0, 0]]  # R2
pre3 = [[100, 424, 7, 20288, 7, 289, 289, 0, 8], [100, 424, 7, 20312, 7, 289, 289, 0, 8], [100, 424, 7, 20337, 7, 290, 290, 0, 8],
        [100, 424, 7, 20360, 7, 290, 290, 0, 8], [100, 424, 7, 20384, 7, 290, 290, 0, 8], [100, 424, 7, 20409, 7, 290, 290, 0, 8],
        [100, 424, 7, 20432, 7, 291, 291, 0, 8], [100, 424, 7, 20456, 7, 291, 291, 0, 8], [100, 424, 7, 20481, 7, 292, 292, 0, 8],
        [100, 424, 7, 20504, 7, 292, 292, 0, 8], [100, 424, 7, 20528, 7, 292, 292, 0, 8], [100, 424, 7, 20552, 7, 293, 293, 0, 8],
        [100, 424, 7, 20577, 7, 294, 294, 0, 8], [100, 424, 7, 20600, 7, 294, 294, 0, 8], [100, 424, 7, 20624, 7, 294, 294, 0, 8],
        [100, 424, 7, 20649, 7, 295, 295, 0, 8], [100, 424, 7, 20672, 7, 295, 295, 0, 8], [100, 424, 7, 20696, 7, 295, 295, 0, 8],
        [100, 424, 7, 20721, 7, 296, 296, 0, 8], [100, 424, 7, 20744, 7, 296, 296, 0, 8]]  # R3
pre4 = [[104, 448, 5, 18510, 5, 216, 216, 0, 0], [104, 448, 5, 18535, 5, 217, 217, 0, 0], [104, 448, 5, 18558, 5, 218, 218, 0, 0],
        [104, 448, 5, 18582, 5, 219, 219, 0, 0], [104, 448, 5, 18607, 5, 219, 219, 0, 0], [104, 448, 5, 18630, 5, 220, 220, 0, 0],
        [104, 448, 5, 18654, 5, 220, 220, 0, 0], [104, 448, 5, 18679, 5, 221, 221, 0, 0], [104, 448, 5, 18702, 5, 221, 221, 0, 0],
        [104, 448, 5, 18726, 5, 221, 221, 0, 0], [104, 448, 5, 18750, 5, 222, 222, 0, 0], [104, 448, 5, 18775, 5, 223, 223, 0, 0],
        [104, 448, 5, 18798, 5, 224, 224, 0, 0], [104, 448, 5, 18822, 5, 224, 224, 0, 0], [104, 448, 5, 18847, 5, 225, 225, 0, 0],
        [104, 448, 5, 18870, 5, 225, 225, 0, 0], [104, 448, 5, 18894, 5, 225, 225, 0, 0], [104, 448, 5, 18919, 5, 226, 226, 0, 0],
        [104, 448, 5, 18942, 5, 226, 226, 0, 0], [104, 448, 5, 18966, 5, 227, 227, 0, 0]]  # R4
pre5 = [[104, 562, 10, 19874, 10, 326, 326, 0, 0], [104, 562, 10, 19898, 10, 326, 326, 0, 0], [104, 562, 10, 19921, 10, 327, 327, 0, 0],
        [104, 562, 10, 19946, 10, 327, 327, 0, 0], [104, 562, 10, 19970, 10, 328, 328, 0, 0], [104, 562, 10, 19994, 10, 328, 328, 0, 0],
        [104, 562, 10, 20017, 10, 328, 328, 0, 0], [104, 562, 10, 20042, 10, 328, 328, 0, 0], [104, 562, 10, 20066, 10, 329, 329, 0, 0],
        [104, 562, 10, 20089, 10, 330, 330, 0, 0], [104, 562, 10, 20114, 10, 330, 330, 0, 0], [104, 562, 10, 20138, 10, 331, 331, 0, 0],
        [104, 562, 10, 20161, 10, 332, 332, 0, 0], [104, 562, 10, 20186, 10, 333, 333, 0, 0], [104, 562, 10, 20210, 10, 333, 333, 0, 0],
        [104, 562, 10, 20234, 10, 334, 334, 0, 0], [104, 562, 10, 20257, 10, 334, 334, 0, 0], [104, 562, 10, 20282, 10, 335, 335, 0, 0],
        [104, 562, 10, 20306, 10, 335, 335, 0, 0], [104, 562, 10, 20329, 10, 336, 336, 0, 0]]  # R5
pre6 = [[107, 0, 3, 4784, 3, 50, 50, 0, 0], [107, 0, 3, 4809, 3, 50, 50, 0, 0], [107, 0, 3, 4833, 3, 50, 50, 0, 0], [107, 0, 3, 4856, 3, 50, 50, 0, 0],
        [107, 0, 3, 4881, 3, 50, 50, 0, 0], [107, 0, 3, 4905, 3, 50, 50, 0, 0], [107, 0, 3, 4928, 3, 50, 50, 0, 0], [107, 0, 3, 4953, 3, 50, 50, 0, 0],
        [107, 0, 3, 4977, 3, 50, 50, 0, 0], [107, 0, 3, 5000, 3, 50, 50, 0, 0], [107, 0, 3, 5024, 3, 50, 50, 0, 0], [107, 0, 3, 5049, 3, 50, 50, 0, 0],
        [107, 0, 3, 5072, 3, 50, 50, 0, 0], [107, 0, 3, 5096, 3, 50, 50, 0, 0], [107, 0, 3, 5121, 3, 50, 50, 0, 0], [107, 0, 3, 5145, 3, 50, 50, 0, 0],
        [107, 0, 3, 5168, 3, 50, 50, 0, 0], [107, 0, 3, 5193, 3, 50, 50, 0, 0], [107, 0, 3, 5217, 3, 50, 50, 0, 0], [107, 0, 3, 5240, 3, 50, 50, 0, 0]]  # R6

# pre1 = np.array(pre1)
# pre1 = pre1[np.newaxis, :, :]
# predict_1st(pre1)
# predict(pre2)
pre3 = np.array(pre3)
pre3 = pre3[np.newaxis, :, :]
predict_1st(pre3)
# predict(pre4)
# predict(pre5)
# pre6 = np.array(pre6)
# pre6 = pre6[np.newaxis, :, :]
# predict_1st(pre6)

# 1st
# max 1365901318 min 0
# max 268 min 0
# max 572 min 0
# max 27 min 1
# max 2004 min 0
# max 8323160 min 0
# max 91 min 0
# max 52228 min 0
# max 65536 min 0
# max 27 min 1
# max 9035 min 1
# max 9035 min 1
# max 52 min 16
# max 3585 min 0
# max 38624 min 0
# max 65 min 0
# max 292 min 0
