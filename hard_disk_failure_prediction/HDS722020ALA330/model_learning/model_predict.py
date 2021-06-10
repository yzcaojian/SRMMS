import numpy as np
import tensorflow as tf

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 一级健康度预测
@Time : 2021/5/24 21:02
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
    # 将SAMRT数据按照训练集同样的方式裁剪选择九个特征：3、4、5、9、12、192、193、196、197
    # 根据提前准备好的训练集中最大最小值进行数据归一化
    smart_data = smart_data.astype(np.float32)
    smart_max = [651, 189, 1976, 53792, 188, 5885, 5885, 2086, 421]
    smart_min = [0, 3, 0, 10, 3, 3, 3, 0, 0]
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
pre1 = [[643, 24, 177, 40995, 24, 1104, 1104, 179, 27], [643, 24, 177, 41019, 24, 1105, 1105, 179, 27], [643, 24, 177, 41043, 24, 1106, 1106, 179, 27],
        [643, 24, 177, 41067, 24, 1107, 1107, 179, 27], [643, 24, 177, 41091, 24, 1107, 1107, 179, 27], [643, 24, 177, 41115, 24, 1108, 1108, 179, 27],
        [643, 24, 177, 41139, 24, 1109, 1109, 179, 27], [643, 24, 177, 41163, 24, 1110, 1110, 179, 27], [643, 24, 177, 41187, 24, 1111, 1111, 179, 27],
        [643, 24, 177, 41211, 24, 1112, 1112, 179, 27], [643, 24, 177, 41235, 24, 1113, 1113, 179, 27], [643, 24, 177, 41259, 24, 1113, 1113, 179, 27],
        [643, 24, 177, 41283, 24, 1114, 1114, 179, 27], [643, 24, 177, 41307, 24, 1115, 1115, 179, 27], [643, 24, 177, 41331, 24, 1116, 1116, 179, 27],
        [643, 24, 177, 41355, 24, 1117, 1117, 179, 27], [643, 24, 177, 41379, 24, 1117, 1117, 179, 27], [643, 24, 177, 41403, 24, 1118, 1118, 179, 27],
        [643, 24, 177, 41427, 24, 1119, 1119, 179, 27], [643, 24, 177, 41451, 24, 1120, 1120, 179, 27]]  # R1
pre2 = [[625, 26, 1, 34559, 25, 1055, 1055, 1, 1], [625, 26, 1, 34583, 25, 1056, 1056, 1, 1], [625, 26, 1, 34607, 25, 1057, 1057, 1, 1],
        [625, 26, 1, 34631, 25, 1058, 1058, 1, 1], [625, 26, 1, 34655, 25, 1058, 1058, 1, 1], [625, 26, 1, 34679, 25, 1059, 1059, 1, 1],
        [625, 26, 1, 34703, 25, 1060, 1060, 1, 1], [625, 26, 1, 34727, 25, 1061, 1061, 1, 1], [625, 26, 1, 34751, 25, 1062, 1062, 1, 1],
        [625, 26, 1, 34774, 25, 1063, 1063, 1, 1], [625, 26, 1, 34798, 25, 1063, 1063, 1, 1], [625, 26, 1, 34822, 25, 1064, 1064, 1, 1],
        [625, 26, 1, 34846, 25, 1065, 1065, 1, 1], [625, 26, 1, 34870, 25, 1066, 1066, 1, 1], [625, 26, 1, 34894, 25, 1067, 1067, 1, 1],
        [625, 26, 1, 34918, 25, 1068, 1068, 1, 1], [625, 26, 1, 34942, 25, 1069, 1069, 1, 1], [625, 26, 1, 34966, 25, 1069, 1069, 1, 1],
        [625, 26, 1, 34990, 25, 1070, 1070, 1, 1], [625, 26, 1, 35014, 25, 1071, 1071, 1, 1]]  # R2
pre3 = [[627, 52, 0, 48924, 52, 1635, 1635, 0, 0], [627, 52, 0, 48947, 52, 1636, 1636, 0, 0], [627, 52, 0, 48971, 52, 1637, 1637, 0, 0],
        [627, 52, 0, 48996, 52, 1638, 1638, 0, 0], [627, 52, 0, 49019, 52, 1639, 1639, 0, 0], [627, 52, 0, 49043, 52, 1640, 1640, 0, 0],
        [627, 52, 0, 49067, 52, 1641, 1641, 0, 0], [627, 52, 0, 49092, 52, 1642, 1642, 0, 0], [627, 52, 0, 49115, 52, 1643, 1643, 0, 0],
        [627, 52, 0, 49139, 52, 1643, 1643, 0, 0], [627, 52, 0, 49163, 52, 1644, 1644, 0, 0], [627, 52, 0, 49187, 52, 1644, 1644, 0, 0],
        [627, 52, 0, 49211, 52, 1644, 1644, 0, 0], [627, 52, 0, 49235, 52, 1644, 1644, 0, 0], [627, 52, 0, 49259, 52, 1644, 1644, 0, 0],
        [627, 52, 0, 49283, 52, 1644, 1644, 0, 0], [627, 52, 0, 49307, 52, 1644, 1644, 0, 0], [627, 52, 0, 49332, 52, 1644, 1644, 0, 0],
        [627, 52, 0, 49355, 52, 1644, 1644, 0, 0], [627, 52, 0, 49379, 52, 1644, 1644, 0, 0]]  # R3
