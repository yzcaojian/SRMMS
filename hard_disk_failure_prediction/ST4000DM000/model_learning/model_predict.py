import tensorflow as tf
import numpy as np

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 一级健康度预测
@Time : 2021/5/24 16:52
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
    # 将SAMRT数据按照训练集同样的方式裁剪选择九个特征：4、9、12、187、193、197、198、241、242
    temp = [4, 9, 12, 187, 193, 197, 198, 241, 242]
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
    smart_max = [2690, 51311, 76, 65535, 786529, 60440, 60440, 68843842616, 921249276720]
    smart_min = [1, 0, 0, 0, 2, 0, 0, 0, 1614]
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
        saver.restore(sess, tf.train.latest_checkpoint('../hard_disk_failure_prediction/ST4000DM000/model_learning/model/'))

        prediction = sess.run(pred, feed_dict={x: smart_data_})
        print(prediction)
        # print(prediction.shape)  # 结果是二维数组
        print(np.max(prediction, axis=1))  # 概率最大的健康度预测结果
        for i in range(len(prediction[0])):
            if prediction[0][i] == np.max(prediction, axis=1):
                print(classes[i])


# 预测数据
pre1 = [[13, 43936, 13, 113, 9302, 616, 616, 60224817208, 265343691068], [13, 43960, 13, 117, 9302, 608, 608, 60234351768, 265516650592],
        [13, 43984, 13, 117, 9302, 608, 608, 60246286488, 265793475446], [13, 44007, 13, 118, 9302, 600, 600, 60252346792, 266156752130],
        [13, 44031, 13, 119, 9302, 600, 600, 60263742400, 266340259350], [13, 44055, 13, 119, 9302, 608, 608, 60273042712, 266564075754],
        [13, 44079, 13, 133, 9302, 664, 664, 60282768560, 266789651225], [13, 44103, 13, 134, 9302, 688, 688, 60291664640, 266918817201],
        [13, 44127, 13, 134, 9302, 688, 688, 60301284800, 267129703349], [13, 44151, 13, 134, 9302, 688, 688, 60310678144, 267338808433],
        [13, 44175, 13, 137, 9302, 688, 688, 60317475824, 267515442967], [13, 44198, 13, 137, 9302, 656, 656, 60329774120, 267613513635],
        [13, 44222, 13, 144, 9302, 640, 640, 60338894584, 267704207362], [13, 44246, 13, 144, 9302, 672, 672, 60347610992, 267858722065],
        [13, 44270, 13, 145, 9302, 672, 672, 60355999160, 268005721507], [13, 44294, 13, 150, 9302, 712, 712, 60368074976, 268152592399],
        [13, 44318, 13, 155, 9302, 736, 736, 60379156576, 268339233410], [13, 44342, 13, 160, 9302, 840, 840, 60391412888, 268472339015],
        [13, 44366, 13, 160, 9302, 864, 864, 60399217736, 268607903043], [13, 44389, 13, 178, 9302, 936, 936, 60407582456, 268756286998]]  # R1
pre2 = [[14, 44924, 14, 0, 6452, 0, 0, 63304851472, 268497343297], [14, 44948, 14, 0, 6452, 0, 0, 63310428776, 268681757554], [14, 44972, 14, 0, 6452, 0, 0, 63317989344, 268899838771],
        [14, 44996, 14, 0, 6452, 0, 0, 63323723048, 269145644214], [14, 45020, 14, 0, 6452, 0, 0, 63333847944, 269319613858], [14, 45044, 14, 0, 6452, 0, 0, 63337808328, 269564354727],
        [14, 45068, 14, 0, 6452, 0, 0, 63347332600, 269805369229], [14, 45092, 14, 0, 6452, 0, 0, 63354903312, 269974643750], [14, 45116, 14, 0, 6452, 0, 0, 63366619688, 270077790462],
        [14, 45139, 14, 0, 6452, 0, 0, 63376165360, 270251879779], [14, 45163, 14, 0, 6452, 0, 0, 63384790536, 270469765094], [14, 45187, 14, 0, 6452, 0, 0, 63391382080, 270542805876],
        [14, 45211, 14, 0, 6452, 0, 0, 63406890176, 270791958599], [14, 45235, 14, 0, 6452, 0, 0, 63421567752, 270945390697], [14, 45259, 14, 0, 6452, 0, 0, 63437973544, 271110269320],
        [14, 45283, 14, 0, 6452, 0, 0, 63446238208, 271234321208], [14, 45307, 14, 0, 6452, 0, 0, 63454024792, 271380866786], [14, 45331, 14, 0, 6452, 0, 0, 63462386736, 271566707518],
        [14, 45367, 14, 0, 6452, 0, 0, 63484429952, 271898062386], [14, 45379, 14, 0, 6452, 0, 0, 63489187576, 271981358368]]  # R2
