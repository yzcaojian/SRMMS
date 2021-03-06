import tensorflow as tf
import numpy as np

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 二级健康度预测
@Time : 2021/5/24 16:55
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
    # 将SAMRT数据按照训练集同样的方式裁剪选择九个特征：1、9、187、193、194、197、198、241、242
    temp = [1, 9, 187, 193, 194, 197, 198, 241, 242]
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
    smart_max = [244133784, 51311, 65535, 2656, 786529, 141, 60440, 68843842616, 921249276720]
    smart_min = [0, 0, 0, 0, 4, 14, 0, 0, 3912]
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
        # saver = tf.train.import_meta_graph('./model/hdd_GRU_model.ckpt.meta')  # 不能加这一步
        saver.restore(sess, tf.train.latest_checkpoint('./resources/hard_disk_failure_prediction/ST4000DM000/model_learning/model_2/'))

        prediction = sess.run(pred, feed_dict={x: smart_data})
        print(prediction)
        # print(prediction.shape)  # 结果是二维数组
        print(np.max(prediction, axis=1))  # 概率最大的健康度预测结果
        for i in range(len(prediction[0])):
            if prediction[0][i] == np.max(prediction, axis=1):
                return classes[i]


# 预测数据
pre1 = [[98055032, 44007, 118, 9302, 21, 600, 600, 60252346792, 266156752130], [146155976, 44031, 119, 9302, 21, 600, 600, 60263742400, 266340259350],
        [64838608, 44055, 119, 9302, 21, 608, 608, 60273042712, 266564075754], [211848120, 44079, 133, 9302, 21, 664, 664, 60282768560, 266789651225],
        [234734480, 44103, 134, 9302, 21, 688, 688, 60291664640, 266918817201], [68823264, 44127, 134, 9302, 21, 688, 688, 60301284800, 267129703349],
        [16833304, 44151, 134, 9302, 21, 688, 688, 60310678144, 267338808433], [64725976, 44175, 137, 9302, 21, 688, 688, 60317475824, 267515442967],
        [200252480, 44198, 137, 9302, 21, 656, 656, 60329774120, 267613513635], [112725736, 44222, 144, 9302, 21, 640, 640, 60338894584, 267704207362],
        [92370048, 44246, 144, 9302, 21, 672, 672, 60347610992, 267858722065], [231854168, 44270, 145, 9302, 21, 672, 672, 60355999160, 268005721507],
        [53214056, 44294, 150, 9302, 21, 712, 712, 60368074976, 268152592399], [37645040, 44318, 155, 9302, 21, 736, 736, 60379156576, 268339233410],
        [126225808, 44342, 160, 9302, 22, 840, 840, 60391412888, 268472339015], [106413528, 44366, 160, 9302, 22, 864, 864, 60399217736, 268607903043],
        [71496064, 44389, 178, 9302, 21, 936, 936, 60407582456, 268756286998], [235697920, 44413, 180, 9302, 21, 952, 952, 60417804792, 268893651664],
        [59623896, 44437, 185, 9302, 21, 1000, 1000, 60429335640, 269123156267], [73056600, 44461, 189, 9302, 21, 992, 992, 60435541848, 269233274681]]  # R1-1