pre4 = [[632, 15, 2, 45960, 15, 1333, 1333, 2, 1], [632, 15, 2, 45984, 15, 1334, 1334, 2, 1], [632, 15, 2, 46008, 15, 1334, 1334, 2, 1],
        [632, 15, 2, 46032, 15, 1335, 1335, 2, 1], [632, 15, 2, 46056, 15, 1336, 1336, 2, 1], [632, 15, 2, 46080, 15, 1337, 1337, 2, 1],
        [632, 15, 2, 46104, 15, 1338, 1338, 2, 1], [632, 15, 2, 46128, 15, 1339, 1339, 2, 1], [632, 15, 2, 46152, 15, 1340, 1340, 2, 1],
        [632, 15, 2, 46176, 15, 1341, 1341, 2, 1], [632, 15, 2, 46200, 15, 1342, 1342, 2, 1], [632, 15, 2, 46224, 15, 1342, 1342, 2, 1],
        [632, 15, 2, 46248, 15, 1343, 1343, 2, 1], [632, 15, 2, 46272, 15, 1344, 1344, 2, 1], [632, 15, 2, 46296, 15, 1345, 1345, 2, 1],
        [632, 15, 2, 46320, 15, 1346, 1346, 2, 1], [632, 15, 2, 46344, 15, 1347, 1347, 2, 1], [632, 15, 2, 46368, 15, 1348, 1348, 2, 1],
        [632, 15, 2, 46392, 15, 1349, 1349, 2, 1], [632, 15, 2, 46416, 15, 1350, 1350, 2, 1]]  # R4
pre5 = [[622, 30, 0, 44821, 28, 1452, 1452, 0, 0], [622, 30, 0, 44845, 28, 1452, 1452, 0, 0], [622, 30, 0, 44868, 28, 1453, 1453, 0, 0],
        [622, 30, 0, 44893, 28, 1454, 1454, 0, 0], [622, 30, 0, 44916, 28, 1454, 1454, 0, 0], [622, 30, 0, 44941, 28, 1455, 1455, 0, 0],
        [622, 30, 0, 44964, 28, 1456, 1456, 0, 0], [622, 30, 0, 44988, 28, 1457, 1457, 0, 0], [622, 30, 0, 45013, 28, 1458, 1458, 0, 0],
        [622, 30, 0, 45037, 28, 1459, 1459, 0, 0], [622, 30, 0, 45060, 28, 1460, 1460, 0, 0], [622, 30, 0, 45084, 28, 1460, 1460, 0, 0],
        [622, 30, 0, 45109, 28, 1461, 1461, 0, 0], [622, 30, 0, 45132, 28, 1462, 1462, 0, 0], [622, 30, 0, 45156, 28, 1463, 1463, 0, 0],
        [622, 30, 0, 45181, 28, 1464, 1464, 0, 0], [622, 30, 0, 45205, 28, 1465, 1465, 0, 0], [622, 30, 0, 45228, 28, 1466, 1466, 0, 0],
        [622, 30, 0, 45253, 28, 1467, 1467, 0, 0], [622, 30, 0, 45277, 28, 1468, 1468, 0, 0]]  # R5
pre6 = [[625, 17, 0, 35365, 17, 926, 926, 0, 0], [625, 17, 0, 35390, 17, 927, 927, 0, 0], [625, 17, 0, 35414, 17, 928, 928, 0, 0],
        [625, 17, 0, 35437, 17, 929, 929, 0, 0], [625, 17, 0, 35461, 17, 929, 929, 0, 0], [625, 17, 0, 35486, 17, 930, 930, 0, 0],
        [625, 17, 0, 35509, 17, 931, 931, 0, 0], [625, 17, 0, 35533, 17, 932, 932, 0, 0], [625, 17, 0, 35558, 17, 933, 933, 0, 0],
        [625, 17, 0, 35581, 17, 934, 934, 0, 0], [625, 17, 0, 35605, 17, 934, 934, 0, 0], [625, 17, 0, 35629, 17, 935, 935, 0, 0],
        [625, 17, 0, 35654, 17, 936, 936, 0, 0], [625, 17, 0, 35677, 17, 937, 937, 0, 0], [625, 17, 0, 35701, 17, 938, 938, 0, 0],
        [625, 17, 0, 35726, 17, 939, 939, 0, 0], [625, 17, 0, 35749, 17, 940, 940, 0, 0], [625, 17, 0, 35773, 17, 941, 941, 0, 0],
        [625, 17, 0, 35798, 17, 942, 942, 0, 0], [625, 17, 0, 35821, 17, 942, 942, 0, 0]]  # R6

# pre1 = np.array(pre1)
# pre1 = pre1[np.newaxis, :, :]
# predict_1st(pre1, "")
pre2 = np.array(pre2)
pre2 = pre2[np.newaxis, :, :]
predict_1st(pre2, "")
# pre3 = np.array(pre3)
# pre3 = pre3[np.newaxis, :, :]
# predict_1st(pre3, "")
# predict(pre4)
# pre5 = np.array(pre5)
# pre5 = pre5[np.newaxis, :, :]
# predict_1st(pre5, "")
pre6 = np.array(pre6)
pre6 = pre6[np.newaxis, :, :]
predict_1st(pre6, "")

# 1st
# max 3831944120 min 0
# max 194 min 0
# max 651 min 0
# max 189 min 3
# max 1976 min 0
# max 327680 min 0
# max 75 min 0
# max 53792 min 10
# max 1638425 min 0
# max 188 min 3
# max 5885 min 3
# max 5885 min 3
# max 50 min 18
# max 2086 min 0
# max 421 min 0
# max 4 min 0
# max 19822 min 0
