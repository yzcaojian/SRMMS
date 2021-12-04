import tensorflow as tf
import numpy as np

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 一级健康度预测
@Time : 2021/12/4 16:39
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


def predict_1st(smart_data, smart_id):
    tf.reset_default_graph()
    # 将SAMRT数据按照训练集同样的方式裁剪选择九个特征：4、5、7、190、191、192、193、241、242
    temp = [4, 5, 7, 190, 191, 192, 193, 241, 242]
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
    smart_data_ = smart_data_.astype(np.float32)
    smart_max = [779, 65288, 8589849444, 59, 438903, 100, 55227, 88016819424, 314552762456]
    smart_min = [1, 0, 57827, 18, 0, 0, 1, 0, 0, 2366]
    for i in range(len(smart_max)):
        for j in range(smart_data_.shape[1]):
            if smart_data_[0][j][i] >= smart_max[i]:
                smart_data_[0][j][i] = 1
            elif smart_data_[0][j][i] <= smart_min[i]:
                smart_data_[0][j][i] = 0
            else:
                smart_data_[0][j][i] = float((smart_data_[0][j][i] - smart_min[i]) / (smart_max[i] - smart_min[i]))

    # 数据通过GRU网络计算
    x = tf.compat.v1.placeholder(dtype=tf.float32, shape=[None, 20, 9])
    pred = mulitGRU(x)

    saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(), max_to_keep=15)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # 先加载图和参数变量
        saver.restore(sess, tf.train.latest_checkpoint('./resources/hard_disk_failure_prediction/ST8000DM002/model_learning/model/'))

        prediction = sess.run(pred, feed_dict={x: smart_data_})
        print(prediction)
        # print(prediction.shape)  # 结果是二维数组
        print(np.max(prediction, axis=1))  # 概率最大的健康度预测结果
        for i in range(len(prediction[0])):
            if prediction[0][i] == np.max(prediction, axis=1):
                print(classes[i])

# max 244139040 min 0
# max 0 min 0
# max 779 min 1
# max 65288 min 0
# max 8589849444 min 57827
# max 39385 min 0
# max 0 min 0
# max 26 min 1
# max 7 min 0
# max 489 min 0
# max 30065229833 min 0
# max 0 min 0
# max 59 min 18
# max 438903 min 0
# max 100 min 0
# max 55227 min 1
# max 59 min 18
# max 244139040 min 0
# max 44784 min 0
# max 44784 min 0
# max 297 min 0
# max 281466386778578 min 0
# max 88016819424 min 0
# max 314552762456 min 2366