pre2 = [[131710360, 44770, 0, 13558, 27, 0, 0, 60186786424, 237871446900], [143315760, 44793, 3, 13558, 26, 64, 64, 60197426536, 238103981093],
        [146828392, 44817, 3, 13558, 27, 64, 64, 60206385984, 238360427095],[149682208, 44841, 3, 13558, 26, 64, 64, 60216598144, 238482718657],
        [229406872, 44865, 3, 13558, 26, 64, 64, 60224588904, 238704542405], [206825400, 44889, 3, 13558, 26, 64, 64, 60237708232, 238818166564],
        [106334360, 44913, 3, 13558, 27, 64, 64, 60251453880, 238970825728], [129377136, 44937, 3, 13558, 28, 64, 64, 60271848416, 239121321190],
        [62387688, 44961, 3, 13558, 26, 568, 568, 60285130848, 239238145865], [234104296, 44985, 3, 13558, 27, 568, 568, 60295800424, 239423999153],
        [24938280, 45008, 5, 13558, 27, 568, 568, 60307815816, 239561392437], [88341688, 45032, 8, 13558, 27, 568, 568, 60328484264, 239734159964],
        [142103112, 45056, 8, 13558, 26, 568, 568, 60342335120, 239813159897], [68610096, 45080, 8, 13558, 26, 568, 568, 60353030688, 239868011933],
        [231427672, 45104, 8, 13558, 26, 568, 568, 60363599736, 240050322872], [187041328, 45128, 8, 13558, 27, 568, 568, 60378158816, 240200279769],
        [183416624, 45152, 8, 13558, 27, 528, 528, 60392735432, 240384346583], [151591056, 45176, 8, 13558, 27, 528, 528, 60401957400, 240642460050],
        [84270136, 45200, 8, 13558, 26, 528, 528, 60411292440, 240951992152], [217138224, 45224, 8, 13558, 27, 560, 560, 60437564944, 241112042563]]  # R1-2
pre3 = [[176799160, 43444, 0, 10021, 27, 0, 0, 62301233136, 335569952833], [115231928, 43468, 0, 10021, 27, 0, 0, 62332893296, 335766259942], [3808512, 43492, 0, 10021, 27, 0, 0, 62355677448, 335844964146],
        [33827496, 43515, 0, 10022, 27, 0, 0, 62377530472, 335989403505], [169403584, 43539, 0, 10022, 27, 0, 0, 62402085040, 336167222665], [229314448, 43563, 0, 10022, 28, 0, 0, 62438310640, 336353376001],
        [50519208, 43587, 0, 10022, 27, 0, 0, 62461699288, 336496109403], [205412912, 43611, 0, 10022, 27, 0, 0, 62480670848, 336706533850], [137127040, 43635, 0, 10022, 27, 0, 0, 62500951120, 336894962071],
        [75945056, 43658, 0, 10022, 27, 0, 0, 62520372064, 336987118752], [232337304, 43682, 0, 10023, 27, 0, 0, 62544928208, 337134166244], [202473096, 43706, 0, 10023, 27, 0, 0, 62561083720, 337349916445],
        [199967280, 43730, 0, 10023, 27, 0, 0, 62577611656, 337537186922], [205141192, 43754, 0, 10026, 28, 0, 0, 62600955616, 337662508205], [66193352, 43778, 0, 10026, 28, 0, 0, 62621138016, 337889316699],
        [119996680, 43801, 0, 10026, 27, 0, 0, 62649213448, 338073879063], [10422432, 43825, 0, 10026, 28, 0, 0, 62663228488, 338152549363], [243861704, 43849, 0, 10027, 28, 0, 0, 62676163224, 338425799466],
        [22182720, 43873, 0, 10027, 28, 0, 0, 62690337112, 338784458510], [90194024, 43897, 0, 10027, 27, 0, 0, 62699876304, 339142768698]]  # R1-3

# pre1 = np.array(pre1)
# pre1 = pre1[np.newaxis, :, :]
# predict_2nd(pre1, "")
# pre2 = np.array(pre2)
# pre2 = pre2[np.newaxis, :, :]
# predict_2nd(pre2, "")
pre3 = np.array(pre3)
pre3 = pre3[np.newaxis, :, :]
predict_2nd(pre3, "")

# 2nd
# max 244133784 min 0
# max 0 min 0
# max 2690 min 1
# max 65392 min 0
# max 281471681281690 min 7
# max 51311 min 0
# max 0 min 0
# max 76 min 0
# max 6032 min 0
# max 254 min 0
# max 65535 min 0
# max 4295032837 min 0
# max 264 min 0
# max 141 min 14
# max 0 min 0
# max 2656 min 0
# max 786529 min 4
# max 141 min 14
# max 60440 min 0
# max 60440 min 0
# max 5415 min 0
# max 281148559218533 min 0
# max 68843842616 min 0
# max 921249276720 min 3912
