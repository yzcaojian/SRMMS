import tensorflow as tf
import numpy as np

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 二级健康度预测
@Time : 2021/12/4 17:02
@Author : cao jian
"""

# Parameters
n_input = 9
n_steps = 20
n_hidden = 128
n_classes = 3
classes = ["R1-1", "R1-2", "R1-3"]

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
    tf.reset_default_graph()
    # 将SAMRT数据按照训练集同样的方式裁剪选择九个特征：1、5、7、9、187、191、193、241、242
    temp = [1, 5, 7, 9, 187, 191, 193, 241, 242]
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
    smart_data_ = smart_data_[np.newaxis, :, :]
    smart_data_ = smart_data_.astype(np.float32)
    smart_max = [244139968, 65168, 30082046003, 33081, 214, 751305, 48994, 77690256632, 276474980020]
    smart_min = [0, 0, 14212, 0, 0, 0, 1, 0, 2112]
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
        # saver = tf.train.import_meta_graph('./model_learning/hdd_GRU_model.ckpt.meta')  # 不能加这一步
        saver.restore(sess, tf.train.latest_checkpoint('./resources/hard_disk_failure_prediction/ST8000NM0055/model_learning/model_2/'))

        prediction = sess.run(pred, feed_dict={x: smart_data_})
        print(prediction)
        # print(prediction.shape)  # 结果是二维数组
        print(np.max(prediction, axis=1))  # 概率最大的健康度预测结果
        for i in range(len(prediction[0])):
            if prediction[0][i] == np.max(prediction, axis=1):
                print(classes[i])

# max 244139968 min 0
# max 0 min 0
# max 5403 min 1
# max 65168 min 0
# max 30082046003 min 14212
# max 33081 min 0
# max 0 min 0
# max 163 min 1
# max 42 min 0
# max 214 min 0
# max 107377984081 min 0
# max 0 min 0
# max 60 min 18
# max 751305 min 0
# max 162 min 0
# max 48994 min 1
# max 60 min 18
# max 244139968 min 0
# max 2008 min 0
# max 2008 min 0
# max 455 min 0
# max 273739740611744 min 0
# max 77690256632 min 0
# max 276474980020 min 2112