pre3 = [[13, 40316, 12, 0, 7872, 0, 0, 55095770400, 247317243624], [13, 40340, 12, 0, 7872, 0, 0, 55106728440, 247590931025], [13, 40364, 12, 0, 7872, 0, 0, 55117944232, 247839535773],
        [13, 40388, 12, 0, 7872, 0, 0, 55133995960, 248108433683], [13, 40412, 12, 0, 7872, 0, 0, 55148068176, 248394730194], [13, 40436, 12, 0, 7872, 0, 0, 55159791352, 248684188932],
        [13, 40460, 12, 0, 7872, 0, 0, 55169488072, 248920899626], [13, 40484, 12, 0, 7872, 0, 0, 55187351264, 249095987658], [13, 40508, 12, 0, 7872, 0, 0, 55199326336, 249429273487],
        [13, 40532, 12, 0, 7872, 0, 0, 55214008224, 249730953719], [13, 40556, 12, 0, 7872, 0, 0, 55226153376, 250017155820], [13, 40580, 12, 0, 7872, 0, 0, 55236869584, 250305288981],
        [13, 40604, 12, 0, 7872, 0, 0, 55243131672, 250621980164], [13, 40628, 12, 0, 7872, 0, 0, 55250257888, 250856345069], [13, 40652, 12, 0, 7872, 0, 0, 55255628608, 251092480727],
        [13, 40676, 12, 0, 7872, 0, 0, 55262069712, 251378477427], [14, 40701, 13, 0, 7873, 0, 0, 55273307088, 251628404429], [14, 40725, 13, 0, 7873, 0, 0, 55280867336, 251914503537],
        [14, 40749, 13, 0, 7873, 0, 0, 55290083440, 252243029836], [14, 40773, 13, 0, 7873, 0, 0, 55301233496, 252526169879]]  # R3
pre4 = [[7, 42318, 7, 0, 13557, 0, 0, 58823964832, 211859060215], [7, 42342, 7, 0, 13557, 0, 0, 58839946168, 212034512424], [7, 42366, 7, 0, 13557, 0, 0, 58856079264, 212112061697],
        [7, 42390, 7, 0, 13557, 0, 0, 58870202832, 212205013650], [7, 42414, 7, 0, 13557, 0, 0, 58882791208, 212265255864], [7, 42438, 7, 0, 13557, 0, 0, 58896436384, 212477190099],
        [7, 42461, 7, 0, 13557, 0, 0, 58915932584, 212614600734], [7, 42485, 7, 0, 13557, 0, 0, 58938568528, 212832446303], [7, 42509, 7, 0, 13557, 0, 0, 58965325120, 213017137823],
        [7, 42533, 7, 0, 13557, 0, 0, 58975413488, 213187122521], [7, 42556, 7, 0, 13557, 0, 0, 59000821032, 213425291974], [7, 42580, 7, 0, 13557, 0, 0, 59031681664, 213744082470],
        [7, 42604, 7, 0, 13557, 0, 0, 59046749968, 214075831372], [7, 42628, 7, 0, 13557, 0, 0, 59059643200, 214383510710], [7, 42652, 7, 0, 13557, 0, 0, 59076482784, 214661353287],
        [7, 42676, 7, 0, 13557, 0, 0, 59094271984, 214915677212], [7, 42700, 7, 0, 13557, 0, 0, 59112056648, 215059927966], [7, 42724, 7, 0, 13557, 0, 0, 59124333656, 215178374103],
        [7, 42760, 7, 0, 13557, 0, 0, 59155035840, 215472931244], [7, 42784, 7, 0, 13557, 0, 0, 59173958112, 215699112542]]  # R4
