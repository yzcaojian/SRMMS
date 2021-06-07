import tensorflow as tf
import numpy as np

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 二级健康度预测
@Time : 2021/5/23 14:59
@Author : cao jian
"""

# Parameters
n_input = 9
n_steps = 20
n_hidden = 128
n_classes = 3
# classes = ["R1-1", "R1-2", "R1-3"]
classes = [7, 8, 9]

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


def predict_2nd(smart_data, smart_id):
    # 将SAMRT数据按照训练集同样的方式裁剪选择九个特征：2、3、4、8、9、192、193、194、197
    # 根据提前准备好的训练集中最大最小值进行数据归一化
    smart_data = smart_data.astype(np.float32)
    smart_max = [268, 572, 27, 91, 52228, 9035, 9035, 44, 38624]
    smart_min = [0, 0, 1, 0, 26, 1, 1, 18, 0]
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
        saver.restore(sess, tf.train.latest_checkpoint('./model_2/'))

        prediction = sess.run(pred, feed_dict={x: smart_data})
        print(prediction)
        # print(prediction.shape)  # 结果是二维数组
        print(np.max(prediction, axis=1))  # 概率最大的健康度预测结果
        for i in range(len(prediction[0])):
            if prediction[0][i] == np.max(prediction, axis=1):
                print(classes[i])


# 预测数据
pre1 = [[107, 553, 9, 42, 32546, 555, 555, 26, 0], [107, 553, 9, 42, 32570, 555, 555, 26, 0], [107, 553, 9, 42, 32594, 555, 555, 25, 0],
        [107, 553, 9, 42, 32618, 556, 556, 25, 0], [107, 553, 9, 42, 32642, 557, 557, 25, 0], [107, 553, 9, 42, 32666, 557, 557, 25, 0],
        [107, 553, 9, 42, 32690, 558, 558, 25, 0], [107, 553, 9, 42, 32714, 558, 558, 26, 0], [107, 553, 9, 42, 32744, 558, 558, 25, 0],
        [107, 553, 9, 42, 32768, 558, 558, 25, 0], [107, 553, 9, 42, 32793, 558, 558, 25, 0], [107, 553, 9, 42, 32817, 558, 558, 25, 0],
        [107, 553, 9, 42, 32841, 558, 558, 25, 0], [107, 553, 9, 44, 32865, 1050, 1050, 25, 0], [107, 553, 9, 44, 32889, 1144, 1144, 26, 0],
        [107, 553, 9, 44, 32913, 1160, 1160, 25, 0], [107, 553, 9, 44, 32937, 1310, 1310, 25, 0], [107, 553, 9, 44, 32954, 1856, 1856, 25, 0],
        [107, 553, 9, 44, 32978, 1875, 1875, 26, 0], [107, 553, 9, 44, 33002, 1878, 1878, 26, 0]]  # R1-1
pre2 = [[104, 562, 14, 42, 38261, 388, 388, 31, 0], [104, 562, 14, 41, 38285, 389, 389, 27, 0], [104, 562, 14, 42, 38309, 390, 390, 28, 0],
        [104, 562, 14, 42, 38333, 390, 390, 27, 0], [104, 562, 14, 40, 38357, 391, 391, 28, 0], [104, 562, 14, 40, 38381, 391, 391, 26, 0],
        [104, 562, 14, 41, 38405, 392, 392, 29, 0], [104, 562, 14, 41, 38429, 392, 392, 28, 0], [104, 562, 14, 42, 38453, 393, 393, 27, 0],
        [104, 562, 14, 42, 38477, 393, 393, 29, 0], [103, 562, 14, 41, 38501, 394, 394, 29, 0], [103, 562, 14, 41, 38525, 394, 394, 29, 0],
        [103, 562, 14, 41, 38549, 394, 394, 29, 0], [103, 562, 14, 40, 38573, 395, 395, 30, 0], [103, 562, 14, 40, 38597, 395, 395, 30, 0],
        [102, 562, 14, 42, 38622, 395, 395, 29, 0], [102, 562, 14, 42, 38646, 396, 396, 31, 0], [102, 562, 14, 42, 38670, 396, 396, 31, 0],
        [102, 562, 14, 42, 38694, 397, 397, 30, 0], [103, 562, 14, 42, 38718, 397, 397, 31, 0]]  # R1-2
pre3 = [[98, 551, 10, 42, 14286, 352, 352, 27, 0], [97, 551, 10, 42, 14310, 353, 353, 27, 0], [99, 551, 10, 42, 14334, 354, 354, 27, 0],
        [99, 551, 10, 43, 14358, 355, 355, 27, 0], [98, 551, 10, 42, 14382, 356, 356, 28, 0], [98, 551, 10, 42, 14406, 357, 357, 28, 0],
        [97, 551, 10, 42, 14429, 358, 358, 26, 0], [97, 551, 10, 42, 14454, 359, 359, 26, 0], [97, 551, 10, 42, 14478, 360, 360, 26, 0],
        [99, 551, 10, 42, 14502, 361, 361, 26, 0], [99, 551, 10, 42, 14525, 361, 361, 26, 0], [99, 551, 10, 42, 14550, 362, 362, 27, 0],
        [99, 551, 10, 42, 14574, 363, 363, 26, 0], [98, 551, 10, 42, 14598, 363, 363, 26, 0], [98, 551, 10, 43, 14622, 364, 364, 25, 0],
        [98, 551, 10, 42, 14646, 365, 365, 27, 0], [99, 551, 10, 43, 14670, 366, 366, 25, 0], [98, 551, 10, 42, 14693, 367, 367, 25, 0],
        [98, 551, 10, 42, 14718, 368, 368, 26, 0], [98, 551, 10, 42, 14742, 369, 369, 25, 0]]  # R1-3

pre1 = np.array(pre1)
pre1 = pre1[np.newaxis, :, :]
predict_2nd(pre1, "")
# pre2 = np.array(pre2)
# pre2 = pre2[np.newaxis, :, :]
# predict_2nd(pre2, "")
# pre3 = np.array(pre3)
# pre3 = pre3[np.newaxis, :, :]
# predict_2nd(pre3, "")

# 2nd
# max 1365901318 min 0
# max 268 min 0
# max 572 min 0
# max 27 min 1
# max 2004 min 0
# max 8323160 min 0
# max 91 min 0
# max 52228 min 26
# max 65536 min 0
# max 27 min 1
# max 9035 min 1
# max 9035 min 1
# max 44 min 18
# max 3585 min 0
# max 38624 min 0
# max 65 min 0
# max 292 min 0
