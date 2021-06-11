import numpy as np
import tensorflow as tf

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 二级健康度预测
@Time : 2021/5/24 16:25
@Author : cao jian
"""

# Parameters
n_input = 9
n_steps = 20
n_hidden = 128
n_classes = 3
# classes = ["R1-1", "R1-2", "R1-3"]
classes = [7, 8, 9]


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


def predict_2nd(smart_data, smart_id):
    tf.reset_default_graph()
    # 将SAMRT数据按照训练集同样的方式裁剪选择九个特征：1、3、4、9、12、192、193、194、197
    # 根据提前准备好的训练集中最大最小值进行数据归一化
    smart_data = smart_data[np.newaxis, :, :]
    smart_data = smart_data.astype(np.float32)
    smart_max = [68186, 7025, 86, 40223, 86, 63, 743480, 39, 960]
    smart_min = [0, 0, 1, 7, 1, 0, 0, 15, 0]
    for i in range(len(smart_max)):
        for j in range(smart_data.shape[1]):
            if smart_data[0][j][i] >= smart_max[i]:
                smart_data[0][j][i] = 1
            elif smart_data[0][j][i] <= smart_min[i]:
                smart_data[0][j][i] = 0
            else:
                smart_data[0][j][i] = float((smart_data[0][j][i] - smart_min[i]) / (smart_max[i] - smart_min[i]))
    # print(smart_data)

    # 数据通过GRU网络计算
    x = tf.compat.v1.placeholder(dtype=tf.float32, shape=[None, 20, 9])
    pred = mulitGRU(x)

    saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(), max_to_keep=15)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # 先加载图和参数变量
        # saver = tf.train.import_meta_graph('./model/hdd_GRU_model.ckpt.meta')  # 不能加这一步
        saver.restore(sess, tf.train.latest_checkpoint('../hard_disk_failure_prediction/WD30EFRX/model_learning/model_2/'))

        prediction = sess.run(pred, feed_dict={x: smart_data})
        print(prediction)
        # print(prediction.shape)  # 结果是二维数组
        print(np.max(prediction, axis=1))  # 概率最大的健康度预测结果
        for i in range(len(prediction[0])):
            if prediction[0][i] == np.max(prediction, axis=1):
                return classes[i]


# 预测数据
pre1 = [[0, 6258, 23, 22016, 21, 6, 738, 22, 0], [0, 6258, 23, 22040, 21, 6, 739, 21, 0], [0, 6258, 23, 22064, 21, 6, 739, 21, 0],
        [0, 6258, 23, 22088, 21, 6, 740, 21, 0], [0, 6258, 23, 22112, 21, 6, 740, 21, 0], [0, 6258, 23, 22136, 21, 6, 740, 22, 0],
        [0, 6258, 23, 22160, 21, 6, 741, 22, 0], [0, 6258, 23, 22184, 21, 6, 741, 22, 0], [0, 6258, 23, 22208, 21, 6, 741, 22, 0],
        [0, 6258, 23, 22232, 21, 6, 742, 21, 0], [0, 6258, 23, 22256, 21, 6, 742, 21, 0], [0, 6258, 23, 22279, 21, 6, 742, 21, 0],
        [0, 6258, 23, 22304, 21, 6, 742, 21, 0], [0, 6258, 23, 22328, 21, 6, 742, 22, 0], [0, 6258, 23, 22351, 21, 6, 742, 22, 0],
        [0, 6258, 23, 22376, 21, 6, 742, 21, 0], [0, 6258, 23, 22400, 21, 6, 742, 21, 0], [0, 6258, 23, 22423, 21, 6, 742, 21, 0],
        [0, 6258, 23, 22448, 21, 6, 742, 22, 0], [0, 6258, 23, 22472, 21, 6, 742, 22, 0]]  # R1-1
pre2 = [[0, 6291, 15, 26713, 15, 2, 209482, 25, 0], [0, 6291, 15, 26736, 15, 2, 209488, 25, 0], [0, 6291, 15, 26760, 15, 2, 209498, 25, 0],
        [0, 6291, 15, 26785, 15, 2, 209503, 24, 0], [0, 6291, 15, 26808, 15, 2, 209508, 24, 0], [0, 6291, 15, 26832, 15, 2, 209515, 26, 0],
        [0, 6291, 15, 26857, 15, 2, 209518, 25, 0], [0, 6291, 15, 26880, 15, 2, 209621, 24, 0], [0, 6291, 15, 26904, 15, 2, 209935, 24, 0],
        [0, 6291, 15, 26929, 15, 2, 210469, 25, 0], [0, 6291, 15, 26952, 15, 2, 210665, 24, 0], [0, 6291, 15, 26976, 15, 2, 210794, 24, 0],
        [0, 6291, 15, 27001, 15, 2, 211400, 23, 0], [0, 6291, 15, 27024, 15, 2, 212477, 23, 0], [0, 6291, 15, 27048, 15, 2, 212579, 23, 0],
        [0, 6291, 15, 27072, 15, 2, 212672, 23, 0], [0, 6291, 15, 27096, 15, 2, 212790, 23, 0], [0, 6291, 15, 27120, 15, 2, 212874, 24, 0],
        [0, 6291, 15, 27144, 15, 2, 212948, 24, 0], [0, 6291, 15, 27168, 15, 2, 212948, 24, 0]]  # R1-2
pre3 = [[0, 4608, 14, 16097, 14, 4, 62, 21, 0], [0, 4608, 14, 16121, 14, 4, 62, 21, 0], [0, 4608, 14, 16145, 14, 4, 62, 21, 0],
        [0, 4608, 14, 16169, 14, 4, 62, 33, 0], [0, 5433, 15, 16193, 15, 4, 63, 27, 0], [0, 5433, 15, 16217, 15, 4, 63, 25, 0],
        [0, 5433, 15, 16241, 15, 4, 63, 27, 0], [0, 5433, 15, 16265, 15, 4, 63, 27, 0], [0, 5433, 15, 16288, 15, 4, 63, 25, 0],
        [0, 5433, 15, 16313, 15, 4, 63, 24, 0], [0, 5433, 15, 16337, 15, 4, 63, 24, 0], [0, 5433, 15, 16360, 15, 4, 63, 26, 0],
        [0, 5433, 15, 16385, 15, 4, 63, 26, 0], [0, 5433, 15, 16408, 15, 4, 63, 25, 0], [0, 5433, 15, 16432, 15, 4, 63, 25, 0],
        [0, 5433, 15, 16456, 15, 4, 63, 25, 0], [0, 5433, 15, 16481, 15, 4, 63, 26, 0], [0, 5433, 15, 16504, 15, 4, 63, 26, 0],
        [0, 5433, 15, 16528, 15, 4, 63, 25, 0], [0, 5433, 15, 16552, 15, 4, 63, 25, 0]]  # R1-3

# pre1 = np.array(pre1)
# pre1 = pre1[np.newaxis, :, :]
# predict_2nd(pre1, "")
# pre2 = np.array(pre2)
# pre2 = pre2[np.newaxis, :, :]
# predict_2nd(pre2, "")
# pre3 = np.array(pre3)
# pre3 = pre3[np.newaxis, :, :]
# predict_2nd(pre3, "")

# 2nd
# max 68186 min 0
# max 6841 min 0
# max 86 min 1
# max 1967 min 0
# max 124955 min 0
# max 40223 min 7
# max 0 min 0
# max 0 min 0
# max 86 min 1
# max 63 min 0
# max 743480 min 0
# max 37 min 15
# max 1953 min 0
# max 187 min 0
# max 0 min 0
# max 19 min 0
# max 0 min 0