pre5 = [[21, 38160, 21, 0, 9820, 0, 0, 59109648032, 190801691467], [21, 38184, 21, 0, 9820, 0, 0, 59123918888, 191075933026], [22, 38208, 22, 0, 9822, 0, 0, 59143795400, 191346885984],
        [22, 38232, 22, 0, 9822, 0, 0, 59174708248, 191538781422], [22, 38256, 22, 0, 9822, 0, 0, 59194963176, 191745295218], [22, 38280, 22, 0, 9822, 0, 0, 59213005944, 191828439359],
        [22, 38303, 22, 0, 9822, 0, 0, 59228893824, 191969006862], [22, 38327, 22, 0, 9822, 0, 0, 59245659920, 192163975352], [22, 38351, 22, 0, 9823, 0, 0, 59261668408, 192347310223],
        [22, 38375, 22, 0, 9823, 0, 0, 59280320576, 192471913751], [22, 38399, 22, 0, 9823, 0, 0, 59294198840, 192730612590], [22, 38423, 22, 0, 9823, 0, 0, 59312224368, 192931418065],
        [22, 38447, 22, 0, 9823, 0, 0, 59331268328, 192988620641], [22, 38471, 22, 0, 9823, 0, 0, 59353185328, 193143198319], [22, 38494, 22, 0, 9824, 0, 0, 59375012184, 193309372896],
        [22, 38519, 22, 0, 9824, 0, 0, 59398508832, 193509668717], [22, 38543, 22, 0, 9824, 0, 0, 59424450448, 193697011524], [22, 38567, 22, 0, 9824, 0, 0, 59448200200, 193867534144],
        [23, 38590, 23, 0, 9832, 0, 0, 59471832272, 194085413353], [23, 38614, 23, 0, 9832, 0, 0, 59493596760, 194158507423]]  # R5
pre6 = [[14, 31477, 14, 0, 208339, 0, 0, 31285253728, 152615521354], [14, 31501, 14, 0, 208342, 0, 0, 31286893176, 152747384676], [14, 31525, 14, 0, 208344, 0, 0, 31300928448, 152934996454],
        [14, 31549, 14, 0, 208347, 0, 0, 31302674616, 153173810640], [14, 31573, 14, 0, 208349, 0, 0, 31316590968, 153394976175], [14, 31596, 14, 0, 208386, 0, 0, 31318588232, 153619550322],
        [14, 31620, 14, 0, 208387, 0, 0, 31322112888, 153928151973], [14, 31644, 14, 0, 208391, 0, 0, 31324558144, 154153531242], [14, 31669, 14, 0, 208393, 0, 0, 31327363424, 154331695816],
        [14, 31693, 14, 0, 208393, 0, 0, 31340983392, 154597497767], [14, 31717, 14, 0, 208397, 0, 0, 31343646592, 154906087826], [14, 31741, 14, 0, 208416, 0, 0, 31357382592, 155154102884],
        [14, 31765, 14, 0, 208441, 0, 0, 31360662800, 155464360818], [14, 31789, 14, 0, 208445, 0, 0, 31363245936, 155717622617], [14, 31813, 14, 0, 208449, 0, 0, 31366322208, 155877622638],
        [14, 31837, 14, 0, 208452, 0, 0, 31368502312, 156119886789], [14, 31861, 14, 0, 208454, 0, 0, 31382710064, 156446917419], [14, 31885, 14, 0, 208493, 0, 0, 31385046680, 156718966819],
        [14, 31909, 14, 0, 208503, 0, 0, 31400266968, 157012277755], [14, 31933, 14, 0, 208507, 0, 0, 31403320536, 157268218414]]  # R6

# pre1 = np.array(pre1)
# pre1 = pre1[np.newaxis, :, :]
# predict_1st(pre1, "")
# predict(pre2)
# pre3 = np.array(pre3)
# pre3 = pre3[np.newaxis, :, :]
# predict_1st(pre3, "")
# predict(pre4)
# predict(pre5)
pre6 = np.array(pre6)
pre6 = pre6[np.newaxis, :, :]
predict_1st(pre6, "")

# 1st
# max 244140616 min 0
# max 0 min 0
# max 2690 min 1
# max 65392 min 0
# max 281471681281690 min 6
# max 51311 min 0
# max 0 min 0
# max 76 min 0
# max 6032 min 0
# max 254 min 0
# max 65535 min 0
# max 8933668292646 min 0
# max 264 min 0
# max 141 min 12
# max 0 min 0
# max 2656 min 0
# max 786529 min 2
# max 141 min 12
# max 60440 min 0
# max 60440 min 0
# max 5415 min 0
# max 281453501897496 min 0
# max 68843842616 min 0
# max 921249276720 min 1614
