import tensorflow as tf
import numpy as np

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 二级健康度预测
@Time : 2021/5/24 21:03
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
    # 将SAMRT数据按照训练集同样的方式裁剪选择九个特征：1、3、4、9、192、193、194、196、197
    temp = [1, 3, 4, 9, 192, 193, 194, 196, 197]
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
    smart_max = [3831944120, 651, 189, 53792, 5885, 5885, 50, 2086, 421]
    smart_min = [0, 0, 4, 1419, 5, 5, 20, 0, 0]
    for i in range(len(smart_max)):
        for j in range(smart_data_.shape[1]):
            if smart_data_[0][j][i] >= smart_max[i]:
                smart_data_[0][j][i] = 1
            elif smart_data_[0][j][i] <= smart_min[i]:
                smart_data_[0][j][i] = 0
            else:
                smart_data_[0][j][i] = float((smart_data_[0][j][i] - smart_min[i]) / (smart_max[i] - smart_min[i]))
    # print(smart_data_)

    # 数据通过GRU网络计算
    x = tf.compat.v1.placeholder(dtype=tf.float32, shape=[None, 20, 9])
    pred = mulitGRU(x)

    saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(), max_to_keep=15)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # 先加载图和参数变量
        # saver = tf.train.import_meta_graph('./model/hdd_GRU_model.ckpt.meta')  # 不能加这一步
        saver.restore(sess, tf.train.latest_checkpoint('./resources/hard_disk_failure_prediction/HDS722020ALA330/model_learning/model_2/'))

        prediction = sess.run(pred, feed_dict={x: smart_data_})
        print(prediction)
        # print(prediction.shape)  # 结果是二维数组
        print(np.max(prediction, axis=1))  # 概率最大的健康度预测结果
        for i in range(len(prediction[0])):
            if prediction[0][i] == np.max(prediction, axis=1):
                return classes[i]


# 预测数据
pre1 = [[0, 625, 17, 35726, 766, 766, 28, 0, 0], [0, 625, 17, 35751, 766, 766, 27, 0, 0], [0, 625, 17, 35774, 767, 767, 27, 0, 0],
        [0, 625, 17, 35798, 768, 768, 27, 0, 0], [0, 625, 17, 35823, 769, 769, 27, 0, 0], [0, 625, 17, 35847, 770, 770, 27, 0, 0],
        [0, 625, 17, 35870, 771, 771, 27, 0, 0], [1, 625, 17, 35894, 772, 772, 27, 0, 0], [0, 625, 17, 35919, 773, 773, 27, 0, 0],
        [0, 625, 17, 35942, 774, 774, 27, 0, 0], [0, 625, 17, 35966, 774, 774, 27, 0, 0], [0, 625, 17, 35991, 775, 775, 27, 0, 0],
        [0, 625, 17, 36014, 776, 776, 27, 0, 0], [0, 625, 17, 36038, 777, 777, 28, 0, 0], [0, 625, 17, 36063, 778, 778, 28, 0, 0],
        [0, 625, 17, 36086, 779, 779, 28, 0, 0], [0, 625, 17, 36110, 780, 780, 28, 0, 0], [0, 625, 17, 36135, 780, 780, 27, 0, 0],
        [1, 625, 17, 36159, 781, 781, 26, 0, 0], [65536, 625, 17, 36182, 782, 782, 26, 0, 0]]  # R1-1
pre2 = [[691799322, 626, 40, 37221, 931, 931, 29, 0, 0], [65537, 626, 40, 37245, 931, 931, 30, 0, 0], [131073, 626, 40, 37268, 932, 932, 29, 0, 0],
        [262144, 626, 40, 37293, 933, 933, 30, 0, 0], [1, 626, 40, 37317, 934, 934, 29, 0, 0], [65537, 626, 40, 37340, 935, 935, 28, 0, 0],
        [851975, 626, 40, 37365, 936, 936, 29, 0, 0], [3801160, 626, 40, 37389, 937, 937, 28, 0, 0], [6554104, 626, 40, 37412, 938, 938, 28, 0, 0],
        [65545, 626, 40, 37437, 939, 939, 28, 0, 0], [589837, 626, 40, 37461, 939, 939, 28, 0, 0], [102302149, 626, 40, 37484, 940, 940, 29, 0, 0],
        [1179811, 626, 40, 37508, 941, 941, 28, 0, 0], [852267, 626, 40, 37533, 942, 942, 28, 0, 0], [11665410, 626, 40, 37557, 943, 943, 28, 0, 0],
        [131075, 626, 40, 37580, 944, 944, 29, 0, 0], [2752517, 626, 40, 37605, 944, 944, 28, 0, 0], [196609, 626, 40, 37629, 945, 945, 27, 0, 0],
        [46465050, 626, 40, 37652, 946, 946, 27, 0, 0], [2686988, 626, 40, 37677, 947, 947, 28, 0, 0]]  # R1-2
pre3 = [[0, 625, 23, 34770, 1062, 1062, 21, 1, 1], [0, 625, 23, 34794, 1063, 1063, 21, 1, 1], [0, 625, 23, 34818, 1064, 1064, 22, 1, 1],
        [65536, 625, 23, 34841, 1064, 1064, 22, 1, 1], [0, 625, 23, 34865, 1065, 1065, 22, 1, 1], [0, 625, 23, 34889, 1066, 1066, 22, 1, 1],
        [0, 625, 23, 34913, 1066, 1066, 22, 1, 1], [0, 625, 23, 34937, 1067, 1067, 22, 1, 1], [0, 625, 23, 34961, 1068, 1068, 22, 1, 1],
        [0, 625, 23, 34985, 1069, 1069, 22, 1, 1], [0, 625, 23, 35009, 1070, 1070, 22, 1, 1], [0, 625, 23, 35033, 1070, 1070, 26, 1, 1],
        [0, 625, 23, 35057, 1071, 1071, 27, 1, 1], [0, 625, 23, 35081, 1072, 1072, 21, 1, 1], [1, 625, 23, 35105, 1073, 1073, 21, 1, 1],
        [3, 625, 23, 35129, 1074, 1074, 21, 1, 1], [0, 625, 23, 35153, 1074, 1074, 21, 1, 1], [0, 625, 23, 35177, 1075, 1075, 21, 1, 2],
        [0, 625, 23, 35201, 1075, 1075, 21, 1, 2], [0, 625, 23, 35225, 1076, 1076, 21, 1, 2]]  # R1-3

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
# max 3831944120 min 0
# max 163 min 0
# max 651 min 0
# max 189 min 4
# max 1976 min 0
# max 262144 min 0
# max 68 min 0
# max 53792 min 1419
# max 1638425 min 0
# max 188 min 4
# max 5885 min 5
# max 5885 min 5
# max 50 min 20
# max 2086 min 0
# max 421 min 0
# max 4 min 0
# max 19822 min 0
